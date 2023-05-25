import random
import discord
import json
import openai
import os
from utils import send_embed, read_blacklist

BLACKLIST_FILE_PATH = "./files/blacklist.txt"
COMMANDS_FILE_PATH = "./files/commands.json"
LOG_FILE_PATH = "./files/log.txt"
isServer = False

blacklist = read_blacklist()

# Define your command functions here. For example:
async def blacklist_command(interaction, method, user):
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

async def nya_command(interaction):
    message = random.choice(["にゃーん", "みゃ", "にゃう", "しゃーっ", "みゃおん", "nyancat"])
    await interaction.response.send_message(message, ephemeral=False) if message != "nyancat" else await interaction.response.send_message(file=discord.File("nyancat.gif"), ephemeral=False)

async def omikuzi_command(interaction: discord.Interaction) -> None:
    omikuzi = random.choice(["大吉", "吉", "半吉", "凶", "半凶", "大凶"])
    await interaction.response.send_message(omikuzi, ephemeral=False)

async def member_command(interaction):
    """コマンド使用者の通話にいるメンバー一覧を表示"""
    # コマンド使用者の通話にいるか判定する
    if interaction.user.voice is None:
        await interaction.response.send_message("ボイスチャンネルに接続中のときにのみ使用可能です", ephemeral=True)
        return
    # コマンド使用者がいる通話のメンバーを取得する
    members = interaction.user.voice.channel.members
    member_list = "\n".join([member.name for member in members])
    await send_embed(interaction, "ボイスチャンネルに接続中のメンバー一覧", member_list)

async def help_command(interaction: discord.Interaction) -> None:
    """コマンド一覧を表示"""
    with open(COMMANDS_FILE_PATH, "r", encoding="utf-8") as f:
        commands = json.load(f)

    embed = discord.Embed(title="Help", description="コマンド一覧", color=discord.Color.blue())
    for command in commands.values():
        embed.add_field(name=command["name"], value=command["description"], inline=False)
    await interaction.response.send_message(embed=embed)

async def gpt_command(interaction: discord.Interaction, question: str) -> None:
    """GPT-3を使用したコマンド"""
    await interaction.response.defer(thinking=True)
    openai.api_key = os.environ['OPENAI_APIKEY']
    prompt = [
        {"role": "user", "content": question}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        message = question[:15] + "..." if len(question) > 15 else question
        answer = response["choices"][0]["message"]["content"]
        await interaction.followup.send(f"```質問内容: {message}\n\n{answer}```", ephemeral=True)
    except:
        await interaction.followup.send("エラーが発生しました。再度実行してください", ephemeral=True)

async def translate_command(interaction: discord.Interaction, lang: str, text: str) -> None:
    """gptを使用したコマンド"""
    await interaction.response.defer(thinking=True)
    openai.api_key = os.environ['OPENAI_APIKEY']
    prompt = [
        {"role": "user", "content": f"以下の文を{lang}にしてください。\n{text}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.7,
        max_tokens=4000
    )
    answer = response["choices"][0]["message"]["content"]
    await interaction.followup.send(f"```[原文]\n{text}\n[翻訳]\n{answer}```", ephemeral=True)
