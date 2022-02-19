from pyrogram.errors import UserNotParticipant

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config


async def handle_fsub(c, m):
    try:
        user = await c.get_chat_member(config.fsub_chid, m.from_user.id)
        if user.status not in ["creator", "member", "administrator"] and user.status == "kicked":
            await c.send_message(
                m.from_user.id,
                "You are not allowed to use this bot.",
                reply_to_message_id=m.message_id
            )
            return False
        return True
    except UserNotParticipant:
        await c.send_message(
            m.from_user.id,
            "**Masuk ke channel terlebih dahulu untuk menbbunakan bot!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Channel", c.fsub_ch_link)
                    ]
                ]
            )
        )
