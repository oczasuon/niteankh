"""File storage abstraction: local disk for development, Cloudflare R2 for
deployment. Controlled entirely by environment variables — if the R2_* vars
aren't set, everything falls back to local disk under static/, exactly as
before. No caller needs to know which one is active."""

import os
from uuid import uuid4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_VIDEO_EXT = {'mp4', 'webm', 'ogg', 'mov', 'm4v'}
ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

# subfolder name -> local disk directory (used when R2 isn't configured)
LOCAL_DIRS = {
    'videos': os.path.join(BASE_DIR, 'static', 'uploads', 'videos'),
    'thumbnails': os.path.join(BASE_DIR, 'static', 'uploads', 'thumbnails'),
    'slides': os.path.join(BASE_DIR, 'static', 'uploads', 'slides'),
    'settings': os.path.join(BASE_DIR, 'static', 'images'),
}

# subfolder name -> path under /static/ (used to build local URLs)
STATIC_SUBPATH = {
    'videos': 'uploads/videos',
    'thumbnails': 'uploads/thumbnails',
    'slides': 'uploads/slides',
    'settings': 'images',
}

R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET = os.environ.get('R2_BUCKET')
R2_PUBLIC_BASE_URL = os.environ.get('R2_PUBLIC_BASE_URL', '').rstrip('/')

USE_R2 = bool(R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY and R2_BUCKET)

_r2_client = None


def get_r2_client():
    global _r2_client
    if _r2_client is None:
        import boto3
        from botocore.client import Config
        _r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto',
        )
    return _r2_client


def ensure_local_dirs():
    if not USE_R2:
        for path in LOCAL_DIRS.values():
            os.makedirs(path, exist_ok=True)


def allowed_file(filename, allowed_ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


def save_file(file_storage, subfolder, allowed_ext):
    """Saves an uploaded file to R2 or local disk. Returns the generated
    filename, or None if the file was missing/had a disallowed extension."""
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename, allowed_ext):
        return None

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid4().hex}.{ext}'

    if USE_R2:
        get_r2_client().upload_fileobj(
            file_storage.stream, R2_BUCKET, f'{subfolder}/{filename}',
            ExtraArgs={'ContentType': file_storage.mimetype or 'application/octet-stream'},
        )
    else:
        file_storage.save(os.path.join(LOCAL_DIRS[subfolder], filename))

    return filename


def delete_file(subfolder, filename):
    if not filename:
        return
    if USE_R2:
        get_r2_client().delete_object(Bucket=R2_BUCKET, Key=f'{subfolder}/{filename}')
    else:
        path = os.path.join(LOCAL_DIRS[subfolder], filename)
        if os.path.exists(path):
            os.remove(path)


def file_url(subfolder, filename):
    if not filename:
        return None
    if USE_R2:
        return f'{R2_PUBLIC_BASE_URL}/{subfolder}/{filename}'
    from flask import url_for
    return url_for('static', filename=f'{STATIC_SUBPATH[subfolder]}/{filename}')
