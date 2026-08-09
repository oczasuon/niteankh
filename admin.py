import secrets
from datetime import datetime, timezone

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

import storage
import telegram_userbot
from helpers import admin_required, get_categories, get_current_user, get_setting, set_setting, staff_required, to_embeddable_url
from models import Category, Episode, Movie, User, WalletTransaction, db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.is_staff and user.check_password(password):
            session['user_id'] = user.id
            if user.role == User.ROLE_POSTER:
                return redirect(url_for('admin.upload'))
            return redirect(url_for('admin.dashboard'))
        flash('ព័ត៌មានចូលប្រើមិនត្រឹមត្រូវ', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_movies = Movie.query.count()
    admin_uploads = Movie.query.filter_by(is_admin_upload=True).count()
    vip_count = Movie.query.filter_by(vip=True).count()
    recent = Movie.query.filter_by(is_admin_upload=True).order_by(Movie.created_at.desc()).limit(8).all()
    return render_template('admin/dashboard.html', total_movies=total_movies, admin_uploads=admin_uploads,
                            vip_count=vip_count, category_count=len(get_categories()), recent=recent)


@admin_bp.route('/upload', methods=['GET', 'POST'], defaults={'movie_id': None})
@admin_bp.route('/upload/<int:movie_id>', methods=['GET', 'POST'])
@staff_required
def upload(movie_id):
    movie = Movie.query.get_or_404(movie_id) if movie_id else None
    if movie and not movie.is_admin_upload:
        flash('ខ្លឹមសារកសាងស្រាប់ មិនអាចកែសម្រួលបានទេ', 'error')
        return redirect(url_for('admin.manage'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '')
        quality = request.form.get('quality', 'FHD')
        total_episodes = request.form.get('total_episodes', type=int, default=12)
        year = request.form.get('year', type=int, default=2026)
        rating = request.form.get('rating', type=float, default=8.0)
        vip = request.form.get('vip') == 'on'
        featured = request.form.get('featured') == 'on'
        description = request.form.get('description', '').strip()
        bg_grad = request.form.get('bg_grad', 'from-teal-800 via-purple-900 to-rose-900')

        video_file = request.files.get('video')
        embed_url_input = request.form.get('embed_url', '').strip()
        thumb_file = request.files.get('thumbnail')
        slide_file = request.files.get('slide_image')
        remove_thumb = request.form.get('remove_thumbnail') == '1'

        if not title:
            flash('សូមបញ្ចូលចំណងជើងរឿង', 'error')
            return redirect(request.url)

        has_new_video = bool(video_file and video_file.filename)
        if movie is None and not has_new_video and not embed_url_input:
            flash('សូមជ្រើសរើសឯកសារវីដេអូ ឬបញ្ចូលតំណ Embed មុននឹងបង្ហោះ', 'error')
            return redirect(request.url)

        has_existing_slide = movie and movie.slide_image_filename
        if featured and not has_existing_slide and (not slide_file or slide_file.filename == ''):
            flash('សូមផ្ទុករូបភាព Slide ព្រោះអ្នកបានជ្រើសរើសបង្ហាញនៅ Hero Slider', 'error')
            return redirect(request.url)

        if movie is None:
            movie = Movie(is_admin_upload=True)
            db.session.add(movie)

        movie.title = title
        movie.category = category
        movie.quality = quality
        movie.total_episodes = max(1, total_episodes or 1)
        movie.year = year or 2026
        movie.rating = max(0.0, min(10.0, rating or 0.0))
        movie.vip = vip
        movie.featured = featured
        movie.description = description
        movie.bg_grad = bg_grad

        if video_file and video_file.filename:
            new_filename = storage.save_file(video_file, 'videos', storage.ALLOWED_VIDEO_EXT)
            if new_filename:
                storage.delete_file('videos', movie.video_filename)
                movie.video_filename = new_filename
                movie.embed_url = None  # a direct upload replaces any embed link
            else:
                flash('ប្រភេទឯកសារវីដេអូមិនត្រូវបានអនុញ្ញាតទេ', 'error')
                return redirect(request.url)
        elif embed_url_input:
            storage.delete_file('videos', movie.video_filename)  # switching to embed replaces any uploaded file
            movie.video_filename = None
            movie.embed_url = to_embeddable_url(embed_url_input)

        if thumb_file and thumb_file.filename:
            new_thumb = storage.save_file(thumb_file, 'thumbnails', storage.ALLOWED_IMAGE_EXT)
            if new_thumb:
                storage.delete_file('thumbnails', movie.thumbnail_filename)
                movie.thumbnail_filename = new_thumb
        elif remove_thumb and movie.thumbnail_filename:
            storage.delete_file('thumbnails', movie.thumbnail_filename)
            movie.thumbnail_filename = None

        if slide_file and slide_file.filename:
            new_slide = storage.save_file(slide_file, 'slides', storage.ALLOWED_IMAGE_EXT)
            if new_slide:
                storage.delete_file('slides', movie.slide_image_filename)
                movie.slide_image_filename = new_slide
            else:
                flash('ប្រភេទឯកសាររូបភាព Slide មិនត្រូវបានអនុញ្ញាតទេ', 'error')
                return redirect(request.url)

        if not featured and movie.slide_image_filename:
            storage.delete_file('slides', movie.slide_image_filename)
            movie.slide_image_filename = None

        db.session.commit()
        flash('បានរក្សាទុករួចរាល់', 'success')
        return redirect(url_for('admin.upload', movie_id=movie.id))

    episodes_by_num = {}
    if movie:
        episodes_by_num = {e.episode_num: e for e in Episode.query.filter_by(movie_id=movie.id).all()}

    return render_template('admin/upload.html', movie=movie, categories=get_categories(), episodes_by_num=episodes_by_num)


@admin_bp.post('/upload/<int:movie_id>/episode/<int:ep_num>')
@staff_required
def upload_episode(movie_id, ep_num):
    movie = Movie.query.get_or_404(movie_id)
    if not movie.is_admin_upload:
        flash('ខ្លឹមសារកសាងស្រាប់ មិនអាចកែសម្រួលបានទេ', 'error')
        return redirect(url_for('admin.manage'))
    if ep_num < 2 or ep_num > movie.total_episodes:
        flash('ភាគទី១ប្រើវីដេអូចម្បង សូមកែវីដេអូនៅផ្នែក "ឯកសារវីដេអូ" ខាងលើ', 'error')
        return redirect(url_for('admin.upload', movie_id=movie_id))

    video_file = request.files.get('video')
    embed_url_input = request.form.get('embed_url', '').strip()
    has_new_video = bool(video_file and video_file.filename)

    if not has_new_video and not embed_url_input:
        flash('សូមជ្រើសរើសឯកសារវីដេអូ ឬបញ្ចូលតំណ Embed', 'error')
        return redirect(url_for('admin.upload', movie_id=movie_id))

    episode = Episode.query.filter_by(movie_id=movie_id, episode_num=ep_num).first()
    if not episode:
        episode = Episode(movie_id=movie_id, episode_num=ep_num)
        db.session.add(episode)

    if has_new_video:
        filename = storage.save_file(video_file, 'videos', storage.ALLOWED_VIDEO_EXT)
        if not filename:
            flash('ប្រភេទឯកសារវីដេអូមិនត្រូវបានអនុញ្ញាតទេ', 'error')
            return redirect(url_for('admin.upload', movie_id=movie_id))
        storage.delete_file('videos', episode.video_filename)
        episode.video_filename = filename
        episode.embed_url = None
    else:
        storage.delete_file('videos', episode.video_filename)
        episode.video_filename = None
        episode.embed_url = to_embeddable_url(embed_url_input)

    db.session.commit()
    flash(f'បានផ្ទុកវីដេអូភាគ {ep_num} រួចរាល់', 'success')
    return redirect(url_for('admin.upload', movie_id=movie_id))


@admin_bp.post('/upload/<int:movie_id>/episode/<int:ep_num>/delete')
@staff_required
def delete_episode_video(movie_id, ep_num):
    episode = Episode.query.filter_by(movie_id=movie_id, episode_num=ep_num).first()
    if episode:
        storage.delete_file('videos', episode.video_filename)
        db.session.delete(episode)
        db.session.commit()
        flash(f'បានលុបវីដេអូភាគ {ep_num}', 'success')
    return redirect(url_for('admin.upload', movie_id=movie_id))


@admin_bp.route('/manage')
@admin_required
def manage():
    source = request.args.get('source', 'all')
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Movie.query
    if source == 'admin':
        query = query.filter_by(is_admin_upload=True)
    if q:
        query = query.filter(Movie.title.ilike(f'%{q}%'))

    pagination = query.order_by(Movie.id.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/manage.html', movies=pagination.items, pagination=pagination, source=source, q=q)


@admin_bp.post('/manage/delete/<int:movie_id>')
@admin_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if not movie.is_admin_upload:
        flash('ខ្លឹមសារកសាងស្រាប់ មិនអាចលុបបានទេ', 'error')
        return redirect(url_for('admin.manage'))

    storage.delete_file('videos', movie.video_filename)
    storage.delete_file('thumbnails', movie.thumbnail_filename)
    storage.delete_file('slides', movie.slide_image_filename)
    for episode in movie.episodes:
        storage.delete_file('videos', episode.video_filename)
    db.session.delete(movie)
    db.session.commit()
    flash('បានលុបខ្លឹមសាររួចរាល់', 'success')
    return redirect(url_for('admin.manage'))


@admin_bp.route('/reports')
@admin_required
def reports():
    users = User.query.filter_by(role=User.ROLE_CLIENT).order_by(User.created_at.desc()).all()

    rows = []
    total_balance = 0
    total_topped_up = 0
    total_spent = 0
    active_vip = 0

    for user in users:
        tx = WalletTransaction.query.filter_by(user_id=user.id).all()
        topped_up = sum(t.amount for t in tx if t.type in ('topup', 'redeem') and t.amount > 0)
        spent = sum(-t.amount for t in tx if t.type == 'vip' and t.amount < 0)

        total_balance += user.balance
        total_topped_up += topped_up
        total_spent += spent
        if user.is_vip_active:
            active_vip += 1

        rows.append(dict(user=user, topped_up=topped_up, spent=spent, tx_count=len(tx)))

    total_movies = Movie.query.count()
    admin_uploads = Movie.query.filter_by(is_admin_upload=True).count()
    vip_movie_count = Movie.query.filter_by(vip=True).count()

    category_counts = []
    max_count = 1
    for cat in get_categories():
        count = Movie.query.filter_by(category=cat).count()
        max_count = max(max_count, count)
        category_counts.append((cat, count))
    category_counts = [(cat, count, round(count / max_count * 100)) for cat, count in category_counts]

    return render_template(
        'admin/reports.html', rows=rows, total_users=len(users), total_balance=total_balance,
        total_topped_up=total_topped_up, total_spent=total_spent, active_vip=active_vip,
        total_movies=total_movies, admin_uploads=admin_uploads,
        seeded_count=total_movies - admin_uploads, vip_movie_count=vip_movie_count,
        category_counts=category_counts,
    )


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('សូមបញ្ចូលឈ្មោះប្រភេទ', 'error')
        elif Category.query.filter_by(name=name).first():
            flash('ប្រភេទនេះមានរួចហើយ', 'error')
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash('បានបន្ថែមប្រភេទថ្មីរួចរាល់', 'success')
        return redirect(url_for('admin.categories'))

    cats = Category.query.order_by(Category.name).all()
    movie_counts = {cat.name: Movie.query.filter_by(category=cat.name).count() for cat in cats}
    return render_template('admin/categories.html', cats=cats, movie_counts=movie_counts)


@admin_bp.post('/categories/<int:cat_id>/rename')
@admin_required
def rename_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    new_name = request.form.get('name', '').strip()

    if not new_name:
        flash('សូមបញ្ចូលឈ្មោះថ្មី', 'error')
        return redirect(url_for('admin.categories'))
    if new_name != cat.name and Category.query.filter_by(name=new_name).first():
        flash('ប្រភេទឈ្មោះនេះមានរួចហើយ', 'error')
        return redirect(url_for('admin.categories'))

    old_name = cat.name
    if new_name != old_name:
        cat.name = new_name
        Movie.query.filter_by(category=old_name).update({'category': new_name})
        db.session.commit()
        flash('បានប្តូរឈ្មោះប្រភេទរួចរាល់ (ខ្លឹមសារពាក់ព័ន្ធត្រូវបានធ្វើបច្ចុប្បន្នភាពដែរ)', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.post('/categories/<int:cat_id>/delete')
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('បានលុបប្រភេទរួចរាល់ (ខ្លឹមសារចាស់ដែលប្រើប្រភេទនេះនៅតែមាន គ្រាន់តែលែងបង្ហាញនៅក្នុងបញ្ជីជម្រើសទៀតហើយ)', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        qr_file = request.files.get('payment_qr')
        if not qr_file or qr_file.filename == '':
            flash('សូមជ្រើសរើសរូបភាព QR', 'error')
            return redirect(url_for('admin.settings'))

        filename = storage.save_file(qr_file, 'settings', storage.ALLOWED_IMAGE_EXT)
        if not filename:
            flash('ប្រភេទឯកសារមិនត្រូវបានអនុញ្ញាតទេ', 'error')
            return redirect(url_for('admin.settings'))

        storage.delete_file('settings', get_setting('payment_qr_filename'))
        set_setting('payment_qr_filename', filename)
        flash('បានរក្សាទុក QR ការទូទាត់រួចរាល់', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', payment_qr_filename=get_setting('payment_qr_filename'))


@admin_bp.post('/settings/backfill-telegram')
@admin_required
def backfill_telegram():
    stored = telegram_userbot.backfill_history(current_app._get_current_object(), limit=300)
    if stored:
        flash(f'បានស្កេនរកឃើញ និងរក្សាទុកប្រតិបត្តិការចាស់ចំនួន {stored} ថ្មី', 'success')
    else:
        flash('មិនមានប្រតិបត្តិការចាស់ថ្មីត្រូវរកឃើញទេ (ឬមុខងារ Telegram userbot មិនទាន់បានកំណត់)', 'error')
    return redirect(url_for('admin.settings'))


@admin_bp.route('/users')
@admin_required
def users():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    client_query = User.query.filter_by(role=User.ROLE_CLIENT)
    if q:
        client_query = client_query.filter(
            db.or_(User.name.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))
        )
    pagination = client_query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    staff = User.query.filter(User.role.in_(User.STAFF_ROLES)).order_by(User.role, User.created_at).all()

    return render_template(
        'admin/users.html', clients=pagination.items, pagination=pagination, q=q,
        staff=staff, total_clients=User.query.filter_by(role=User.ROLE_CLIENT).count(),
    )


@admin_bp.post('/users/staff/add')
@admin_required
def add_staff():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    role = request.form.get('role', '')

    if role not in User.STAFF_ROLES:
        flash('សូមជ្រើសរើសតួនាទីត្រឹមត្រូវ', 'error')
    elif not name or not email or len(password) < 6:
        flash('សូមបំពេញឈ្មោះ អ៊ីមែល និងពាក្យសម្ងាត់ (យ៉ាងតិច ៦ តួ)', 'error')
    elif User.query.filter_by(email=email).first():
        flash('អ៊ីមែលនេះមានគណនីរួចហើយ', 'error')
    else:
        staff_user = User(name=name, email=email, role=role)
        staff_user.set_password(password)
        db.session.add(staff_user)
        db.session.commit()
        flash('បានបន្ថែមគណនីបុគ្គលិកថ្មីរួចរាល់', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.post('/users/staff/<int:user_id>/role')
@admin_required
def change_staff_role(user_id):
    target = User.query.get_or_404(user_id)
    new_role = request.form.get('role', '')
    current = get_current_user()

    if target.id == current.id:
        flash('អ្នកមិនអាចផ្លាស់ប្តូរតួនាទីគណនីខ្លួនឯងបានទេ', 'error')
    elif target.role not in User.STAFF_ROLES:
        flash('គណនីនេះមិនមែនជាបុគ្គលិកទេ', 'error')
    elif new_role not in User.STAFF_ROLES:
        flash('សូមជ្រើសរើសតួនាទីត្រឹមត្រូវ', 'error')
    else:
        target.role = new_role
        db.session.commit()
        flash('បានប្តូរតួនាទីរួចរាល់', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.post('/users/staff/<int:user_id>/delete')
@admin_required
def delete_staff(user_id):
    target = User.query.get_or_404(user_id)
    current = get_current_user()

    if target.id == current.id:
        flash('អ្នកមិនអាចលុបគណនីខ្លួនឯងបានទេ', 'error')
    elif target.role not in User.STAFF_ROLES:
        flash('គណនីនេះមិនមែនជាបុគ្គលិកទេ', 'error')
    else:
        target.role = User.ROLE_CLIENT
        db.session.commit()
        flash('បានដកសិទ្ធិបុគ្គលិករួចរាល់ (គណនីប្រែជាអតិថិជនធម្មតា)', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.post('/users/<int:user_id>/reset-password')
@admin_required
def reset_user_password(user_id):
    target = User.query.get_or_404(user_id)
    new_password = secrets.token_urlsafe(6)
    target.set_password(new_password)
    db.session.commit()
    flash(f'ពាក្យសម្ងាត់ថ្មីសម្រាប់ {target.name} ({target.email}): {new_password} — សូមចម្លងទុកឥឡូវនេះ វានឹងមិនបង្ហាញម្តងទៀតទេ', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/account/password', methods=['GET', 'POST'])
@staff_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        user = get_current_user()

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
            return redirect(url_for('admin.change_password'))
    return render_template('admin/change_password.html')
