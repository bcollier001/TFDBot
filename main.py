import os
import asyncio
import platform
import discord
import updater
import pytz

from errorHandler import send_error_message

from datetime import datetime
from discord.ext import commands, tasks

client = commands.Bot(command_prefix="!",
                      intents=discord.Intents.all(),
                      application_id='1287679358168727593')

@client.event
async def on_ready():
    synced = await client.tree.sync()
    activity = discord.Activity(type=discord.ActivityType.custom, name='TFD', state='Waiting for Oct 10th')
    await client.change_presence(status=discord.Status.online, activity=activity)
    change_status.start()
    print("\n\n---------------------------------")
    print(f"Logged in as {client.user.name}")
    print(f"Synced {len(synced)} command(s)")
    print(f"Discord Version: {discord.__version__}")
    print(f"Python Version: {platform.python_version()}")
    print("---------------------------------\n\n")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction,
                               error: discord.app_commands.AppCommandError):
    await send_error_message(interaction, error)


#Update jsonData
@client.command()
async def update(ctx, folder = None):
#@app_commands.command(name="updatedata", description="Search for a player's basic information")
#async def update(interaction: discord.Interaction, folder = None):
    if ctx.author.id == 292003372649807872:

        await ctx.send("Updating...")
        
        remove_success = bool()
        get_success = bool()
        folders_removed = int()
        files_removed = int()
        folders_processed = int()
        files_processed = int()
        error_message = str()
        if folder is not None and folder.endswith('s'):
            folder = folder.strip('s')
        if folder is not None:
            remove_success, folders_removed, files_removed, error_message = updater.remove_jsonData(folder)
            if remove_success:
                get_success, folders_processed, files_processed, error_message = updater.get_jsonData(folder)
        else:
            remove_success, folders_removed, files_removed, error_message = updater.remove_jsonData()
            if remove_success:
                get_success, folders_processed, files_processed, error_message = updater.get_jsonData()
    
        if remove_success:
            await ctx.send(f"{ctx.author.mention} I removed {folders_removed} folder(s) with {files_removed} file(s)")
            if get_success:
                await ctx.send(f"{ctx.author.mention} I updated {folders_processed} folder(s) and {files_processed} file(s)")
            else:
                await ctx.send(f"Get Error: {error_message}")
        else:
            await ctx.send(f"Remove Error: {error_message}")
            
    else:
        await ctx.send("You do not have permission to use this command.")

@tasks.loop(minutes=5)
async def change_status():
    tz = pytz.timezone('America/Los_Angeles')
    la_time_now = datetime.now(tz)
    if la_time_now.date() == '2024-10-10':
        activity = discord.Activity(type=discord.ActivityType.playing('The First Descendant'))
        await client.change_presence(status=discord.Status.online, activity=activity)
        change_status.stop()

    

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load()
        await client.start(os.environ['DISCORD_API_KEY'])

asyncio.run(main())