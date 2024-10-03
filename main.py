import os
import asyncio
import platform
import discord
import updater
import pytz
import json

from message_embeds import send_error_message

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


@client.command()
async def update(ctx, file: str = None):
    if ctx.author.id == 292003372649807872:
        await ctx.send("Updating...")
        #Helper function
        def process_update(func, file=None):
            success, files, item_count, error = func(file)
            if success:
                return f"{'='*30}\n{ctx.author.mention} I {'removed' if func.__name__ == 'remove_json' else 'fetched'} {len(files)} files:\n- " \
                       f"{'\n- '.join(files)}\nContaining {item_count} items\n{'='*30}", None
            else:
                return None, error

        #Handle plural "s" at the end of the file
        if file and file.endswith('s'):
            file = file.rstrip('s')

        #Removing and fetching logic
        remove_message, remove_error = process_update(updater.remove_json, file)
        if remove_error:
            await ctx.send(f"Remove Error: {remove_error}")
            return
        await ctx.send(remove_message)

        fetch_message, fetch_error = process_update(updater.fetch_json, file)
        if fetch_error:
            await ctx.send(f"Fetch Error: {fetch_error}")
            return
        await ctx.send(fetch_message)

    else:
        await ctx.send("You do not have permission to use this command.")

@client.command()
async def count(ctx, file: str):
    if file.endswith('s'):
        file = file.rstrip('s')
    try:
        with open(f'jsonData/{file}s.json') as f:
            await ctx.send(f"There are {len(json.load(f))} {file}s")
    except Exception as e:
        await ctx.send(f"Error: {e}")



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
