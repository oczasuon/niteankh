"""One-off migration: adds avatar_filename column to User for profile photos.
Non-destructive — existing rows get NULL."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

if 'avatar_filename' in cols:
    print('avatar_filename column already exists, skipping.')
else:
    cur.execute('ALTER TABLE user ADD COLUMN avatar_filename VARCHAR(255)')
    print('Added avatar_filename column.')

con.commit()
con.close()
print('Done.')
