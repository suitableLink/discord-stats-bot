import logging
import os
import discord
from discord.ext import commands
from database import initialize
from trackers import messages, reactions, voice

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('stats')

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
# Message content is not required: we only count messages.

class StatsBot(commands.Bot):
    async def setup_hook(self):
        initialize()
        await self.load_extension('commands.stats')
        guild_id = os.getenv('DISCORD_GUILD_ID')
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info('Synced commands to test guild %s',guild_id)
        else:
            await self.tree.sync()
            log.info('Synced global commands')

bot = StatsBot(command_prefix='!', intents=intents)
_reconciled = False

@bot.event
async def on_ready():
    global _reconciled
    log.info('Logged in as %s',bot.user)
    if not _reconciled:
        voice.reconcile(bot.guilds)
        _reconciled = True

@bot.event
async def on_message(message):
    if message.guild and not message.author.bot:
        messages.record(message)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if not payload.guild_id or payload.user_id == bot.user.id:
        return
    if payload.member and payload.member.bot:
        return
    author_id = None
    try:
        channel = bot.get_channel(payload.channel_id) or await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.bot:
            return
        author_id = message.author.id
    except (discord.Forbidden, discord.NotFound, discord.HTTPException, AttributeError):
        pass
    reactions.add(payload,author_id)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id:
        reactions.remove(payload)

@bot.event
async def on_raw_reaction_clear(payload):
    if payload.guild_id:
        reactions.clear_message(payload)

@bot.event
async def on_raw_reaction_clear_emoji(payload):
    if payload.guild_id:
        reactions.clear_emoji(payload)

@bot.event
async def on_voice_state_update(member,before,after):
    if not member.bot and before.channel != after.channel:
        voice.transition(member.guild.id,member.id,after.channel.id if after.channel else None)

bot.run(os.environ['DISCORD_BOT_TOKEN'])
