# Changelog

## 1.1.1 – Professional Commands

- سیستم ثبت دستورات فوق‌حرفه‌ای: `@router.command("name", description=...)`
- `router.sync_commands(bot)` برای همگام‌سازی خودکار با `setCommands`
- پشتیبانی از aliases، hidden و admin_only
- مثال async_bot کاملاً بازنویسی‌شده با منوی زیبا و پاسخ‌های تمیز

## 1.1.0 – Super Professional

- **Complete API coverage**: `updateBotEndpoints`, full file pipeline (`requestSendFile` → upload → `sendFile` → `getFile` → download), `metadata` support, richer `send_message` / `send_file` signatures.
- **Fixed Polling**: correct `offset_id` / `next_offset_id` handling for both Async and Sync runners.
- **Webhook helper**: lightweight ASGI `WebhookApp` + `create_webhook_app`.
- **Richer models**: `BotInfo`, `ChatInfo`, `BotCommand`, `Metadata`, `MetaDataPart`, `FileInfo`.
- **Better filters**: `Sender`, `UpdateType`, `Private`, `Group`, improved `Command` / `Text`.
- **Middleware integration** into `Dispatcher`.
- **Professional packaging**, type hints, logging, structured exceptions.
- Backward compatible with 1.0.x public API.

## 1.0.1
- Corrected getUpdates pagination to offset_id / next_offset_id.
- Added documented file upload/download helpers.
- Added SyncPolling runner and sync polling example.

## 1.0.0
- Expanded Async and Sync clients and API wrappers.
- Polling runner, dispatcher, router, filters and keyboard helpers.
- JSON/SQLite storage and middleware extension points.
- Retry/backoff and structured exceptions.
- Tests, examples and architecture documentation.
