import json
import re
import discord
import TFD_API

from message_embeds import send_error_message, send_success_message, send_info_message
from discord import app_commands
from discord.ext import commands



class Link(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready")

    @app_commands.command(name="link", description="Links your discord account with the provided Nexon account")
    async def link(self, interaction: discord.Interaction, nexon_account_name: str):
        nexon_account_name = nexon_account_name.strip()
        pattern = re.compile(r'^.*#\d{4}$', re.IGNORECASE)
        if pattern.match(nexon_account_name):
            nexon_ouid_lookup = TFD_API.search_ouid(nexon_account_name)
            if 'error' not in nexon_ouid_lookup:
                account_data = {
                    "Discord_Username":interaction.user.name,
                    "Discord_User_ID":interaction.user.id,
                    "Nexon_Username":nexon_account_name,
                    "Nexon_User_ID":nexon_ouid_lookup['ouid']
                }
                with open('jsonData/userlinks.json', 'r') as f:
                    links = json.load(f)

                #convert lists to sets for O(1) time complexity
                current_discord_ids = set([link['Discord_User_ID'] for link in links])
                current_nexon_ids = set([link['Nexon_User_ID'] for link in links])

                if account_data['Discord_User_ID'] not in current_discord_ids and account_data['Nexon_User_ID'] not in current_nexon_ids:
                    links.append(account_data)
                    try:
                        with open('jsonData/userlinks.json', 'w') as f:
                            json.dump(links, f, indent=4)
                        await send_success_message(interaction, f"{account_data['Discord_Username']} has been linked to the Nexon Account:\n`{nexon_account_name}`")
                    except Exception as e:
                        await send_error_message(interaction, e)

                elif account_data['Discord_User_ID'] in current_discord_ids:
                    await send_error_message(interaction, f"Your Discord is already linked to a Nexon account")
                
                elif account_data['Nexon_User_ID'] in current_nexon_ids:
                    await send_error_message(interaction, f"The Nexon account `{nexon_account_name}` is already linked to another Discord account")

            else:
                await send_error_message(interaction, f"The account `{nexon_account_name}` was not found")
        else:
            await send_error_message(interaction, f"`{nexon_account_name}` does not match the username format. Example: `username#1234`")
    
    @app_commands.command(name="unlink", description="Unlinks your discord account from your Nexon account")
    async def unlink(self, interaction: discord.Interaction):
        with open('jsonData/userlinks.json', 'r') as f:
            links = json.load(f)
        removed = False
        for link in links:
            if link["Discord_User_ID"] == interaction.user.id:
                links.remove(link)
                with open('jsonData/userlinks.json', 'w') as f:
                    json.dump(links, f, indent=4)
                removed = True
                break
        if removed:
            await send_info_message(interaction, "Your account has been unlinked")
        else:
            await send_error_message(interaction, "Your account is not linked")
                
        


async def setup(client):
    await client.add_cog(Link(client))
