"""One-off migration: replaces the User.is_admin boolean with a role string
('client' | 'poster' | 'admin'). Non-destructive to existing data — existing
is_admin=True accounts become role='admin', everyone else becomes 'client'."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

if 'role' in cols:
    print('role column already exists, skipping add.')
else:
    cur.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'client'")
    print('Added role column.')

if 'is_admin' in cols:
    cur.execute("UPDATE user SET role = 'admin' WHERE is_admin = 1")
    print(f'Migrated {cur.rowcount} admin account(s) to role=admin.')
    cur.execute('ALTER TABLE user DROP COLUMN is_admin')
    print('Dropped is_admin column.')
else:
    print('is_admin column already gone, skipping.')

con.commit()
con.close()
print('Done.')
