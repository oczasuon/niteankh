"""One-off migration: creates the comment table for video comments.
Non-destructive — only adds a new table, touches nothing existing."""
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'niteankh.db'

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comment'")
if cur.fetchone():
    print('comment table already exists, skipping.')
else:
    cur.execute('''
        CREATE TABLE comment (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER NOT NULL REFERENCES movie(id),
            user_id INTEGER NOT NULL REFERENCES "user"(id),
            text VARCHAR(1000) NOT NULL,
            created_at DATETIME
        )
    ''')
    cur.execute('CREATE INDEX ix_comment_movie_id ON comment (movie_id)')
    print('Created comment table.')

con.commit()
con.close()
print('Done.')
