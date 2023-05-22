from utils import save_log, manage_role

async def voice_state_update_handler(member, before, after):
    if before.channel is None and after.channel is not None:
        save_log(member, 1)
        print(f"{member.name}が通話に参加しました")
        await manage_role(member, 1)
    if before.channel is not None and after.channel is None:
        save_log(member, 2)
        print(f"{member.name}が通話から退出しました")
        await manage_role(member, 2)
