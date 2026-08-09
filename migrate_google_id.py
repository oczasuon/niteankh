"""One-off migration: adds google_id column to User for Google Sign-In.
Non-destructive — existing rows get NULL."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

if 'google_id' in cols:
    print('google_id column already exists, skipping.')
else:
    cur.execute('ALTER TABLE user ADD COLUMN google_id VARCHAR(64)')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_user_google_id ON user (google_id)')
    print('Added google_id column with unique index.')

con.commit()
con.close()
print('Done.')
