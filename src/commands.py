import discord
from discord import app_commands
from command_functions import blacklist_command, nya_command, omikuzi_command, member_command, help_command

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

