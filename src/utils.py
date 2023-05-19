import os
import json
import datetime
import discord

BLACKLIST_FILE_PATH = "./files/blacklist.txt"
COMMANDS_FILE_PATH = "./files/commands.json"
LOG_FILE_PATH = "./files/log.txt"

# Define utility functions here. For example:
def read_blacklist() -> set:
    """ブラックリストを読み込んでsetで返す"""
    with open(BLACKLIST_FILE_PATH, "r") as f:
        return set(line.strip() for line in f)


def read_commands() -> dict:
    """コマンド一覧を読み込んでdictで返す"""
    with open(COMMANDS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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