import re
from functools import wraps
from urllib.parse import parse_qs, urlparse

from flask import redirect, request, session, url_for

from models import Category, Setting, User, db


def get_categories():
    """List of category names, managed by admins via /admin/categories."""
    return [c.name for c in Category.query.order_by(Category.name).all()]


def to_embeddable_url(url):
    """Converts a normal share link (YouTube watch/shorts/youtu.be, Google Drive
    file link, Vimeo) into its embeddable iframe form. Anything else is
    returned unchanged, on the assumption it's already a direct embed URL."""
    url = (url or '').strip()
    if not url:
        return url

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if 'youtube.com' in host or 'youtu.be' in host:
        video_id = None
        if 'youtu.be' in host:
            video_id = parsed.path.strip('/').split('/')[0]
        elif '/shorts/' in parsed.path:
            video_id = parsed.path.split('/shorts/')[1].split('/')[0]
        elif '/embed/' in parsed.path:
            return url  # already embeddable
        elif parsed.path == '/watch':
            video_id = (parse_qs(parsed.query).get('v') or [None])[0]
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'

    if 'drive.google.com' in host:
        if '/preview' in parsed.path:
            return url  # already embeddable
        m = re.search(r'/file/d/([^/]+)', parsed.path)
        if not m:
            m = re.search(r'[?&]id=([^&]+)', url)
        if m:
            return f'https://drive.google.com/file/d/{m.group(1)}/preview'

    if 'vimeo.com' in host and 'player.vimeo.com' not in host:
        m = re.search(r'vimeo\.com/(\d+)', url)
        if m:
            return f'https://player.vimeo.com/video/{m.group(1)}'

    return url


# Guest (not-logged-in) viewing limits — session-based, resets when the
# browser session ends. Logged-in users are never subject to these.
GUEST_WATCH_SECONDS_LIMIT = 8 * 60  # 8 minutes of actual video playback
GUEST_MOVIE_LIMIT = 2  # distinct movies


def get_guest_watch_seconds():
    return session.get('guest_watch_seconds', 0)


def add_guest_watch_seconds(delta):
    session['guest_watch_seconds'] = get_guest_watch_seconds() + max(0, delta)


def get_guest_movies_watched():
    return session.get('guest_movies', [])


def register_guest_movie_view(movie_id):
    movies = get_guest_movies_watched()
    if movie_id not in movies:
        movies = movies + [movie_id]
        session['guest_movies'] = movies


def guest_time_limit_reached():
    return get_guest_watch_seconds() >= GUEST_WATCH_SECONDS_LIMIT


def guest_would_exceed_movie_limit(movie_id):
    watched = get_guest_movies_watched()
    return movie_id not in watched and len(watched) >= GUEST_MOVIE_LIMIT


VIP_PLANS = [
    {'days': 7, 'cost': 500, 'label': '7 ថ្ងៃ'},
    {'days': 30, 'cost': 1500, 'label': '30 ថ្ងៃ', 'tag': 'ពេញនិយម'},
    {'days': 90, 'cost': 3800, 'label': '90 ថ្ងៃ'},
]

TOPUP_PACKAGES = [
    {'coins': 100, 'price': '2,000៛', 'price_khr': 2000},
    {'coins': 300, 'price': '5,000៛', 'price_khr': 5000},
    {'coins': 650, 'price': '10,000៛', 'price_khr': 10000},
    {'coins': 1400, 'price': '20,000៛', 'price_khr': 20000},
    {'coins': 3600, 'price': '50,000៛', 'price_khr': 50000},
    {'coins': 7500, 'price': '100,000៛', 'price_khr': 100000},
]

REDEEM_CODES = {'WELCOME50': 50, 'NITEANKH100': 100}

# Base rate used for any deposit that doesn't exactly match a discounted
# package tier above — derived from the smallest package (the "retail" rate,
# since bigger packages are bulk discounts on top of this).
_BASE_COINS_PER_KHR = TOPUP_PACKAGES[0]['coins'] / TOPUP_PACKAGES[0]['price_khr']


def calculate_coins_for_khr(amount_khr):
    """Coins for a real deposited amount: the discounted package rate if it
    matches a tier exactly, otherwise the base rate — so any amount (e.g. an
    odd 2,500៛ deposit) still converts to a sensible coin amount."""
    for pkg in TOPUP_PACKAGES:
        if pkg['price_khr'] == amount_khr:
            return pkg['coins']
    return round(amount_khr * _BASE_COINS_PER_KHR)


def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)
    return wrapped


def safe_redirect_target(target):
    if target and target.startswith('/') and not target.startswith('//'):
        return target
    return None


def get_setting(key, default=None):
    row = Setting.query.filter_by(key=key).first()
    return row.value if row else default


def set_setting(key, value):
    row = Setting.query.filter_by(key=key).first()
    if row:
        row.value = value
    else:
        db.session.add(Setting(key=key, value=value))
    db.session.commit()
