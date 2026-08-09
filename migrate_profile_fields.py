"""One-off migration: adds phone, sex, dob, location columns to User for the
profile-editing feature. Non-destructive — existing rows get NULL for these."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]

NEW_COLUMNS = {
    'phone': 'VARCHAR(30)',
    'sex': 'VARCHAR(10)',
    'dob': 'DATE',
    'location': 'VARCHAR(255)',
}

for name, coltype in NEW_COLUMNS.items():
    if name in cols:
        print(f'{name} column already exists, skipping.')
    else:
        cur.execute(f'ALTER TABLE user ADD COLUMN {name} {coltype}')
        print(f'Added {name} column.')

con.commit()
con.close()
print('Done.')
