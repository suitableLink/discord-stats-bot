# Discord Activity Stats Bot

Tracks server message counts, reactions, and time connected to voice channels. Commands: `/stats [member]` and `/serverstats`.

## Requirements
- Python 3.10+ and discord.py 2.x
- Discord bot with **Server Members Intent** enabled in Developer Portal (required for member/voice startup reconciliation)
- Bot invited with `bot` and `applications.commands` scopes; View Channels, Read Message History, and Add Reactions are sufficient for tracking accessible text channels. Voice tracking uses voice-state events and access to guild state.
- Do not enable Message Content intent: message bodies are not stored.

## Local setup
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
DISCORD_BOT_TOKEN=... DISCORD_GUILD_ID=... .venv/bin/python bot.py
```
Windows PowerShell: set `$env:DISCORD_BOT_TOKEN` and `$env:DISCORD_GUILD_ID` in the session, then run `.venv\Scripts\python.exe bot.py`. Never commit tokens.

## Notes / known limitations
- Only activity after the bot starts is recorded. There is no history import.
- Reactions on older messages are recorded when events arrive, but received-reaction totals require successfully fetching the message author; some cannot be attributed.
- Reaction removals update counts; `reactions` is a current-state table, not a lifetime history.
- The bot excludes other bots' messages and known bot reactors; reactions on messages authored by bots are excluded when author lookup succeeds.
- Voice time measures connection time, not actual speech. The basic startup reconciliation **counts any VM downtime as voice time** for sessions that were open when the process stopped. Improve this with a heartbeat checkpoint before relying on exact totals.
- Voice joins during a disconnected interval are not reconstructable.
- Commands default to global registration; set `DISCORD_GUILD_ID` for immediate development guild sync.
- Keep `stats.db` on the VM and back it up separately; it is intentionally gitignored.
