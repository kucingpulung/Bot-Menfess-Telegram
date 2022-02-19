from dotenv import load_dotenv
from os import getenv, path

load_dotenv() if not path.exists("local.env") else load_dotenv("local.env")


class Config:
    api_id = int(getenv("API_ID", "0"))
    api_hash = getenv("API_HASH", "abc")
    bot_token = getenv("BOT_TOKEN", "123:Abc")
    log_channel = int(getenv("LOG_CHANNEL"))
    fsub_chid = int(getenv("FORCESUB_CHANNEL"))
    db_chid = int(getenv("DB_CHANNEL"))
    blacklisted_channel = [int(x) for x in getenv("BLACKLISTED_CHANNEL", "123").split(",") if x is not None]
    channel1 = int(getenv("CHANNEL_1"))
    channel2 = int(getenv("CHANNEL_2"))
    channel3 = int(getenv("CHANNEL_3"))


config = Config()
