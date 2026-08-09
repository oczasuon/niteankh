"""One-off migration: adds telegram_id column to User for Telegram Login Widget.
Non-destructive — existing rows get NULL."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

if 'telegram_id' in cols:
    print('telegram_id column already exists, skipping.')
else:
    cur.execute('ALTER TABLE user ADD COLUMN telegram_id VARCHAR(64)')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_user_telegram_id ON user (telegram_id)')
    print('Added telegram_id column with unique index.')

con.commit()
con.close()
print('Done.')
