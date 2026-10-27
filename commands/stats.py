import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from database import connection

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='stats', description='Show activity statistics for a member')
    @app_commands.guild_only()
    async def stats(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        gid,uid = interaction.guild_id,member.id
        with connection() as con:
            messages = con.execute('SELECT COUNT(*) FROM messages WHERE guild_id=? AND author_id=?',(gid,uid)).fetchone()[0]
            given = con.execute('SELECT COUNT(*) FROM reactions WHERE guild_id=? AND reactor_id=?',(gid,uid)).fetchone()[0]
            received = con.execute('SELECT COUNT(*) FROM reactions WHERE guild_id=? AND author_id=?',(gid,uid)).fetchone()[0]
            total = con.execute('SELECT seconds,sessions FROM voice_totals WHERE guild_id=? AND user_id=?',(gid,uid)).fetchone() or (0,0)
            live = con.execute('SELECT started_at FROM voice_sessions WHERE guild_id=? AND user_id=?',(gid,uid)).fetchone()
        seconds = total[0] + (max(0,int((datetime.now(timezone.utc)-datetime.fromisoformat(live[0])).total_seconds())) if live else 0)
        embed = discord.Embed(title=f'Activity: {member.display_name}',color=discord.Color.blurple())
        embed.add_field(name='Messages',value=f'{messages:,}')
        embed.add_field(name='Reactions given',value=f'{given:,}')
        embed.add_field(name='Reactions received*',value=f'{received:,}')
        embed.add_field(name='Voice time',value=f'{seconds//3600}h {(seconds%3600)//60}m')
        embed.add_field(name='Completed voice sessions',value=str(total[1]))
        embed.set_footer(text='*Received reactions may be incomplete for older messages.')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='serverstats', description='Show server activity totals')
    @app_commands.guild_only()
    async def serverstats(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        with connection() as con:
            messages = con.execute('SELECT COUNT(*) FROM messages WHERE guild_id=?',(gid,)).fetchone()[0]
            reactions = con.execute('SELECT COUNT(*) FROM reactions WHERE guild_id=?',(gid,)).fetchone()[0]
            voice = con.execute('SELECT COALESCE(SUM(seconds),0) FROM voice_totals WHERE guild_id=?',(gid,)).fetchone()[0]
            active = con.execute('SELECT started_at FROM voice_sessions WHERE guild_id=?',(gid,)).fetchall()
        current = datetime.now(timezone.utc)
        voice += sum(max(0,int((current-datetime.fromisoformat(s)).total_seconds())) for (s,) in active)
        embed = discord.Embed(title=f'Activity: {interaction.guild.name}',color=discord.Color.blurple())
        embed.add_field(name='Messages',value=f'{messages:,}')
        embed.add_field(name='Reactions currently recorded',value=f'{reactions:,}')
        embed.add_field(name='Voice time',value=f'{voice//3600}h {(voice%3600)//60}m')
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
