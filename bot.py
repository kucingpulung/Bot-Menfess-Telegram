import asyncio
import sys
from typing import Union

from pyrogram import Client as BotClient, filters, raw, idle
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)
from config import config
from db import db
from fsubs_handler import handle_fsub
from functions import b64_to_string, string_to_b64


class Client(BotClient):
    def __init__(self, session_name, api_id, api_hash, bot_token):
        super().__init__(session_name, api_id, api_hash, bot_token=bot_token)
        self.fsub_ch_link = None
        self.db_channel = None
        self.bot_username = None

    async def add_user_(self, m: Message):
        user_id = m.from_user.id
        if not await db.is_exist(user_id):
            await db.add_user(user_id)
            if config.log_channel:
                await self.send_message(
                    config.log_channel,
                    f"#NEW_USER\n\nNama: {m.from_user.first_name}\nId: {m.from_user.id}\nLink: {m.from_user.mention}"
                )

    async def start(self):
        await super().start()
        try:
            invite_link = await self.export_chat_invite_link(config.fsub_chid)
            self.fsub_ch_link = invite_link
        except ChatAdminRequired:
            await self.send_message(
                config.log_channel,
                "**Bot harus menjadi admin di channel force subs!**\n**Sistem dimatikan**"
            )
            return sys.exit()
        try:
            self.db_channel = (await self.get_chat(config.db_chid)).invite_link
        except ChatAdminRequired:
            await self.send_message(
                config.log_channel,
                "**Bot harus menjadi admin di channel database!**\n**Sistem dimatikan**"
            )
            return sys.exit()
        self.bot_username = (await self.get_me()).username

    async def stop(self, *args, **kwargs):
        return await super().stop()

    async def leave_chat(
        self,
        chat_id: Union[int, str],
        delete: bool = False
    ):
        await self.send_message(
            chat_id,
            "**Maaf, chat ini ada pada list banned dan tidak bisa diakses!**",
        )
        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerChannel):
            return await self.send(
                raw.functions.channels.LeaveChannel(
                    channel=await self.resolve_peer(chat_id)
                )
            )
        elif isinstance(peer, raw.types.InputPeerChat):
            r = await self.send(
                raw.functions.messages.DeleteChatUser(
                    chat_id=peer.chat_id,
                    user_id=raw.types.InputUserSelf()
                )
            )

            if delete:
                await self.send(
                    raw.functions.messages.DeleteHistory(
                        peer=peer,
                        max_id=0
                    )
                )

            return r


bot = Client(
    ":memory:",
    config.api_id,
    config.api_hash,
    bot_token=config.bot_token
)
media_list = {}


@bot.on_message(filters.command("start") & filters.private)
async def start_hndlr(c: Client, m: Message):
    if m.from_user.id in await db.get_all_banned_user():
        return await m.reply("Maaf, anda terban oleh owner kami.")
    if len(m.command) == 1:
        await c.add_user_(m)
        return await m.reply(
            "Hi",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("About Bot", "aboutbot"),
                        InlineKeyboardButton("About Dev", "aboutdev")
                    ]
                ]
            )
        )


@bot.on_message(
    filters.text
    | filters.media
    & ~filters.sticker
    & ~filters.edited
)
async def send_media_(c: Client, m: Message):
    chat_type = m.chat.type
    if chat_type == "private" and config.fsub_chid:
        await c.add_user_(m)
        await handle_fsub(c, m)
        return await m.reply(
            f"**Mau kirim {'media' if not m.text else 'pesan'} kemana?**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Channel 1", "channel1"),
                    InlineKeyboardButton("Channel 2", "channel2"),
                    InlineKeyboardButton("Channel 3", "channel3"),
                ]
            ]),
            quote=True
        )


@bot.on_callback_query(filters.regex(r"channel(\d+)"))
async def get_mode(c: Client, cb: CallbackQuery):
    m = cb.message
    match = int(cb.matches[0].group(1))
    message_id = m.reply_to_message.message_id
    if match == 1:
        channel_tujuan = config.channel1
    elif match == 2:
        channel_tujuan = config.channel2
    else:
        channel_tujuan = config.channel3
    x = await c.copy_message(
        channel_tujuan,
        m.chat.id,
        message_id,
        caption=m.caption or None
    )
    if isinstance(x, Message):
        message_id = x.message_id
        chat_id = x.chat.id
    else:
        message_id = None
        chat_id = None
    await m.delete()
    await m.reply(
        "**Pesan berhasil terkirim, silakan lihat dengan klik tombol dibawah ini!**",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Klik disini", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")
            ]
        ])
    )
    fwd = await c.forward_messages(
        config.log_channel,
        m.chat.id,
        message_id
    )
    m = m.reply_to_message
    await fwd.reply(
        (
            "**User mengirim pesan**\n"
            f"Nama: {m.from_user.first_name}\n"
            f"Id: {m.from_user.id}\n"
            f"Username: {m.from_user.mention}"
        )
    )


async def main():
    try:
        await db.connect()
        await db.init()
        print("Berjalan")
        await bot.start()
        await idle()
        await bot.stop()
    except KeyboardInterrupt:
        return sys.exit()


asyncio.get_event_loop().run_until_complete(main())
