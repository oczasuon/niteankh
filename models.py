from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    ROLE_CLIENT = 'client'
    ROLE_POSTER = 'poster'
    ROLE_ADMIN = 'admin'
    STAFF_ROLES = (ROLE_ADMIN, ROLE_POSTER)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=ROLE_CLIENT, nullable=False)
    balance = db.Column(db.Integer, default=0, nullable=False)
    vip_expiry = db.Column(db.DateTime, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    sex = db.Column(db.String(10), nullable=True)  # 'male' | 'female' | 'other'
    dob = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(64), unique=True, nullable=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=True)
    session_token = db.Column(db.String(64), nullable=True)  # single-active-session enforcement
    created_at = db.Column(db.DateTime, default=now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == User.ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role in User.STAFF_ROLES

    @property
    def is_vip_active(self):
        return self.vip_expiry is not None and self.vip_expiry.replace(tzinfo=timezone.utc) > now()

    @property
    def vip_days_left(self):
        if not self.is_vip_active:
            return 0
        delta = self.vip_expiry.replace(tzinfo=timezone.utc) - now()
        return max(0, delta.days + (1 if delta.seconds else 0))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    total_episodes = db.Column(db.Integer, default=12)
    quality = db.Column(db.String(10), default='FHD')
    year = db.Column(db.Integer, default=2026)
    rating = db.Column(db.Float, default=8.0)
    vip = db.Column(db.Boolean, default=False, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    bg_grad = db.Column(db.String(120), default='from-teal-800 via-purple-900 to-rose-900')
    video_filename = db.Column(db.String(255), nullable=True)
    embed_url = db.Column(db.String(500), nullable=True)  # alternative to video_filename: YouTube/Drive/Vimeo/etc.
    thumbnail_filename = db.Column(db.String(255), nullable=True)
    slide_image_filename = db.Column(db.String(255), nullable=True)  # wide hero-banner image, for featured slides
    is_admin_upload = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

    def ep_label(self, ep_num=1):
        return f'ភាគ {ep_num:02d}'

    @property
    def has_slide_image(self):
        return bool(self.slide_image_filename)

    @property
    def is_new(self):
        if not self.created_at:
            return False
        created = self.created_at if self.created_at.tzinfo else self.created_at.replace(tzinfo=timezone.utc)
        return (now() - created) <= timedelta(days=7)

    @property
    def has_video(self):
        return bool(self.video_filename)

    @property
    def has_embed(self):
        return bool(self.embed_url)

    @property
    def has_thumbnail(self):
        return bool(self.thumbnail_filename)


class Episode(db.Model):
    """Per-episode video override. If a movie has no matching Episode row for a
    given number, watch() falls back to the Movie's own video/embed (the single
    legacy/default). video_filename and embed_url are alternatives — a direct
    upload or an embed link (YouTube/Drive/Vimeo/etc.), not both."""
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    episode_num = db.Column(db.Integer, nullable=False)
    video_filename = db.Column(db.String(255), nullable=True)
    embed_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=now)

    movie = db.relationship('Movie', backref=db.backref('episodes', cascade='all, delete-orphan'))
    __table_args__ = (db.UniqueConstraint('movie_id', 'episode_num', name='uq_movie_episode_num'),)


class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # topup | vip | redeem
    bank_name = db.Column(db.String(120), nullable=True)  # account holder name on the transfer (topups only)
    bank_ref = db.Column(db.String(120), nullable=True)  # bank transaction reference / hash (topups only)
    created_at = db.Column(db.DateTime, default=now)

    user = db.relationship('User', backref=db.backref('transactions', order_by='WalletTransaction.created_at.desc()'))


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)


class BankTransaction(db.Model):
    """A parsed bank-payment notification, forwarded into the verification Telegram
    group and picked up by the poller. A wallet top-up only credits coins once its
    claimed reference matches an unused row here with the right amount."""
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(20), nullable=False)  # 'external' | 'internal'
    reference = db.Column(db.String(120), unique=True, nullable=False)  # hash or TXN ID
    amount_khr = db.Column(db.Integer, nullable=False)
    sender_name = db.Column(db.String(255), nullable=True)
    raw_message = db.Column(db.Text, nullable=False)
    telegram_message_id = db.Column(db.BigInteger, nullable=True)
    matched = db.Column(db.Boolean, default=False, nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    received_at = db.Column(db.DateTime, default=now)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now)


class MyListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now)

    movie = db.relationship('Movie')
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_list'),)


class HistoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    episode_num = db.Column(db.Integer, default=1)
    watched_at = db.Column(db.DateTime, default=now)

    movie = db.relationship('Movie')
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_history'),)
