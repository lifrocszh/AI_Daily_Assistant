import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_subscribers():
    raw_list = os.getenv("SUBSCRIBER_LIST", "")
    # Returns a list of strings (IDs)
    return [s.strip() for s in raw_list.split(",") if s.strip()]

async def broadcast():
    if len(sys.argv) < 2:
        print("Usage: python filename.py <your message>")
        return

    # Join all arguments after the filename into a single string
    message_text = " ".join(sys.argv[1:])

    user_ids = get_subscribers()
    if not user_ids:
        print("No subscribers found in SUBSCRIBER_LIST.")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    print(f"Starting broadcast to {len(user_ids)} users...")

    for user_id in user_ids:
        try:
            # We use Markdown parse mode so you can still send *bold* or _italic_ from CLI
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode='Markdown'
            )
            print(f"✅ Sent to {user_id}")
            # Avoid hitting Telegram rate limits
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"❌ Failed to send to {user_id}: {e}")

    print("Broadcast complete.")

if __name__ == "__main__":
    asyncio.run(broadcast())
