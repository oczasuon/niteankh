"""One-off migration: re-encodes already-uploaded thumbnails, slides and
avatars as downscaled WebP (same rules as new uploads, see
storage.IMAGE_MAX_SIZE) and points the DB rows at the new files.

Non-destructive — originals are moved to static/uploads/_originals/<subfolder>/
rather than deleted. Already-WebP files and GIFs are skipped, so it's safe to
re-run. Pass --dry-run to only report what would change.

Usage: python migrate_optimize_images.py [niteankh.db] [--dry-run]"""
import os
import shutil
import sqlite3
import sys
from uuid import uuid4

import storage

args = [a for a in sys.argv[1:] if a != '--dry-run']
DRY_RUN = '--dry-run' in sys.argv
DB_PATH = args[0] if args else 'niteankh.db'
BACKUP_DIR = os.path.join(storage.BASE_DIR, 'static', 'uploads', '_originals')

# (table, column, storage subfolder)
TARGETS = [
    ('movie', 'thumbnail_filename', 'thumbnails'),
    ('movie', 'slide_image_filename', 'slides'),
    ('user', 'avatar_filename', 'avatars'),
]

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
before_total = after_total = converted = 0

for table, column, subfolder in TARGETS:
    rows = cur.execute(f'SELECT id, {column} FROM "{table}" WHERE {column} IS NOT NULL AND {column} != ""').fetchall()
    for row_id, filename in rows:
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext in ('webp', 'gif'):
            continue
        src = os.path.join(storage.LOCAL_DIRS[subfolder], filename)
        if not os.path.exists(src):
            print(f'  missing: {subfolder}/{filename} ({table} {row_id})')
            continue
        with open(src, 'rb') as f:
            webp_bytes = storage.optimize_image(f, storage.IMAGE_MAX_SIZE[subfolder])
        if webp_bytes is None:
            print(f'  not an image, skipped: {subfolder}/{filename}')
            continue

        old_size = os.path.getsize(src)
        new_name = f'{uuid4().hex}.webp'
        before_total += old_size
        after_total += len(webp_bytes)
        converted += 1
        print(f'  {table} {row_id}: {subfolder}/{filename} {old_size // 1024}KB -> {new_name} {len(webp_bytes) // 1024}KB')
        if DRY_RUN:
            continue

        with open(os.path.join(storage.LOCAL_DIRS[subfolder], new_name), 'wb') as f:
            f.write(webp_bytes)
        cur.execute(f'UPDATE "{table}" SET {column} = ? WHERE id = ?', (new_name, row_id))
        con.commit()
        os.makedirs(os.path.join(BACKUP_DIR, subfolder), exist_ok=True)
        shutil.move(src, os.path.join(BACKUP_DIR, subfolder, filename))

con.close()
print(f'{"Would convert" if DRY_RUN else "Converted"} {converted} images: '
      f'{before_total / 1048576:.1f}MB -> {after_total / 1048576:.1f}MB')
print('Done.')
