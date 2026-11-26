# RadRub 1.1.0 – Super Professional

**فریم‌ورک حرفه‌ای پایتون برای Rubika Bot API v3**

- کلاینت Async + Sync کامل
- Long-Polling (با `offset_id` / `next_offset_id` صحیح)
- Webhook helper (ASGI)
- Router / Dispatcher / Filters / Middleware
- Keypad builder (Chat + Inline)
- آپلود و دانلود فایل کامل
- Storage (JSON + SQLite)
- مدل‌های غنی، Exceptionهای ساختاریافته، Retry خودکار

مستندات رسمی: https://rubika.ir/botapi

---

## نصب

```bash
python -m pip install .
# یا حالت توسعه
python -m pip install -e ".[dev]"
```

## شروع سریع (Async)

```python
import asyncio, os
from radrub import AsyncBot, Router, Dispatcher, Polling, filters

router = Router()

@router.message(filters.Command("start"))
async def start(update, bot):
    await bot.send_message(update.chat_id, "درود! RadRub 1.1 آماده است.")

@router.message(filters.ButtonClick("help"))
async def on_help(update, bot):
    await bot.send_message(update.chat_id, "راهنما: /start")

async def main():
    async with AsyncBot(os.environ["RUBIKA_BOT_TOKEN"]) as bot:
        me = await bot.get_me()
        print(f"Bot: @{me.username} ({me.bot_title})")
        await Polling(bot, Dispatcher(router)).run()

asyncio.run(main())
```

## شروع سریع (Sync)

```python
import os
from radrub import Bot, Router, Dispatcher, SyncPolling, filters

router = Router()

@router.message(filters.Command("start"))
def start(update, bot):
    bot.send_message(update.chat_id, "درود از نسخه Sync")

with Bot(os.environ["RUBIKA_BOT_TOKEN"]) as bot:
    SyncPolling(bot, Dispatcher(router)).run()
```

## کیبورد

```python
from radrub import Button, chat, inline

# دکمه‌های پایین صفحه (ChatKeypad) – بهترین گزینه برای Polling
kb = chat(
    [("help", "راهنما"), ("about", "درباره")],
    [("contact", "تماس")],
    resize=True,
)

# دکمه‌های شیشه‌ای زیر پیام (InlineKeypad)
ikb = inline([("details", "جزئیات"), ("buy", "خرید")])

await bot.send_message(chat_id, "منو", chat_keypad=kb, chat_keypad_type="New")
await bot.send_message(chat_id, "جزئیات", inline_keypad=ikb)
```

> **نکته مهم:** کلیک روی InlineKeypad فقط از طریق Webhook (`receiveInlineMessage`) قابل اطمینان دریافت می‌شود. برای Polling از ChatKeypad استفاده کنید.

## فایل‌ها (آپلود و ارسال)

```python
# آپلود + ارسال در یک خط
file_id = await bot.upload_file("photo.jpg", file_type="Image")
await bot.send_file(chat_id, file_id, text="عکس جدید")

# دانلود
await bot.download_file(file_id, "downloaded.jpg")
```

## Webhook

```python
from radrub import AsyncBot, Router, Dispatcher, create_webhook_app

router = Router()
# ... handlers ...

async def main():
    async with AsyncBot(TOKEN) as bot:
        # ثبت endpointها
        await bot.update_bot_endpoints("https://your.domain/receiveUpdate", "ReceiveUpdate")
        await bot.update_bot_endpoints("https://your.domain/receiveInlineMessage", "ReceiveInlineMessage")

        app = create_webhook_app(Dispatcher(router), bot)
        # حالا app را با uvicorn / hypercorn / aiohttp اجرا کنید
```

## متدهای پوشش‌داده‌شده

| متد | توضیح |
|-----|--------|
| `getMe` | اطلاعات بات |
| `sendMessage` | متن + keypad + metadata |
| `sendPoll` / `sendLocation` / `sendContact` | انواع پیام |
| `getChat` | اطلاعات چت |
| `getUpdates` | Long Polling |
| `forwardMessage` | فوروارد |
| `editMessageText` / `editMessageKeypad` | ویرایش |
| `deleteMessage` | حذف پیام |
| `setCommands` | تنظیم دستورات |
| `deleteChatKeypad` / `editChatKeypad` | مدیریت keypad |
| `banChatMember` / `unbanChatMember` | مدیریت اعضا |
| `getFile` / `requestSendFile` / `sendFile` | فایل |
| `updateBotEndpoints` | Webhook |
| `call("AnyMethod", ...)` | هر متد دیگر |

## Environment

```bash
export RUBIKA_BOT_TOKEN="YOUR_TOKEN"
python examples/async_bot.py
```

هرگز توکن را داخل کد کامیت نکنید.

## لایسنس

MIT

## Video search bot project
See `README_VIDEO_BOT.md`. The ready-to-run entrypoint is `main.py`; configure the search domain in `config.py` and token in `.env`.
