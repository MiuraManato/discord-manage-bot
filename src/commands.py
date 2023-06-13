import discord
from discord import app_commands
from command_functions import blacklist_command, nya_command, omikuzi_command, member_command, help_command, gpt_command, translate_command, minecraft_command

def setup_commands(tree):
    @tree.command(name="blacklist", description="メンバーのブラックリストへの追加、削除、一覧表示")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.choices(
        method=[
            discord.app_commands.Choice(name="add", value="add"),
            discord.app_commands.Choice(name="remove", value="remove"),
            discord.app_commands.Choice(name="list", value="list")
        ])
    @discord.app_commands.describe(user="ユーザー名   例:USER#0000")
    async def _blacklist_command(interaction: discord.Interaction, method: str, user: str = None) -> None:
        await blacklist_command(interaction, method, user)

    @tree.command(name="nya", description="ねこが鳴きます")
    async def _nya_command(interaction: discord.Interaction) -> None:
        await nya_command(interaction)

    @tree.command(name="omikuzi", description="おみくじを引く")
    async def _omikuzi_command(interaction: discord.Interaction) -> None:
        await omikuzi_command(interaction)

    @tree.command(name="member", description="コマンド使用者の通話にいるメンバー一覧を表示")
    async def _member_command(interaction: discord.Interaction) -> None:
        await member_command(interaction)

    @tree.command(name="help", description="コマンド一覧を表示")
    async def _help_command(interaction: discord.Interaction) -> None:
        await help_command(interaction)

    @tree.command(name="gpt", description="GPTを使用できます")
    @app_commands.describe(question="GPTへの質問内容")
    async def _gpt_command(interaction: discord.Interaction, question: str) -> None:
        await gpt_command(interaction, question)

    @tree.command(name="translate", description="GPTを使い翻訳できます")
    @app_commands.choices(
        lang=[
            discord.app_commands.Choice(name="日本語", value="日本語"),
            discord.app_commands.Choice(name="英語", value="英語"),
            discord.app_commands.Choice(name="韓国語", value="韓国語")
        ]
    )
    @app_commands.describe(lang="翻訳後の言語")
    @app_commands.describe(text="翻訳する文章")
    async def _translate_command(interaction: discord.Interaction, lang: str, text: str) -> None:
        await translate_command(interaction, lang, text)

    @tree.command(name="minecraft", description="Minecraftサーバーを起動/停止します")
    @app_commands.choices(
        commands=[
            discord.app_commands.Choice(name="start", value="start"),
            discord.app_commands.Choice(name="stop", value="stop"),
            discord.app_commands.Choice(name="status", value="status")
        ]
    )
    async def _minecraft_command(interaction: discord.Interaction, commands: str) -> None:
        await minecraft_command(interaction, commands)
