import os
import asyncio
from telethon import TelegramClient, events

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = TelegramClient("video_converter", API_ID, API_HASH)

@bot.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    message = event.message

    if not message.media or not message.file:
        return

    filename = message.file.name or "video.mp4"

    # نقبل MP4 فقط
    if not filename.lower().endswith(".mp4"):
        await event.reply("❌ ابعت ملف MP4.")
        return

    status = await event.reply("⏳ جاري تحويل الفيديو...")

    os.makedirs("downloads", exist_ok=True)

    try:
        path = await bot.download_media(
            message,
            file="downloads/"
        )

        if not path:
            await status.edit("❌ حصلت مشكلة في تنزيل الملف.")
            return

        await status.edit("📤 جاري إرساله كفيديو...")

        await bot.send_file(
            event.chat_id,
            path,
            force_document=False,
            supports_streaming=True,
            caption="🎬 تم تحويله إلى Video"
        )

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ حصل خطأ:\n{str(e)[:500]}")

    finally:
        if path and os.path.exists(path):
            os.remove(path)


async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()


asyncio.run(main())
