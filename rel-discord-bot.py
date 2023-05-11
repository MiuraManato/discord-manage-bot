import discord
from discord.ext import commands
import asyncio,os

bot = commands.Bot(command_prefix="/",intents=discord.Intents.all())
TOKEN = os.environ["VCtoTEXT_TOKEN"]

@bot.event
async def on_ready():
  """Print a message to indicate that the bot has logged in successfully."""
  print(f"Bot logged in as {bot.user}")

BLACKLIST_FILE = "blacklist.txt"
# blacklistにメンバーを追加
@bot.command()
# ブラックリストに追加・削除する処理
async def blacklist(ctx,*args):
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
      lines = f.read()
      await ctx.send(lines)
  # ---ブラックリスト表示処理ここまで---

def checkBlacklist(member):
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

bot.run(TOKEN)