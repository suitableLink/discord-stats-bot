import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.getenv('STATS_DB_PATH', 'stats.db')

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def connection():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.execute('PRAGMA busy_timeout=30000')
    con.execute('PRAGMA journal_mode=WAL')
    try:
        yield con
        con.commit()
    finally:
        con.close()

def initialize():
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS messages (
          message_id INTEGER PRIMARY KEY, guild_id INTEGER NOT NULL,
          channel_id INTEGER NOT NULL, author_id INTEGER NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_messages_guild_author ON messages(guild_id,author_id);
        CREATE TABLE IF NOT EXISTS reactions (
          message_id INTEGER NOT NULL, guild_id INTEGER NOT NULL,
          reactor_id INTEGER NOT NULL, emoji TEXT NOT NULL,
          author_id INTEGER, created_at TEXT NOT NULL,
          PRIMARY KEY(message_id,reactor_id,emoji)
        );
        CREATE INDEX IF NOT EXISTS idx_reactions_guild ON reactions(guild_id);
        CREATE TABLE IF NOT EXISTS voice_sessions (
          guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
          channel_id INTEGER NOT NULL, started_at TEXT NOT NULL,
          PRIMARY KEY(guild_id,user_id)
        );
        CREATE TABLE IF NOT EXISTS voice_totals (
          guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
          seconds INTEGER NOT NULL DEFAULT 0,
          sessions INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(guild_id,user_id)
        );
        ''')
