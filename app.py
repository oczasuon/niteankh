import os
import secrets
from datetime import datetime, timedelta, timezone

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

import storage
import telegram_userbot
import telegram_verify
from helpers import (
    REDEEM_CODES, TOPUP_PACKAGES, VIP_PLANS, add_guest_watch_seconds, calculate_coins_for_khr,
    get_categories, get_current_user, get_setting, guest_time_limit_reached,
    guest_would_exceed_movie_limit, login_required, register_guest_movie_view,
    safe_redirect_target, verify_telegram_auth,
)
from models import BankTransaction, Episode, HistoryItem, Movie, MyListItem, User, WalletTransaction, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
oauth = OAuth()


def get_database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return f"sqlite:///{os.path.join(BASE_DIR, 'niteankh.db')}"
    # Some providers (Heroku-style) hand out postgres:// — SQLAlchemy 1.4+ wants postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url


def create_app(start_services=True):
    """start_services=False is for one-off scripts/diagnostics (seeding, DB
    queries in a shell, etc.) — it skips opening the live Telegram session and
    starting the background poller, so running a quick script doesn't spin up
    a second concurrent connection alongside an already-running server."""
    app = Flask(__name__)
    # Trusts X-Forwarded-Proto/Host from the reverse proxy (Cloudflare) in front
    # of the Pi, so url_for(..., _external=True) generates https:// URLs — the
    # app itself is only ever reached over plain HTTP from the tunnel.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB upload cap

    storage.ensure_local_dirs()

    db.init_app(app)

    oauth.init_app(app)
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_OAUTH_ENABLED'] = bool(google_client_id and google_client_secret)
    if app.config['GOOGLE_OAUTH_ENABLED']:
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    app.config['TELEGRAM_LOGIN_BOT_TOKEN'] = os.environ.get('TELEGRAM_LOGIN_BOT_TOKEN')
    app.config['TELEGRAM_LOGIN_BOT_USERNAME'] = os.environ.get('TELEGRAM_LOGIN_BOT_USERNAME')

    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    app.jinja_env.globals['media_url'] = storage.file_url

    # The dev server runs with use_reloader=False specifically so create_app()
    # only ever executes once per process — these background connections
    # (a live Telegram session in particular) must not be started twice.
    if start_services:
        telegram_verify.start_background_poller(app)
        telegram_userbot.start_userbot_listener(app)

    @app.context_processor
    def inject_globals():
        return dict(
            current_user=get_current_user(), categories=get_categories(),
            telegram_login_bot_username=app.config['TELEGRAM_LOGIN_BOT_USERNAME'],
        )

    register_routes(app)
    return app


