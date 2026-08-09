"""Listens for new messages in the verification Telegram group using a real
user session (not a bot), since Telegram bots can't see messages posted by
other bots — and bank notification services almost always post as bots.

Requires TELEGRAM_API_ID / TELEGRAM_API_HASH / TELEGRAM_SESSION_STRING in the
environment, generated once via telegram_userbot_login.py. If any are missing,
this module does nothing (the app still runs fine without it).
"""

import asyncio
import os
import threading

API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
GROUP_ID = os.environ.get('TELEGRAM_GROUP_ID')


def _store_if_bank_message(app, text, message_id):
    """Parses text as a bank notification and stores it if new. Returns True
    if a new BankTransaction row was created, False otherwise."""
    from telegram_verify import parse_bank_message

    parsed = parse_bank_message(text)
    if not parsed:
        return False

    with app.app_context():
        from models import BankTransaction, db
        if BankTransaction.query.filter_by(reference=parsed['reference']).first():
            return False
        db.session.add(BankTransaction(
            source=parsed['source'], reference=parsed['reference'], amount_khr=parsed['amount_khr'],
            sender_name=parsed['sender_name'], raw_message=text, telegram_message_id=message_id,
        ))
        db.session.commit()
        print(f"[telegram-userbot] stored transaction ref={parsed['reference']} amount={parsed['amount_khr']} KHR")
        return True


def start_userbot_listener(app):
    if not (API_ID and API_HASH and SESSION_STRING and GROUP_ID):
        print('Telegram userbot listener disabled (missing TELEGRAM_API_ID / TELEGRAM_API_HASH / '
              'TELEGRAM_SESSION_STRING / TELEGRAM_GROUP_ID). Run telegram_userbot_login.py to set it up.')
        return

    def run():
        from telethon import TelegramClient, events
        from telethon.sessions import StringSession

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH, loop=loop)

        @client.on(events.NewMessage(chats=int(GROUP_ID)))
        async def handler(event):
            try:
                _store_if_bank_message(app, event.raw_text or '', event.id)
            except Exception as exc:
                print('[telegram-userbot] error handling message:', exc)

        async def main():
            await client.start()
            me = await client.get_me()
            print(f'[telegram-userbot] listening as {me.first_name} (@{me.username or "no username"})')
            await client.run_until_disconnected()

        try:
            loop.run_until_complete(main())
        except Exception as exc:
            print('[telegram-userbot] fatal error:', exc)

    threading.Thread(target=run, daemon=True, name='telegram-userbot').start()


def backfill_history(app, limit=300):
    """Scans the last `limit` messages in the group for bank notifications the
    live listener missed (e.g. sent before it was connected) and stores any
    new ones. Uses its own short-lived connection — safe to run while the
    persistent listener thread is also connected. Returns the count stored."""
    if not (API_ID and API_HASH and SESSION_STRING and GROUP_ID):
        return 0

    from telethon import TelegramClient
    from telethon.sessions import StringSession

    stored = 0

    async def scan():
        nonlocal stored
        async with TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH) as client:
            async for message in client.iter_messages(int(GROUP_ID), limit=limit):
                if _store_if_bank_message(app, message.raw_text or '', message.id):
                    stored += 1

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(scan())
    finally:
        loop.close()

    return stored
