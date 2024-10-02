import re
import os
import io
import json
import math
import discord
import pytz

import TFD_API
import ConvertImage

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime, timedelta
from errorHandler import send_error_message

def get_current_rotation():
    # Set the timezone
    time_in_timezone = datetime(2024, 7, 30, 12, 0)
    tz = pytz.timezone('America/Los_Angeles')

    # Get the current time in the specified timezone
    current_time = datetime.now(tz)

    # Ensure the input time is also in the correct timezone
    if time_in_timezone.tzinfo is None:
        time_in_timezone = tz.localize(time_in_timezone)

    # Calculate the time difference
    time_diff = current_time - time_in_timezone

    # Convert the time difference to weeks
    current_rotation = (time_diff.days // 7) + 1
    return current_rotation

def get_current_rotation_dates(rotation_number):
    # Set the reference time (start of rotation 1)
    time_in_timezone = datetime(2024, 7, 30, 12, 0)  # Start date of the first rotation
    tz = pytz.timezone('America/Los_Angeles')

    # Ensure the input time is also in the correct timezone
    if time_in_timezone.tzinfo is None:
        time_in_timezone = tz.localize(time_in_timezone)

    # Calculate the start date of the given rotation
    start_date = time_in_timezone + timedelta(weeks=(rotation_number - 1))
    end_date = start_date + timedelta(days=6)

    # Format the start and end dates in 'm/d' format (manually stripping leading zeros)
    start_date_str = start_date.strftime("%m/%d").lstrip("0").replace("/0", "/")
    end_date_str = end_date.strftime("%m/%d").lstrip("0").replace("/0", "/")

    # Return the formatted date range
    return f"{start_date_str} - {end_date_str}"

class SkillButton(Button):
    def __init__(self, label, skill, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)
        self.skill = skill  # Store the skill data

    async def callback(self, interaction: discord.Interaction):
        # When button is clicked, send the skill details
        await self.view.parent.get_d_skill(interaction, self.skill)

class Search(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user or reaction:
            return


    #Full Search
    @app_commands.command(name="search", description="Search for a player")
    async def search(self, interaction: discord.Interaction, name: str):
        descendantJSON = TFD_API.search_player_descendant(name)
        if 'error' not in descendantJSON:
            descendant_id = descendantJSON['descendant_id']
            descendant_files = os.listdir('jsonData/descendants')
            pattern = re.compile(rf'.* - {descendant_id}\.json')
            descendant_filename = next((f for f in descendant_files if pattern.search(f)), None)
            with open(f'jsonData/descendants/{descendant_filename}', 'r') as f:
                descendant_data = json.load(f)
    
            descendant_embed = discord.Embed(title=f"__**{descendant_data['descendant_name']}**__",color=discord.Color.blurple())
            descendant_embed.set_thumbnail(url=descendant_data['descendant_image_url'])
    
            module_files = os.listdir('jsonData/modules')
            for module in descendantJSON['module']:
                pattern = re.compile(rf'.* - {module["module_id"]}\.json')
                module_filename = next((f for f in module_files if pattern.search(f)), None)
                with open(f'jsonData/modules/{module_filename}', 'r') as f:
                    module_data = json.load(f)
                descendant_embed.add_field(name=f"**{module_data['module_name']}**", value=f"```Enhancement Level: {module['module_enchant_level']}```", inline=True)
            descendant_embed.add_field(name='OUID',value=f"{descendantJSON['ouid']}", inline=False)
            descendant_embed.set_author(name=f"{descendantJSON['user_name']}")
            await interaction.response.send_message(embed=descendant_embed)
        else:
            await send_error_message(interaction, f"{descendantJSON['error']['message']}")

    

    
    
    #Basic Search
    @app_commands.command(name="bsearch", description="Search for a player's basic information")
    async def bsearch(self, interaction: discord.Interaction, name: str):

        infoJSON = TFD_API.search_playerBasic_descendant(name)
        if 'error' not in infoJSON:
            platform_url = str()

            if infoJSON['platform_type'] == 'Steam':
                platform_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2048px-Steam_icon_logo.svg.png'
            elif infoJSON['platform_type'] == 'Xbox':
                platform_url = 'https://www.citypng.com/public/uploads/preview/png-xbox-green-symbol-logo-icon-701751694970230bvp7gefsu3.png'
            elif infoJSON['platform_type'] == 'PlayStation':
                platform_url = 'https://static-00.iconduck.com/assets.00/playstation-icon-2048x1665-icu9gzjj.png'

            basicInfo_embed = discord.Embed(title=f"Mastery Rank: {infoJSON['mastery_rank_level']}",color=discord.Color.blurple())
            basicInfo_embed.add_field(name="Mastery Rank XP", value=f"{infoJSON['mastery_rank_exp']:,}")
            basicInfo_embed.add_field(name="OUID", value=f"{infoJSON['ouid']}", inline=False)
            basicInfo_embed.set_thumbnail(url=TFD_API.mastery_rank_icon_urls[f"{infoJSON['mastery_rank_level']}"])
            basicInfo_embed.set_author(name=f"{infoJSON['user_name']}", icon_url=platform_url)
            await interaction.response.send_message(embed=basicInfo_embed)
        else:
            basicInfo_embed = discord.Embed(title=f"Error",
                 description=f"{infoJSON['error']['message']}",
                 color=discord.Color.red())
            thumbnail_filename = 'ErrorIcon.png'
            thumbnail_file = discord.File(f'icons/{thumbnail_filename}',
            filename=f'{thumbnail_filename}')
            basicInfo_embed.set_thumbnail(url=f'attachment://{thumbnail_file.filename}')
            await interaction.response.send_message(embed=basicInfo_embed,file=thumbnail_file)



    async def get_d_skill(self, interaction, descendant_skill_data):
        try:
            skill_name = descendant_skill_data["skill_name"]
            skill_type = descendant_skill_data["skill_type"]
            skill_arche_type = descendant_skill_data["arche_type"]
            skill_element_type = descendant_skill_data["element_type"]
            skill_description = descendant_skill_data["skill_description"]
            skill_image = descendant_skill_data["skill_image_url"]
            skill_embed = discord.Embed(title=skill_name, color=discord.Color.gold())
            skill_embed.add_field(name="Skill Type", value=skill_type, inline=False)
            skill_embed.add_field(name="Element Type", value=skill_element_type, inline=False)
            skill_embed.add_field(name="Arche Type", value=skill_arche_type, inline=False)
            skill_embed.add_field(name="Description", value=skill_description, inline=False)
            skill_embed.set_thumbnail(url=skill_image)
            await interaction.response.send_message(embed=skill_embed)
        except Exception as e:
            await send_error_message(interaction, str(e))

    
    async def descendant_autocomplete(self, interaction: discord.Interaction, current: str):
        descendant_files = os.listdir('jsonData/descendants')
        choices = [
            app_commands.Choice(name=file.split(' ')[0].replace('_',' '), value=file.split(' ')[0])
            for file in descendant_files if current.replace(' ','_').lower() in file.lower()
        ]
        return choices
    
    #dsearch
    @app_commands.command(name="dsearch", description="Search for a descendant")
    @app_commands.autocomplete(descendant=descendant_autocomplete)
    async def dsearch(self, interaction: discord.Interaction, descendant: str, level: app_commands.Range[int, 1, 40] = 1):
        pattern = re.compile(rf"{descendant.strip().replace(' ','_')}.*\.json", re.IGNORECASE)
        descendant_filename = next((f for f in os.listdir('jsonData/descendants') if pattern.search(f)), None)
        #print('filename:', descendant_filename)
        if descendant_filename is None:
            await send_error_message(interaction, f"No descendant found with the name '{descendant}'")
            return
        with open(f'jsonData/descendants/{descendant_filename}', 'r') as f:
            descendant_data = json.load(f)
        descendant_name = descendant_data['descendant_name']
        descendant_image_url = descendant_data['descendant_image_url']
        for stat in descendant_data['descendant_stat']:
            if stat['level'] == level:
                descendant_level_stat = stat
                break
        
        #create skill buttons
        skill_view = View()
        skill_view.parent = self
            # Add a button for each skill
        for skill in descendant_data['descendant_skill']:
            skill_button = SkillButton(label=skill['skill_name'], skill=skill, emoji="🌟")
            skill_view.add_item(skill_button)
        
        descendant_level_stat_embed = discord.Embed(title=f"__**{descendant_name}**__",
                                                    description=f"Level: {descendant_level_stat['level']}",
                                                    color=discord.Color.gold() if descendant_data['descendant_name'].startswith('Ultimate') else discord.Color.blurple())
        descendant_level_stat_embed.set_thumbnail(url=descendant_image_url)
        for detail in descendant_level_stat['stat_detail']:
            descendant_level_stat_embed.add_field(name=f"{detail['stat_type']}", value=detail['stat_value'], inline=False)
        await interaction.response.send_message(embed=descendant_level_stat_embed, view=skill_view)
        
                                   





    weapon_ammo_type_serials = {
        "General": 25201,
        "Special": 25202,
        "Impact": 25203,
        "High-Power": 25204,
    }

    TierColors = {
        'Standard': discord.Color.light_grey(),
        'Rare': discord.Color.purple(),
        'Ultimate': discord.Color.gold(),
        'Transcendent': discord.Color.red()
    }

    async def fetch_emoji(self, emoji_id: int):
        emoji = await self.client.fetch_application_emoji(emoji_id)
        return emoji
    

    async def create_module_embed(self, module_filename):
        with open(f'jsonData/modules/{module_filename}', 'r') as f:
            module_data = json.load(f)
        cata_emoji = await self.fetch_emoji(1288695979402592358)
        module_emoji = await self.fetch_emoji(1289360620717867109)
        module_name = module_data['module_name']
        module_type = module_data['module_type']
        module_tier = module_data['module_tier']
        module_socket_type = module_data['module_socket_type']
        module_class = module_data['module_class']
        module_img_url = module_data['image_url']
        module_stats = module_data['module_stat']

        module_embed = discord.Embed(
            title=f"{module_name}",
            description=f"{module_tier} - {module_class} - {module_socket_type}",
            color=self.TierColors[module_tier])
        module_embed.set_thumbnail(url=module_img_url)
        module_embed.add_field(name="Module Type", value=module_type)
        for stat in module_stats:
            catalyst_value = math.ceil(stat['module_capacity'] / 2)
            module_embed.add_field(
                name=f"**Level {stat['level']}:**",
                value=
                f"{module_emoji}: `{stat['module_capacity']}` | {cata_emoji}: `{catalyst_value}`\n{stat['value']}",
                inline=False)
        return module_embed




    #module Search
    @app_commands.command(name="msearch", description="Search for a module")
    @app_commands.choices(ammo_type=[
        app_commands.Choice(name='General', value=1),
        app_commands.Choice(name='Special', value=2),
        app_commands.Choice(name='Impact', value=3),
        app_commands.Choice(name='High-Power', value=4),
    ])
    async def msearch(self, interaction: discord.Interaction,
                      module_name: str,
                      ammo_type: app_commands.Choice[int] = None):
        module_files = os.listdir('jsonData/modules')
        module_name = module_name.strip().replace(' ', '_')
        print(f'looking for "{module_name} - *.json"')
        #broad search for module name
        pattern = re.compile(rf"{module_name}.*\.json", re.IGNORECASE)
        module_filenames = [f for f in module_files if pattern.search(f)]
        print(module_filenames)
        if len(module_filenames) > 0:

            if ammo_type is not None:
                matching_module_files = []

                for module in module_filenames:
                    module_serial = module.split(' ')[-1].split('.')[0]

                    if module_serial.startswith(
                            str(self.weapon_ammo_type_serials[ammo_type.name])):
                        matching_module_files.append(module)

                if len(matching_module_files) > 1:
                    await interaction.response.send_message(
                        embed = await self.create_module_embed(matching_module_files[0]))
                    #await interaction.response.send_message(f"Found {len(matching_module_files)} modules with ammo type {ammo_type.name} and name {module_name}.")

                elif len(matching_module_files) == 1:
                    module_embed = await self.create_module_embed(matching_module_files[0])
                    await interaction.response.send_message(embed=module_embed)

                else:
                    await interaction.response.send_message(
                        f"No modules found with ammo type {ammo_type.name}.")

            elif len(module_filenames) > 1 and module_filenames[0].split(
                    ' ')[-1].split('.')[0].startswith('252'):
                await interaction.response.send_message(
                    "You seem to be looking for weapon module, please specify the ammo type."
                )
            elif len(module_filenames) > 1 and module_filenames[0].split(
                    ' ')[-1].split('.')[0].startswith('25'):
                found_modules = '\n- '.join([
                    filename[:-9].replace('25201', 'General').replace(
                        '25202', 'Special').replace('25203', 'Imapact').replace(
                            '25204', 'High-Power').replace('25100', 'Descendant') for filename in module_filenames
                ])
                await interaction.response.send_message(
                    f"I have found multiple modules that match your search. Please be more specific.\n\nModules Found:\n- {found_modules}"
                )

            elif len(module_filenames) == 1:
                module_embed = await self.create_module_embed(module_filenames[0])
                await interaction.response.send_message(embed=module_embed)
                #cata_emoji = await self.fetch_emoji(1288695979402592358)
                #message = await interaction.original_response()
                #await message.add_reaction(cata_emoji)
                #print('added emoji')
        else:
            await interaction.response.send_message(
                f"No modules found with name {module_name}.")





    
    #reward search
    @app_commands.command(name="rsearch", description="Search for weekly rewards")
    @app_commands.choices(reward_type=[
        app_commands.Choice(name='Reactor', value=1),
        app_commands.Choice(name='Auxiliary Power', value=2),
        app_commands.Choice(name='Sensor', value=3),
        app_commands.Choice(name='Memory', value=4),
        app_commands.Choice(name='Processor', value=5),
    ])
    @app_commands.choices(element_type=[
        app_commands.Choice(name='Chill', value=1),
        app_commands.Choice(name='Electric', value=2),
        app_commands.Choice(name='Fire', value=3),
        app_commands.Choice(name='Non-Attribute', value=4),
        app_commands.Choice(name='Toxic', value=5),
    ])
    @app_commands.choices(ammo_type=[
        app_commands.Choice(name='General Rounds', value=1),
        app_commands.Choice(name='Special Rounds', value=2),
        app_commands.Choice(name='Impact Rounds', value=3),
        app_commands.Choice(name='High-Power Rounds', value=4),
    ])
    @app_commands.choices(arche_type=[
        app_commands.Choice(name='Dimension', value=1),
        app_commands.Choice(name='Fusion', value=2),
        app_commands.Choice(name='Tech', value=3),
        app_commands.Choice(name='Singular', value=4),
    ])
    async def rsearch(self,
                      interaction: discord.Interaction,
                      reward_type: app_commands.Choice[int],
                      element_type: app_commands.Choice[int] = None,
                      ammo_type: app_commands.Choice[int] = None,
                      arche_type: app_commands.Choice[int] = None,
                      rotations_ahead: int = 0):
        
        search = [reward_type.name,
                  element_type.name if element_type is not None else None,
                  ammo_type.name if ammo_type is not None else None,
                  arche_type.name if arche_type is not None else None]
        
        keys = ["reward_type", "reactor_element_type", "weapon_rounds_type", "arche_type"]
        pattern = re.compile(r'^(?!\d)')
        reward_files = [f for f in os.listdir('jsonData/rewards') if pattern.search(f)]
        current_rewards = []
        for file in reward_files:
            with open(f'jsonData/rewards/{file}', 'r') as f:
                rewards_data = json.load(f)
            map_name = rewards_data['map_name']
            for battle_zone in rewards_data['battle_zone']:
                battle_zone_name = battle_zone['battle_zone_name']
                for reward in battle_zone['reward']:
                    if reward['rotation'] == get_current_rotation() + rotations_ahead:
                        reward['map_name'] = map_name
                        reward['battle_zone_name'] = battle_zone_name
                        current_rewards.append(reward)
        #print('current_rewards', current_rewards)
        filtered_rewards = [
            reward for reward in current_rewards
            if all(
                search_val is None or reward.get(key) == search_val
                for key, search_val in zip(keys, search)
            )
        ]
        #print('filtered_rewards', filtered_rewards)
        reward_embed = discord.Embed(title=f"__**Weekly Rewards:**__ {get_current_rotation_dates(get_current_rotation() + rotations_ahead)}",
                                     description=f"{' | '.join(item for item in search if item is not None)}",
                                    color=self.TierColors['Ultimate'])
        reward_embed.set_thumbnail(url='https://pics.freeicons.io/uploads/icons/png/7766604441644374638-512.png')
        if len(filtered_rewards) > 0:
            rewards_by_map = {}
            for reward in filtered_rewards:
                map_name = reward['map_name']
                if map_name not in rewards_by_map:
                    rewards_by_map[map_name] = []
                rewards_by_map[map_name].append(reward)
            #print('rewards_by_map', rewards_by_map)
            for map_name, rewards in rewards_by_map.items():
                reward_details = "\n".join(f"- __{reward['battle_zone_name']}__ - {reward['reward_type']}, {reward.get('reactor_element_type', 'N/A')}, {reward.get('weapon_rounds_type', 'N/A')}, {reward.get('arche_type', 'N/A')}" for reward in rewards)
                reward_embed.add_field(name=map_name, value=reward_details, inline=False)
        else:
            reward_embed.add_field(name="No Rewards Found", value="No rewards found based on your search")
        await interaction.response.send_message(embed=reward_embed)



    async def get_w_special_ability(self, interaction, weapon_data):
        ability_name = weapon_data["weapon_perk_ability_name"]
        ability_description = weapon_data["weapon_perk_ability_description"]
        ability_image = weapon_data["weapon_perk_ability_image_url"]
        ability_embed = discord.Embed(title=ability_name,description=ability_description, color=discord.Color.gold())
        ability_embed.set_thumbnail(url=ability_image)
        await interaction.response.send_message(embed=ability_embed)



    
    
    #weapon Search
    @app_commands.command(name="wsearch", description="Search for a weapon")
    async def wsearch(self, interaction: discord.Interaction, weapon_name: str):
        #search for weapon name
        weapon_files = os.listdir('jsonData/weapons')
        #print(weapon_files)
        weapon_name = weapon_name.strip().replace(' ','_')
        print(f'looking for "{weapon_name} - *.json"')
        #broad search for weapon name
        pattern = re.compile(rf"{weapon_name}.*\.json", re.IGNORECASE)
        weapon_filename = next((f for f in weapon_files if pattern.search(f)), None)
        #load weapon data
        if weapon_filename is not None:
            with open(f'jsonData/weapons/{weapon_filename}', 'r') as f:
                weapon_data = json.load(f)
            TierColors = {
                'Standard': discord.Color.light_grey(),
                'Rare': discord.Color.purple(),
                'Ultimate': discord.Color.gold()
            }
            weapon_embed = discord.Embed(title=f"__**{weapon_data['weapon_name']}**__",
                                         color=TierColors[f'{weapon_data["weapon_tier"]}'])

            image = ConvertImage.trim_transparent(weapon_data['image_url'])
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                thumbnail = discord.File(image_binary, filename='image.png')
                weapon_embed.set_image(url='attachment://image.png')


            #weapon_embed.set_thumbnail(url=weapon_data['image_url'])
            weapon_embed.add_field(name="Type", value=f"```{weapon_data['weapon_type']}```",
                                   inline=True)
            weapon_embed.add_field(name="Tier", value=f"```{weapon_data['weapon_tier']}```",
                                   inline=True)
            weapon_embed.add_field(name="Rounds Type",
                                   value=f"```{weapon_data['weapon_rounds_type']}```",
                                   inline=True)
            #load stats
            stat_files = os.listdir('jsonData/stats')
            stat_entries = 0
            for stat in weapon_data['base_stat']:
                pattern = re.compile(rf'.* - {stat["stat_id"]}\.json')
                stat_filename = next((f for f in stat_files if pattern.search(f)), None)
                if stat_filename is not None:
                    with open(f'jsonData/stats/{stat_filename}', 'r') as f:
                        stat_data = json.load(f)
                    #display each stat and its value
                    weapon_embed.add_field(name=f"{stat_data['stat_name']}",
                                           value=f"```{stat['stat_value']}```",
                                           inline=True)
                    stat_entries += 1
                    if stat_entries == 21:
                        break
                else:
                    print(f"Error: stat_id {stat['stat_id']} not found")
            if weapon_data["weapon_tier"] == 'Ultimate':
                # Assigning the callback for the button
                special_ability_button = Button(label="Special Ability", style=discord.ButtonStyle.primary, emoji="🌟")
                
                async def special_ability_button_callback(interaction: discord.Interaction):
                    await self.get_w_special_ability(interaction, weapon_data)

                special_ability_button.callback = special_ability_button_callback
                special_ability_view = View()
                special_ability_view.add_item(special_ability_button)
                await interaction.response.send_message(embed=weapon_embed, file=thumbnail, view=special_ability_view)
            else:
                await interaction.response.send_message(embed=weapon_embed, file=thumbnail)
        else:
            await send_error_message(interaction, f"{weapon_name.replace(' ','_')} weapon not found")




async def setup(client):
    await client.add_cog(Search(client))