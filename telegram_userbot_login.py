"""Run this ONCE, yourself, in an interactive terminal to log in with your own
Telegram account and generate a reusable session string.

Why: Telegram bots cannot see messages sent by other bots (a platform-level
restriction), and your bank's notification service posts via its own bot
account. Logging in as your real account (a "userbot") bypasses that, since
real user sessions can see all messages in groups they're a member of.

You'll need an API ID + API Hash from https://my.telegram.org (log in with
your phone number there, go to "API development tools", create an app — it's
free and instant). This script will then ask for your phone number and the
login code Telegram sends you.

Run:
    venv\\Scripts\\python.exe telegram_userbot_login.py

At the end, copy the three printed lines into your .env file. The session
string is as sensitive as your Telegram password — keep it out of git,
exactly like the bot token.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print(__doc__)

api_id = input('API ID (from my.telegram.org): ').strip()
api_hash = input('API Hash (from my.telegram.org): ').strip()

with TelegramClient(StringSession(), int(api_id), api_hash) as client:
    session_string = client.session.save()
    me = client.get_me()
    print(f'\nLogged in as: {me.first_name} (@{me.username or "no username"})')
    print('\n=== Add these lines to your .env file ===')
    print(f'TELEGRAM_API_ID={api_id}')
    print(f'TELEGRAM_API_HASH={api_hash}')
    print(f'TELEGRAM_SESSION_STRING={session_string}')
    print('\nKeep TELEGRAM_SESSION_STRING secret — it grants full access to your Telegram account.')
