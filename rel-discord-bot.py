import asyncio
import os
import random
import json
import datetime

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
TOKEN = os.environ["DISCORD_TOKEN"]

BLACKLIST_FILE = "./files/blacklist.txt"
COMMANDS = "./files/commands.json"
in_voice_member = set()


@bot.event
async def on_ready():
    """Print a message to indicate that the bot has logged in successfully."""
    print(f"Bot logged in as {bot.user}")


@bot.command()
async def blacklist(ctx, *args):
    """Add or remove members from the blacklist."""
    if not ctx.author.guild_permissions.administrator:
        return

    if args[0] == "add":
        with open(BLACKLIST_FILE, "a") as f:
            f.write(f"{args[1]}\n")
    elif args[0] == "remove":
        with open(BLACKLIST_FILE, "r") as f:
            lines = f.readlines()
            for line in lines:
                if args[1] in line:
                    lines.remove(line)
        with open(BLACKLIST_FILE, "w") as f:
            f.writelines(lines)
    elif args[0] == "list":
        with open(BLACKLIST_FILE, "r") as f:
            lines = f.read().splitlines()
            fields = {f"Member {i+1}": member for i, member in enumerate(lines)}
            await send_embed(
                ctx,
                "Blacklist Members",
                "Here are the members in the blacklist.",
                fields=fields,
            )


def check_blacklist(member):
    """Check if the member is in the blacklist."""
    with open(BLACKLIST_FILE) as f:
        return any(member == line.strip() for line in f)


async def manage_role(member, id):
    """Manage roles.
    id = 1 : add role
    id = 2 : remove role
    """
    if check_blacklist(str(member)):
        return
    role = discord.utils.get(member.guild.roles, name="通話中")

    if id == 1:
        await member.add_roles(role)
        in_voice_member.add(member)
    elif id == 2:
        await member.remove_roles(role)
        in_voice_member.remove(member)


@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates."""
    if before.channel is None and after.channel is not None and member not in in_voice_member:
        save_log(member, 1)
        await manage_role(member, 1)
    if member in in_voice_member and after.channel is None:
        save_log(member, 2)
        await asyncio.sleep(60)
        await manage_role(member, 2)


def save_log(member, id):
    """Save the log."""
    inout = "入室" if id == 1 else "退室"
    now = lambda: datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open("./files/log.txt", "a") as f:
        f.write(f"[{now()}] {member.name}が{inout}しました。\n")




async def send_embed(ctx, title, description, color=discord.Color.blue(), fields=None):
    """Send an embed."""
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def omikuzi(ctx):
    """Draw a fortune."""
    await ctx.send(random.choice(["大吉", "吉", "半吉", "凶", "半凶", "大凶"]))


@bot.command()
async def nya(ctx):
    """Send a random cat message."""
    message = random.choice(["にゃーん", "みゃ", "にゃう", "しゃーっ", "みゃおん", "nyancat"])
    await ctx.send(file=discord.File("nyancat.gif")) if message == "nyancat" else await ctx.send(message)

@bot.command()
async def members(ctx):
    if ctx.author.voice is None:
        return
    members = ctx.author.voice.channel.members
    member_list = "\n".join([member.name for member in members])
    await send_embed(ctx, "Voice Channel Members", member_list)


bot.remove_command('help')
@bot.command()
async def help(ctx):
    """Show the bot's help message."""
    with open(COMMANDS) as f:
        commands = json.load(f)

    embed = discord.Embed(title="Help", description="List of commands", color=discord.Color.blue())
    for command in commands.values():
        embed.add_field(name=command["name"], value=command["description"], inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
