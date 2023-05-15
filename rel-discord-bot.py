import asyncio
import os
import random
import json
import datetime

import discord
from discord.ext import commands

# Botの設定
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
TOKEN = os.environ["VCtoTEXT_TOKEN"]

# ファイルパスの設定
BLACKLIST_FILE_PATH = "./files/blacklist.txt"
COMMANDS_FILE_PATH = "./files/commands.json"
LOG_FILE_PATH = "./files/log.txt"


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")


@bot.command()
async def blacklist(ctx, *args) -> None:
    """blacklistへの追加、削除、一覧表示"""
    # 管理者以外の場合に実行しない
    if not ctx.author.guild_permissions.administrator:
        return

    # 追加
    if args[0] == "add":
        member_name = " ".join(args[1:])
        with open(BLACKLIST_FILE_PATH, "a") as f:
            f.write(f"{member_name}\n")
    # 削除
    elif args[0] == "remove":
        with open(BLACKLIST_FILE_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                if " ".join(args[1:]) in line:
                    lines.remove(line)
        with open(BLACKLIST_FILE_PATH, "w") as f:
            f.writelines(lines)
    # 一覧表示
    elif args[0] == "list":
        with open(BLACKLIST_FILE_PATH, "r") as f:
            lines = f.read().splitlines()
            fields = {f"Member {i+1}": member for i, member in enumerate(lines)}
            await send_embed(ctx, "Blacklist Members", "Here are the members in the blacklist.", fields=fields)



def check_blacklist(member) -> bool:
    """メンバーがブラックリストに入っているか確認"""
    with open(BLACKLIST_FILE_PATH) as f:
        return any(member == line.strip() for line in f)


async def manage_role(member, id) -> None:
    """ロール管理.
    id = 1 : ロールを付与する
    id = 2 : ロールを削除する
    """
    # ブラックリストに入っているか確認する
    if check_blacklist(str(member)):
        return

    # ロールの設定
    role = discord.utils.get(member.guild.roles, name="通話中")
    if id == 1:
        await member.add_roles(role)
    elif id == 2:
        await member.remove_roles(role)


@bot.event
async def on_voice_state_update(member, before, after) -> None:
    """ボイスステータスハンドルを受け取り処理する"""
    # 直前までボイスチャンネルにいない、直後にボイスチャンネルにいる、通話中ではない場合に実行
    if before.channel is None and after.channel is not None:
        save_log(member, 1)
        await manage_role(member, 1)
    # 直前までボイスチャンネルにいる、直後にボイスチャンネルにいない場合に実行
    if before.channel is not None and after.channel is None:
        save_log(member, 2)
        await asyncio.sleep(60)
        await manage_role(member, 2)


def save_log(member, id) -> None:
    """ログを保存する"""
    text = "入室" if id == 1 else "退室"
    now = lambda: datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(LOG_FILE_PATH, "a") as f:
        f.write(f"[{now()}] {member.name}が{text}しました。\n")


async def send_embed(ctx, title, description, color=discord.Color.blue(), fields=None) -> None:
    """embedに加工してメッセージを送信する"""
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def omikuzi(ctx) -> None:
    """運勢を占う"""
    await ctx.send(random.choice(["大吉", "吉", "半吉", "凶", "半凶", "大凶"]))


@bot.command()
async def nya(ctx) -> None:
    """ネコがなく"""
    message = random.choice(["にゃーん", "みゃ", "にゃう", "しゃーっ", "みゃおん", "nyancat"])
    await ctx.send(file=discord.File("nyancat.gif")) if message == "nyancat" else await ctx.send(message)

@bot.command()
async def members(ctx) -> None:
    """コマンド使用者の通話にいるメンバー一覧を表示"""
    if ctx.author.voice is None:
        return
    members = ctx.author.voice.channel.members
    member_list = "\n".join([member.name for member in members])
    await send_embed(ctx, "Voice Channel Members", member_list)


bot.remove_command('help')
@bot.command()
async def help(ctx) -> None:
    """ヘルプメッセージを表示する"""
    with open(COMMANDS_FILE_PATH) as f:
        commands = json.load(f)

    embed = discord.Embed(title="Help", description="List of commands", color=discord.Color.blue())
    for command in commands.values():
        embed.add_field(name=command["name"], value=command["description"], inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
