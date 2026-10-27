from datetime import datetime, timezone
from database import connection, now

def _close(con, guild_id, user_id, end):
    row = con.execute('SELECT started_at FROM voice_sessions WHERE guild_id=? AND user_id=?',
                      (guild_id, user_id)).fetchone()
    if row is None:
        return
    started = datetime.fromisoformat(row[0])
    seconds = max(0, int((end - started).total_seconds()))
    con.execute('''INSERT INTO voice_totals(guild_id,user_id,seconds,sessions)
      VALUES(?,?,?,1) ON CONFLICT(guild_id,user_id) DO UPDATE SET
      seconds=seconds+excluded.seconds,sessions=sessions+1''',
      (guild_id,user_id,seconds))
    con.execute('DELETE FROM voice_sessions WHERE guild_id=? AND user_id=?', (guild_id,user_id))

def transition(guild_id, user_id, channel_id):
    end = datetime.now(timezone.utc)
    with connection() as con:
        existing = con.execute('SELECT channel_id FROM voice_sessions WHERE guild_id=? AND user_id=?',
                               (guild_id,user_id)).fetchone()
        if existing and existing[0] == channel_id:
            return
        _close(con,guild_id,user_id,end)
        if channel_id is not None:
            con.execute('INSERT INTO voice_sessions VALUES(?,?,?,?)',
                        (guild_id,user_id,channel_id,end.isoformat()))

def reconcile(guilds):
    """On startup, discard offline intervals; resume currently connected members."""
    end = datetime.now(timezone.utc)
    active = {(g.id,m.id):m.voice.channel.id
              for g in guilds for m in g.members
              if not m.bot and m.voice and m.voice.channel}
    with connection() as con:
        rows = con.execute('SELECT guild_id,user_id FROM voice_sessions').fetchall()
        for gid,uid in rows:
            _close(con,gid,uid,end)  # Includes downtime: see README caveat
        for (gid,uid),cid in active.items():
            con.execute('INSERT OR REPLACE INTO voice_sessions VALUES(?,?,?,?)',
                        (gid,uid,cid,end.isoformat()))
