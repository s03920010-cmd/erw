# Rubika Video Search Bot (RadRub)

## Setup
1. Put your domain in `config.py`:
   `SEARCH_URL = "https://DOMAIN.COM/video/search?search="`
2. Copy `.env.example` to `.env` and set your Rubika bot token.
3. Install Python 3.10+ and dependencies:
   `python -m pip install -r requirements.txt`
4. Run:
   `python main.py`

The bot asks for a search phrase, attempts to extract result cards from the HTML page, and presents one result at a time. The user must press **Confirm & send video** before the bot downloads and uploads it.

## Limitations
- The extractor is heuristic. Sites rendered entirely by JavaScript, protected by login/anti-bot systems, or using unusual markup may not return results. In those cases, customize `extract_results()` in `main.py` using the site's HTML/API structure.
- Video pages must expose a direct video URL in a `<video>` tag or supported Open Graph metadata.
- Download cap is 80 MB by default; change `MAX_VIDEO_MB` in `config.py`.
- Only search sites you have permission to use. Respect copyright, site rules, and privacy. Do not use this bot to obtain restricted/adult material.
- Keyword blocking is a basic guard, not comprehensive moderation.


## نصب RadRub از pip

کتابخانه داخل این پروژه vendored نیست؛ با نصب وابستگی‌ها از PyPI نصب می‌شود:

```powershell
python -m pip install -r requirements.txt
```

توکن را در PowerShell تنظیم کنید و سپس اجرا کنید:

```powershell
$env:RUBIKA_BOT_TOKEN="YOUR_TOKEN"
python main.py
```
