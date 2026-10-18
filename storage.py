"""File storage abstraction: local disk for development, Cloudflare R2 for
deployment. Controlled entirely by environment variables — if the R2_* vars
aren't set, everything falls back to local disk under static/, exactly as
before. No caller needs to know which one is active."""

import io
import os
from uuid import uuid4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_VIDEO_EXT = {'mp4', 'webm', 'ogg', 'mov', 'm4v'}
ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

# Uploaded images in these subfolders are downscaled to fit (width, height)
# and stored as WebP. 'settings' (payment QR) is left untouched on purpose —
# recompressing a QR code risks making it unscannable.
IMAGE_MAX_SIZE = {
    'thumbnails': (1280, 1280),
    'slides': (1920, 1080),
    'avatars': (400, 400),
}
WEBP_QUALITY = 82

# subfolder name -> local disk directory (used when R2 isn't configured)
LOCAL_DIRS = {
    'videos': os.path.join(BASE_DIR, 'static', 'uploads', 'videos'),
    'thumbnails': os.path.join(BASE_DIR, 'static', 'uploads', 'thumbnails'),
    'slides': os.path.join(BASE_DIR, 'static', 'uploads', 'slides'),
    'settings': os.path.join(BASE_DIR, 'static', 'images'),
    'avatars': os.path.join(BASE_DIR, 'static', 'uploads', 'avatars'),
}

# subfolder name -> path under /static/ (used to build local URLs)
STATIC_SUBPATH = {
    'videos': 'uploads/videos',
    'thumbnails': 'uploads/thumbnails',
    'slides': 'uploads/slides',
    'settings': 'images',
    'avatars': 'uploads/avatars',
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


def optimize_image(stream, max_size):
    """Downscales an image to fit within max_size and re-encodes it as WebP.
    Returns the WebP bytes, or None if the stream isn't a decodable image.
    Raw uploads (multi-MB PNG screenshots/posters) made the movie grid very
    slow to load, since every card downloaded the full-size original."""
    from PIL import Image, ImageFilter, ImageOps
    try:
        img = Image.open(stream)
        img.draft('RGB', max_size)  # JPEG only: decode at reduced scale — far less RAM on the Pi
        img = ImageOps.exif_transpose(img)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA' if 'A' in img.getbands() or 'transparency' in img.info else 'RGB')
        original_size = img.size
        img.thumbnail(max_size, Image.LANCZOS)
        if img.size != original_size:
            # downscaling softens detail; a light unsharp mask restores crispness
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
        out = io.BytesIO()
        img.save(out, 'WEBP', quality=WEBP_QUALITY, method=6)
        return out.getvalue()
    except Exception:
        return None


def save_file(file_storage, subfolder, allowed_ext):
    """Saves an uploaded file to R2 or local disk. Returns the generated
    filename, or None if the file was missing/had a disallowed extension."""
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename, allowed_ext):
        return None

    ext = file_storage.filename.rsplit('.', 1)[1].lower()

    if subfolder in IMAGE_MAX_SIZE and ext != 'gif':
        webp_bytes = optimize_image(file_storage.stream, IMAGE_MAX_SIZE[subfolder])
        if webp_bytes is not None:
            filename = f'{uuid4().hex}.webp'
            if USE_R2:
                get_r2_client().upload_fileobj(
                    io.BytesIO(webp_bytes), R2_BUCKET, f'{subfolder}/{filename}',
                    ExtraArgs={'ContentType': 'image/webp'},
                )
            else:
                with open(os.path.join(LOCAL_DIRS[subfolder], filename), 'wb') as f:
                    f.write(webp_bytes)
            return filename
        file_storage.stream.seek(0)  # not a decodable image — store it as uploaded

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
