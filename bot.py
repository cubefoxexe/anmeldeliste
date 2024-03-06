import discord
from discord.ext import commands
import scrape
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()
token = os.getenv('token')
roleid = os.getenv('roleid')
guildid = os.getenv('guildid')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

scrapeing = {}

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

async def check(channelid):
    info = await scrape.weeks()
    with open("info.json", "r") as f:
        old_info = json.load(f)
    with open("info.json", "w") as f:
        json.dump(info, f)
    new_week = await scrape.new_week(old_info, info)
    if new_week is not None:
        guild = bot.get_guild(int(guildid))
        role = guild.get_role(int(roleid))
        await role.edit(mentionable=True)
        await guild.get_channel(int(channelid)).send(f"{role.mention} New week: {new_week} has been added.")

    embed = discord.Embed(title="Status", description="Status of the next 4 weeks", color=0x00ff00)
    for key, value in info.items():
        embed.add_field(name=key, value=":white_check_mark:" if value else ":x:", inline=True)

    return embed

@bot.tree.command(name="status")
async def status(interaction: discord.Interaction, hidden: bool=None):
    hidden = hidden if hidden is not None else False

    if interaction.user.id in scrapeing and scrapeing[interaction.user.id]:
        await interaction.response.send_message("You are already scrapeing", ephemeral=True)
        return
    
    scrapeing[interaction.user.id] = True

    try:
        channelid = interaction.channel_id
        channel = bot.get_channel(channelid)
        await interaction.response.defer(ephemeral=True)
        embed = await check(channelid)

        if hidden:
            await interaction.edit_original_response(content="Status updated", embed=embed)
        else:
            await interaction.delete_original_response()
            await channel.send(embed=embed)
        
        scrapeing[interaction.user.id] = False
    except:
        pass

@bot.tree.command(name="start")
async def start(interaction: discord.Interaction, interval: int, hidden: bool=None):
    hidden = hidden if hidden is not None else False
    if interaction.user.id in scrapeing and scrapeing[interaction.user.id]:
        await interaction.response.send_message("You are already scrapeing", ephemeral=True)
        return
    
    scrapeing[interaction.user.id] = True
    try:
        channelid = interaction.channel_id
        channel = bot.get_channel(channelid)
        await interaction.response.defer(ephemeral=True)
        if hidden:
            await interaction.edit_original_response(content=f"updating...")
        else:
            await interaction.delete_original_response()
            msg = await channel.send(content=f"updating...")
        while scrapeing[interaction.user.id]:
            embed = await check(channelid)
            if hidden:
                await interaction.edit_original_response(content=f"Status updated next in {interval}", embed=embed)
            else:
                await msg.edit(content=f"Status updated next in {interval}", embed=embed)
            for i in range(interval):
                if scrapeing[interaction.user.id]:
                    await asyncio.sleep(1)
                    if hidden:
                        await interaction.edit_original_response(content=f"Status updated next in {interval-i-1}")
                    else:
                        await msg.edit(content=f"Status updated next in {interval-i-1}")
                else:
                    if hidden:
                        await interaction.edit_original_response(content=f"Stopped scrapeing")
                    else:
                        await msg.edit(content=f"Stopped scrapeing")
                    return

            if hidden:
                await interaction.edit_original_response(content=f"updating...")
            else:
                await msg.edit(content=f"updating...")
                
        
        scrapeing[interaction.user.id] = False
    except:
        pass

@bot.tree.command(name="stop")
async def stop(interaction: discord.Interaction):
    if interaction.user.id in scrapeing:
        scrapeing[interaction.user.id] = False
        await interaction.response.send_message("Stopped scrapeing", ephemeral=True)
    else:
        await interaction.response.send_message("You are not scrapeing", ephemeral=True)

if __name__ == "__main__":
    bot.run(token)
