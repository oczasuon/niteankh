"""Polls a Telegram group for forwarded bank-payment notifications and stores
parsed transactions so wallet top-ups can be verified against a real payment
before crediting coins.

Requires the bot to actually receive the group's messages: either make it a
group admin (bypasses privacy mode) or disable privacy mode via @BotFather
and re-add the bot to the group.
"""

import os
import re
import threading
import time

import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.environ.get('TELEGRAM_GROUP_ID')

API_BASE = f'https://api.telegram.org/bot{BOT_TOKEN}' if BOT_TOKEN else None

# "You have received KHR 20,000 reference Hash : 59c820bf, from LYHOUR CHHIN -
#  Advanced Bank of Asia Limited to A/Cxxxxxxxxxx6001 on 22-06-2026 at 13:53:45"
EXTERNAL_RE = re.compile(
    r'You have received KHR\s*([\d,]+)\s*reference Hash\s*:\s*([a-fA-F0-9]+),\s*'
    r'from\s+(.+?)\s+to\s+A/C\S+\s+on\s+(\d{2}-\d{2}-\d{4})\s+at\s+(\d{2}:\d{2}:\d{2})',
    re.IGNORECASE,
)

# "You have received KHR 20,000 from In Soksomnang to A/Cxxxxxxxxxx6001 on
#  26-06-2026 at 08:19. TXN ID :18078909"
INTERNAL_RE = re.compile(
    r'You have received KHR\s*([\d,]+)\s*from\s+(.+?)\s+to\s+A/C\S+\s+on\s+'
    r'(\d{2}-\d{2}-\d{4})\s+at\s+(\d{2}:\d{2})\.\s*TXN ID\s*:\s*(\d+)',
    re.IGNORECASE,
)


def _normalize_name(name):
    """Lowercases, strips everything but letters/digits, then sorts the
    remaining characters — so word order and spacing don't matter.
    'ocza suon', 'suon ocza', 'oczasuon', 'suonocza' all normalize the same."""
    letters_only = re.sub(r'[^a-z0-9]', '', (name or '').lower())
    return ''.join(sorted(letters_only))


def names_roughly_match(entered_name, sender_name):
    """Compares a user-typed name against a bank message's sender name (which
    often has a bank name suffix, e.g. 'OCZA SOUN - Advanced Bank of Asia
    Limited') — ignores word order, spacing, and the bank suffix."""
    if not entered_name or not sender_name:
        return False
    # Only compare against the person's name, not the bank name after " - "
    sender_person = sender_name.split(' - ')[0]
    return _normalize_name(entered_name) == _normalize_name(sender_person)


def parse_bank_message(text):
    """Returns {source, amount_khr, reference, sender_name} or None if the
    text doesn't match either known bank-notification format."""
    if not text:
        return None

    m = EXTERNAL_RE.search(text)
    if m:
        return {
            'source': 'external',
            'amount_khr': int(m.group(1).replace(',', '')),
            'reference': m.group(2).strip(),
            'sender_name': m.group(3).strip(),
        }

    m = INTERNAL_RE.search(text)
    if m:
        return {
            'source': 'internal',
            'amount_khr': int(m.group(1).replace(',', '')),
            'reference': m.group(5).strip(),
            'sender_name': m.group(2).strip(),
        }

    return None


def poll_once():
    """Fetches new Telegram updates, stores any parsed bank messages from the
    target group as BankTransaction rows, and advances the stored offset so
    the same update is never re-processed. Returns how many new rows were stored."""
    from helpers import get_setting, set_setting
    from models import BankTransaction, db

    if not BOT_TOKEN or not GROUP_ID:
        return 0

    offset = int(get_setting('telegram_update_offset') or 0)

    try:
        resp = requests.get(f'{API_BASE}/getUpdates', params={'offset': offset, 'timeout': 0, 'limit': 100}, timeout=10)
        data = resp.json()
    except (requests.RequestException, ValueError):
        return 0

    if not data.get('ok'):
        return 0

    updates = data.get('result', [])
    if not updates:
        return 0

    stored = 0
    max_update_id = offset - 1

    for update in updates:
        max_update_id = max(max_update_id, update['update_id'])
        message = update.get('message') or update.get('channel_post')
        if not message:
            continue
        if str(message.get('chat', {}).get('id', '')) != str(GROUP_ID):
            continue

        text = message.get('text') or message.get('caption') or ''
        parsed = parse_bank_message(text)
        if not parsed:
            continue
        if BankTransaction.query.filter_by(reference=parsed['reference']).first():
            continue

        db.session.add(BankTransaction(
            source=parsed['source'], reference=parsed['reference'], amount_khr=parsed['amount_khr'],
            sender_name=parsed['sender_name'], raw_message=text, telegram_message_id=message.get('message_id'),
        ))
        stored += 1

    set_setting('telegram_update_offset', str(max_update_id + 1))
    if stored:
        db.session.commit()
    else:
        db.session.commit()  # persist the offset advance even with no matches

    return stored


def start_background_poller(app, interval=10):
    """Runs poll_once() in a loop on a daemon thread for the life of the process."""
    if not BOT_TOKEN or not GROUP_ID:
        print('Telegram verification disabled (TELEGRAM_BOT_TOKEN / TELEGRAM_GROUP_ID not set).')
        return

    def loop():
        while True:
            try:
                with app.app_context():
                    poll_once()
            except Exception as exc:  # keep the poller alive across transient errors
                print('Telegram poll error:', exc)
            time.sleep(interval)

    threading.Thread(target=loop, daemon=True, name='telegram-poller').start()
    print(f'Telegram bank-notification poller started (every {interval}s).')
