import os
import discord
from discord import app_commands
from handlers import voice_state_update_handler
from commands import setup_commands
from utils import read_blacklist, read_commands

TOKEN = os.environ['SBA_TOKEN']
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)

# Load blacklist and commands
blacklist = read_blacklist()
commands = read_commands()

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await tree.sync()

@bot.event
async def on_voice_state_update(member, before, after):
    await voice_state_update_handler(member, before, after)

setup_commands(tree)  # Set up commands

bot.run(TOKEN)
