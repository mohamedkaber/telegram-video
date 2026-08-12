import os
import asyncio
import traceback
from aiohttp import web
from telethon import TelegramClient, events

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = TelegramClient(
    "video_converter_bot",
    API_ID,
    API_HASH
)


@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):

    print("📩 New message received", flush=True)

    if not event.is_private:
        print("❌ Not private", flush=True)
        return

    message = event.message

    if not message.media or not message.file:
        print("❌ No media/file", flush=True)
        return

    filename = message.file.name or "video.mp4"

    print(f"📁 File: {filename}", flush=True)
    print(f"📦 Size: {message.file.size} bytes", flush=True)
    print(f"🎞 MIME: {message.file.mime_type}", flush=True)

    if not filename.lower().endswith(".mp4"):
        await event.reply("❌ من فضلك ابعت ملف MP4.")
        return

    status = await event.reply("⏳ جاري تنزيل الفيديو من Telegram...")

    os.makedirs("downloads", exist_ok=True)

    path = None

    def progress(current, total):
        percent = int(current * 100 / total) if total else 0

        if percent % 10 == 0:
            print(
                f"⬇️ Download: {percent}% "
                f"({current}/{total})",
                flush=True
            )

    try:

        print("⬇️ Starting download...", flush=True)

        path = await bot.download_media(
            message,
            file="downloads/",
            progress_callback=progress
        )

        print(f"✅ Download finished: {path}", flush=True)

        if not path:
            await status.edit("❌ فشل تنزيل الملف.")
            return

        await status.edit("📤 جاري إرساله كـ Video...")

        print("⬆️ Starting upload...", flush=True)

        await bot.send_file(
            event.chat_id,
            path,
            force_document=False,
            supports_streaming=True,
            mime_type="video/mp4",
            caption="🎬 تم تحويل الملف إلى Video"
        )

        print("✅ Upload finished!", flush=True)

        await status.delete()

    except Exception as e:

        print("❌ ERROR:", flush=True)
        traceback.print_exc()

        try:
            await status.edit(
                "❌ حصل خطأ:\n"
                + str(e)[:800]
            )
        except:
            pass

    finally:

        if path and os.path.exists(path):

            try:
                os.remove(path)
                print("🗑 Temporary file deleted", flush=True)
            except:
                pass


async def health(request):
    return web.Response(text="Bot is running!")


async def main():

    await bot.start(bot_token=BOT_TOKEN)

    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print("================================", flush=True)
    print("✅ BOT IS RUNNING", flush=True)
    print(f"🌐 Port: {port}", flush=True)
    print("================================", flush=True)

    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
