import discord


async def send_error_message(interaction: discord.Interaction, error_message: str):
    descendant_embed = discord.Embed(title="Error",
         description=error_message,
         color=discord.Color.red())
    thumbnail_filename = 'ErrorIcon.png'
    thumbnail_file = discord.File(f'icons/{thumbnail_filename}',
    filename=f'{thumbnail_filename}')
    descendant_embed.set_thumbnail(url=f'attachment://{thumbnail_file.filename}')
    await interaction.response.send_message(embed=descendant_embed,file=thumbnail_file)