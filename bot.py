import os
import asyncio
from aiohttp import web
from telethon import TelegramClient, events

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = TelegramClient("video_converter_bot", API_ID, API_HASH)


@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if not event.is_private:
        return

    message = event.message

    if not message.media or not message.file:
        return

    filename = message.file.name or ""

    if not filename.lower().endswith(".mp4"):
        await event.reply("❌ من فضلك ابعت ملف MP4.")
        return

    status = await event.reply("⏳ جاري تجهيز الفيديو...")

    os.makedirs("downloads", exist_ok=True)
    path = None

    try:
        path = await bot.download_media(
            message,
            file="downloads/"
        )

        if not path:
            await status.edit("❌ فشل تحميل الملف.")
            return

        await status.edit("📤 جاري إرساله كـ Video...")

        await bot.send_file(
            event.chat_id,
            path,
            force_document=False,
            supports_streaming=True,
            caption="🎬 تم تحويل الملف إلى Video"
        )

        await status.delete()

    except Exception as e:
        await status.edit("❌ حصل خطأ:\n" + str(e)[:500])

    finally:
        if path and os.path.exists(path):
            os.remove(path)


async def health(request):
    return web.Response(text="Bot is running!")


async def main():
    await bot.start(bot_token=BOT_TOKEN)

    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)

    await site.start()

    print("✅ Bot is running...")
    print(f"🌐 Web server running on port {port}")

    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
