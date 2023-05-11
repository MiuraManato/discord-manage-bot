import discord
from discord.ext import commands
import asyncio,os,random

bot = commands.Bot(command_prefix="/",intents=discord.Intents.all())
TOKEN = os.environ["DISCORD_TOKEN"]

@bot.event
async def on_ready():
  """Print a message to indicate that the bot has logged in successfully."""
  print(f"Bot logged in as {bot.user}")

BLACKLIST_FILE = "blacklist.txt"
# blacklistにメンバーを追加
@bot.command()
# ブラックリストに追加・削除する処理
async def blacklist(ctx,*args):
  # 管理者以外だったら何もしない
  if not ctx.author.guild_permissions.administrator:
    return
  # ---以下追加処理---
  if args[0] == "add":
    with open(BLACKLIST_FILE, 'a') as f:
      f.write(f'{args[1]}\n')
  # ---追加処理ここまで---
  # ---以下削除処理---
  elif args[0] == "remove":
    with open(BLACKLIST_FILE, 'r') as f:
      lines = f.readlines()
      for line in lines:
        if args[1] in line:
          lines.remove(line)
    with open(BLACKLIST_FILE, 'w') as f:
      f.writelines(lines)
  # ---削除処理ここまで---
  # ---ブラックリスト表示処理---
  elif args[0] == "list":
    with open(BLACKLIST_FILE, 'r') as f:
      lines = f.read().splitlines()
      fields = {f'Member {i+1}': member for i, member in enumerate(lines)}
      await send_embed(ctx, "Blacklist Members", "Here are the members in the blacklist", fields=fields)
  # ---ブラックリスト表示処理ここまで---

def checkBlacklist(member):
  """Check if the member is in the blacklist."""
  with open(BLACKLIST_FILE) as f:
    return any(member == line.strip() for line in f)

async def ManageRole(member,id):
  """Manage Roles
  id = 1 : add role
  id = 2 : remove role
  """
  if checkBlacklist(str(member)):
    return
  role = discord.utils.get(member.guild.roles, name="通話中")
  # ロールを付与する処理
  if id == 1:
    await member.add_roles(role)
    inVoiceMember.add(member)
  # ロールを削除する処理
  elif id == 2:
    await member.remove_roles(role)
    inVoiceMember.remove(member)

inVoiceMember = set()
@bot.event
async def on_voice_state_update(member, before, after):
  """ボイスチャンネルに変更があった場合に受け取る"""
  # ボイスチャンネルに新規接続されたユーザーがいたら実行する
  if before.channel is None and after.channel is not None and member not in inVoiceMember:
    
    await ManageRole(member,1)
  # ボイスチャンネルを退出したユーザーがいたら実行する
  if member in inVoiceMember and after.channel is None:
    await asyncio.sleep(60) # 1分間待機
    await ManageRole(member,2)


async def send_embed(ctx, title, description, color=discord.Color.blue(), fields=None):
  """Send an embed."""
  embed = discord.Embed(title=title, description=description, color=color)
  if fields:
      for name, value in fields.items():
          embed.add_field(name=name, value=value, inline=False)
  await ctx.send(embed=embed)


# おみくじ機能
@bot.command()
async def omikuzi(ctx):
  await ctx.send(random.choice(["大吉","吉","半吉","凶","半凶","大凶"]))

# 猫
@bot.command()
async def nya(ctx):
  message = random.choice(["にゃーん","みゃ","にゃう","しゃーっ","みゃおん","nyancat"])
  await ctx.send(file=discord.File("nyancat.gif")) if message == "nyancat" else await ctx.send(message)

# 通話にいるメンバー一覧を表示
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
  """Show this help message."""
  embed = discord.Embed(title="Help", description="List of commands", color=discord.Color.blue())
  embed.add_field(name="/blacklist [add/remove/list] [user]", value="Add, remove or list users in the blacklist. (Administrator only)", inline=False)
  embed.add_field(name="/omikuzi", value="Draw a fortune.", inline=False)
  embed.add_field(name="/nya", value="Send a random cat message.", inline=False)
  embed.add_field(name="/members", value="List members currently in voice channel.", inline=False)
  embed.add_field(name="/help", value="Show this help message.", inline=False)
  await ctx.send(embed=embed)

bot.run(TOKEN)