def register_routes(app):

    @app.route('/')
    def index():
        hero_movies = Movie.query.filter_by(featured=True).order_by(Movie.created_at.desc()).limit(5).all()
        if len(hero_movies) < 5:
            existing_ids = [m.id for m in hero_movies]
            fill_query = Movie.query.order_by(Movie.rating.desc())
            if existing_ids:
                fill_query = fill_query.filter(Movie.id.notin_(existing_ids))
            hero_movies += fill_query.limit(5 - len(hero_movies)).all()

        page = request.args.get('page', 1, type=int)
        pagination = Movie.query.order_by(Movie.id.asc()).paginate(page=page, per_page=30, error_out=False)
        return render_template('index.html', hero_movies=hero_movies, movies=pagination.items, pagination=pagination)

    @app.route('/movies')
    def movies():
        category = request.args.get('category', 'all')
        sort = request.args.get('sort', 'popular')
        page = request.args.get('page', 1, type=int)

        query = Movie.query
        if category != 'all':
            query = query.filter_by(category=category)

        if sort == 'newest':
            query = query.order_by(Movie.year.desc(), Movie.id.asc())
        elif sort == 'rating':
            query = query.order_by(Movie.rating.desc())
        else:
            query = query.order_by(Movie.id.asc())

        pagination = query.paginate(page=page, per_page=24, error_out=False)
        return render_template('movies.html', movies=pagination.items, pagination=pagination,
                                category=category, sort=sort)

    @app.route('/search')
    def search():
        q = request.args.get('q', '').strip()
        category = request.args.get('category', 'all')
        page = request.args.get('page', 1, type=int)

        query = Movie.query
        if q:
            query = query.filter(Movie.title.ilike(f'%{q}%'))
        if category != 'all':
            query = query.filter_by(category=category)

        pagination = query.order_by(Movie.id.asc()).paginate(page=page, per_page=24, error_out=False)
        return render_template('search.html', movies=pagination.items, pagination=pagination, q=q, category=category)

    @app.route('/watch/<int:movie_id>')
    def watch(movie_id):
        movie = Movie.query.get_or_404(movie_id)
        ep = request.args.get('ep', 1, type=int)
        ep = max(1, min(ep, movie.total_episodes))

        user = get_current_user()
        vip_locked = movie.vip and not (user and user.is_vip_active)

        in_list = False
        if user:
            in_list = MyListItem.query.filter_by(user_id=user.id, movie_id=movie.id).first() is not None
            existing = HistoryItem.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            if existing:
                existing.episode_num = ep
                existing.watched_at = datetime.now(timezone.utc)
            else:
                db.session.add(HistoryItem(user_id=user.id, movie_id=movie.id, episode_num=ep))
            db.session.commit()

        # Guests get a taste — up to 2 distinct movies or 8 minutes of actual
        # playback, whichever comes first — then have to register to continue.
        guest_gate = False
        if not user:
            if guest_time_limit_reached() or guest_would_exceed_movie_limit(movie.id):
                guest_gate = True
            else:
                register_guest_movie_view(movie.id)

        same_category = Movie.query.filter(Movie.category == movie.category, Movie.id != movie.id).limit(8).all()
        related = same_category
        if len(related) < 8:
            related += Movie.query.filter(Movie.category != movie.category).limit(8 - len(related)).all()

        episode = Episode.query.filter_by(movie_id=movie.id, episode_num=ep).first()

        # Per-episode file, then per-episode embed, then the movie's own
        # default file, then the movie's own default embed.
        if episode and episode.video_filename:
            player_type, player_value = 'file', episode.video_filename
        elif episode and episode.embed_url:
            player_type, player_value = 'embed', episode.embed_url
        elif movie.video_filename:
            player_type, player_value = 'file', movie.video_filename
        elif movie.embed_url:
            player_type, player_value = 'embed', movie.embed_url
        else:
            player_type, player_value = None, None

        return render_template('watch.html', movie=movie, ep=ep, vip_locked=vip_locked, guest_gate=guest_gate,
                                in_list=in_list, related=related, player_type=player_type, player_value=player_value)

    @app.post('/watch/track-progress')
    def track_progress():
        # Logged-in users aren't rate-limited, so there's nothing to track for them.
        if get_current_user():
            return jsonify(gate=False)

        seconds = (request.get_json(silent=True) or {}).get('seconds', 0)
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            seconds = 0
        add_guest_watch_seconds(seconds)
        return jsonify(gate=guest_time_limit_reached())

    @app.post('/mylist/toggle/<int:movie_id>')
    @login_required
    def toggle_mylist(movie_id):
        user = get_current_user()
        item = MyListItem.query.filter_by(user_id=user.id, movie_id=movie_id).first()
        if item:
            db.session.delete(item)
            in_list = False
        else:
            db.session.add(MyListItem(user_id=user.id, movie_id=movie_id))
            in_list = True
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'fetch':
            return jsonify(in_list=in_list)
        return redirect(safe_redirect_target(request.referrer and request.referrer.replace(request.host_url.rstrip('/'), '')) or url_for('index'))

    @app.route('/membership')
    def membership():
        return render_template('membership.html', vip_plans=VIP_PLANS)

    @app.route('/wallet')
    @login_required
    def wallet():
        user = get_current_user()
        tx = WalletTransaction.query.filter_by(user_id=user.id).order_by(WalletTransaction.created_at.desc()).limit(50).all()
        return render_template('wallet.html', packages=TOPUP_PACKAGES, vip_plans=VIP_PLANS, tx=tx,
                                payment_qr_filename=get_setting('payment_qr_filename'))

    @app.post('/wallet/topup')
    @login_required
    def wallet_topup():
        user = get_current_user()

        bank_name = request.form.get('bank_name', '').strip()
        bank_ref = request.form.get('bank_ref', '').strip()
        if not bank_name or not bank_ref:
            flash('សូមបំពេញឈ្មោះគណនី និងលេខយោងធនាគារ', 'error')
            return redirect(url_for('wallet'))

        # Give the poller one more chance to have picked up a just-arrived message.
        telegram_verify.poll_once()

        bank_tx = BankTransaction.query.filter(
            db.func.lower(BankTransaction.reference) == bank_ref.lower(),
            BankTransaction.matched.is_(False),
        ).first()

        if not bank_tx:
            flash('រកមិនឃើញប្រតិបត្តិការនេះទេ។ សូមប្រាកដថា Hash ឬ TXN ID ត្រឹមត្រូវ ហើយសាកល្បងម្តងទៀតបន្តិចទៀត', 'error')
            return redirect(url_for('wallet'))

        if not telegram_verify.names_roughly_match(bank_name, bank_tx.sender_name):
            flash('ឈ្មោះមិនត្រូវនឹងអ្នកផ្ទេរប្រាក់ក្នុងប្រតិបត្តិការនេះទេ។ សូមបញ្ចូលឈ្មោះឲ្យត្រឹមត្រូវ', 'error')
            return redirect(url_for('wallet'))

        # Coins are computed from what was actually paid, not a selected package —
        # a discounted rate for exact package amounts, base rate for anything else.
        coins = calculate_coins_for_khr(bank_tx.amount_khr)

        bank_tx.matched = True
        bank_tx.matched_user_id = user.id
        user.balance += coins
        db.session.add(WalletTransaction(
            user_id=user.id, desc=f"បញ្ចូលកាបូប ({bank_tx.amount_khr:,}៛)", amount=coins, type='topup',
            bank_name=bank_name, bank_ref=bank_ref,
        ))
        db.session.commit()
        flash(f'បញ្ជាក់ការទូទាត់ជោគជ័យ! បានទទួល {coins:,} កាក់', 'success')
        return redirect(url_for('wallet'))

    @app.post('/wallet/buy-vip')
    @login_required
    def wallet_buy_vip():
        user = get_current_user()
        idx = request.form.get('plan', type=int, default=0)
        idx = max(0, min(idx, len(VIP_PLANS) - 1))
        plan = VIP_PLANS[idx]

        if user.balance < plan['cost']:
            flash('សមតុល្យមិនគ្រប់គ្រាន់ សូមបញ្ចូលកាបូបជាមុន', 'error')
            return redirect(url_for('wallet'))

        user.balance -= plan['cost']
        base = user.vip_expiry.replace(tzinfo=timezone.utc) if (user.vip_expiry and user.is_vip_active) else datetime.now(timezone.utc)
        user.vip_expiry = base + timedelta(days=plan['days'])
        db.session.add(WalletTransaction(user_id=user.id, desc=f"ទិញសមាជិកភាព VIP {plan['days']} ថ្ងៃ", amount=-plan['cost'], type='vip'))
        db.session.commit()
        flash(f"ទិញ VIP {plan['label']} ជោគជ័យ!", 'success')
        return redirect(url_for('wallet'))

    @app.post('/wallet/redeem')
    @login_required
    def wallet_redeem():
        user = get_current_user()
        code = request.form.get('code', '').strip().upper()
        coins = REDEEM_CODES.get(code)
        if coins:
            user.balance += coins
            db.session.add(WalletTransaction(user_id=user.id, desc=f'ប្រើកូដ {code}', amount=coins, type='redeem'))
            db.session.commit()
            flash(f'ទទួលបាន {coins} កាក់ពីកូដ {code}', 'success')
        else:
            flash('កូដមិនត្រឹមត្រូវ ឬបានប្រើរួច', 'error')
        return redirect(url_for('wallet'))

    @app.route('/profile')
    @login_required
    def profile():
        user = get_current_user()
        my_list = MyListItem.query.filter_by(user_id=user.id).order_by(MyListItem.created_at.desc()).all()
        history = HistoryItem.query.filter_by(user_id=user.id).order_by(HistoryItem.watched_at.desc()).all()
        return render_template('profile.html', my_list=my_list, history=history)

    @app.post('/profile/settings')
    @login_required
    def profile_settings():
        user = get_current_user()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        sex = request.form.get('sex', '').strip()
        dob = request.form.get('dob', '').strip()
        location = request.form.get('location', '').strip()

        if name:
            user.name = name
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                flash('អ៊ីមែលនេះត្រូវបានប្រើរួចហើយ', 'error')
                return redirect(url_for('profile'))
            user.email = email

        user.phone = phone or None
        user.sex = sex if sex in ('male', 'female', 'other') else None
        user.location = location or None
        if dob:
            try:
                user.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                flash('ថ្ងៃខែឆ្នាំកំណើតមិនត្រឹមត្រូវទេ', 'error')
                return redirect(url_for('profile'))
        else:
            user.dob = None

        db.session.commit()
        flash('បានរក្សាទុករួចរាល់', 'success')
        return redirect(url_for('profile'))

    @app.post('/profile/change-password')
    @login_required
    def profile_change_password():
        user = get_current_user()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not user.check_password(current_password):
            flash('ពាក្យសម្ងាត់បច្ចុប្បន្នមិនត្រឹមត្រូវទេ', 'error')
        elif len(new_password) < 6:
            flash('ពាក្យសម្ងាត់ថ្មីត្រូវមានយ៉ាងតិច ៦ តួ', 'error')
        elif new_password != confirm_password:
            flash('ការបញ្ជាក់ពាក្យសម្ងាត់ថ្មីមិនត្រូវគ្នាទេ', 'error')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('បានប្តូរពាក្យសម្ងាត់រួចរាល់', 'success')
        return redirect(url_for('profile'))

    @app.post('/profile/history/clear')
    @login_required
    def clear_history():
        user = get_current_user()
        HistoryItem.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return redirect(url_for('profile'))

    @app.route('/login/google')
    def login_google():
        if not app.config['GOOGLE_OAUTH_ENABLED']:
            flash('ការចូលប្រើតាម Google មិនទាន់អាចប្រើបានទេ', 'error')
            return redirect(url_for('login'))
        next_target = safe_redirect_target(request.args.get('next'))
        if next_target:
            session['login_next'] = next_target
        redirect_uri = url_for('login_google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @app.route('/login/google/callback')
    def login_google_callback():
        if not app.config['GOOGLE_OAUTH_ENABLED']:
            return redirect(url_for('login'))
        try:
            token = oauth.google.authorize_access_token()
            userinfo = token.get('userinfo') or oauth.google.userinfo(token=token)
        except Exception:
            flash('ការចូលប្រើតាម Google មិនបានសម្រេចទេ សូមព្យាយាមម្តងទៀត', 'error')
            return redirect(url_for('login'))

        google_id = userinfo.get('sub')
        email = (userinfo.get('email') or '').strip().lower()
        name = userinfo.get('name') or (email.split('@')[0] if email else 'អ្នកប្រើប្រាស់')

        if not google_id or not email:
            flash('មិនអាចទទួលបានព័ត៌មានគណនី Google បានទេ', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id  # link Google to an existing email/password account
            else:
                user = User(name=name, email=email, google_id=google_id)
                user.set_password(secrets.token_urlsafe(32))  # unusable random password
                db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        target = safe_redirect_target(session.pop('login_next', None))
        return redirect(target or url_for('index'))

    @app.route('/login/telegram/callback')
    def login_telegram_callback():
        bot_token = app.config['TELEGRAM_LOGIN_BOT_TOKEN']
        if not bot_token:
            flash('ការចូលប្រើតាម Telegram មិនទាន់អាចប្រើបានទេ', 'error')
            return redirect(url_for('login'))

        data = request.args.to_dict()
        next_target = safe_redirect_target(data.pop('next', None))
        if not verify_telegram_auth(data, bot_token):
            flash('ការផ្ទៀងផ្ទាត់ Telegram មិនត្រឹមត្រូវទេ', 'error')
            return redirect(url_for('login'))

        telegram_id = data.get('id')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        username = data.get('username', '').strip()
        name = f'{first_name} {last_name}'.strip() or username or 'អ្នកប្រើប្រាស់ Telegram'

        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(name=name, email=f'tg{telegram_id}@telegram.niteankh.local', telegram_id=telegram_id)
            user.set_password(secrets.token_urlsafe(32))  # unusable random password
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        return redirect(next_target or url_for('index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                target = safe_redirect_target(request.args.get('next'))
                return redirect(target or url_for('index'))
            flash('អ៊ីមែល ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវ', 'error')
        return render_template('login.html')

    @app.route('/signup', methods=['POST'])
    def signup():
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('សូមបំពេញព័ត៌មានទាំងអស់', 'error')
            return redirect(url_for('login'))
        if len(password) < 6:
            flash('ពាក្យសម្ងាត់ត្រូវមានយ៉ាងតិច ៦ តួអក្សរ', 'error')
            return redirect(url_for('login'))
        if User.query.filter_by(email=email).first():
            flash('អ៊ីមែលនេះមានគណនីរួចហើយ', 'error')
            return redirect(url_for('login'))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))


if __name__ == '__main__':
    application = create_app()
    # use_reloader=False: the reloader spawns a second process that also runs
    # create_app(), which would open a second live Telegram session from the
    # same credentials. Restart the process manually after code changes instead.
    application.run(debug=True, use_reloader=False)
