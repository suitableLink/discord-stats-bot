from database import connection, now

def add(payload, author_id):
    with connection() as con:
        con.execute('''INSERT OR IGNORE INTO reactions
          (message_id,guild_id,reactor_id,emoji,author_id,created_at)
          VALUES(?,?,?,?,?,?)''', (payload.message_id, payload.guild_id,
          payload.user_id, str(payload.emoji), author_id, now()))

def remove(payload):
    with connection() as con:
        con.execute('DELETE FROM reactions WHERE message_id=? AND reactor_id=? AND emoji=?',
                    (payload.message_id, payload.user_id, str(payload.emoji)))

def clear_message(payload):
    with connection() as con:
        con.execute('DELETE FROM reactions WHERE message_id=?', (payload.message_id,))

def clear_emoji(payload):
    with connection() as con:
        con.execute('DELETE FROM reactions WHERE message_id=? AND emoji=?',
                    (payload.message_id, str(payload.emoji)))
