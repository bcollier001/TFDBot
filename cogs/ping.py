import discord

from discord import app_commands
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready")
        
    @app_commands.command(name="ping", description="Shows bot latency")
    async def ping(self, interaction: discord.Interaction):
        bot_latency = round(interaction.client.latency * 1000)
        if bot_latency <= 50:
            color = discord.Color.green()
        elif bot_latency <= 100:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        ping_embed = discord.Embed(title="Pong!",
                                   description=f"Latency: {bot_latency}ms",
                                   color=color)
        ping_embed.set_thumbnail(url=interaction.client .user.avatar)
        ping_embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=ping_embed)

async def setup(client):
    await client.add_cog(Ping(client))