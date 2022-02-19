from databases import Database


class DB:
    def __init__(self):
        self.db = Database("sqlite+aiosqlite:///bot.db")

    async def connect(self):
        return await self.db.connect()

    async def disconnect(self):
        return await self.db.disconnect()

    async def init(self):
        await self.db.execute(
            """
            create table if not exists user_db
            (
                user_id integer,
                user_db,
                is_banned boolean,
                ban_duration integer,
                ban_reason text
            )
            """
        )
        return

    async def add_user(self, user_id: int):
        is_exists = await self.is_exist(user_id)
        if not is_exists:
            data = {
                "user_id": user_id,
                "is_banned": False,
                "ban_duration": 0,
                "ban_reason": ""
            }
            return await self.db.execute("insert into user_db values (:user_id, :is_banned, :ban_duration, :ban_reason)", data)

    async def is_exist(self, user_id: int):
        data = await self.db.fetch_one("select * from user_db where user_id = :user_id", {"user_id": user_id})
        return bool(data)

    async def get_total_users(self):
        count = list(await self.db.fetch_all("select * from user_db"))
        return len(count)

    async def get_all_users(self):
        all_user = await self.db.fetch_all("select user_id from user_db")
        return all_user

    async def del_user(self, user_id: int):
        return await self.db.execute("delete from user_db where user_id = :user_id", {"user_id": user_id})

    async def del_ban(self, user_id: int):
        data = {
            "is_banned": False,
            "ban_duration": 0,
            "ban_reason": "",
            "user_id": user_id,
        }
        await self.db.execute(
            """
            update user_db
            set is_banned = :is_banned,
                ban_duration = :ban_duration,
                ban_reason = :ban_reason
            where user_id = :user_id
            """,
            data
        )

    async def ban(self, user_id: int, ban_duration: int, ban_reason: str):
        is_banned = await self.db.fetch_one("select is_banned from user_db where user_id = :user_id", {"user_id": user_id})
        is_exists = await self.db.fetch_one("select user_id from user_db where user_id = :user_id", {"user_id": user_id})
        is_exists = is_exists[0] if is_exists else is_exists
        is_banned = is_banned[0] if is_banned else is_banned
        if is_exists and not is_banned:
            data = dict(
                is_banned=True,
                ban_duration=ban_duration,
                ban_reason=ban_reason,
                user_id=user_id,
            )
            await self.db.execute(
                """
                update user_db
                set is_banned = :is_banned,
                    ban_duration = :ban_duration,
                    ban_reason = :ban_reason
                where user_id = :user_id
                """,
                data
            )
        elif not is_exists and not is_banned:
            await self.db.execute(
                """
                insert into user_db
                values (
                    :user_id,
                    :is_banned,
                    :ban_duration,
                    :ban_reason
                )
                """,
                {
                    "user_id": user_id,
                    "is_banned": True,
                    "ban_duration": ban_duration,
                    "ban_reason": ban_reason
                }
            )

    async def get_ban_status(self, user_id: int):
        user = await self.db.fetch_one("select * from user_db where user_id = :user_id", {"user_id": user_id})
        _, is_banned, _, _ = user
        return bool(is_banned)

    async def get_all_banned_user(self):
        users = await self.db.fetch_all("select user_id from user_db where is_banned = :is_banned", {"is_banned": True})
        return [user[0] for user in users]


db = DB()
