import asyncio
import os
import random
import json
import datetime
import subprocess

import discord
from discord import app_commands


TOKEN = os.environ['DISCORD_TOKEN']
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)

# ファイルパスの設定
BLACKLIST_FILE_PATH = "./files/blacklist.txt"
COMMANDS_FILE_PATH = "./files/commands.json"
LOG_FILE_PATH = "./files/log.txt"

def read_blacklist() -> set:
    """ブラックリストを読み込んでsetで返す"""
    with open(BLACKLIST_FILE_PATH, "r") as f:
        return set(line.strip() for line in f)


def read_commands() -> dict:
    """コマンド一覧を読み込んでdictで返す"""
    with open(COMMANDS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


blacklist = read_blacklist()
commands = read_commands()


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await tree.sync()
    # await tree.sync(guild=discord.Object(id=int(os.environ['GUILD_ID'])))


@bot.event
async def on_voice_state_update(member, before, after):
    """ボイスステータスハンドルを受け取り処理する"""
    global blacklist
    # 直前までボイスチャンネルにいない、直後にボイスチャンネルにいる、通話中ではない場合に実行
    if before.channel is None and after.channel is not None:
        save_log(member, 1)
        print(f"{member.name}が通話に参加しました")
        await manage_role(member, 1)
    # 直前までボイスチャンネルにいる、直後にボイスチャンネルにいない場合に実行
    if before.channel is not None and after.channel is None:
        save_log(member, 2)
        print(f"{member.name}が通話から退出しました")
        await asyncio.sleep(60)
        await manage_role(member, 2)

# =============以下コマンド=============

@tree.command(name="blacklist", description="メンバーのブラックリストへの追加、削除、一覧表示")
@app_commands.default_permissions(administrator=True)
@discord.app_commands.choices(
    method=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="remove", value="remove"),
        discord.app_commands.Choice(name="list", value="list")
    ])
@discord.app_commands.describe(user="ユーザー名   例:USER#0000")
async def blacklist_command(interaction: discord.Interaction, method: str, user: str = None) -> None:
    """メンバーのブラックリストへの追加、削除、一覧表示"""
    global blacklist
    if method in ["add", "remove"] and user is None:
        await interaction.response.send_message("ユーザー名を指定してください", ephemeral=True)
    if method == "add":
        with open(BLACKLIST_FILE_PATH, "a") as f:
            f.write(f"{user}\n")
        blacklist.add(user)
        await interaction.response.send_message(f"{user}をブラックリストに追加しました", ephemeral=True)
    elif method == "remove":
        with open(BLACKLIST_FILE_PATH, "r") as f:
            lines = f.readlines()
            lines = [line for line in lines if line.strip() != user]
        with open(BLACKLIST_FILE_PATH, "w") as f:
            f.writelines(lines)
        blacklist.discard(user)
        await interaction.response.send_message(f"{user}をブラックリストから削除しました", ephemeral=True)
    elif method == "list":
        fields = {"name": "blacklist", "value": "\n".join(blacklist) or "ブラックリストにはまだ誰もいません", "inline": False}
        embed = discord.Embed(title="ブラックリスト一覧", color=0xff0000)
        embed.add_field(**fields)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="nya", description="ねこが鳴きます")
async def nya_command(interaction: discord.Interaction) -> None:
    message = random.choice(["にゃーん", "みゃ", "にゃう", "しゃーっ", "みゃおん", "nyancat"])
    await interaction.response.send_message(message, ephemeral=False) if message != "nyancat" else await interaction.response.send_message(file=discord.File("nyancat.gif"), ephemeral=False)


@tree.command(name="omikuzi", description="おみくじを引く")
async def omikuzi_command(interaction: discord.Interaction) -> None:
    omikuzi = random.choice(["大吉", "吉", "半吉", "凶", "半凶", "大凶"])
    await interaction.response.send_message(omikuzi, ephemeral=False)


@tree.command(name="member", description="コマンド使用者の通話にいるメンバー一覧を表示")
async def member_command(interaction: discord.Interaction) -> None:
    """コマンド使用者の通話にいるメンバー一覧を表示"""
    # コマンド使用者の通話にいるか判定する
    if interaction.user.voice is None:
        await interaction.response.send_message("ボイスチャンネルに接続中のときにのみ使用可能です", ephemeral=True)
        return
    # コマンド使用者がいる通話のメンバーを取得する
    members = interaction.user.voice.channel.members
    member_list = "\n".join([member.name for member in members])
    await send_embed(interaction, "ボイスチャンネルに接続中のメンバー一覧", member_list)


@tree.command(name="minecraft", description="Minecraftのサーバーを起動")
@discord.app_commands.choices(
    server=[
        discord.app_commands.Choice(name="サバイバル", value="1.19.4"),
        discord.app_commands.Choice(name="カタン", value="カタン"),
    ]
)
@discord.app_commands.describe(server="サーバー名")
async def minecraft_command(interaction: discord.Interaction, server: str) -> None:
    """Minecraftのサーバーを起動"""
    if interaction.user.name not in "ReL":
        await interaction.response.send_message("このコマンドは使用できません", ephemeral=True)
        return

    path = rf"C:\Minecraft server\{server}\start.bat"
    subprocess.Popen(path)
    await interaction.response.send_message("Minecraftサーバーを起動しました", ephemeral=True)


@tree.command(name="help", description="コマンド一覧を表示")
async def help_command(interaction: discord.Interaction) -> None:
    """コマンド一覧を表示"""
    with open(COMMANDS_FILE_PATH, "r", encoding="utf-8") as f:
        commands = json.load(f)

    embed = discord.Embed(title="Help", description="コマンド一覧", color=discord.Color.blue())
    for command in commands.values():
        embed.add_field(name=command["name"], value=command["description"], inline=False)
    await interaction.response.send_message(embed=embed)


# =============コマンドここまで=============

async def manage_role(member, id) -> None:
    """
    ロール管理.
    id = 1 : ロールを付与する
    id = 2 : ロールを削除する
    """
    # ブラックリストに入っていないか確認する
    if check_blacklist(str(member)):
        return

    if id == 1:
        await member.add_roles(discord.utils.get(member.guild.roles, name="通話中"))
    if id == 2:
        await member.remove_roles(discord.utils.get(member.guild.roles, name="通話中"))


def check_blacklist(member) -> bool:
    """ブラックリストに入っているか確認する"""
    with open(BLACKLIST_FILE_PATH) as f:
        return any(member == line.strip() for line in f)


def save_log(member, id) -> None:
    """ログを保存する"""
    text = "入室" if id == 1 else "退室"
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(LOG_FILE_PATH, "a") as f:
        f.write(f"[{now}] {member.name}が{text}しました。\n")


async def send_embed(interaction, title, description, color=discord.Color.blue(), fields=None, ephemeral=False) -> None:
    """embedに加工してメッセージを送信する"""
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

bot.run(TOKEN)
