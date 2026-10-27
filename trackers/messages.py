from database import connection

def record(message):
    with connection() as con:
        con.execute('''INSERT OR IGNORE INTO messages
          (message_id,guild_id,channel_id,author_id,created_at)
          VALUES(?,?,?,?,?)''', (message.id, message.guild.id,
          message.channel.id, message.author.id, message.created_at.isoformat()))
