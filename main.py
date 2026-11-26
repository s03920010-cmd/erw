"""Rubika video search bot using RadRub. Configure SEARCH_URL in config.py."""
from __future__ import annotations
import asyncio, logging, os, re, tempfile
from pathlib import Path
from urllib.parse import quote_plus, urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from radrub import AsyncBot, Router, Dispatcher, Polling, filters, chat
from config import SEARCH_URL, MAX_RESULTS, MAX_VIDEO_MB, REQUEST_TIMEOUT, BLOCKED_TERMS

load_dotenv()
TOKEN = os.getenv("RUBIKA_BOT_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit("Set RUBIKA_BOT_TOKEN in .env first")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("video-search")
router = Router()
# Per-chat state: selected results and pending selection
sessions: dict[str, dict] = {}


def safe_text(text: str) -> bool:
    lowered = (text or "").casefold()
    return not any(term.casefold() in lowered for term in BLOCKED_TERMS if term.strip())


def search_url(query: str) -> str:
    if "{query}" in SEARCH_URL:
        return SEARCH_URL.format(query=quote_plus(query.strip()))
    return SEARCH_URL + quote_plus(query.strip())


def extract_results(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    found, seen = [], set()
    # Heuristic: anchors containing video-like URL/title and nearby image.
    for a in soup.select("a[href]"):
        href = urljoin(base_url, a.get("href", ""))
        if not href.startswith(("http://", "https://")) or href in seen:
            continue
        title = (a.get("title") or a.get_text(" ", strip=True) or "").strip()
        img = a.find("img") or a.parent.find("img") if a.parent else a.find("img")
        image = urljoin(base_url, img.get("src") or img.get("data-src") or img.get("data-lazy-src")) if img else ""
        # Keep links with an image, video-like path, or a meaningful title.
        if not (image or re.search(r"video|watch|play|clip|movie|v\d", href, re.I)):
            continue
        if not title:
            title = (img.get("alt") if img else "") or "نتیجه بدون عنوان"
        title = re.sub(r"\s+", " ", title)[:180]
        if not safe_text(title):
            continue
        seen.add(href)
        found.append({"title": title, "page": href, "image": image})
        if len(found) >= MAX_RESULTS:
            break
    return found


async def do_search(query: str) -> list[dict]:
    url = search_url(query)
    async with httpx.AsyncClient(follow_redirects=True, timeout=REQUEST_TIMEOUT,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; RadRubSearch/1.0)"}) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return extract_results(resp.text, str(resp.url))

async def get_video_url(page_url: str) -> tuple[str, str]:
    # Only direct video URLs explicitly present in the page's HTML metadata.
    async with httpx.AsyncClient(follow_redirects=True, timeout=REQUEST_TIMEOUT,
                                headers={"User-Agent": "Mozilla/5.0"}) as client:
        resp = await client.get(page_url)
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup.select("video source[src], video[src]"):
        src = tag.get("src")
        if src:
            return urljoin(str(resp.url), src), resp.text
    for meta in soup.select('meta[property="og:video"], meta[property="og:video:url"], meta[name="twitter:player:stream"]'):
        val = meta.get("content")
        if val:
            return urljoin(str(resp.url), val), resp.text
    # A direct video page URL can itself be a video file.
    if urlparse(page_url).path.lower().endswith((".mp4", ".webm", ".mov")):
        return page_url, ""
    return "", resp.text

async def download_video(url: str, path: Path):
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise ValueError("Invalid video URL")
    async with httpx.AsyncClient(follow_redirects=True, timeout=REQUEST_TIMEOUT,
                                headers={"User-Agent": "Mozilla/5.0"}) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "").lower()
            if "video" not in ctype and not urlparse(str(resp.url)).path.lower().endswith((".mp4", ".webm", ".mov")):
                raise ValueError("The link did not return a video file")
            total = 0
            limit = MAX_VIDEO_MB * 1024 * 1024
            with path.open("wb") as f:
                async for chunk in resp.aiter_bytes(65536):
                    total += len(chunk)
                    if total > limit:
                        raise ValueError(f"Video exceeds {MAX_VIDEO_MB} MB limit")
                    f.write(chunk)

async def send_results(bot, chat_id: str, results: list[dict]):
    if not results:
        await bot.send_message(chat_id, "نتیجه‌ای پیدا نشد. عبارت دیگری امتحان کن.")
        return
    sessions[chat_id] = {"results": results, "index": 0, "query": ""}
    await show_result(bot, chat_id)

async def show_result(bot, chat_id: str):
    state = sessions.get(chat_id)
    if not state:
        return
    i = state["index"]
    result = state["results"][i]
    text = (f"🎬 نتیجه {i+1} از {len(state['results'])}\n\n{result['title']}\n\n"
            f"🔗 صفحه نتیجه:\n{result['page']}\n\n"
            + (f"🖼 پیش‌نمایش:\n{result['image']}\n\n" if result.get("image") else "")
            + "برای دریافت ویدئو، دکمه تأیید را بزن.")
    rows = [[("send_selected", "✅ تأیید و ارسال ویدئو"), ("next_result", "➡️ بعدی")],
            [("cancel_search", "❌ لغو")]]
    await bot.send_message(chat_id, text, chat_keypad=chat(rows, resize=True), chat_keypad_type="New")

@router.message(filters.Command("start"))
@router.message(filters.Text(value="/start"))
async def start(update, bot):
    sessions.pop(str(update.chat_id), None)
    await bot.send_message(update.chat_id, "🔎 عبارت موردنظرت رو برای جستجوی ویدئو بفرست.\n\nبعد از نمایش نتایج، فقط با تأیید خودت ویدئو ارسال می‌شود.")

@router.message(filters.Command("help"))
async def help_cmd(update, bot):
    await bot.send_message(update.chat_id, "راهنما:\n• یک عبارت سرچ بفرست.\n• نتایج را بررسی کن.\n• برای ارسال ویدئو تأیید را بزن.\n• /start برای شروع دوباره")

@router.message(filters.ButtonClick("next_result"))
async def next_result(update, bot):
    cid = str(update.chat_id)
    state = sessions.get(cid)
    if not state:
        await bot.send_message(cid, "اول یک عبارت سرچ کن.")
        return
    state["index"] = (state["index"] + 1) % len(state["results"])
    await show_result(bot, cid)

@router.message(filters.ButtonClick("cancel_search"))
async def cancel(update, bot):
    sessions.pop(str(update.chat_id), None)
    await bot.send_message(update.chat_id, "جستجو لغو شد. عبارت جدید بفرست.")

@router.message(filters.ButtonClick("send_selected"))
async def send_selected(update, bot):
    cid = str(update.chat_id)
    state = sessions.get(cid)
    if not state:
        await bot.send_message(cid, "نتیجه‌ای برای ارسال انتخاب نشده. دوباره سرچ کن.")
        return
    result = state["results"][state["index"]]
    await bot.send_message(cid, "⏳ در حال بررسی لینک و آماده‌سازی ویدئو…")
    temp_path = None
    try:
        video_url, _ = await get_video_url(result["page"])
        if not video_url:
            await bot.send_message(cid, "از این صفحه لینک مستقیم ویدئو پیدا نشد؛ لینک صفحه را می‌توانی باز کنی:\n" + result["page"])
            return
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            temp_path = Path(tmp.name)
        await download_video(video_url, temp_path)
        file_id = await bot.upload_file(temp_path, file_type="Video")
        await bot.send_file(cid, file_id, text="🎬 " + result["title"][:150])
    except Exception as exc:
        log.exception("Failed sending video")
        await bot.send_message(cid, "⚠️ ارسال نشد. ممکن است سایت لینک مستقیم ندهد یا فایل بیش از حد بزرگ باشد.\n" + result["page"])
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)

@router.message(filters.Text())
async def text_search(update, bot):
    query = (update.text or "").strip()
    if not query or query.startswith("/"):
        return
    if not safe_text(query):
        await bot.send_message(update.chat_id, "این عبارت قابل جستجو نیست. عبارت دیگری بفرست.")
        return
    await bot.send_message(update.chat_id, "🔎 دارم جستجو می‌کنم…")
    try:
        results = await do_search(query)
        if results:
            sessions[str(update.chat_id)] = {"results": results, "index": 0, "query": query}
            await show_result(bot, str(update.chat_id))
        else:
            await bot.send_message(update.chat_id, "نتیجه‌ای پیدا نشد یا ساختار سایت با استخراج‌گر عمومی سازگار نیست.")
    except Exception:
        log.exception("Search error")
        await bot.send_message(update.chat_id, "❌ سرچ با خطا مواجه شد. دامنه/اتصال یا ساختار سایت را بررسی کن.")

async def main():
    async with AsyncBot(TOKEN) as bot:
        log.info("Bot is online")
        await Polling(bot, Dispatcher(router), interval=2.0).run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped")
