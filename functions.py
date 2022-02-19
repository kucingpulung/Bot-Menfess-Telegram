from base64 import b64encode, b64decode

from pyrogram import filters
from pyrogram.errors import UserNotParticipant

from config import config


def b64_to_string(b64_string):
    return b64decode(b64_string.encode("ascii")).decode('ascii')


def string_to_b64(string):
    return b64encode(string.encode('ascii')).decode('ascii')
