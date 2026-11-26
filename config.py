# ===== CONFIGURATION =====
# Replace DOMAIN with the website domain. This endpoint format is from the user:
# /video/search?search=QUERY
# Option A: suffix format (default):
SEARCH_URL = "https://www.pornhub.com/video/search?search="
# Option B: use a template with {query} if your site uses a different format:
# SEARCH_URL = "https://DOMAIN.COM/video/search?search={query}"

MAX_RESULTS = 8
MAX_VIDEO_MB = 80
REQUEST_TIMEOUT = 25.0
# Basic keyword guard; not a full content moderation system.
BLOCKED_TERMS = ["heloo"]
