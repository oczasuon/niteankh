"""One-off migration: adds session_token column to User for single-active-
session enforcement. Non-destructive — existing rows get NULL, meaning any
already-logged-in session (with no session_token in its cookie either) stays
valid until its next login, at which point the new mechanism takes over."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

if 'session_token' in cols:
    print('session_token column already exists, skipping.')
else:
    cur.execute('ALTER TABLE user ADD COLUMN session_token VARCHAR(64)')
    print('Added session_token column.')

con.commit()
con.close()
print('Done.')
