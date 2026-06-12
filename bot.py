# -*- coding: utf-8 -*-
"""
GADGET PREMIUM EMOJI ENTERPRISE BOT
Python + pyTelegramBotAPI + MongoDB + APScheduler

Install:
    pip install pyTelegramBotAPI pymongo apscheduler emoji

Run:
    python GADGET_PREMIUM_EMOJI_VISION_PRO.py

Notes:
- This file keeps your premium emoji conversion engine, colored/custom-emoji buttons pattern,
  Make Post flow, Force Join, multi-admin, broadcast, and adds MongoDB zero-code control.
- All persistent data is stored in MongoDB collections:
  users, admins, channels, emojis, packs, broadcasts, analytics, settings.
"""

import os
import re
import time
import json
import uuid
import random
import logging
import threading
import traceback
import zipfile
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import emoji
import telebot
from telebot import types
from telebot.types import MessageEntity
from telebot.apihelper import ApiTelegramException
from pymongo import MongoClient, ASCENDING, DESCENDING, UpdateOne
from bson import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler

# ======================== CONFIG ========================
# SECURITY NOTE:
# Paste your new BotFather token below OR paste your new BotFather token directly into TOKEN.
# Do not share your real token publicly. If an old token was posted anywhere, revoke it in @BotFather.
TOKEN = "8899427551:AAEY9BkiESAjnjG1JknjAKBeWnRBkUmoHyk"
MASTER_ADMIN_ID = int(os.getenv("MASTER_ADMIN_ID", "8591429820"))

# Paste your MongoDB URI below OR set MONGO_URI in your server environment.
# Example: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://shuvohassan_00:shuvohassan%40%4021@gadgetbot1.ycaaj7i.mongodb.net/?retryWrites=true&w=majority&appName=gadgetbot1")
DB_NAME = os.getenv("MONGO_DB_NAME", "gadget_premium_emoji_enterprise")
APP_TZ = ZoneInfo(os.getenv("APP_TZ", "Asia/Dhaka"))

PLACEHOLDER = "🌟"
P = PLACEHOLDER
MAIN_EMOJI_ID = "6010060634803148161"

# ======================== CREDITS / SUPPORT ========================
# Shown in /about and the Support button. Override any of these via env vars.
BOT_NAME = os.getenv("BOT_NAME", "Gadget Premium Emoji Bot")
BOT_VERSION = os.getenv("BOT_VERSION", "v21.0")
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "Shuvo Hassan")
DEVELOPER_USERNAME = os.getenv("DEVELOPER_USERNAME", "@shuvohassan00")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@shuvohassan00")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("GADGET_ENTERPRISE")

bot = telebot.TeleBot(TOKEN, parse_mode=None, threaded=True, num_threads=24)
scheduler = BackgroundScheduler(timezone=APP_TZ)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=7000,
    connectTimeoutMS=10000,
    socketTimeoutMS=30000,
    retryWrites=True,
    maxPoolSize=100,
    minPoolSize=5,
)
db = client[DB_NAME]
users = db["users"]
admins = db["admins"]
channels = db["channels"]
emojis_col = db["emojis"]
packs = db["packs"]
broadcasts = db["broadcasts"]
analytics = db["analytics"]
settings = db["settings"]
support_tickets = db["support"]
support_messages = db["support_messages"]
support_templates = db["support_templates"]

# ======================== PREMIUM BUTTON ICONS ========================
MAIN_MENU_EMOJI_IDS = {
    "make_post": "6129432481927010933",
    "help": "6129909635613726974",
    "about": "6154335299309672955",
    "stats": "6154621704908839853",
    "broadcast": "6105006251295377689",
    "users_list": "6129909635613726974",
    "admin_panel": "6129432481927010933",
    "add_admin": "6129909635613726974",
    "remove_admin": "6129432481927010933",
    "admin_list": "6129909635613726974",
    "bot_settings": "6129432481927010933",
    "channel_settings": "6129432481927010933",
    "add_channel": "6129909635613726974",
    "remove_channel": "6129432481927010933",
    "channel_list": "6129909635613726974",
    "emoji": "6154335299309672955",
    "pack": "6156715484285770345",
    "analytics": "6154621704908839853",
    "spam": "6138763921147829284",
    "coin": "6138957710072223834",
    "settings": "6129704739903906195",
    "back": "6129909635613726974",
    "success": "6129432481927010933",
    "danger": "6129432481927010933",
}

# Curated premium UI theme IDs. These are used only for bot interface decorations,
# so the same message no longer shows one boring repeated premium emoji everywhere.
UI_PREMIUM_EMOJI_IDS = [
    "6154335299309672955", "6156715484285770345", "6156880045957716584",
    "6154421933095000846", "6156827067536120729", "6156945144777022169",
    "6156936361568901831", "6156541396376361727", "6154257607646255757",
    "6156558816763714393", "6156434919842127016", "6154621704908839853",
    "6138957710072223834", "6138763921147829284", "6138443507997612595",
    "6138557745537751767", "6136461792907370226", "6136389070521114052",
    "6129432481927010933", "6129909635613726974", "6129704739903906195",
]

DEFAULT_EMOJI_IDS = [
    "6129399728506412489", "6129812419028982717", "6129574787078429498", "6129477982810545152",
    "6129550284290006595", "6129479035077531636", "6129932613688764241", "6129444065453808638",
    "6129828611055689014", "6129472184604695207", "6129760505759276442", "6129959208126258284",
    "6129705667616841573", "6129433877791382400", "6129705083501293112", "6131660826924292492",
    "6129727043669072880", "6129415619885407680", "6129909635613726974", "6129627894349045589",
    "6129870783339567154", "6129779562529168023", "6129772480128097710", "6129939837823753679",
    "6129694470637100146", "6129434968713076807", "6129732880529628243", "6129570565125577536",
    "6129782440157256336", "6129731974291527294", "6129532314146838421", "6129805465476929485",
    "6129650399977675538", "6129801569941592173", "6129769198773083022", "6129708236007283169",
    "6129906126625447892", "6129553312241949602", "6129494286506401122", "6129778965528713511",
    "6129915811776698328", "6132184924603554220", "6129572317472233948", "6129950489342647259",
    "6131886699254388574", "6129492160497589882", "6129518870899203008", "6129522839448984992",
    "6129903231817488942", "6129814111246097614", "6129643455015557847", "6129736819014639296",
    "6129622134797900004", "6129704267457501209", "6129653943325694007", "6132019972089585518",
    "6129405805885135490", "6129639980387015660", "6129650743575060215", "6129817830687775854",
    "6129812371784342357", "6129546277085520554", "6129700535130922338", "6129771638314523716",
    "6129780730760273719", "6129488844782836766", "6129672630728400259", "6129792056589031358",
    "6129432683790473996", "6129579803600231171", "6129692490657175257", "6129542888356321971",
    "6129566600870764865", "6129846551134084367", "6129497211379129336", "6129499663805456653",
    "6129432481927010933", "6129635212973316679", "6132195782280879053", "6129873716802231439",
    "6129712921816604452", "6129903927602190764", "6129926111108275647", "6129680679497111287",
    "6129704739903906195", "6129782715035163979", "6129630071897462884", "6129704885932794253",
    "6129888444245089008", "6129889801454754893", "6129891098534877664", "6129625171339778354",
    "6129650777934798600", "6129780378572954907", "6129879029676776924", "6129782839589214594",
    "6129616057419175458", "6129577213734952104", "6129631914438434952", "6129509499280563691",
    "6129781254746282923", "6129455898088709012", "6129776848109836451", "6129470861754771141",
    "6129736771769997767", "6129589862413638401", "6129872028880083998", "6129840374971112593",
    "6129776315533893189", "6129410405795110009", "6129579597441801084", "6129913724422593277",
    "6129668331466135693", "6129746001654718223", "6129574671114313022", "6129652186684070216",
    "6129769130053605799", "6129895818703936830", "6129476453802188018", "6129758830722030858",
    "6129602914819250817", "6129544215501216365", "6129532640564354033", "6129520790749584124",
    "6129517792862413944", "6129863473305230077", "6129440444796378483", "6129443429798648428",
    "6129521443584612989", "6129593109408913890", "6129553763213515073", "6129523887421006760",
    "6129530544620314433", "6129610250623393142", "6129600178925083831", "6129418755211533815",
    "6129700689749744824", "6129672231296440969", "6129741083917162817", "6129741453284350735",
    "6129700595260463994", "6129766986864924223", "6129421254882500490", "6129731845442510016",
    "6129913342170506824", "6129486856212979482", "6129409825974525149", "6129711392808247546",
    "6129410818111970687", "6129562112629938847", "6129695952400820630", "6129873536413605540",
    "6129651868856491132", "6132198982031513203", "6129663516807796597", "6129802875611651951",
    "6129897266107915247", "6129426142555282578", "6129873970205302255", "6129527246085429728",
    "6129934104042412999", "6131893910504480009", "6129758753412619088", "6132118786402163360",
    "6129418815341077483", "6129911435205024348", "6129794302856927889", "6129926467590560665",
    "6129786503196319136", "6129795982189141421", "6136389070521114052", "6136461792907370226",
    "6138557745537751767", "6136269971077995421", "6138763921147829284", "6136565769770637814",
    "6138443507997612595", "6138957710072223834", "6136406830210882173", "6136308217761766184",
    "6138514890354071735", "6138465562654678199", "6136514547990666308", "6154335299309672955",
    "6156715484285770345", "6156880045957716584", "6154421933095000846", "6156827067536120729",
    "6156945144777022169", "6156936361568901831", "6156541396376361727", "6154257607646255757",
    "6156558816763714393", "6156434919842127016", "6154621704908839853", "6156436440260549720",
    "6154177180088670691", "6156599245290872488", "6154294879372450069", "6154239663272893260",
]

# ======================== RUNTIME STATE ========================
temp_data = {}
rate_memory = defaultdict(deque)
emoji_cache = {"expires": 0, "packs": {}}
bot_identity = {"username": None}

# Smart emoji matching: maps each premium custom_emoji_id to the real unicode
# emoji it represents, so "Make Post" can place the SAME emoji the user typed
# (🔥 -> premium 🔥) instead of a random one.
CUSTOM_EMOJI_BASE = {}                       # custom_emoji_id -> normalized base emoji
emoji_base_map_cache = {"expires": 0, "packs": {}}  # pack_slug -> {base_emoji: [ids]}

# Fast runtime caches. These remove repeated MongoDB reads and make the bot smooth.
settings_cache = {"expires": 0, "data": {}}
admin_cache = {"expires": 0, "ids": set()}
channel_cache = {"expires": 0, "data": []}
pack_cache = {"expires": 0, "active": [], "by_slug": {}}
user_presence_cache = {}
join_cache = {}
count_cache = {"expires": 0, "data": {}}
progress_edit_cache = {}
RNG = random.SystemRandom()
render_counter = {"value": 0}
# Live runtime metrics for /ping, /health and the admin panel.
BOT_START_TIME = time.time()
runtime_metrics = {"updates": 0, "conversions": 0, "errors": 0, "last_update": None}


# ======================== HELPERS ========================
def now_local():
    return datetime.now(APP_TZ)


def fmt_uptime(seconds=None):
    """Human friendly uptime like '2d 4h 11m 09s'."""
    try:
        secs = int(seconds if seconds is not None else (time.time() - BOT_START_TIME))
        d, secs = divmod(secs, 86400)
        h, secs = divmod(secs, 3600)
        m, s = divmod(secs, 60)
        parts = []
        if d:
            parts.append(f"{d}d")
        if h or d:
            parts.append(f"{h}h")
        parts.append(f"{m}m")
        parts.append(f"{s:02d}s")
        return " ".join(parts)
    except Exception:
        return "0m 00s"


def now_utc():
    return datetime.now(timezone.utc)


def to_utc(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=APP_TZ)
    return dt.astimezone(timezone.utc)


def fmt_dt(dt):
    try:
        if not dt:
            return "N/A"
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(APP_TZ).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(dt)


def log_exc(where="error"):
    try:
        runtime_metrics["errors"] = runtime_metrics.get("errors", 0) + 1
    except Exception:
        pass
    log.error("%s\n%s", where, traceback.format_exc())


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _utf16_len(ch: str) -> int:
    return len(ch.encode("utf-16-le")) // 2


def _utf16_len_str(s: str) -> int:
    return len((s or "").encode("utf-16-le")) // 2


assert _utf16_len(PLACEHOLDER) == 2, "Placeholder must be a surrogate-pair emoji."


def _emoji_spans(text):
    """Return full emoji grapheme spans, not single codepoints.
    This prevents broken/normal emoji leakage for emojis like ❤️, ☘️, flags, and skin-tone emojis.
    """
    try:
        spans = []
        for item in emoji.emoji_list(text or ""):
            start = item.get("match_start")
            end = item.get("match_end")
            val = item.get("emoji") or (text or "")[start:end]
            if start is not None and end is not None and end > start:
                spans.append((start, end, val))
        spans.sort(key=lambda x: (x[0], x[1]))
        clean = []
        last_end = -1
        for s, e, val in spans:
            if s >= last_end:
                clean.append((s, e, val))
                last_end = e
        return clean
    except Exception:
        spans = []
        try:
            for i, ch in enumerate(text or ""):
                if emoji.is_emoji(ch):
                    spans.append((i, i + 1, ch))
        except Exception:
            pass
        return spans


def _stable_seed(text):
    try:
        return sum((i + 1) * ord(ch) for i, ch in enumerate(text or ""))
    except Exception:
        return 0


def _ui_premium_pool(pack_slug=None):
    """Large mixed premium pool for UI decoration. It avoids the boring repeated-one-emoji look."""
    try:
        pool = []
        try:
            pool.extend(get_pack_emojis(pack_slug or get_default_pack_slug())[:2000])
        except Exception:
            pass
        pool.extend(UI_PREMIUM_EMOJI_IDS or [])
        pool.extend(DEFAULT_EMOJI_IDS or [])
        cleaned, seen = [], set()
        for eid in pool:
            eid = str(eid)
            if eid and eid not in seen:
                seen.add(eid)
                cleaned.append(eid)
        return cleaned or [MAIN_EMOJI_ID]
    except Exception:
        return [MAIN_EMOJI_ID]


def _ui_premium_id(text, seq_index, offset=0, pool=None):
    """Original-code style: every render/click can get a fresh premium ID.
    Different decorative emojis in one message are also distributed across the pool.
    """
    try:
        pool = pool or _ui_premium_pool()
        if not pool:
            return MAIN_EMOJI_ID
        render_counter["value"] = (render_counter.get("value", 0) + 1) % 100000000
        salt = RNG.randrange(len(pool))
        idx = (salt + render_counter["value"] + seq_index * 17 + offset * 7) % len(pool)
        return pool[idx]
    except Exception:
        try:
            return random.choice(UI_PREMIUM_EMOJI_IDS or DEFAULT_EMOJI_IDS)
        except Exception:
            return MAIN_EMOJI_ID

# NOTE: premium_header / premium_footer are defined once below, after the
# typography engine, so they can use the stylish title font.

# ======================== PRO TYPOGRAPHY ENGINE ========================
# Stylish unicode font generator for bot UI + optional user output style.
def _make_trans(src, dst):
    return str.maketrans({a: b for a, b in zip(src, dst)})

_ASCII_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ASCII_LOWER = "abcdefghijklmnopqrstuvwxyz"
_ASCII_DIGIT = "0123456789"


def _range_map(upper_base, lower_base, digit_base=None):
    """Build a {ascii: styled} dict from CONTIGUOUS unicode code-point bases.
    Generating from code points (instead of pasting literal glyphs) guarantees the
    font tables can never get corrupted by copy/paste or file encoding issues."""
    mapping = {}
    for i, ch in enumerate(_ASCII_UPPER):
        mapping[ch] = chr(upper_base + i)
    for i, ch in enumerate(_ASCII_LOWER):
        mapping[ch] = chr(lower_base + i)
    if digit_base is not None:
        for i, ch in enumerate(_ASCII_DIGIT):
            mapping[ch] = chr(digit_base + i)
    return str.maketrans(mapping)


# Code-point bases for each Mathematical Alphanumeric block (all gapless ranges).
STYLE_TABLES = {
    # Sans-serif bold  (𝗔 / 𝗮 / 𝟬)
    "bold":   _range_map(0x1D5D4, 0x1D5EE, 0x1D7EC),
    # Monospace        (𝙰 / 𝚊 / 𝟶)
    "mono":   _range_map(0x1D670, 0x1D68A, 0x1D7F6),
    # Serif bold       (𝐀 / 𝐚 / 𝟎)
    "serif":  _range_map(0x1D400, 0x1D41A, 0x1D7CE),
    # Sans-serif bold italic (𝘼 / 𝙖)  -> "slant"
    "slant":  _range_map(0x1D63C, 0x1D656, 0x1D7EC),
    # Fullwidth        (Ａ / ａ / ０)  -> "wide"
    "wide":   _range_map(0xFF21, 0xFF41, 0xFF10),
}
# Double-struck and script have non-contiguous letterlike exceptions, so they are
# kept as verified literal maps.
STYLE_TABLES["double"] = _make_trans(_ASCII_UPPER + _ASCII_LOWER + _ASCII_DIGIT,
    "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
    "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"
    "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡")
STYLE_TABLES["script"] = _make_trans(_ASCII_UPPER + _ASCII_LOWER,
    "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
    "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃")

# Human-friendly labels used by Style Lab (key -> display name).
STYLE_LABELS = [
    ("normal", "NORMAL"),
    ("bold", "BOLD PRO"),
    ("serif", "SERIF KING"),
    ("slant", "ITALIC FLEX"),
    ("mono", "MONO TECH"),
    ("double", "DOUBLE VIP"),
    ("script", "SCRIPT LUX"),
    ("wide", "WIDE GLOW"),
]

def style_text(text, style="bold"):
    try:
        if not text:
            return text
        style = style or "bold"
        table = STYLE_TABLES.get(style, STYLE_TABLES.get("bold"))
        return str(text).translate(table)
    except Exception:
        return text

def title_style(text):
    return style_text(str(text or "").upper(), "bold")

def section_style(text):
    return style_text(str(text or "").upper(), "double")


def label_style(text):
    return style_text(str(text or "").upper(), "bold")


def soft_style(text):
    return style_text(str(text or ""), "mono")

def user_output_style(user_id):
    try:
        return (get_user(user_id) or {}).get("text_style", "normal") or "normal"
    except Exception:
        return "normal"

def apply_output_style(text, user_id):
    try:
        st = user_output_style(user_id)
        if st == "normal":
            return text, False
        return style_text(text, st), True
    except Exception:
        return text, False

# Stylish, perfectly-aligned header/footer used across the whole bot UI.
_PANEL_WIDTH = 22  # inner width between the corner glyphs


def _center_line(text, width=_PANEL_WIDTH):
    """Center a (possibly styled) title inside the panel. Length is measured on the
    plain text so stylish unicode fonts stay visually centered."""
    plain = emoji.replace_emoji(str(text or ""), replace="").strip()
    pad = max(0, width - len(plain))
    left = pad // 2
    right = pad - left
    return (" " * left) + str(text) + (" " * right)


def premium_header(title):
    plain = emoji.replace_emoji(str(title or ""), replace="").strip() or "PREMIUM"
    t = title_style(plain)
    line = _center_line(t)
    return (
        f"{P}╭{'─' * _PANEL_WIDTH}╮{P}\n"
        f"{P}{line}{P}\n"
        f"{P}╰{'─' * _PANEL_WIDTH}╯{P}"
    )


def premium_footer():
    return (
        f"{P}╶{'─' * (_PANEL_WIDTH - 2)}╴{P}\n"
        f"{P} GADGET PREMIUM ENGINE {P}"
    )


def strip_unicode_emoji(text):
    """Remove normal emoji from button labels; premium icon_custom_emoji_id still remains."""
    try:
        cleaned = emoji.replace_emoji(str(text or ""), replace="")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or str(text or "")
    except Exception:
        return str(text or "")


def cached_count(name, collection, query=None, ttl=12):
    try:
        key = (name, repr(query or {}))
        ts = time.time()
        if count_cache["expires"] > ts and key in count_cache["data"]:
            return count_cache["data"][key]
        value = collection.count_documents(query or {})
        count_cache["data"][key] = value
        count_cache["expires"] = ts + ttl
        return value
    except Exception:
        try:
            return collection.count_documents(query or {})
        except Exception:
            return 0


def progress_bar(done, total, width=14):
    try:
        total = max(int(total), 1)
        done = max(0, min(int(done), total))
        filled = int(width * done / total)
        return "▰" * filled + "▱" * (width - filled), int(done * 100 / total)
    except Exception:
        return "▱" * width, 0


def edit_loading(status_msg, title, stage, done=0, total=100, force=False):
    """Live premium loading animation for large TXT imports, throttled for speed."""
    try:
        if not status_msg:
            return
        key = (status_msg.chat.id, status_msg.message_id)
        ts = time.time()
        if not force and progress_edit_cache.get(key, 0) + 0.7 > ts:
            return
        progress_edit_cache[key] = ts
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame = frames[int(ts * 8) % len(frames)]
        bar, pct = progress_bar(done, total)
        txt = (
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n"
            f"{P}     {title}     {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} {frame} {stage}\n\n"
            f"{P} {bar} {pct}%\n"
            f"{P} Processed: {done}/{total}\n\n"
            f"{P} Bot remains responsive while importing.\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}"
        )
        _edit_pe(status_msg.chat.id, status_msg.message_id, txt, use_main=False)
    except Exception:
        pass

def set_button_visual(btn, style="primary", emoji_key="admin_panel", emoji_id=None):
    """Keeps your colored button + premium emoji button pattern."""
    try:
        btn.style = style
    except Exception:
        pass
    try:
        btn.icon_custom_emoji_id = emoji_id or MAIN_MENU_EMOJI_IDS.get(emoji_key) or MAIN_EMOJI_ID
    except Exception:
        pass
    return btn


def kb_btn(text, emoji_key="admin_panel", style="success"):
    clean_text = strip_unicode_emoji(text)
    return set_button_visual(types.KeyboardButton(clean_text), style=style, emoji_key=emoji_key)

def i_btn(text, callback_data=None, style="primary", emoji_key="admin_panel", url=None, emoji_id=None):
    clean_text = strip_unicode_emoji(text)
    if url:
        btn = types.InlineKeyboardButton(clean_text, url=url)
    else:
        btn = types.InlineKeyboardButton(clean_text, callback_data=callback_data)
    return set_button_visual(btn, style=style, emoji_key=emoji_key, emoji_id=emoji_id)

def get_bot_username():
    try:
        if bot_identity.get("username"):
            return bot_identity["username"]
        me = bot.get_me()
        bot_identity["username"] = me.username or "your_bot"
        return bot_identity["username"]
    except Exception:
        return "your_bot"

# ======================== DATABASE BOOTSTRAP ========================
def ensure_indexes():
    try:
        users.create_index([("user_id", ASCENDING)], unique=True)
        users.create_index([("joined_at", DESCENDING)])
        users.create_index([("last_seen", DESCENDING)])
        admins.create_index([("user_id", ASCENDING)], unique=True)
        channels.create_index([("channel_id", ASCENDING)], unique=True)
        emojis_col.create_index([("emoji_id", ASCENDING), ("pack_slug", ASCENDING)], unique=True)
        emojis_col.create_index([("pack_slug", ASCENDING), ("active", ASCENDING)])
        packs.create_index([("slug", ASCENDING)], unique=True)
        broadcasts.create_index([("status", ASCENDING), ("scheduled_at", ASCENDING)])
        analytics.create_index([("event", ASCENDING), ("created_at", DESCENDING)])
        analytics.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        settings.create_index([("key", ASCENDING)], unique=True)
        users.create_index([("banned", ASCENDING)])
        users.create_index([("username", ASCENDING)])
        support_tickets.create_index([("user_id", ASCENDING)], unique=True)
        support_tickets.create_index([("status", ASCENDING), ("last_user_at", DESCENDING)])
        support_messages.create_index([("user_id", ASCENDING), ("at", DESCENDING)])
    except Exception:
        log_exc("ensure_indexes")


def ensure_default_settings():
    defaults = {
        "bot": {
            "active": True,
            "force_join_enabled": True,
            "default_pack_slug": "default",
            "welcome_title": "💎 𝙂𝘼𝘿𝙂𝙀𝙏 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝙀𝙈𝙊𝙅𝙄 🔥",
            "support_username": "@shuvohassan00",
            "maintenance_message": "THE BOT IS CURRENTLY OFFLINE FOR MAINTENANCE. PLEASE TRY AGAIN LATER.",
            "inline_mode_enabled": True,
            "direct_convert_enabled": True,
            "support_chat_enabled": True,
        },
        "spam": {
            "enabled": True,
            "max_actions": 8,
            "window_seconds": 10,
            "mute_minutes": 3,
            "ban_after_violations": 5,
            "ban_minutes": 60,
        },
        "growth": {
            "coins_enabled": True,
            "starting_coins": 20,
            "conversion_cost": 0,
            "daily_bonus": 10,
            "referral_bonus": 25,
            "referred_user_bonus": 10,
            "leaderboard_enabled": True,
        },
    }
    try:
        for key, data in defaults.items():
            settings.update_one(
                {"key": key},
                {"$setOnInsert": {"key": key, "data": data, "created_at": now_utc()}},
                upsert=True,
            )
    except Exception:
        log_exc("ensure_default_settings")


def ensure_seed_data():
    try:
        admins.update_one(
            {"user_id": MASTER_ADMIN_ID},
            {"$set": {"role": "owner", "active": True, "is_master": True, "updated_at": now_utc()},
             "$setOnInsert": {"created_at": now_utc()}},
            upsert=True,
        )
        packs.update_one(
            {"slug": "default"},
            {"$set": {"name": "GADGET Default Premium Pack", "description": "Original premium emoji pool.", "active": True,
                       "is_default": True, "updated_at": now_utc()},
             "$setOnInsert": {"slug": "default", "created_by": MASTER_ADMIN_ID, "created_at": now_utc()}},
            upsert=True,
        )
        if emojis_col.count_documents({"pack_slug": "default"}) == 0:
            ops = []
            for eid in DEFAULT_EMOJI_IDS:
                ops.append(UpdateOne(
                    {"emoji_id": eid, "pack_slug": "default"},
                    {"$set": {"emoji_id": eid, "pack_slug": "default", "active": True, "source": "seed", "updated_at": now_utc()},
                     "$setOnInsert": {"created_by": MASTER_ADMIN_ID, "created_at": now_utc()}},
                    upsert=True,
                ))
            if ops:
                emojis_col.bulk_write(ops, ordered=False)
        refresh_pack_count("default")
        if channels.count_documents({}) == 0:
            channels.insert_one({
                "channel_id": "-1003759610418",
                "name": "𝗚𝗔𝗗𝗚𝗘𝗧 𝗕𝗢𝗫 ☘️",
                "link": "https://t.me/gadget_box_back",
                "active": True,
                "created_by": MASTER_ADMIN_ID,
                "created_at": now_utc(),
            })
    except Exception:
        log_exc("ensure_seed_data")


def bootstrap_database():
    try:
        client.admin.command("ping")
        ensure_indexes()
        ensure_default_settings()
        ensure_seed_data()
        log.info("MongoDB bootstrap complete.")
    except Exception:
        log_exc("bootstrap_database")

# ======================== SETTINGS + ANALYTICS ========================
def get_setting(key, field=None, default=None):
    try:
        ts = time.time()
        if settings_cache["expires"] <= ts or key not in settings_cache["data"]:
            doc = settings.find_one({"key": key}) or {}
            settings_cache["data"][key] = doc.get("data", {}) or {}
            settings_cache["expires"] = ts + 30
        data = settings_cache["data"].get(key, {}) or {}
        if field is None:
            return data if data else default
        return data.get(field, default)
    except Exception:
        return default

def set_setting(key, field, value):
    try:
        settings.update_one({"key": key}, {"$set": {f"data.{field}": value, "updated_at": now_utc()}}, upsert=True)
        settings_cache["expires"] = 0
        count_cache["expires"] = 0
        return True
    except Exception:
        log_exc("set_setting")
        return False

def set_settings_bulk(key, data):
    try:
        payload = {f"data.{k}": v for k, v in data.items()}
        payload["updated_at"] = now_utc()
        settings.update_one({"key": key}, {"$set": payload}, upsert=True)
        settings_cache["expires"] = 0
        count_cache["expires"] = 0
        return True
    except Exception:
        log_exc("set_settings_bulk")
        return False

def track_event(event, user_id=None, meta=None, value=1):
    try:
        analytics.insert_one({"event": event, "user_id": int(user_id) if user_id is not None else None,
                              "meta": meta or {}, "value": value, "created_at": now_utc()})
    except Exception:
        log_exc("track_event")

# ======================== USER + ADMIN ========================
def is_admin(user_id: int) -> bool:
    try:
        uid = int(user_id)
        if uid == MASTER_ADMIN_ID:
            return True
        ts = time.time()
        if admin_cache["expires"] <= ts:
            admin_cache["ids"] = set(a.get("user_id") for a in admins.find({"active": True}, {"user_id": 1}))
            admin_cache["expires"] = ts + 30
        return uid in admin_cache["ids"]
    except Exception:
        return int(user_id) == MASTER_ADMIN_ID

def is_owner(user_id: int) -> bool:
    return int(user_id) == MASTER_ADMIN_ID


def get_all_admin_ids():
    """All active admin Telegram IDs, including the master admin."""
    ids = {MASTER_ADMIN_ID}
    try:
        for a in admins.find({"active": True}, {"user_id": 1}):
            if a.get("user_id"):
                ids.add(int(a["user_id"]))
    except Exception:
        log_exc("get_all_admin_ids")
    return [i for i in ids if i]


def make_ref_code(user_id):
    try:
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        n = int(user_id)
        out = ""
        while n:
            n, r = divmod(n, 36)
            out = chars[r] + out
        return out or "0"
    except Exception:
        return str(user_id)


def parse_ref_code(code):
    try:
        code = (code or "").replace("ref_", "").strip().upper()
        if not code:
            return None
        if code.isdigit() and len(code) > 7:
            return int(code)
        return int(code, 36)
    except Exception:
        return None


def get_user(user_id):
    try:
        return users.find_one({"user_id": int(user_id)})
    except Exception:
        return None


def is_user_banned(user_id):
    """Manual admin ban (separate from anti-spam temporary bans)."""
    try:
        u = users.find_one({"user_id": int(user_id)}, {"banned": 1}) or {}
        return bool(u.get("banned"))
    except Exception:
        return False


def find_user_doc(query_text):
    """Look up a user by numeric Telegram ID or by @username (case-insensitive)."""
    try:
        q = str(query_text or "").strip()
        if not q:
            return None
        if q.startswith("@"):
            q = q[1:]
        if re.fullmatch(r"\d{4,15}", q):
            doc = users.find_one({"user_id": int(q)})
            if doc:
                return doc
        # username lookup (stored without @)
        return users.find_one({"username": re.compile(f"^{re.escape(q)}$", re.I)})
    except Exception:
        log_exc("find_user_doc")
        return None


def register_user_from_message(message, referrer_id=None):
    try:
        if not message or not message.from_user:
            return
        tg = message.from_user
        uid = int(tg.id)
        ts = time.time()
        cached = user_presence_cache.get(uid)
        if cached and cached.get("expires", 0) > ts and not referrer_id:
            if cached.get("last_write", 0) + 120 < ts:
                users.update_one({"user_id": uid}, {"$set": {"last_seen": now_utc(), "active": True}})
                cached["last_write"] = ts
            return
        old = users.find_one({"user_id": uid}, {"user_id": 1})
        growth = get_setting("growth", default={}) or {}
        doc = {
            "user_id": uid,
            "first_name": tg.first_name,
            "last_name": tg.last_name,
            "username": tg.username,
            "language_code": getattr(tg, "language_code", None),
            "active": True,
            "last_seen": now_utc(),
            "updated_at": now_utc(),
        }
        if old:
            users.update_one({"user_id": uid}, {"$set": doc})
            user_presence_cache[uid] = {"expires": ts + 300, "last_write": ts}
            return
        doc.update({
            "joined_at": now_utc(),
            "preferred_pack": get_default_pack_slug(),
            "auto_pack": False,
            "text_style": "normal",
            "coins": int(growth.get("starting_coins", 20)),
            "score": 0,
            "conversions": 0,
            "inline_conversions": 0,
            "post_conversions": 0,
            "referral_code": make_ref_code(uid),
            "referred_by": None,
            "referrals": 0,
            "daily_streak": 0,
            "last_daily_bonus": None,
            "spam": {"violations": 0, "muted_until": None, "banned_until": None},
        })
        if referrer_id and int(referrer_id) != uid and users.find_one({"user_id": int(referrer_id)}, {"user_id": 1}):
            doc["referred_by"] = int(referrer_id)
        users.update_one({"user_id": uid}, {"$setOnInsert": doc}, upsert=True)
        user_presence_cache[uid] = {"expires": ts + 300, "last_write": ts}
        count_cache["expires"] = 0
        track_event("new_user", uid, {"referrer_id": doc.get("referred_by")})
        if doc.get("referred_by"):
            inviter_bonus = int(growth.get("referral_bonus", 25))
            new_user_bonus = int(growth.get("referred_user_bonus", 10))
            users.update_one({"user_id": doc["referred_by"]}, {"$inc": {"coins": inviter_bonus, "referrals": 1, "score": 5}})
            users.update_one({"user_id": uid}, {"$inc": {"coins": new_user_bonus}})
            track_event("referral_join", uid, {"referrer_id": doc["referred_by"], "inviter_bonus": inviter_bonus, "new_user_bonus": new_user_bonus})
            try:
                _send_pe(doc["referred_by"], f"{P} REFERRAL REWARD\n\n{P} A new user joined from your link.\n{P} You earned {inviter_bonus} coins.", use_main=False)
            except Exception:
                pass
    except Exception:
        log_exc("register_user_from_message")

def inc_user(user_id, field, amount=1):
    try:
        users.update_one({"user_id": int(user_id)}, {"$inc": {field: amount}, "$set": {"last_seen": now_utc()}})
    except Exception:
        log_exc("inc_user")

# ======================== EMOJI PACK ENGINE ========================
def invalidate_emoji_cache():
    emoji_cache["expires"] = 0
    emoji_cache["packs"] = {}


def get_default_pack_slug():
    return get_setting("bot", "default_pack_slug", "default") or "default"


def get_pack(slug):
    try:
        ts = time.time()
        if pack_cache["expires"] <= ts:
            active = list(packs.find({"active": True}).sort([("is_default", DESCENDING), ("name", ASCENDING)]).limit(100))
            pack_cache["active"] = active
            pack_cache["by_slug"] = {p.get("slug"): p for p in active}
            pack_cache["expires"] = ts + 45
        return pack_cache["by_slug"].get(slug)
    except Exception:
        try:
            return packs.find_one({"slug": slug, "active": True})
        except Exception:
            return None

def get_active_packs(limit=50):
    try:
        ts = time.time()
        if pack_cache["expires"] <= ts:
            active = list(packs.find({"active": True}).sort([("is_default", DESCENDING), ("name", ASCENDING)]).limit(100))
            pack_cache["active"] = active
            pack_cache["by_slug"] = {p.get("slug"): p for p in active}
            pack_cache["expires"] = ts + 45
        return pack_cache["active"][:limit]
    except Exception:
        return []

def refresh_pack_count(slug):
    try:
        count = emojis_col.count_documents({"pack_slug": slug, "active": True})
        packs.update_one({"slug": slug}, {"$set": {"emoji_count": count, "updated_at": now_utc()}})
        invalidate_emoji_cache()
        pack_cache["expires"] = 0
        count_cache["expires"] = 0
        return count
    except Exception:
        return 0

def get_pack_emojis(pack_slug=None):
    try:
        pack_slug = pack_slug or get_default_pack_slug()
        ts = time.time()
        if emoji_cache["expires"] > ts and pack_slug in emoji_cache["packs"]:
            return emoji_cache["packs"][pack_slug]
        docs = list(emojis_col.find({"pack_slug": pack_slug, "active": True}, {"emoji_id": 1}).limit(20000))
        ids = [d.get("emoji_id") for d in docs if d.get("emoji_id")]
        if not ids and pack_slug != "default":
            ids = get_pack_emojis("default")
        if not ids:
            ids = DEFAULT_EMOJI_IDS[:]
        emoji_cache["packs"][pack_slug] = ids
        emoji_cache["expires"] = ts + 30
        return ids
    except Exception:
        return DEFAULT_EMOJI_IDS[:]


def _norm_emoji(seq):
    """Normalize an emoji grapheme for matching: drop the FE0F variation selector
    and skin-tone modifiers so '🔥', '👍🏽' and '☘️' match their premium twins."""
    try:
        s = str(seq or "")
        out = []
        for ch in s:
            cp = ord(ch)
            if cp == 0xFE0F or cp == 0xFE0E:          # variation selectors
                continue
            if 0x1F3FB <= cp <= 0x1F3FF:               # skin-tone modifiers
                continue
            if cp == 0x200D:                            # zero-width joiner
                continue
            out.append(ch)
        return "".join(out) or s
    except Exception:
        return str(seq or "")


_base_resolve_lock = threading.Lock()
_base_resolving = set()  # pack_slugs currently being resolved in the background


def resolve_emoji_bases(ids, persist=True, limit=None):
    """Resolve the real unicode emoji behind each premium custom_emoji_id using
    Telegram's getCustomEmojiStickers (batched by 200). Results are cached in
    memory and (optionally) saved to MongoDB so later runs are instant.

    NOTE: this performs network calls and may be slow, so it must NEVER run on
    the message/conversion path. Call it only from a background thread."""
    unknown = []
    for eid in ids or []:
        eid = str(eid)
        if eid and eid not in CUSTOM_EMOJI_BASE:
            unknown.append(eid)
    unknown = list(dict.fromkeys(unknown))
    if limit:
        unknown = unknown[:limit]
    for start in range(0, len(unknown), 200):
        batch = unknown[start:start + 200]
        try:
            stickers = bot.get_custom_emoji_stickers(batch)
        except Exception:
            log_exc("resolve_emoji_bases.api")
            continue
        for st in stickers or []:
            try:
                cid = str(getattr(st, "custom_emoji_id", "") or "")
                base = _norm_emoji(getattr(st, "emoji", "") or "")
                if cid and base:
                    CUSTOM_EMOJI_BASE[cid] = base
                    if persist:
                        try:
                            emojis_col.update_many(
                                {"emoji_id": cid},
                                {"$set": {"base_emoji": base, "base_resolved_at": now_utc()}},
                            )
                        except Exception:
                            pass
            except Exception:
                pass
    return CUSTOM_EMOJI_BASE


def _background_resolve_pack(pack_slug, ids):
    """Resolve missing base emojis off the main thread, then refresh the cache."""
    try:
        resolve_emoji_bases(ids, persist=True, limit=2000)
        # Invalidate so the next conversion rebuilds the (now richer) base map.
        emoji_base_map_cache["expires"] = 0
    except Exception:
        log_exc("_background_resolve_pack")
    finally:
        with _base_resolve_lock:
            _base_resolving.discard(pack_slug)


def resolve_all_emoji_bases(silent=False, progress_cb=None):
    """Resolve the real unicode for EVERY active premium emoji that has no base yet.
    Runs in the background; makes Smart Emoji Match accurate across all packs.
    Returns the number of newly resolved emojis."""
    try:
        cursor = emojis_col.find(
            {"active": True, "$or": [{"base_emoji": {"$exists": False}}, {"base_emoji": None}, {"base_emoji": ""}]},
            {"emoji_id": 1},
        )
        ids = []
        seen = set()
        for d in cursor:
            eid = str(d.get("emoji_id") or "")
            if eid and eid not in seen:
                seen.add(eid)
                ids.append(eid)
        before = len(CUSTOM_EMOJI_BASE)
        total = len(ids)
        for start in range(0, total, 200):
            resolve_emoji_bases(ids[start:start + 200], persist=True)
            if progress_cb:
                try:
                    progress_cb(min(start + 200, total), total)
                except Exception:
                    pass
        emoji_base_map_cache["expires"] = 0
        gained = len(CUSTOM_EMOJI_BASE) - before
        if not silent:
            log.info("resolve_all_emoji_bases: resolved %s new bases (scanned %s).", gained, total)
        return gained
    except Exception:
        log_exc("resolve_all_emoji_bases")
        return 0


def ensure_bases_for(needed_emojis, pack_slug=None, max_batches=10, time_budget=6.0):
    """Resolve JUST enough of a pack's premium emojis to cover the emojis the user
    actually typed, with an early stop and a hard cap so it can NEVER hang Make Post.

    Used only when the user explicitly taps AUTO SMART PREMIUM. Bounded by both a
    batch count and a time budget; whatever is left is finished in the background."""
    try:
        needed = {_norm_emoji(e) for e in (needed_emojis or []) if e}
        needed.discard("")
        if not needed:
            return
        pack_slug = pack_slug or get_default_pack_slug()
        ids = [str(x) for x in (get_pack_emojis(pack_slug) or []) if x]
        unresolved = [i for i in ids if i not in CUSTOM_EMOJI_BASE]
        if not unresolved:
            return
        start_t = time.time()
        batches = 0
        for s in range(0, len(unresolved), 200):
            if batches >= max_batches or (time.time() - start_t) > time_budget:
                break
            resolve_emoji_bases(unresolved[s:s + 200], persist=True)
            batches += 1
            # Rebuild the pack base map and stop early once all typed emojis match.
            emoji_base_map_cache["expires"] = 0
            bm = get_pack_base_map(pack_slug)
            if needed.issubset(set(bm.keys())):
                break
        # Hand off the rest to the background so the whole pack gets cached over time.
        remaining = [i for i in unresolved if i not in CUSTOM_EMOJI_BASE]
        if remaining:
            with _base_resolve_lock:
                if pack_slug not in _base_resolving:
                    _base_resolving.add(pack_slug)
                    threading.Thread(
                        target=_background_resolve_pack,
                        args=(pack_slug, remaining),
                        daemon=True,
                    ).start()
    except Exception:
        log_exc("ensure_bases_for")


def get_pack_base_map(pack_slug=None):
    """Return {normalized_base_emoji: [premium_id, ...]} for a pack so AUTO mode can
    place the matching premium emoji.

    This is FAST and non-blocking: it only reads base emojis already stored in the
    DB/cache and NEVER calls the Telegram API inline. Any unresolved ids are filled
    in by a background thread, so 'Make Post' is never delayed."""
    try:
        pack_slug = pack_slug or get_default_pack_slug()
        ts = time.time()
        if emoji_base_map_cache["expires"] > ts and pack_slug in emoji_base_map_cache["packs"]:
            return emoji_base_map_cache["packs"][pack_slug]
        docs = list(emojis_col.find(
            {"pack_slug": pack_slug, "active": True},
            {"emoji_id": 1, "base_emoji": 1},
        ).limit(20000))
        need = []
        base_map = {}
        for d in docs:
            eid = str(d.get("emoji_id") or "")
            if not eid:
                continue
            base = d.get("base_emoji")
            if base:
                base = _norm_emoji(base)
                CUSTOM_EMOJI_BASE[eid] = base
                base_map.setdefault(base, []).append(eid)
            elif eid in CUSTOM_EMOJI_BASE:
                base_map.setdefault(CUSTOM_EMOJI_BASE[eid], []).append(eid)
            else:
                need.append(eid)
        # Cache whatever we have right now (could be empty on first run).
        emoji_base_map_cache["packs"][pack_slug] = base_map
        emoji_base_map_cache["expires"] = ts + 1800
        # Fill the gaps in the background so future posts get smarter automatically.
        if need:
            with _base_resolve_lock:
                if pack_slug not in _base_resolving:
                    _base_resolving.add(pack_slug)
                    threading.Thread(
                        target=_background_resolve_pack,
                        args=(pack_slug, need),
                        daemon=True,
                    ).start()
        return base_map
    except Exception:
        log_exc("get_pack_base_map")
        return {}


def match_premium_for_emoji(seq, base_map, used=None):
    """Pick a premium id whose base unicode equals the typed emoji `seq`.
    Returns None when no smart match exists (caller falls back to random)."""
    try:
        used = used or set()
        candidates = base_map.get(_norm_emoji(seq)) or []
        if not candidates:
            return None
        fresh = [c for c in candidates if c not in used]
        pool = fresh or candidates
        return pool[RNG.randrange(len(pool))]
    except Exception:
        return None


def get_user_pack_slug(user_id):
    try:
        u = get_user(user_id) or {}
        slug = u.get("preferred_pack") or get_default_pack_slug()
        return slug if get_pack(slug) else get_default_pack_slug()
    except Exception:
        return get_default_pack_slug()


def smart_pack_for_text(text, user_id=None):
    try:
        lower = (text or "").lower()
        best_slug = get_user_pack_slug(user_id) if user_id else get_default_pack_slug()
        best_score = 0
        for pdoc in get_active_packs(50):
            score = sum(1 for kw in (pdoc.get("keywords") or []) if kw and kw.lower() in lower)
            if score > best_score:
                best_score = score
                best_slug = pdoc.get("slug", best_slug)
        return best_slug
    except Exception:
        return get_user_pack_slug(user_id) if user_id else get_default_pack_slug()


def user_auto_pack(user_id):
    try:
        return bool((get_user(user_id) or {}).get("auto_pack"))
    except Exception:
        return False


def valid_emoji_id(value):
    return bool(re.fullmatch(r"\d{10,25}", str(value or "").strip()))


def extract_emoji_ids(text):
    seen = set()
    out = []
    for eid in re.findall(r"\b\d{10,25}\b", text or ""):
        if eid not in seen:
            seen.add(eid)
            out.append(eid)
    return out


def bulk_import_emoji_ids(ids, pack_slug, admin_id=None, source="bulk", progress_callback=None):
    try:
        pack_slug = pack_slug or get_default_pack_slug()
        if progress_callback:
            progress_callback("Preparing target pack", 3, 100, True)
        if not get_pack(pack_slug):
            packs.update_one(
                {"slug": pack_slug},
                {"$set": {"name": pack_slug.replace("_", " ").title(), "description": "Auto-created pack.", "active": True,
                           "is_default": False, "updated_at": now_utc()},
                 "$setOnInsert": {"slug": pack_slug, "created_by": admin_id, "created_at": now_utc()}},
                upsert=True,
            )
            pack_cache["expires"] = 0
        unique = []
        seen = set()
        raw_total = max(len(ids or []), 1)
        for idx, eid in enumerate(ids or [], 1):
            if valid_emoji_id(eid) and eid not in seen:
                seen.add(eid)
                unique.append(eid)
            if progress_callback and (idx % 5000 == 0 or idx == raw_total):
                progress_callback("Scanning and removing duplicates", idx, raw_total, False)
        if progress_callback:
            progress_callback("Checking existing IDs", 15, 100, True)
        before = emojis_col.count_documents({"pack_slug": pack_slug, "emoji_id": {"$in": unique}}) if unique else 0
        ops = [UpdateOne(
            {"emoji_id": eid, "pack_slug": pack_slug},
            {"$set": {"emoji_id": eid, "pack_slug": pack_slug, "active": True, "source": source, "updated_at": now_utc()},
             "$setOnInsert": {"created_by": admin_id, "created_at": now_utc()}},
            upsert=True,
        ) for eid in unique]
        inserted = 0
        total_ops = max(len(ops), 1)
        if not ops:
            count = refresh_pack_count(pack_slug)
            if progress_callback:
                progress_callback("No valid IDs found", 100, 100, True)
            return {"found": 0, "inserted": 0, "duplicates": 0, "pack_count": count}
        for i in range(0, len(ops), 1000):
            res = emojis_col.bulk_write(ops[i:i + 1000], ordered=False)
            inserted += len(res.upserted_ids or {})
            if progress_callback:
                progress_callback("Saving premium emoji IDs to MongoDB", min(i + 1000, total_ops), total_ops, False)
        if progress_callback:
            progress_callback("Refreshing premium pack cache", 95, 100, True)
        count = refresh_pack_count(pack_slug)
        track_event("emoji_import", admin_id, {"pack_slug": pack_slug, "found": len(unique), "inserted": inserted})
        if progress_callback:
            progress_callback("Import complete", 100, 100, True)
        return {"found": len(unique), "inserted": inserted, "duplicates": before, "pack_count": count}
    except Exception:
        log_exc("bulk_import_emoji_ids")
        if progress_callback:
            progress_callback("Import failed", 100, 100, True)
        return {"found": 0, "inserted": 0, "duplicates": 0, "pack_count": 0, "error": True}

# ======================== PREMIUM ENTITY ENGINE ========================
_TITLE_RE = re.compile(r"(?:GADGET|HOW TO USE|BOT STATISTICS|ADMIN PANEL|POST CREATOR|INLINE BUTTON|BUTTON NAME|BUTTON LINK|ADD FILE|BROADCAST|REGISTERED USERS|CHANNEL MANAGEMENT|EMOJI PACKS|ANALYTICS|ANTI SPAM|BOT SETTINGS|REFERRAL|DAILY BONUS|PREMIUM EMOJI)", re.I)
_KEYWORD_RE = re.compile(r"\b(STEP\s*\d+|MAKE POST|REFRESH|DELETE|DONE|CANCEL|ONLINE|OFFLINE|BROADCAST|USERS LIST|BOT STATS|Developer|Version|Total Users|Emoji Pool|Bot Status|CHANNEL|PACK|COINS|STREAK)\b", re.I)


def _collect_bold_ranges(text):
    seen, out = set(), []
    try:
        for pat in (_TITLE_RE, _KEYWORD_RE):
            for m in pat.finditer(text or ""):
                start = _utf16_len_str(text[:m.start()])
                length = _utf16_len_str(m.group())
                if length > 0 and (start, length) not in seen:
                    seen.add((start, length))
                    out.append((start, length))
    except Exception:
        pass
    return out


def _build_pe_entities(text, use_main=True, italic=True):
    entities = []
    try:
        text = text or ""
        total = _utf16_len_str(text)
        if italic and total > 0:
            entities.append(MessageEntity(type="italic", offset=0, length=total))
            for start, length in _collect_bold_ranges(text):
                entities.append(MessageEntity(type="bold", offset=start, length=length))

        spans = _emoji_spans(text)
        if not spans:
            return entities

        # Shuffle once per outgoing message/edit. This gives the old-bot feeling:
        # new click/new message = new premium emoji look, without repeating one emoji everywhere.
        ui_pool = _ui_premium_pool()
        try:
            RNG.shuffle(ui_pool)
        except Exception:
            random.shuffle(ui_pool)
        if not ui_pool:
            ui_pool = [MAIN_EMOJI_ID]

        same_emoji_map = {}
        for seq_index, (start_i, end_i, seq) in enumerate(spans):
            start_utf16 = _utf16_len_str(text[:start_i])
            length_utf16 = _utf16_len_str(text[start_i:end_i])
            if length_utf16 <= 0:
                continue

            if not use_main:
                # Every placeholder/decorative emoji receives a fresh visual in this UI message.
                custom_id = ui_pool[seq_index % len(ui_pool)]
            else:
                # Legacy compatibility for special MAIN placeholder screens.
                if seq == PLACEHOLDER:
                    custom_id = MAIN_EMOJI_ID
                else:
                    if seq not in same_emoji_map:
                        same_emoji_map[seq] = ui_pool[len(same_emoji_map) % len(ui_pool)]
                    custom_id = same_emoji_map[seq]

            entities.append(MessageEntity(
                type="custom_emoji",
                offset=start_utf16,
                length=length_utf16,
                custom_emoji_id=custom_id,
            ))
    except Exception:
        log_exc("_build_pe_entities")
    return entities


def _send_pe(chat_id, text, use_main=True, reply_markup=None, disable_web_page_preview=True):
    try:
        ents = _build_pe_entities(text, use_main=use_main)
        return bot.send_message(chat_id, text, entities=ents or None, reply_markup=reply_markup, parse_mode=None,
                                disable_web_page_preview=disable_web_page_preview)
    except Exception:
        log_exc("_send_pe")
        try:
            return bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
        except Exception:
            return None


def _edit_pe(chat_id, message_id, text, use_main=True, reply_markup=None):
    try:
        ents = _build_pe_entities(text, use_main=use_main)
        return bot.edit_message_text(text, chat_id, message_id, entities=ents or None, reply_markup=reply_markup,
                                     parse_mode=None, disable_web_page_preview=True)
    except Exception:
        try:
            return bot.edit_message_reply_markup(chat_id, message_id, reply_markup=reply_markup)
        except Exception:
            return None



def _custom_emoji_map_from_entities(original_entities=None):
    """Map Telegram premium/custom emoji entities by UTF-16 offset.
    This keeps forwarded posts' original premium emoji IDs instead of changing them randomly.
    """
    out = {}
    try:
        for ent in (original_entities or []):
            if getattr(ent, "type", None) == "custom_emoji" and getattr(ent, "custom_emoji_id", None):
                out[(int(ent.offset), int(ent.length))] = str(ent.custom_emoji_id)
                out[int(ent.offset)] = str(ent.custom_emoji_id)
    except Exception:
        pass
    return out


def process_text_with_duplicate_emojis(text, original_entities=None, pack_slug=None, manual_map=None, preserve_original_custom=True, smart_match=True, allow_resolve=False):
    """Convert every normal/custom emoji in a post into Telegram premium custom_emoji entities.

    Modes:
    - manual_map: user-selected mapping from source emoji -> premium custom_emoji_id.
    - preserve_original_custom: if the forwarded/source post already had premium custom emojis,
      keep those exact IDs. This fixes the issue where forwarded posts were getting random wrong emojis.
    - auto: when neither is available, generate fresh random premium IDs from the selected pack.
    """
    final_text = ""
    new_entities = []
    offset_map = {}
    old_off = 0
    new_off = 0
    emoji_id_map = {}
    try:
        text = text or ""
        manual_map = {str(k): str(v) for k, v in (manual_map or {}).items() if v}
        original_custom_by_offset = _custom_emoji_map_from_entities(original_entities)
        active_slug = pack_slug or get_default_pack_slug()
        pool = list(dict.fromkeys(get_pack_emojis(active_slug) or DEFAULT_EMOJI_IDS))
        if not pool:
            pool = DEFAULT_EMOJI_IDS[:]
        # Smart base map (typed emoji -> premium twin). Only built in AUTO mode.
        base_map = {}
        if smart_match and not manual_map:
            try:
                # On an explicit AUTO tap, resolve just enough so the emojis the
                # user typed get matched right now (bounded; never hangs).
                if allow_resolve:
                    typed = [seq for _, _, seq in _emoji_spans(text)]
                    ensure_bases_for(typed, active_slug)
                base_map = get_pack_base_map(active_slug)
            except Exception:
                base_map = {}
        used_custom_ids = set()
        spans = _emoji_spans(text)
        span_by_start = {s: (e, seq) for s, e, seq in spans}
        i = 0
        while i < len(text):
            offset_map[old_off] = new_off
            if i in span_by_start:
                end_i, seq = span_by_start[i]
                seq_text = text[i:end_i]
                seq_len = _utf16_len_str(seq_text)
                ph_len = _utf16_len(PLACEHOLDER)

                original_custom_id = original_custom_by_offset.get((old_off, seq_len)) or original_custom_by_offset.get(old_off)
                if seq in manual_map:
                    chosen = manual_map[seq]
                elif preserve_original_custom and original_custom_id:
                    chosen = original_custom_id
                elif seq not in emoji_id_map:
                    # 1) Try the SAME emoji as a premium twin (fixes wrong/random emoji).
                    chosen = match_premium_for_emoji(seq, base_map, used_custom_ids) if base_map else None
                    # 2) Fall back to a fresh random premium id from the pool.
                    if not chosen:
                        base_idx = RNG.randrange(len(pool)) if pool else 0
                        chosen = pool[base_idx]
                        if len(used_custom_ids) < len(pool):
                            for step in range(len(pool)):
                                candidate = pool[(base_idx + step * 37) % len(pool)]
                                if candidate not in used_custom_ids:
                                    chosen = candidate
                                    break
                    emoji_id_map[seq] = chosen
                    used_custom_ids.add(chosen)
                else:
                    chosen = emoji_id_map[seq]

                new_entities.append(MessageEntity(
                    type="custom_emoji",
                    offset=new_off,
                    length=ph_len,
                    custom_emoji_id=str(chosen),
                ))
                final_text += PLACEHOLDER
                old_off += seq_len
                new_off += ph_len
                offset_map[old_off] = new_off
                i = end_i
                continue

            ch = text[i]
            ch_len = _utf16_len(ch)
            final_text += ch
            old_off += ch_len
            new_off += ch_len
            offset_map[old_off] = new_off
            i += 1

        for ent in (original_entities or []):
            try:
                if ent.type == "custom_emoji":
                    continue
                ns = offset_map.get(ent.offset)
                ne = offset_map.get(ent.offset + ent.length)
                if ns is not None and ne is not None and ne > ns:
                    new_entities.append(MessageEntity(
                        type=ent.type,
                        offset=ns,
                        length=ne - ns,
                        url=getattr(ent, "url", None),
                        user=getattr(ent, "user", None),
                        language=getattr(ent, "language", None),
                    ))
            except Exception:
                pass
    except Exception:
        log_exc("process_text_with_duplicate_emojis")
        final_text = text or ""
        new_entities = original_entities or []
    return final_text, new_entities


def source_emoji_stats(text):
    """Return unique source emojis with counts, preserving full emoji graphemes."""
    items = []
    try:
        counts = {}
        order = []
        for _, _, seq in _emoji_spans(text or ""):
            if seq not in counts:
                counts[seq] = 0
                order.append(seq)
            counts[seq] += 1
        for seq in order:
            items.append({"emoji": seq, "count": counts.get(seq, 0)})
    except Exception:
        pass
    return items


def original_custom_map_for_text(text, original_entities=None):
    """Map source emoji grapheme -> original custom emoji ID when a forwarded premium emoji exists."""
    out = {}
    try:
        by_offset = _custom_emoji_map_from_entities(original_entities)
        for s, e, seq in _emoji_spans(text or ""):
            start_utf16 = _utf16_len_str((text or "")[:s])
            length_utf16 = _utf16_len_str((text or "")[s:e])
            custom_id = by_offset.get((start_utf16, length_utf16)) or by_offset.get(start_utf16)
            if custom_id and seq not in out:
                out[seq] = str(custom_id)
    except Exception:
        pass
    return out


def init_manual_emoji_selector(uid, keep_existing=True):
    try:
        data = temp_data.get(uid) or {}
        text = data.get("original_text") or ""
        items = source_emoji_stats(text)
        old_map = data.get("manual_map") or {}
        original_map = original_custom_map_for_text(text, data.get("original_entities") or [])
        active_slug = data.get("pack_slug") or get_default_pack_slug()
        pool = list(dict.fromkeys(get_pack_emojis(active_slug) or DEFAULT_EMOJI_IDS))
        if not pool:
            pool = DEFAULT_EMOJI_IDS[:]
        try:
            base_map = get_pack_base_map(active_slug)
        except Exception:
            base_map = {}
        manual_map = {}
        used = set()
        for idx, item in enumerate(items):
            seq = item.get("emoji")
            if keep_existing and seq in old_map:
                chosen = str(old_map[seq])
            elif seq in original_map:
                chosen = str(original_map[seq])
            else:
                # Prefer the matching premium twin of the typed emoji.
                chosen = match_premium_for_emoji(seq, base_map, used) if base_map else None
                if not chosen:
                    chosen = pool[(RNG.randrange(len(pool)) + idx * 19) % len(pool)]
                    if len(used) < len(pool):
                        for step in range(len(pool)):
                            candidate = pool[(idx * 19 + step * 37 + RNG.randrange(len(pool))) % len(pool)]
                            if candidate not in used:
                                chosen = candidate
                                break
            manual_map[seq] = str(chosen)
            used.add(str(chosen))
        data["emoji_items"] = items
        data["manual_map"] = manual_map
        data["original_custom_map"] = original_map
        data["emoji_pick_index"] = min(int(data.get("emoji_pick_index", 0) or 0), max(len(items) - 1, 0))
        temp_data[uid] = data
        return items
    except Exception:
        log_exc("init_manual_emoji_selector")
        return []


def rebuild_post_conversion(uid, randomize=False, allow_resolve=False):
    try:
        data = temp_data.get(uid) or {}
        mode = data.get("emoji_mode", "auto")
        manual_map = data.get("manual_map") if mode == "manual" else None
        preserve = bool(data.get("preserve_original_custom", mode == "keep"))
        if randomize and mode == "auto":
            preserve = False
        # AUTO mode = smart match (same emoji). A shuffle tap forces fresh random.
        smart = (mode == "auto") and not randomize
        data["processed_text"], data["processed_entities"] = process_text_with_duplicate_emojis(
            data.get("original_text"),
            data.get("original_entities"),
            data.get("pack_slug"),
            manual_map=manual_map,
            preserve_original_custom=preserve,
            smart_match=smart,
            allow_resolve=allow_resolve,
        )
        temp_data[uid] = data
        return data
    except Exception:
        log_exc("rebuild_post_conversion")
        return temp_data.get(uid) or {}


def ask_emoji_mode(chat_id, uid):
    try:
        data = temp_data.get(uid) or {}
        items = init_manual_emoji_selector(uid, keep_existing=True)
        if not items:
            data["emoji_mode"] = "auto"
            data["preserve_original_custom"] = False
            temp_data[uid] = data
            rebuild_post_conversion(uid)
            ask_add_button(chat_id, uid)
            return
        has_original = bool(data.get("original_custom_map"))
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(i_btn("AUTO SMART PREMIUM", f"wizard:emojiauto:{uid}", "success", "emoji"))
        m.add(i_btn("CHOOSE EMOJI MYSELF", f"wizard:emojimanual:{uid}", "primary", "pack"))
        if has_original:
            m.add(i_btn("KEEP FORWARDED PREMIUM", f"wizard:emojikeep:{uid}", "success", "success"))
        m.add(i_btn("SKIP EMOJI STEP", f"wizard:emojiauto:{uid}", "danger", "back"))
        text = (
            f"{premium_header('EMOJI STYLE SELECTOR')}\n\n"
            f"{P} Found {len(items)} emoji in your post.\n\n"
            f"{P} AUTO SMART = same emoji, premium look.\n"
            f"{P} CHOOSE = pick each premium emoji yourself.\n"
        )
        if has_original:
            text += f"{P} KEEP = preserve forwarded premium emojis.\n"
        text += f"\n{P} Tip: AUTO SMART now matches what you typed.\n{premium_footer()}"
        _send_pe(chat_id, text, use_main=False, reply_markup=m)
    except Exception:
        log_exc("ask_emoji_mode")
        ask_add_button(chat_id, uid)


def emoji_picker_markup(uid):
    data = temp_data.get(uid) or {}
    items = data.get("emoji_items") or []
    idx = int(data.get("emoji_pick_index", 0) or 0)
    current_seq = items[idx]["emoji"] if items else ""
    current_id = (data.get("manual_map") or {}).get(current_seq) or MAIN_EMOJI_ID
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("PREV EMOJI", f"wizard:epprevemoji:{uid}", "primary", "back"),
          i_btn("NEXT EMOJI", f"wizard:epnextemoji:{uid}", "primary", "emoji"))
    m.add(i_btn("PREV STYLE", f"wizard:epprevstyle:{uid}", "primary", "emoji", emoji_id=current_id),
          i_btn("NEXT STYLE", f"wizard:epnextstyle:{uid}", "success", "emoji", emoji_id=current_id))
    m.add(i_btn("RANDOM THIS", f"wizard:eprandomthis:{uid}", "success", "emoji", emoji_id=current_id),
          i_btn("RANDOM ALL", f"wizard:eprandomall:{uid}", "danger", "danger"))
    if current_seq in (data.get("original_custom_map") or {}):
        m.add(i_btn("USE ORIGINAL PREMIUM", f"wizard:eporiginal:{uid}", "success", "success", emoji_id=(data.get("original_custom_map") or {}).get(current_seq)))
    m.add(i_btn("SAVE AND CONTINUE", f"wizard:epsave:{uid}", "success", "success"),
          i_btn("AUTO INSTEAD", f"wizard:epauto:{uid}", "primary", "back"))
    return m


def show_emoji_picker(chat_id, uid, message_id=None):
    try:
        data = temp_data.get(uid) or {}
        items = data.get("emoji_items") or init_manual_emoji_selector(uid, keep_existing=True)
        if not items:
            _send_pe(chat_id, f"{P} No emoji found in this post.", use_main=False)
            ask_add_button(chat_id, uid)
            return
        idx = int(data.get("emoji_pick_index", 0) or 0)
        idx = max(0, min(idx, len(items) - 1))
        data["emoji_pick_index"] = idx
        data["emoji_mode"] = "manual"
        data["preserve_original_custom"] = True
        temp_data[uid] = data
        seq = items[idx]["emoji"]
        count = items[idx].get("count", 1)
        current_id = (data.get("manual_map") or {}).get(seq) or MAIN_EMOJI_ID
        original_note = "YES" if seq in (data.get("original_custom_map") or {}) else "NO"
        text = (
            f"{premium_header('MANUAL EMOJI PICKER')}\n\n"
            f"{P} Emoji Slot : {idx + 1}/{len(items)}\n"
            f"{P} Found Count: {count}\n"
            f"{P} Original Premium Found: {original_note}\n\n"
            f"{P} Selected Premium ID:\n{current_id}\n\n"
            f"{P} Use NEXT STYLE / PREV STYLE until the button icon looks perfect.\n"
            f"{P} Then SAVE AND CONTINUE.\n{premium_footer()}"
        )
        if message_id:
            _edit_pe(chat_id, message_id, text, use_main=False, reply_markup=emoji_picker_markup(uid))
        else:
            _send_pe(chat_id, text, use_main=False, reply_markup=emoji_picker_markup(uid))
    except Exception:
        log_exc("show_emoji_picker")


def change_manual_style(uid, direction=1, random_this=False):
    try:
        data = temp_data.get(uid) or {}
        items = data.get("emoji_items") or []
        if not items:
            return
        idx = int(data.get("emoji_pick_index", 0) or 0)
        seq = items[idx]["emoji"]
        pool = list(dict.fromkeys(get_pack_emojis(data.get("pack_slug") or get_default_pack_slug()) or DEFAULT_EMOJI_IDS))
        if not pool:
            pool = DEFAULT_EMOJI_IDS[:]
        current = (data.get("manual_map") or {}).get(seq)
        if random_this or current not in pool:
            chosen = RNG.choice(pool)
        else:
            chosen = pool[(pool.index(current) + direction) % len(pool)]
        data.setdefault("manual_map", {})[seq] = str(chosen)
        data["emoji_mode"] = "manual"
        temp_data[uid] = data
    except Exception:
        log_exc("change_manual_style")


def randomize_all_manual_styles(uid):
    try:
        data = temp_data.get(uid) or {}
        items = data.get("emoji_items") or []
        pool = list(dict.fromkeys(get_pack_emojis(data.get("pack_slug") or get_default_pack_slug()) or DEFAULT_EMOJI_IDS))
        if not pool:
            pool = DEFAULT_EMOJI_IDS[:]
        try:
            RNG.shuffle(pool)
        except Exception:
            random.shuffle(pool)
        manual = {}
        for idx, item in enumerate(items):
            manual[item["emoji"]] = str(pool[idx % len(pool)])
        data["manual_map"] = manual
        data["emoji_mode"] = "manual"
        temp_data[uid] = data
    except Exception:
        log_exc("randomize_all_manual_styles")

def has_unicode_emoji(text):
    try:
        return bool(_emoji_spans(text or ""))
    except Exception:
        return False


# ======================== AI EMOJI INTELLIGENCE ENGINE ========================
# Context-aware suggestion engine. It reads the "vibe" of a post (intent + tone),
# scores every intent category with weighted keywords, and returns ranked
# premium-ready unicode emojis plus catchy hook lines. When AI_API_KEY is set it
# upgrades to a real LLM, with a safe automatic fallback to the local engine.

# Each category: weighted keyword map + curated emoji set + tone (+1/-1/0).
AI_INTENTS = {
    "sale":        {"tone": 1,  "emojis": ["🔥", "💥", "💸", "⚡", "🏷️", "🛒", "✅"],
                    "kw": {"sale": 3, "discount": 3, "offer": 3, "deal": 3, "off": 1, "cheap": 2, "save": 2, "coupon": 2, "promo": 2, "buy": 1, "shop": 1, "price": 1, "% off": 3}},
    "launch":      {"tone": 1,  "emojis": ["🚀", "✨", "🆕", "🎉", "📢", "🔓", "🌟"],
                    "kw": {"new": 2, "launch": 3, "release": 3, "introducing": 3, "update": 2, "drop": 2, "coming soon": 3, "announce": 2, "available": 2, "version": 1}},
    "giveaway":    {"tone": 1,  "emojis": ["🎁", "🎉", "🍀", "🎊", "🤑", "🏆", "✨"],
                    "kw": {"giveaway": 3, "contest": 3, "win": 2, "winner": 2, "prize": 3, "lucky": 2, "draw": 2, "free": 2, "enter": 1, "participate": 2}},
    "love":        {"tone": 1,  "emojis": ["❤️", "😍", "💖", "🥰", "💕", "😘", "💞"],
                    "kw": {"love": 3, "heart": 2, "romantic": 3, "valentine": 3, "crush": 2, "couple": 2, "darling": 2, "sweetheart": 2, "miss you": 2}},
    "gift":        {"tone": 1,  "emojis": ["🎁", "💎", "⭐", "🎀", "💝", "🛍️", "✨"],
                    "kw": {"gift": 3, "bonus": 3, "free": 2, "reward": 3, "freebie": 3, "voucher": 2, "complimentary": 2, "claim": 2}},
    "urgent":      {"tone": -1, "emojis": ["⚠️", "🚨", "❗", "⏰", "🔴", "📣", "‼️"],
                    "kw": {"urgent": 3, "warning": 3, "alert": 3, "hurry": 3, "now": 1, "last chance": 3, "deadline": 3, "expires": 3, "ending": 2, "act fast": 3, "limited time": 3}},
    "premium":     {"tone": 1,  "emojis": ["💎", "👑", "⭐", "🏆", "🥇", "✨", "🔱"],
                    "kw": {"premium": 3, "vip": 3, "pro": 2, "luxury": 3, "exclusive": 3, "elite": 3, "best": 1, "top": 1, "ultimate": 2, "platinum": 2, "gold": 2}},
    "money":       {"tone": 1,  "emojis": ["💰", "💵", "🤑", "📈", "💹", "🏦", "💸"],
                    "kw": {"money": 3, "earn": 3, "income": 3, "profit": 3, "cash": 3, "salary": 2, "rich": 2, "wealth": 2, "invest": 2, "payout": 2, "withdraw": 2, "dollar": 1, "taka": 1}},
    "crypto":      {"tone": 0,  "emojis": ["🪙", "📈", "🚀", "💹", "🔗", "⛓️", "💎"],
                    "kw": {"crypto": 3, "bitcoin": 3, "btc": 3, "eth": 2, "token": 2, "blockchain": 3, "trading": 2, "wallet": 2, "nft": 2, "airdrop": 3, "web3": 2}},
    "tech":        {"tone": 0,  "emojis": ["💻", "📱", "🤖", "⚙️", "🔌", "🖥️", "🛰️"],
                    "kw": {"tech": 2, "gadget": 3, "app": 2, "software": 2, "ai": 2, "robot": 2, "device": 2, "smartphone": 2, "laptop": 2, "code": 2, "digital": 1, "feature": 1}},
    "gaming":      {"tone": 1,  "emojis": ["🎮", "🕹️", "🏆", "👾", "🔥", "⚔️", "🎯"],
                    "kw": {"game": 2, "gaming": 3, "play": 1, "level": 2, "player": 2, "esports": 3, "stream": 1, "score": 1, "match": 1, "pubg": 2, "freefire": 2}},
    "music":       {"tone": 1,  "emojis": ["🎵", "🎶", "🎧", "🎤", "🔊", "🎸", "🥁"],
                    "kw": {"music": 3, "song": 3, "track": 2, "album": 2, "concert": 2, "beat": 2, "playlist": 2, "remix": 2, "artist": 1, "spotify": 2}},
    "food":        {"tone": 1,  "emojis": ["🍔", "🍕", "🍟", "😋", "🤤", "🥗", "🍰"],
                    "kw": {"food": 3, "eat": 2, "delicious": 3, "tasty": 3, "recipe": 2, "restaurant": 2, "menu": 2, "meal": 2, "snack": 2, "hungry": 2, "foodie": 3}},
    "travel":      {"tone": 1,  "emojis": ["✈️", "🌍", "🏖️", "🧳", "🗺️", "🏝️", "📸"],
                    "kw": {"travel": 3, "trip": 3, "tour": 2, "flight": 2, "hotel": 2, "vacation": 3, "holiday": 2, "adventure": 2, "destination": 2, "explore": 1}},
    "fitness":     {"tone": 1,  "emojis": ["💪", "🏋️", "🔥", "🏃", "🥗", "⚡", "🧘"],
                    "kw": {"fitness": 3, "gym": 3, "workout": 3, "health": 2, "diet": 2, "muscle": 2, "training": 2, "weight": 1, "exercise": 3, "wellness": 2}},
    "education":   {"tone": 1,  "emojis": ["📚", "🎓", "✏️", "🧠", "💡", "📝", "🔬"],
                    "kw": {"learn": 3, "course": 3, "study": 3, "education": 3, "tutorial": 2, "class": 2, "school": 2, "exam": 2, "lesson": 2, "knowledge": 2, "training": 1}},
    "celebrate":   {"tone": 1,  "emojis": ["🎉", "🎊", "🥳", "🎈", "🍾", "✨", "🎆"],
                    "kw": {"celebrate": 3, "party": 3, "festival": 2, "anniversary": 3, "birthday": 3, "cheers": 2, "congrats": 2, "milestone": 2, "eid": 2, "puja": 2}},
    "news":        {"tone": 0,  "emojis": ["📢", "📰", "🗞️", "🔔", "📣", "🆕", "👀"],
                    "kw": {"news": 3, "announcement": 3, "update": 1, "breaking": 3, "report": 2, "alert": 1, "notice": 2, "important": 2, "headline": 2}},
    "achievement": {"tone": 1,  "emojis": ["🏆", "🥇", "🎯", "🚀", "👏", "🙌", "⭐"],
                    "kw": {"achievement": 3, "success": 3, "won": 2, "reached": 2, "goal": 2, "record": 2, "proud": 2, "accomplish": 2, "thank you": 1, "grateful": 1}},
    "motivation":  {"tone": 1,  "emojis": ["💪", "🔥", "🚀", "🌟", "💯", "⚡", "🦁"],
                    "kw": {"motivation": 3, "inspire": 3, "dream": 2, "hustle": 3, "grind": 2, "believe": 2, "mindset": 2, "success": 1, "never give up": 3, "discipline": 2}},
    "question":    {"tone": 0,  "emojis": ["🤔", "❓", "💭", "👇", "🗳️", "💬", "👀"],
                    "kw": {"?": 1, "poll": 3, "vote": 3, "question": 2, "what do you think": 3, "comment": 2, "your opinion": 3, "guess": 2}},
    "thanks":      {"tone": 1,  "emojis": ["🙏", "❤️", "🥰", "🤝", "✨", "🙌", "💐"],
                    "kw": {"thank": 3, "thanks": 3, "grateful": 3, "appreciate": 3, "gratitude": 3, "blessed": 2, "respect": 1}},
    "sad":         {"tone": -1, "emojis": ["😢", "💔", "😞", "🥺", "😔", "🙏", "🕊️"],
                    "kw": {"sad": 3, "sorry": 3, "miss": 1, "loss": 3, "rip": 3, "condolence": 3, "broken": 2, "cry": 2, "heartbroken": 3}},
    "funny":       {"tone": 1,  "emojis": ["😂", "🤣", "😆", "😜", "🤪", "😅", "💀"],
                    "kw": {"funny": 3, "lol": 3, "lmao": 3, "joke": 3, "haha": 3, "meme": 3, "comedy": 2, "hilarious": 3, "rofl": 3}},
    "fashion":     {"tone": 1,  "emojis": ["👗", "👠", "💄", "🕶️", "👜", "✨", "💅"],
                    "kw": {"fashion": 3, "style": 2, "outfit": 3, "dress": 2, "beauty": 2, "makeup": 3, "trend": 2, "collection": 2, "wear": 1, "clothing": 2}},
    "sports":      {"tone": 1,  "emojis": ["⚽", "🏏", "🏀", "🥅", "🏆", "🔥", "🥇"],
                    "kw": {"sports": 2, "football": 3, "cricket": 3, "match": 2, "team": 1, "goal": 1, "tournament": 2, "league": 2, "player": 1, "score": 1}},
    "job":         {"tone": 1,  "emojis": ["💼", "📈", "🤝", "📝", "🏢", "🎯", "✅"],
                    "kw": {"job": 3, "hiring": 3, "career": 3, "vacancy": 3, "apply": 2, "recruit": 3, "salary": 1, "interview": 2, "remote": 2, "position": 2, "opportunity": 2}},
    "security":    {"tone": 0,  "emojis": ["🔒", "🛡️", "🔐", "✅", "⚠️", "🕵️", "🔑"],
                    "kw": {"security": 3, "privacy": 3, "protect": 2, "safe": 2, "password": 2, "scam": 2, "verify": 2, "secure": 2, "fraud": 2, "encrypt": 2}},
}

AI_HOOKS = {
    "sale":        ["🔥 BIG SALE IS LIVE — don't miss out!", "💸 Lowest price ever, today only!", "🛒 Grab yours before stock runs out!"],
    "launch":      ["🚀 IT'S FINALLY HERE!", "✨ Introducing something special for you!", "🆕 Brand new — be the first to try it!"],
    "giveaway":    ["🎁 GIVEAWAY ALERT — join now!", "🍀 Your lucky day starts here!", "🏆 Win big, it's totally free!"],
    "love":        ["❤️ Made with love, just for you.", "🥰 You're going to adore this!", "💖 Spread the love today!"],
    "gift":        ["🎁 A special gift is waiting for you!", "💝 Claim your free reward now!", "⭐ Exclusive bonus unlocked!"],
    "urgent":      ["⏰ HURRY — offer ends very soon!", "🚨 Last chance, act now!", "‼️ Don't wait, this won't last!"],
    "premium":     ["👑 Premium quality, premium feel.", "💎 Step into the VIP experience.", "🏆 Only the best, for the best."],
    "money":       ["💰 Start earning today!", "📈 Turn your time into income!", "🤑 Real money, real results!"],
    "crypto":      ["🚀 To the moon — don't miss this!", "🪙 The next big move starts now!", "💹 Smart money is already in!"],
    "tech":        ["🤖 The future is here!", "💻 Smarter, faster, better!", "⚙️ Next-level tech, unlocked!"],
    "gaming":      ["🎮 Game on — let's go!", "🏆 Level up like a pro!", "👾 New challenge awaits!"],
    "music":       ["🎵 Press play and vibe!", "🎧 Your new favorite track is here!", "🔊 Turn it up loud!"],
    "food":        ["😋 Too tasty to resist!", "🍔 Hungry yet? Dig in!", "🤤 Flavor you'll fall for!"],
    "travel":      ["✈️ Adventure is calling!", "🌍 Pack your bags, let's explore!", "🏖️ Your dream trip starts here!"],
    "fitness":     ["💪 Stronger every single day!", "🔥 No excuses — let's get it!", "🏋️ Transform starts today!"],
    "education":   ["🎓 Learn it, master it!", "🧠 Level up your skills today!", "💡 Knowledge that pays off!"],
    "celebrate":   ["🎉 Let's celebrate together!", "🥳 The party starts now!", "🎊 Big moment, big vibes!"],
    "news":        ["📢 BIG announcement inside!", "🔔 You need to see this!", "🆕 Fresh update just dropped!"],
    "achievement": ["🏆 We did it — thank you!", "🙌 A milestone worth celebrating!", "🎯 Goal smashed!"],
    "motivation":  ["💪 Your time is NOW!", "🚀 Dream big, work hard!", "🔥 Keep pushing — you've got this!"],
    "question":    ["🤔 What do you think? 👇", "🗳️ Vote and let us know!", "💬 Drop your answer below!"],
    "thanks":      ["🙏 Thank you for the love!", "❤️ We appreciate you so much!", "🙌 Grateful for this community!"],
    "sad":         ["🕊️ Sending love and strength.", "🙏 Stay strong, we're with you.", "💔 Tough times, but together we rise."],
    "funny":       ["😂 You'll laugh, guaranteed!", "🤣 This one's too good!", "😜 Warning: highly addictive fun!"],
    "fashion":     ["✨ Slay the look!", "👗 Style that turns heads!", "💄 Glow up time!"],
    "sports":      ["🔥 Game day energy!", "🏆 Cheer for the win!", "⚽ Don't miss the action!"],
    "job":         ["💼 We're hiring — apply now!", "🎯 Your next big role awaits!", "🤝 Join our growing team!"],
    "security":    ["🔒 Stay safe, stay protected!", "🛡️ Your security comes first!", "🔐 Lock it down today!"],
}

AI_DEFAULT_EMOJIS = ["✨", "🔥", "⭐", "💯", "🚀", "👑", "🎯"]

# Optional real-LLM upgrade. Disabled automatically when no key is configured.
AI_LLM_ENABLED = bool(os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY"))
AI_LLM_KEY = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
AI_LLM_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_LLM_BASE = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
_ai_llm_cache = {}


def _ai_tokenized(text):
    return " " + re.sub(r"\s+", " ", (text or "").lower()) + " "


def ai_analyze_text(text):
    """Score every intent against the text and return a ranked analysis dict:
    {intents: [(name, score)...], top: name, tone: 'positive'/'negative'/'neutral'}."""
    blob = _ai_tokenized(text)
    scores = {}
    tone_score = 0
    for name, spec in AI_INTENTS.items():
        s = 0
        for kw, w in spec["kw"].items():
            if kw == "?":
                s += w * blob.count("?")
            elif " " in kw or not kw.isalpha():
                if kw in blob:
                    s += w
            else:
                # word-boundary match so "win" doesn't fire inside "window"
                if re.search(r"\b" + re.escape(kw) + r"\b", blob):
                    s += w
        if s > 0:
            scores[name] = s
            tone_score += spec["tone"] * s
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    tone = "positive" if tone_score > 0 else ("negative" if tone_score < 0 else "neutral")
    return {"intents": ranked, "top": (ranked[0][0] if ranked else None), "tone": tone}


def ai_emoji_suggestions(text, limit=6):
    """Ranked, de-duplicated unicode emoji list based on detected vibe.
    Falls back to a tasteful default set when nothing is detected."""
    # Try real LLM first (safe, cached, optional).
    llm = ai_llm_suggest(text, want="emojis") if AI_LLM_ENABLED else None
    if llm:
        return llm[:limit]
    analysis = ai_analyze_text(text)
    out, seen = [], set()
    for name, _score in analysis["intents"]:
        for e in AI_INTENTS[name]["emojis"]:
            if e not in seen:
                seen.add(e)
                out.append(e)
            if len(out) >= limit:
                return out
    for e in AI_DEFAULT_EMOJIS:
        if e not in seen:
            seen.add(e)
            out.append(e)
        if len(out) >= limit:
            break
    return out[:limit]


# Backward-compatible alias used by inline mode and older call sites.
def smart_emoji_suggestions(text):
    return ai_emoji_suggestions(text, limit=5)


def ai_generate_hook(text, seed_shift=0):
    """Pick a catchy hook line matched to the post's strongest intent."""
    llm = ai_llm_suggest(text, want="hook") if AI_LLM_ENABLED else None
    if llm and isinstance(llm, str) and llm.strip():
        return llm.strip()
    analysis = ai_analyze_text(text)
    top = analysis["top"]
    pool = AI_HOOKS.get(top) if top else None
    if not pool:
        pool = ["✨ Don't miss this!", "🔥 You'll love this one!", "🚀 Big things inside!"]
    idx = (_stable_seed(text) + seed_shift) % len(pool)
    return pool[idx]


def ai_sprinkle_text(text, density=2):
    """Insert intent-matched emojis at the end of sentences for an engaging look."""
    try:
        emos = ai_emoji_suggestions(text, limit=max(2, density + 1))
        if not emos:
            return text
        parts = re.split(r"(\n+|(?<=[.!?])\s+)", text or "")
        out, ei = [], 0
        for chunk in parts:
            out.append(chunk)
            if chunk.strip() and not chunk.startswith("\n") and len(chunk.strip()) > 8:
                out.append(" " + emos[ei % len(emos)])
                ei += 1
        result = "".join(out).strip()
        return result or text
    except Exception:
        return text


def ai_vibe_label(text):
    analysis = ai_analyze_text(text)
    top = analysis["top"]
    name = (top or "general").replace("_", " ").title()
    tone_icon = {"positive": "📈", "negative": "🛟", "neutral": "🎯"}.get(analysis["tone"], "🎯")
    return f"{name} · {analysis['tone'].title()} {tone_icon}"


def ai_llm_suggest(text, want="emojis"):
    """Optional OpenAI-compatible call. Returns list (emojis) or str (hook),
    or None on any failure so callers fall back to the local engine."""
    if not AI_LLM_ENABLED or not (text or "").strip():
        return None
    cache_key = f"{want}:{(text or '').strip().lower()[:160]}"
    cached = _ai_llm_cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        if want == "hook":
            prompt = ("Write ONE short, catchy marketing hook line (max 8 words) for this "
                      "Telegram post. Include 1-2 fitting emojis. Reply with only the line.\n\nPost:\n" + text[:600])
        else:
            prompt = ("Suggest 6 emojis that best match the vibe of this Telegram post. "
                      "Reply with only the emojis, no spaces, no text.\n\nPost:\n" + text[:600])
        payload = json.dumps({
            "model": AI_LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 60,
        }).encode("utf-8")
        req = urllib.request.Request(
            AI_LLM_BASE + "/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {AI_LLM_KEY}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = (data["choices"][0]["message"]["content"] or "").strip()
        if want == "hook":
            result = content.splitlines()[0].strip().strip('"') if content else None
        else:
            spans = _emoji_spans(content)
            result = [val for _s, _e, val in spans] or None
        _ai_llm_cache[cache_key] = result
        return result
    except Exception:
        log_exc("ai_llm_suggest")
        _ai_llm_cache[cache_key] = None
        return None

# ======================== KEYBOARDS ========================
def main_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # Create
    m.add(kb_btn("MAKE POST", "make_post", "success"), kb_btn("STYLE LAB", "emoji", "success"))
    m.add(kb_btn("TEMPLATES", "emoji", "primary"), kb_btn("MY VAULT", "coin", "primary"))
    # Rewards
    m.add(kb_btn("DAILY BONUS", "coin", "success"), kb_btn("REFERRAL", "coin", "success"))
    # System
    m.add(kb_btn("STATS", "stats", "primary"), kb_btn("SETTINGS", "settings", "primary"))
    m.add(kb_btn("LIVE SUPPORT", "broadcast", "success"), kb_btn("HELP", "help", "primary"))
    m.add(kb_btn("ABOUT BOT", "about", "primary"))
    return m


def admin_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # Create
    m.add(kb_btn("MAKE POST", "make_post", "success"), kb_btn("STYLE LAB", "emoji", "success"))
    m.add(kb_btn("TEMPLATES", "emoji", "primary"), kb_btn("MY VAULT", "coin", "primary"))
    # Admin control
    m.add(kb_btn("ADMIN PANEL", "admin_panel", "success"), kb_btn("BROADCAST", "broadcast", "primary"))
    # Emoji operations
    m.add(kb_btn("EMOJI COLLECTOR", "emoji", "success"), kb_btn("EXPORT EMOJIS", "pack", "primary"))
    # Analytics + system
    m.add(kb_btn("USERS LIST", "users_list", "primary"), kb_btn("BOT STATS", "stats", "primary"))
    m.add(kb_btn("SETTINGS", "settings", "primary"), kb_btn("LIVE SUPPORT", "broadcast", "success"))
    m.add(kb_btn("HELP", "help", "primary"), kb_btn("ABOUT BOT", "about", "primary"))
    return m


def user_keyboard(uid=None):
    return admin_menu() if uid and is_admin(uid) else main_menu()

# ======================== FORCE JOIN + RATE LIMIT ========================
def required_channels():
    try:
        ts = time.time()
        if channel_cache["expires"] <= ts:
            channel_cache["data"] = list(channels.find({"active": True}).sort("created_at", ASCENDING))
            channel_cache["expires"] = ts + 45
        return channel_cache["data"]
    except Exception:
        return []

def check_joined(uid, force=False):
    missing = []
    try:
        uid = int(uid)
        if is_admin(uid) or not get_setting("bot", "force_join_enabled", True):
            return []
        ts = time.time()
        cached = join_cache.get(uid)
        if cached and not force and cached.get("expires", 0) > ts:
            return cached.get("missing", [])
        for ch in required_channels():
            try:
                member = bot.get_chat_member(ch["channel_id"], uid)
                if member.status in ("left", "kicked", "banned"):
                    missing.append(ch)
            except Exception:
                missing.append(ch)
        join_cache[uid] = {"missing": missing, "expires": ts + (300 if not missing else 45)}
    except Exception:
        log_exc("check_joined")
    return missing

def send_join_notice(chat_id, missing):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in missing:
        markup.add(i_btn(f"JOIN {ch.get('name', 'Channel')}", url=ch.get("link"), style="danger", emoji_key="channel_settings"))
    markup.add(i_btn("CHECK JOIN", "user:check_join", "success", "success"))
    text = f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n{P}       JOIN REQUIRED       {P}\n{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
    text += f"{P} Join all channels to use this bot:\n\n"
    for i, ch in enumerate(missing, 1):
        text += f"{P} {i}. {ch.get('name', 'Channel')}\n"
    text += f"\n{P} Then tap CHECK JOIN.\n{P}━━━━━━━━━━━━━━━━━━━━{P}"
    _send_pe(chat_id, text, use_main=False, reply_markup=markup)


def user_spam_status(uid):
    try:
        spam = (get_user(uid) or {}).get("spam", {}) or {}
        now = now_utc()
        for key in ("banned_until", "muted_until"):
            val = spam.get(key)
            if val and val.tzinfo is None:
                val = val.replace(tzinfo=timezone.utc)
            if val and val > now:
                return ("banned" if key == "banned_until" else "muted"), val
    except Exception:
        pass
    return None, None


def rate_limit_ok(message, silent=False):
    try:
        uid = int(message.from_user.id)
        if is_admin(uid) or not get_setting("spam", "enabled", True):
            return True
        status, until = user_spam_status(uid)
        if status:
            if not silent:
                _send_pe(message.chat.id, f"{P} Anti-spam active. You are temporarily {status} until {fmt_dt(until)}.", use_main=False)
            return False
        s = get_setting("spam", default={}) or {}
        max_actions = int(s.get("max_actions", 8))
        window = int(s.get("window_seconds", 10))
        q = rate_memory[uid]
        now_ts = time.time()
        while q and now_ts - q[0] > window:
            q.popleft()
        q.append(now_ts)
        if len(q) <= max_actions:
            return True
        violations = int(((get_user(uid) or {}).get("spam", {}) or {}).get("violations", 0)) + 1
        update = {"spam.violations": violations, "spam.muted_until": now_utc() + timedelta(minutes=int(s.get("mute_minutes", 3)))}
        if violations >= int(s.get("ban_after_violations", 5)):
            update["spam.banned_until"] = now_utc() + timedelta(minutes=int(s.get("ban_minutes", 60)))
        users.update_one({"user_id": uid}, {"$set": update})
        track_event("spam_limit", uid, {"violations": violations})
        if not silent:
            _send_pe(message.chat.id, f"{P} Too many requests. Anti-spam protection applied.", use_main=False)
        return False
    except Exception:
        log_exc("rate_limit_ok")
        return True


def precheck(message, require_join=True):
    try:
        runtime_metrics["updates"] = runtime_metrics.get("updates", 0) + 1
        runtime_metrics["last_update"] = now_utc()
        uid = message.from_user.id
        register_user_from_message(message)
        if not is_admin(uid) and is_user_banned(uid):
            _send_pe(message.chat.id, f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n{P} ACCESS BLOCKED {P}\n{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n{P} Your access to this bot has been disabled by an administrator.\n{P} Contact {get_setting('bot', 'support_username', SUPPORT_USERNAME)} if you think this is a mistake.\n{P}━━━━━━━━━━━━━━━━━━━━{P}", use_main=False)
            return False
        if not get_setting("bot", "active", True) and not is_admin(uid):
            _send_pe(message.chat.id, f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n{P} OFFLINE {P}\n{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n{P} {get_setting('bot', 'maintenance_message', 'Bot offline.')}\n{P}━━━━━━━━━━━━━━━━━━━━{P}", use_main=False)
            return False
        if require_join and not is_admin(uid):
            missing = check_joined(uid)
            if missing:
                send_join_notice(message.chat.id, missing)
                return False
        return rate_limit_ok(message)
    except Exception:
        log_exc("precheck")
        return True


def charge_conversion(uid, reason="conversion"):
    try:
        if is_admin(uid):
            return True
        g = get_setting("growth", default={}) or {}
        if not g.get("coins_enabled", True):
            return True
        cost = int(g.get("conversion_cost", 0))
        if cost <= 0:
            return True
        if int((get_user(uid) or {}).get("coins", 0)) < cost:
            return False
        users.update_one({"user_id": int(uid)}, {"$inc": {"coins": -cost}})
        track_event("coins_spent", uid, {"reason": reason, "cost": cost})
        return True
    except Exception:
        return True

# ======================== ADMIN PANEL UI ========================
def admin_home_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("User Management", "admin:users", "success", "users_list"), i_btn("Live Support", "admin:support", "success", "broadcast"))
    m.add(i_btn("Analytics", "admin:analytics", "primary", "analytics"), i_btn("Emojis & Packs", "admin:packs", "success", "pack"))
    m.add(i_btn("Forward Collector", "admin:collector", "success", "emoji"), i_btn("Export Backup", "admin:export_backup", "primary", "pack"))
    m.add(i_btn("Broadcasts", "admin:broadcasts", "primary", "broadcast"), i_btn("Force Join", "admin:channels", "primary", "channel_settings"))
    m.add(i_btn("Anti-Spam", "admin:spam", "danger", "spam"), i_btn("Admins", "admin:admins", "primary", "admin_panel"))
    m.add(i_btn("Growth & Coins", "admin:growth", "success", "coin"), i_btn("Bot Settings", "admin:settings", "primary", "settings"))
    m.add(i_btn("Live Status", "admin:health", "success", "stats"), i_btn("Refresh Panel", "admin:home", "primary", "back"))
    return m


def back_markup(target="admin:home"):
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(i_btn("BACK", target, "primary", "back"))
    return m


def send_admin_panel(chat_id, message_id=None):
    status = "ONLINE 🟢" if get_setting('bot', 'active', True) else "OFFLINE 🔴"
    today = to_utc(now_local().replace(hour=0, minute=0, second=0, microsecond=0))
    text = (
        f"{premium_header('⚡ GADGET CONTROL NEXUS ⚡')}\n\n"
        f"{P} Zero-Code Enterprise Command Center\n"
        f"{P} Manage users, packs, broadcasts, coins and growth from here.\n\n"
        f"{P} {section_style('STATUS MATRIX')}\n"
        f"{P} Bot Engine   : {status}\n"
        f"{P} Uptime       : {fmt_uptime()}\n"
        f"{P} Total Users  : {cached_count('users', users)}\n"
        f"{P} New Today    : {cached_count('new_today', users, {'joined_at': {'$gte': today}}, ttl=10)}\n"
        f"{P} Banned Users : {cached_count('banned_users', users, {'banned': True}, ttl=15)}\n"
        f"{P} Active Packs : {cached_count('packs', packs, {'active': True})}\n"
        f"{P} Premium IDs  : {cached_count('emojis', emojis_col, {'active': True})}\n"
        f"{P} Force Join   : {cached_count('channels', channels, {'active': True})} channels\n\n"
        f"{P} Choose a control module below.\n"
        f"{premium_footer()}"
    )
    if message_id:
        _edit_pe(chat_id, message_id, text, use_main=False, reply_markup=admin_home_markup())
    else:
        _send_pe(chat_id, text, use_main=False, reply_markup=admin_home_markup())


def analytics_text():
    today = to_utc(now_local().replace(hour=0, minute=0, second=0, microsecond=0))
    week = now_utc() - timedelta(days=7)
    month = now_utc() - timedelta(days=30)
    return (
        f"{premium_header('📊 LIVE ANALYTICS VAULT 📊')}\n\n"
        f"{P} Growth Pulse\n"
        f"{P} New Users Today      : {cached_count('new_today', users, {'joined_at': {'$gte': today}}, ttl=10)}\n"
        f"{P} Total Users          : {cached_count('users', users)}\n"
        f"{P} Active Users 30 Days : {cached_count('active30', users, {'last_seen': {'$gte': month}}, ttl=10)}\n\n"
        f"{P} Conversion Engine\n"
        f"{P} Weekly Conversions   : {cached_count('conv_week', analytics, {'event': 'conversion', 'created_at': {'$gte': week}}, ttl=10)}\n"
        f"{P} Weekly Inline Uses   : {cached_count('inline_week', analytics, {'event': 'inline_conversion', 'created_at': {'$gte': week}}, ttl=10)}\n"
        f"{P} Weekly Posts Done    : {cached_count('post_week', analytics, {'event': 'post_done', 'created_at': {'$gte': week}}, ttl=10)}\n\n"
        f"{P} Assets\n"
        f"{P} Premium Emoji IDs    : {cached_count('emojis', emojis_col, {'active': True})}\n"
        f"{P} Active Packs         : {cached_count('packs', packs, {'active': True})}\n"
        f"{P} Sent Broadcasts      : {cached_count('sent_broadcasts', broadcasts, {'status': 'sent'})}\n"
        f"{premium_footer()}"
    )


def packs_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("Create Pack", "admin:pack_create", "success", "pack"), i_btn("Add Emoji ID", "admin:emoji_add", "success", "emoji"))
    m.add(i_btn("Bulk .TXT Import", "admin:emoji_bulk", "primary", "emoji"), i_btn("Forward Collector", "admin:collector", "success", "emoji"))
    m.add(i_btn("Export Pack TXT", "admin:export_pack", "primary", "pack"), i_btn("Remove Emoji", "admin:emoji_remove", "danger", "danger"))
    for pdoc in get_active_packs(20):
        m.add(i_btn(("✅ " if pdoc.get("is_default") else "📦 ") + f"{pdoc.get('name', pdoc.get('slug'))} ({pdoc.get('emoji_count', 0)})", f"admin:pack_view:{pdoc.get('slug')}", "primary", "pack"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def channels_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("Add Channel", "admin:channel_add", "success", "add_channel"), i_btn("Toggle Force Join", "admin:force_toggle", "primary", "settings"))
    for ch in required_channels():
        cid = ch.get("channel_id")
        m.add(i_btn(f"📢 {ch.get('name', cid)}", url=ch.get("link"), style="primary", emoji_key="channel_settings"), i_btn("Remove", f"admin:channel_remove:{cid}", "danger", "remove_channel"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def admins_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("Add Admin", "admin:add_admin", "success", "add_admin"), i_btn("List Admins", "admin:list_admins", "primary", "admin_list"))
    for adm in admins.find({"active": True}).sort("created_at", ASCENDING):
        uid = adm.get("user_id")
        if uid != MASTER_ADMIN_ID:
            m.add(i_btn(f"⭐ {uid}", "admin:list_admins", "primary", "admin_panel"), i_btn("Remove", f"admin:remove_admin:{uid}", "danger", "remove_admin"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def spam_markup():
    s = get_setting("spam", default={}) or {}
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("✅ Enabled" if s.get("enabled", True) else "❌ Disabled", "admin:spam_toggle", "success" if s.get("enabled", True) else "danger", "spam"), i_btn("Set Limits", "admin:spam_set", "primary", "settings"))
    m.add(i_btn("Reset User Spam", "admin:spam_reset_user", "danger", "danger"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def growth_markup():
    g = get_setting("growth", default={}) or {}
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("💰 Coins ON" if g.get("coins_enabled", True) else "💰 Coins OFF", "admin:coins_toggle", "success" if g.get("coins_enabled", True) else "danger", "coin"), i_btn("🏆 Leaderboard ON" if g.get("leaderboard_enabled", True) else "🏆 Leaderboard OFF", "admin:leaderboard_toggle", "success", "coin"))
    m.add(i_btn("Set Bonuses", "admin:growth_set", "primary", "settings"), i_btn("Top Users", "admin:top_users", "primary", "analytics"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def settings_markup():
    active = get_setting("bot", "active", True)
    inline = get_setting("bot", "inline_mode_enabled", True)
    direct = get_setting("bot", "direct_convert_enabled", True)
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("🟢 Bot Online" if active else "🔴 Bot Offline", "admin:bot_toggle", "success" if active else "danger", "settings"), i_btn("Welcome Text", "admin:set_welcome", "primary", "settings"))
    m.add(i_btn("Inline ON" if inline else "Inline OFF", "admin:inline_toggle", "success" if inline else "danger", "settings"), i_btn("Direct ON" if direct else "Direct OFF", "admin:direct_toggle", "success" if direct else "danger", "settings"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


# ======================== USER MANAGEMENT ========================
def users_overview_text():
    total = cached_count("users", users)
    active = cached_count("active_users", users, {"active": True}, ttl=15)
    banned = cached_count("banned_users", users, {"banned": True}, ttl=15)
    blocked = cached_count("blocked_users", users, {"active": False}, ttl=15)
    today = to_utc(now_local().replace(hour=0, minute=0, second=0, microsecond=0))
    new_today = cached_count("new_today", users, {"joined_at": {"$gte": today}}, ttl=10)
    return (
        f"{premium_header('👥 USER COMMAND CENTER 👥')}\n\n"
        f"{P} {section_style('AUDIENCE MATRIX')}\n"
        f"{P} Total Users   : {total}\n"
        f"{P} Active Users  : {active}\n"
        f"{P} New Today     : {new_today}\n"
        f"{P} Banned Users  : {banned}\n"
        f"{P} Blocked Bot   : {blocked}\n\n"
        f"{P} Tap SEARCH USER to manage anyone by ID or @username,\n"
        f"{P} or pick one from the recent list below.\n"
        f"{premium_footer()}"
    )


def users_overview_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("Search User", "admin:user_search", "success", "users_list"),
          i_btn("Recent Users", "admin:users_recent:0", "primary", "users_list"))
    m.add(i_btn("Top Users", "admin:top_users", "primary", "analytics"),
          i_btn("Banned List", "admin:users_banned:0", "danger", "danger"))
    m.add(i_btn("BACK", "admin:home", "primary", "back"))
    return m


def _user_display_name(u):
    name = " ".join([x for x in [u.get("first_name"), u.get("last_name")] if x]).strip()
    return name or "Unknown"


def user_detail_text(u):
    if not u:
        return f"{premium_header('USER NOT FOUND')}\n\n{P} No user matched that ID or @username.\n{premium_footer()}"
    uid = u.get("user_id")
    uname = ("@" + u.get("username")) if u.get("username") else "—"
    status = "🔴 BANNED" if u.get("banned") else ("🟢 ACTIVE" if u.get("active", True) else "⚪ INACTIVE")
    spam = u.get("spam", {}) or {}
    mute_until = spam.get("muted_until")
    ban_until = spam.get("banned_until")
    role = "👑 OWNER" if uid == MASTER_ADMIN_ID else ("⭐ ADMIN" if is_admin(uid) else "👤 MEMBER")
    return (
        f"{premium_header('🪪 USER PROFILE 🪪')}\n\n"
        f"{P} {section_style('IDENTITY')}\n"
        f"{P} Name      : {_user_display_name(u)}\n"
        f"{P} Username  : {uname}\n"
        f"{P} User ID   : {uid}\n"
        f"{P} Role      : {role}\n"
        f"{P} Status    : {status}\n\n"
        f"{P} {section_style('WALLET & ACTIVITY')}\n"
        f"{P} Coins     : {u.get('coins', 0)}\n"
        f"{P} Score     : {u.get('score', 0)}\n"
        f"{P} Conversions : {u.get('conversions', 0)}\n"
        f"{P} Referrals : {u.get('referrals', 0)} (streak {u.get('daily_streak', 0)})\n"
        f"{P} Pack      : {u.get('preferred_pack') or get_default_pack_slug()}\n\n"
        f"{P} {section_style('TIMELINE')}\n"
        f"{P} Joined    : {fmt_dt(u.get('joined_at'))}\n"
        f"{P} Last Seen : {fmt_dt(u.get('last_seen'))}\n"
        f"{P} Spam Mute : {fmt_dt(mute_until) if mute_until else '—'}\n"
        f"{P} Spam Ban  : {fmt_dt(ban_until) if ban_until else '—'}\n"
        f"{premium_footer()}"
    )


def user_detail_markup(uid):
    uid = int(uid)
    u = get_user(uid) or {}
    m = types.InlineKeyboardMarkup(row_width=2)
    if u.get("banned"):
        m.add(i_btn("Unban User", f"admin:user_unban:{uid}", "success", "success"))
    else:
        m.add(i_btn("Ban User", f"admin:user_ban:{uid}", "danger", "danger"))
    m.add(i_btn("Add Coins", f"admin:user_addcoins:{uid}", "success", "coin"),
          i_btn("Remove Coins", f"admin:user_subcoins:{uid}", "danger", "coin"))
    m.add(i_btn("Reset Spam", f"admin:user_resetspam:{uid}", "primary", "spam"),
          i_btn("Send Message", f"admin:user_dm:{uid}", "primary", "broadcast"))
    m.add(i_btn("Refresh", f"admin:user_view:{uid}", "primary", "back"),
          i_btn("BACK", "admin:users", "primary", "back"))
    return m


def users_list_markup(skip=0, only_banned=False, page_size=8):
    m = types.InlineKeyboardMarkup(row_width=1)
    query = {"banned": True} if only_banned else {}
    cursor = users.find(query, {"user_id": 1, "username": 1, "first_name": 1, "coins": 1, "banned": 1}) \
        .sort("joined_at", DESCENDING).skip(int(skip)).limit(page_size)
    rows = list(cursor)
    for u in rows:
        uid = u.get("user_id")
        tag = u.get("username") and ("@" + u.get("username")) or (u.get("first_name") or str(uid))
        flag = "🔴 " if u.get("banned") else ""
        label = f"{flag}{tag} • {u.get('coins', 0)}c • {uid}"
        m.add(i_btn(label[:60], f"admin:user_view:{uid}", "primary", "users_list"))
    base = "admin:users_banned" if only_banned else "admin:users_recent"
    nav = []
    if skip > 0:
        nav.append(i_btn("Prev", f"{base}:{max(0, skip - page_size)}", "primary", "back"))
    if len(rows) == page_size:
        nav.append(i_btn("Next", f"{base}:{skip + page_size}", "primary", "back"))
    if nav:
        m.add(*nav)
    m.add(i_btn("BACK", "admin:users", "primary", "back"))
    return m


# ======================== BROADCASTS ========================
def broadcast_to_all(from_chat_id, message_id, admin_id=None, broadcast_id=None):
    success = failed = total = 0
    try:
        targets = list(users.find({"active": True}, {"user_id": 1}))
        total = len(targets)
        for u in targets:
            uid = u.get("user_id")
            try:
                bot.copy_message(uid, from_chat_id, message_id)
                success += 1
                time.sleep(0.04)
            except Exception as e:
                failed += 1
                if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                    users.update_one({"user_id": uid}, {"$set": {"active": False, "blocked_at": now_utc()}})
                if "too many requests" in str(e).lower():
                    time.sleep(1.5)
        if broadcast_id:
            broadcasts.update_one({"_id": ObjectId(broadcast_id)}, {"$set": {"status": "sent", "sent_at": now_utc(), "success": success, "failed": failed, "total": total}})
        track_event("broadcast_sent", admin_id, {"success": success, "failed": failed, "total": total})
    except Exception:
        log_exc("broadcast_to_all")
        if broadcast_id:
            broadcasts.update_one({"_id": ObjectId(broadcast_id)}, {"$set": {"status": "failed", "failed_at": now_utc()}})
    finally:
        if admin_id:
            try:
                _send_pe(admin_id, f"{P} Broadcast complete.\nTotal: {total}\nSuccess: {success}\nFailed: {failed}", use_main=False)
            except Exception:
                pass
    return success, failed, total


def execute_broadcast(bid):
    try:
        doc = broadcasts.find_one({"_id": ObjectId(bid)})
        if not doc or doc.get("status") != "scheduled":
            return
        broadcasts.update_one({"_id": ObjectId(bid)}, {"$set": {"status": "sending", "started_at": now_utc()}})
        broadcast_to_all(doc.get("from_chat_id"), doc.get("message_id"), doc.get("created_by"), bid)
    except Exception:
        log_exc("execute_broadcast")


def schedule_broadcast_doc(doc):
    try:
        bid = str(doc["_id"])
        run_date = doc.get("scheduled_at")
        if run_date.tzinfo is None:
            run_date = run_date.replace(tzinfo=timezone.utc)
        if run_date <= now_utc():
            execute_broadcast(bid)
            return
        scheduler.add_job(execute_broadcast, "date", run_date=run_date, args=[bid], id=f"broadcast_{bid}", replace_existing=True, misfire_grace_time=3600)
    except Exception:
        log_exc("schedule_broadcast_doc")


def schedule_pending_broadcasts():
    try:
        for doc in broadcasts.find({"status": "scheduled"}):
            schedule_broadcast_doc(doc)
    except Exception:
        log_exc("schedule_pending_broadcasts")


def parse_schedule_time(text):
    raw = (text or "").strip().lower()
    try:
        m = re.fullmatch(r"\+(\d+)\s*(m|min|minute|minutes)", raw)
        if m:
            return now_utc() + timedelta(minutes=int(m.group(1)))
        m = re.fullmatch(r"\+(\d+)\s*(h|hour|hours)", raw)
        if m:
            return now_utc() + timedelta(hours=int(m.group(1)))
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M")
        return to_utc(dt.replace(tzinfo=APP_TZ))
    except Exception:
        return None

# ======================== POST WIZARD ========================
def build_post_markup(data):
    try:
        if not data.get("btn_name") or not data.get("btn_url"):
            return None
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(i_btn(data["btn_name"], url=data["btn_url"], style=data.get("btn_color") or "primary", emoji_key="emoji", emoji_id=data.get("btn_emoji_id") or MAIN_EMOJI_ID))
        return m
    except Exception:
        return None


def send_converted_post(chat_id, data):
    try:
        markup = build_post_markup(data)
        text = data.get("processed_text") or ""
        entities = data.get("processed_entities") or None
        if data.get("photo_id"):
            return bot.send_photo(chat_id, data["photo_id"], caption=text[:1024] if text else None, caption_entities=entities, reply_markup=markup)
        if data.get("document_id"):
            return bot.send_document(chat_id, data["document_id"], caption=text[:1024] if text else None, caption_entities=entities, reply_markup=markup)
        return bot.send_message(chat_id, text or " ", entities=entities, reply_markup=markup, parse_mode=None)
    except Exception:
        log_exc("send_converted_post")
        _send_pe(chat_id, f"{P} Failed to send post. Reduce caption length or try again.", use_main=False)
        return None



def action_markup(uid):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("EMOJI PICKER", f"wizard:emojimanual:{uid}", "success", "emoji"),
          i_btn("REFRESH", f"wizard:refresh:{uid}", "primary", "success"))
    m.add(i_btn("AI STUDIO", f"wizard:aistudio:{uid}", "success", "emoji"),
          i_btn("DELETE", f"wizard:delete:{uid}", "danger", "danger"))
    m.add(i_btn("DONE", f"wizard:done:{uid}", "success", "success"))
    return m


def ai_studio_markup(uid):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("ADD SMART EMOJIS", f"wizard:aiemoji:{uid}", "success", "emoji"),
          i_btn("ADD HOOK LINE", f"wizard:aihook:{uid}", "success", "make_post"))
    m.add(i_btn("SPRINKLE INLINE", f"wizard:aisprinkle:{uid}", "primary", "emoji"),
          i_btn("MAX BOOST", f"wizard:aiboost:{uid}", "primary", "spam"))
    m.add(i_btn("REGENERATE", f"wizard:airegen:{uid}", "primary", "success"),
          i_btn("CLEAR AI", f"wizard:aiclear:{uid}", "danger", "back"))
    m.add(i_btn("BACK TO POST", f"wizard:aiback:{uid}", "success", "success"))
    return m


def ai_compose(uid):
    """Rebuild the post text from the pristine base + the AI add-ons the user
    has toggled, so AI actions never stack or corrupt the original message."""
    data = temp_data.get(uid) or {}
    base = data.get("original_text_pristine")
    if base is None:
        base = data.get("original_text") or ""
        data["original_text_pristine"] = base
    hook = data.get("ai_hook")
    emojis = data.get("ai_emoji_add") or ""
    sprinkle = data.get("ai_sprinkle")
    body = ai_sprinkle_text(base) if sprinkle else base
    text = body
    if emojis:
        text = (text + "  " + emojis).strip()
    if hook:
        text = hook + "\n\n" + text
    data["original_text"] = text
    temp_data[uid] = data
    if data.get("emoji_mode") == "manual":
        init_manual_emoji_selector(uid, keep_existing=True)
    rebuild_post_conversion(uid, randomize=False, allow_resolve=True)


def send_ai_studio(chat_id, uid):
    try:
        data = temp_data.get(uid) or {}
        base = data.get("original_text_pristine") or data.get("original_text") or ""
        vibe = ai_vibe_label(base)
        sug = " ".join(ai_emoji_suggestions(base, limit=6))
        hook_on = "ON" if data.get("ai_hook") else "off"
        emoji_on = "ON" if data.get("ai_emoji_add") else "off"
        sprinkle_on = "ON" if data.get("ai_sprinkle") else "off"
        text = (
            f"{premium_header('AI STUDIO')}\n\n"
            f"{P} Detected Vibe : {vibe}\n"
            f"{P} Top Emojis    : {sug}\n\n"
            f"{P} Smart Emojis  : {emoji_on}\n"
            f"{P} Hook Line     : {hook_on}\n"
            f"{P} Inline Sprinkle: {sprinkle_on}\n\n"
            f"{P} ADD SMART EMOJIS = vibe-matched premium set\n"
            f"{P} ADD HOOK LINE = catchy headline on top\n"
            f"{P} SPRINKLE INLINE = emojis between sentences\n"
            f"{P} MAX BOOST = hook + emojis + sprinkle\n"
            f"{P} REGENERATE = fresh AI variation\n"
            f"{premium_footer()}"
        )
        act = _send_pe(chat_id, text, use_main=False, reply_markup=ai_studio_markup(uid))
        if act:
            data.setdefault("ai_studio_msgs", [])
            data["ai_studio_msgs"].append(act.message_id)
            temp_data[uid] = data
        track_event("ai_studio_open", uid)
    except Exception:
        log_exc("send_ai_studio")

def send_preview_and_actions(chat_id, uid):
    try:
        data = temp_data.get(uid)
        if not data:
            _send_pe(chat_id, f"{P} Session expired. Tap MAKE POST again.", use_main=False)
            return
        for mid in [data.get("preview_msg_id"), data.get("action_msg_id")]:
            if mid:
                try:
                    bot.delete_message(chat_id, mid)
                except Exception:
                    pass
        preview = send_converted_post(chat_id, data)
        if preview:
            data["preview_msg_id"] = preview.message_id
        act = _send_pe(
            chat_id,
            f"{premium_header('POST READY')}\n\n"
            f"{P} Your premium post is ready above.\n\n"
            f"{P} EMOJI PICKER = fine-tune each emoji\n"
            f"{P} REFRESH = reshuffle premium style\n"
            f"{P} AI STUDIO = smart emojis, hooks & boost\n"
            f"{P} DELETE = remove this preview\n"
            f"{P} DONE = finish & post\n"
            f"{premium_footer()}",
            use_main=False,
            reply_markup=action_markup(uid),
        )
        if act:
            data["action_msg_id"] = act.message_id
        temp_data[uid] = data
        track_event("post_preview", uid)
    except Exception:
        log_exc("send_preview_and_actions")


def ask_add_button(chat_id, uid):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("ADD BUTTON", f"wizard:addbtn:{uid}", "success", "success"), i_btn("SKIP", f"wizard:skipbtn:{uid}", "danger", "danger"))
    _send_pe(
        chat_id,
        f"{premium_header('INLINE BUTTON')}\n\n"
        f"{P} Add a colored button with a premium emoji icon under your post?\n"
        f"{premium_footer()}",
        use_main=False,
        reply_markup=m,
    )


def ask_button_name(chat_id, uid):
    sent = _send_pe(chat_id, f"{premium_header('BUTTON NAME')}\n\n{P} Send button name. Include any emoji to use a premium button icon.\n{P} /cancel to stop.\n{premium_footer()}", use_main=False)
    if sent:
        bot.register_next_step_handler(sent, receive_button_name)


def receive_button_name(message):
    try:
        uid = message.from_user.id
        if message.text and message.text.strip() == "/cancel":
            cancel_step(message)
            return
        if uid not in temp_data:
            _send_pe(message.chat.id, f"{P} Session expired.", use_main=False)
            return
        name = (message.text or "").strip()
        if not name:
            sent = _send_pe(message.chat.id, f"{P} Empty name. Send again:", use_main=False)
            if sent:
                bot.register_next_step_handler(sent, receive_button_name)
            return
        pool = get_pack_emojis(temp_data[uid].get("pack_slug"))
        icon = None
        clean = ""
        for ch in name:
            if emoji.is_emoji(ch):
                icon = icon or random.choice(pool)
            else:
                clean += ch
        temp_data[uid]["btn_name"] = clean.strip() or name
        temp_data[uid]["btn_emoji_id"] = icon or MAIN_EMOJI_ID
        sent = _send_pe(message.chat.id, f"{premium_header('BUTTON LINK')}\n\n{P} Send button URL.\n{P} Must start with https://, http://, or tg://\n{premium_footer()}", use_main=False)
        if sent:
            bot.register_next_step_handler(sent, receive_button_url)
    except Exception:
        log_exc("receive_button_name")


def receive_button_url(message):
    try:
        uid = message.from_user.id
        if message.text and message.text.strip() == "/cancel":
            cancel_step(message)
            return
        url = (message.text or "").strip()
        if uid not in temp_data:
            _send_pe(message.chat.id, f"{P} Session expired.", use_main=False)
            return
        if not url.startswith(("https://", "http://", "tg://")):
            sent = _send_pe(message.chat.id, f"{P} Invalid URL. Try again:", use_main=False)
            if sent:
                bot.register_next_step_handler(sent, receive_button_url)
            return
        temp_data[uid]["btn_url"] = url
        ask_button_color(message.chat.id, uid)
    except Exception:
        log_exc("receive_button_url")


def ask_button_color(chat_id, uid):
    """Required colored button step: green/blue/red/plain + premium emoji icon support."""
    try:
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            i_btn("SUCCESS (green)", f"wizard:colorsuccess:{uid}", "success", "success"),
            i_btn("PRIMARY (blue)", f"wizard:colorprimary:{uid}", "primary", "settings"),
        )
        m.add(
            i_btn("DANGER (red)", f"wizard:colordanger:{uid}", "danger", "danger"),
            i_btn("NO COLOUR", f"wizard:colornone:{uid}", "primary", "back"),
        )
        _send_pe(
            chat_id,
            f"{P}━━━━━━━━━━━━���━━━━━━━{P}\n"
            f"{P}     CHOOSE BUTTON COLOUR     {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} SUCCESS = Green\n"
            f"{P} PRIMARY = Blue\n"
            f"{P} DANGER  = Red\n"
            f"{P} NONE    = Plain\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}",
            use_main=False,
            reply_markup=m,
        )
    except Exception:
        log_exc("ask_button_color")


def ask_add_file(chat_id, uid):
    data = temp_data.get(uid, {})
    if data.get("photo_id") or data.get("document_id"):
        send_preview_and_actions(chat_id, uid)
        return
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("ADD FILE", f"wizard:addfile:{uid}", "success", "success"), i_btn("SKIP", f"wizard:skipfile:{uid}", "danger", "danger"))
    _send_pe(chat_id, f"{premium_header('ADD FILE')}\n\n{P} Attach photo or document to this premium post?\n{premium_footer()}", use_main=False, reply_markup=m)


def receive_file(message):
    try:
        uid = message.from_user.id
        if message.text and message.text.strip() == "/cancel":
            cancel_step(message)
            return
        if uid not in temp_data:
            _send_pe(message.chat.id, f"{P} Session expired.", use_main=False)
            return
        if message.content_type == "photo":
            temp_data[uid]["photo_id"] = message.photo[-1].file_id
        elif message.content_type == "document":
            temp_data[uid]["document_id"] = message.document.file_id
            temp_data[uid]["doc_name"] = message.document.file_name
        else:
            sent = _send_pe(message.chat.id, f"{P} Send photo or document only:", use_main=False)
            if sent:
                bot.register_next_step_handler(sent, receive_file)
            return
        send_preview_and_actions(message.chat.id, uid)
    except Exception:
        log_exc("receive_file")

# ======================== USER HANDLERS ========================
@bot.message_handler(commands=["start"])
def welcome(message):
    try:
        ref = None
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) > 1:
            ref = parse_ref_code(parts[1])
        register_user_from_message(message, ref)
        if not precheck(message):
            return
        uid = message.from_user.id
        name = message.from_user.first_name or "Friend"
        u = get_user(uid) or {}
        text = (
            f"{premium_header('💎 GADGET PREMIUM EMOJI 💎')}\n\n"
            f"{P} Welcome, {name}!\n\n"
            f"{P} Your private premium emoji studio is online.\n"
            f"{P} Convert posts, captions, buttons and inline text in seconds.\n\n"
            f"{P} {section_style('ACCOUNT SNAPSHOT')}\n"
            f"{P} Active Pack : {get_user_pack_slug(uid)}\n"
            f"{P} Coins       : {u.get('coins', 0)}\n"
            f"{P} Streak      : {u.get('daily_streak', 0)} days\n"
            f"{P} Referrals   : {u.get('referrals', 0)}\n\n"
            f"{P} {section_style('QUICK ACTIONS')}\n"
            f"{P} {label_style('MAKE POST')}    - Create premium posts\n"
            f"{P} {label_style('SETTINGS')}     - Select emoji pack\n"
            f"{P} {label_style('REFERRAL')}     - Earn coins with invites\n"
            f"{P} DAILY BONUS  - Claim streak reward\n\n"
            f"{P} Inline Mode: @{get_bot_username()} your text\n"
            f"{premium_footer()}"
        )
        _send_pe(message.chat.id, text, use_main=False, reply_markup=user_keyboard(uid))
    except Exception:
        log_exc("welcome")


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda m: m.text == "HELP")
def help_msg(message):
    if not precheck(message):
        return
    text = (
        f"{premium_header('⚡ HOW TO USE ⚡')}\n\n"
        f"{P} {section_style('MAKE POST')}\n"
        f"{P} Send text, photo caption, or document caption.\n"
        f"{P} Add a colored button with a premium emoji icon.\n\n"
        f"{P} {section_style('DIRECT CONVERT')}\n"
        f"{P} Send any text containing emojis.\n"
        f"{P} The bot returns a premium emoji version instantly.\n\n"
        f"{P} {section_style('INLINE MODE')}\n"
        f"{P} Type @{get_bot_username()} your text in any chat.\n\n"
        f"{P} {section_style('GROWTH SYSTEM')}\n"
        f"{P} DAILY BONUS gives coins and streak rewards.\n"
        f"{P} REFERRAL gives real coins when new users join.\n\n"
        f"{P} {section_style('LIVE SUPPORT')}\n"
        f"{P} Tap LIVE SUPPORT or send /support to chat\n"
        f"{P} directly with a human agent inside this bot.\n"
        f"{premium_footer()}"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=user_keyboard(message.from_user.id))


def _support_url():
    handle = (SUPPORT_USERNAME or "").lstrip("@").strip()
    return f"https://t.me/{handle}" if handle else None


@bot.message_handler(commands=["about"])
@bot.message_handler(func=lambda m: m.text == "ABOUT BOT")
def about_bot(message):
    if not precheck(message):
        return
    text = (
        f"{premium_header('🚀 PREMIUM BOT INFO 🚀')}\n\n"
        f"{P} Enterprise MongoDB Storage\n"
        f"{P} Ultra-Fast Runtime Cache Layer\n"
        f"{P} Premium Emoji Entity Engine\n"
        f"{P} Smart Emoji Match (same emoji you type)\n"
        f"{P} Inline Mode + Make Post Wizard\n"
        f"{P} Scheduled Broadcast System\n"
        f"{P} Anti-Spam Protection Shield\n"
        f"{P} Referral, Coins and Daily Streaks\n\n"
        f"{P} {section_style('LIVE NUMBERS')}\n"
        f"{P} Users  : {cached_count('users', users)}\n"
        f"{P} Emojis : {cached_count('emojis', emojis_col, {'active': True})}\n"
        f"{P} Packs  : {cached_count('packs', packs, {'active': True})}\n"
        f"{P} Uptime : {fmt_uptime()}\n\n"
        f"{P} {section_style('DEVELOPER & SUPPORT')}\n"
        f"{P} Bot        : {BOT_NAME}\n"
        f"{P} Version    : {BOT_VERSION}\n"
        f"{P} Developer  : {DEVELOPER_NAME} ({DEVELOPER_USERNAME})\n"
        f"{P} Support    : {SUPPORT_USERNAME}\n"
        f"{premium_footer()}"
    )
    m = types.InlineKeyboardMarkup(row_width=1)
    url = _support_url()
    if url:
        m.add(i_btn("CONTACT SUPPORT", url=url, style="success", emoji_key="help"))
    _send_pe(message.chat.id, text, use_main=False, reply_markup=(m if m.keyboard else user_keyboard(message.from_user.id)))


@bot.message_handler(commands=["stats"])
@bot.message_handler(func=lambda m: m.text in ("STATS", "BOT STATS"))
def stats_msg(message):
    if not precheck(message):
        return
    text = (
        f"{premium_header('📈 BOT STATISTICS 📈')}\n\n"
        f"{P} Engine Status : {'ONLINE 🟢' if get_setting('bot', 'active', True) else 'OFFLINE 🔴'}\n"
        f"{P} Total Users   : {cached_count('users', users)}\n"
        f"{P} Premium IDs   : {cached_count('emojis', emojis_col, {'active': True})}\n"
        f"{P} Emoji Packs   : {cached_count('packs', packs, {'active': True})}\n"
        f"{P} Force Channels: {cached_count('channels', channels, {'active': True})}\n"
        f"{P} Server Time   : {now_local().strftime('%Y-%m-%d %H:%M')}\n"
        f"{premium_footer()}"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=user_keyboard(message.from_user.id))


def build_style_lab_view(uid):
    """Build the Style Lab text + inline keyboard. Shared by the menu entry and the
    live in-place refresh when a style is selected."""
    current = user_output_style(uid)
    m = types.InlineKeyboardMarkup(row_width=2)
    for key, label in STYLE_LABELS:
        mark = "✅ " if current == key else ""
        prefix = mark + ("ACTIVE  " if current == key else "USE  ")
        m.add(i_btn(prefix + label, f"user:style:{key}", "success" if current == key else "primary", "emoji"))
    m.add(i_btn("CLOSE", "user:close", "primary", "back"))

    # Live preview of EVERY style so the user can compare before choosing.
    word = "Gadget Pro"
    previews = []
    for key, label in STYLE_LABELS:
        sample = word if key == "normal" else style_text(word, key)
        tick = " ◄ active" if key == current else ""
        previews.append(f"{P} {label:11}: {sample}{tick}")
    preview_block = "\n".join(previews)

    text = (
        f"{premium_header('STYLE LAB')}\n\n"
        f"{P} {section_style('Text Look Engine')}\n"
        f"{P} Pick a font for your text conversions.\n"
        f"{P} Emojis always stay premium quality.\n\n"
        f"{P} {section_style('Live Preview')}\n"
        f"{preview_block}\n\n"
        f"{P} Current : {current.upper()}\n"
        f"{premium_footer()}"
    )
    return text, m


@bot.message_handler(commands=["stylelab"])
@bot.message_handler(func=lambda m: m.text == "STYLE LAB")
def style_lab(message):
    try:
        if not precheck(message):
            return
        text, m = build_style_lab_view(message.from_user.id)
        _send_pe(message.chat.id, text, use_main=False, reply_markup=m)
    except Exception:
        log_exc("style_lab")


@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda m: m.text == "SETTINGS")
def user_settings(message):
    if not precheck(message):
        return
    uid = message.from_user.id
    u = get_user(uid) or {}
    m = types.InlineKeyboardMarkup(row_width=1)
    for pdoc in get_active_packs(30):
        slug = pdoc.get("slug")
        label = ("SELECTED  " if u.get("preferred_pack") == slug else "PACK  ") + f"{pdoc.get('name', slug)} ({pdoc.get('emoji_count', 0)})"
        m.add(i_btn(label, f"user:setpack:{slug}", "success" if u.get("preferred_pack") == slug else "primary", "pack"))
    m.add(i_btn("AUTO SMART PACK ON" if u.get("auto_pack") else "AUTO SMART PACK OFF", "user:auto_pack", "success" if u.get("auto_pack") else "primary", "settings"))
    m.add(i_btn("OPEN STYLE LAB", "user:open_style", "success", "emoji"))
    text = (
        f"{premium_header('⚙ USER SETTINGS ⚙')}\n\n"
        f"{P} Current Pack : {get_user_pack_slug(uid)}\n"
        f"{P} Auto Pack    : {'ON' if u.get('auto_pack') else 'OFF'}\n"
        f"{P} Coins        : {u.get('coins', 0)}\n"
        f"{P} Streak       : {u.get('daily_streak', 0)} days\n\n"
        f"{P} Select a premium emoji pack below.\n"
        f"{premium_footer()}"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=m)


@bot.message_handler(commands=["vault", "mystats"])
@bot.message_handler(func=lambda m: m.text == "MY VAULT")
def my_vault(message):
    try:
        if not precheck(message):
            return
        uid = message.from_user.id
        u = get_user(uid) or {}
        rank = 1 + users.count_documents({"score": {"$gt": int(u.get("score", 0))}})
        code = u.get("referral_code") or make_ref_code(uid)
        users.update_one({"user_id": uid}, {"$set": {"referral_code": code}})
        link = f"https://t.me/{get_bot_username()}?start=ref_{code}"
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(i_btn("OPEN REFERRAL LINK", url=link, style="success", emoji_key="coin"))
        m.add(i_btn("STYLE LAB", "user:open_style", "primary", "emoji"), i_btn("CLOSE", "user:close", "primary", "back"))
        text = (
            f"{premium_header('MEMBER VAULT')}\n\n"
            f"{P} {section_style('Your Premium Profile')}\n"
            f"{P} User ID      : {uid}\n"
            f"{P} Rank         : #{rank}\n"
            f"{P} Score        : {u.get('score', 0)}\n"
            f"{P} Coins        : {u.get('coins', 0)}\n"
            f"{P} Streak       : {u.get('daily_streak', 0)} days\n"
            f"{P} Referrals    : {u.get('referrals', 0)}\n"
            f"{P} Conversions  : {u.get('conversions', 0)}\n\n"
            f"{P} {section_style('Referral Link')}\n{link}\n"
            f"{premium_footer()}"
        )
        _send_pe(message.chat.id, text, use_main=False, reply_markup=m)
    except Exception:
        log_exc("my_vault")


@bot.message_handler(commands=["templates"])
@bot.message_handler(func=lambda m: m.text == "TEMPLATES")
def premium_templates(message):
    try:
        if not precheck(message):
            return
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(i_btn("SALE POST", "tpl:sale", "success", "emoji"), i_btn("CHANNEL JOIN", "tpl:join", "primary", "channel_settings"))
        m.add(i_btn("GIVEAWAY", "tpl:giveaway", "success", "coin"), i_btn("VIP LAUNCH", "tpl:launch", "primary", "pack"))
        m.add(i_btn("CLOSE", "user:close", "primary", "back"))
        text = (
            f"{premium_header('SMART POST TEMPLATES')}\n\n"
            f"{P} {section_style('One Tap Premium Captions')}\n"
            f"{P} Choose a template below.\n"
            f"{P} The bot will generate a stylish caption with premium emoji entities.\n\n"
            f"{P} You can copy, edit, then use MAKE POST.\n"
            f"{premium_footer()}"
        )
        _send_pe(message.chat.id, text, use_main=False, reply_markup=m)
    except Exception:
        log_exc("premium_templates")


@bot.message_handler(commands=["referral"])
@bot.message_handler(func=lambda m: m.text == "REFERRAL")
def referral(message):
    if not precheck(message):
        return
    uid = message.from_user.id
    u = get_user(uid) or {}
    code = u.get("referral_code") or make_ref_code(uid)
    users.update_one({"user_id": uid}, {"$set": {"referral_code": code}})
    link = f"https://t.me/{get_bot_username()}?start=ref_{code}"
    g = get_setting("growth", default={}) or {}
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(i_btn("OPEN REFERRAL LINK", url=link, style="success", emoji_key="coin"))
    m.add(i_btn("CLOSE", "user:close", "primary", "back"))
    text = (
        f"{premium_header('💰 REFERRAL VAULT 💰')}\n\n"
        f"{P} Share your link with new users.\n"
        f"{P} When they start the bot, rewards are added automatically.\n\n"
        f"{P} Your Link:\n{link}\n\n"
        f"{P} Your Referrals : {u.get('referrals', 0)}\n"
        f"{P} Your Coins     : {u.get('coins', 0)}\n"
        f"{P} Invite Bonus   : {g.get('referral_bonus', 25)} coins\n"
        f"{P} New User Bonus : {g.get('referred_user_bonus', 10)} coins\n"
        f"{premium_footer()}"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=m)


@bot.message_handler(commands=["daily"])
@bot.message_handler(func=lambda m: m.text == "DAILY BONUS")
def daily_bonus(message):
    if not precheck(message):
        return
    uid = message.from_user.id
    u = get_user(uid) or {}
    today = now_local().date().isoformat()
    if u.get("last_daily_bonus") == today:
        text = (
            f"{premium_header('🎁 DAILY BONUS 🎁')}\n\n"
            f"{P} You already claimed today's reward.\n"
            f"{P} Come back tomorrow to continue your streak.\n\n"
            f"{P} Current Coins : {u.get('coins', 0)}\n"
            f"{P} Streak        : {u.get('daily_streak', 0)} days\n"
            f"{premium_footer()}"
        )
        _send_pe(message.chat.id, text, use_main=False, reply_markup=user_keyboard(uid))
        return
    yday = (now_local().date() - timedelta(days=1)).isoformat()
    streak = int(u.get("daily_streak", 0)) + 1 if u.get("last_daily_bonus") == yday else 1
    base = int((get_setting("growth", default={}) or {}).get("daily_bonus", 10))
    bonus = base + min(streak - 1, 10)
    users.update_one({"user_id": uid}, {"$set": {"last_daily_bonus": today, "daily_streak": streak}, "$inc": {"coins": bonus, "score": 2}})
    track_event("daily_bonus", uid, {"bonus": bonus, "streak": streak})
    new_total = int(u.get('coins', 0)) + bonus
    text = (
        f"{premium_header('🎁 DAILY BONUS UNLOCKED 🎁')}\n\n"
        f"{P} Reward Added : {bonus} coins\n"
        f"{P} Total Coins  : {new_total}\n"
        f"{P} Streak       : {streak} days\n\n"
        f"{P} Keep claiming daily to increase your bonus.\n"
        f"{premium_footer()}"
    )
    _send_pe(message.chat.id, text, use_main=False, reply_markup=user_keyboard(uid))


@bot.message_handler(commands=["admin"])
@bot.message_handler(func=lambda m: m.text == "ADMIN PANEL" and is_admin(m.from_user.id))
def admin_panel_cmd(message):
    if is_admin(message.from_user.id):
        register_user_from_message(message)
        send_admin_panel(message.chat.id)


@bot.message_handler(commands=["on"])
def bot_on(message):
    if is_admin(message.from_user.id):
        set_setting("bot", "active", True)
        _send_pe(message.chat.id, f"{P} BOT TURNED ON 🟢", use_main=False, reply_markup=admin_menu())


@bot.message_handler(commands=["off"])
def bot_off(message):
    if is_admin(message.from_user.id):
        set_setting("bot", "active", False)
        _send_pe(message.chat.id, f"{P} BOT TURNED OFF 🔴", use_main=False, reply_markup=admin_menu())


@bot.message_handler(func=lambda m: m.text == "USERS LIST" and is_admin(m.from_user.id))
def users_list(message):
    register_user_from_message(message)
    _send_pe(message.chat.id, users_overview_text(), use_main=False, reply_markup=users_overview_markup())


@bot.message_handler(func=lambda m: m.text == "MAKE POST")
def start_post(message):
    if not precheck(message):
        return
    uid = message.from_user.id
    if not charge_conversion(uid, "post_start"):
        _send_pe(message.chat.id, f"{P} Not enough coins. Use DAILY BONUS or REFERRAL.", use_main=False)
        return
    sent = _send_pe(message.chat.id, f"{premium_header('POST CREATOR')}\n\n{P} Send text, photo+caption, or document+caption now.\n{P} Every emoji will become premium style.\n{P} /cancel to stop.\n{premium_footer()}", use_main=False)
    if sent:
        bot.register_next_step_handler(sent, process_post_content)



def process_post_content(message):
    try:
        uid = message.from_user.id
        if message.text and message.text.strip() == "/cancel":
            cancel_step(message)
            return
        if not precheck(message):
            return
        if message.content_type not in ("text", "photo", "document"):
            sent = _send_pe(message.chat.id, f"{P} Only text, photo, or document supported. Send again:", use_main=False)
            if sent:
                bot.register_next_step_handler(sent, process_post_content)
            return
        original_text = message.text or message.caption or ""
        original_entities = message.entities or message.caption_entities or []
        pack_slug = smart_pack_for_text(original_text, uid) if user_auto_pack(uid) else get_user_pack_slug(uid)
        temp_data[uid] = {
            "original_text": original_text,
            "original_text_pristine": original_text,
            "ai_hook": None,
            "ai_emoji_add": "",
            "ai_sprinkle": False,
            "original_entities": original_entities,
            "photo_id": message.photo[-1].file_id if message.content_type == "photo" else None,
            "document_id": message.document.file_id if message.content_type == "document" else None,
            "doc_name": message.document.file_name if message.content_type == "document" else None,
            "processed_text": "",
            "processed_entities": [],
            "pack_slug": pack_slug,
            "emoji_mode": "auto",
            "manual_map": {},
            "original_custom_map": {},
            "preserve_original_custom": False,
            "btn_name": None,
            "btn_url": None,
            "btn_color": None,
            "btn_emoji_id": None,
            "preview_msg_id": None,
            "action_msg_id": None,
        }
        if has_unicode_emoji(original_text) or any(getattr(ent, "type", None) == "custom_emoji" for ent in (original_entities or [])):
            ask_emoji_mode(message.chat.id, uid)
        else:
            rebuild_post_conversion(uid)
            ask_add_button(message.chat.id, uid)
    except Exception:
        log_exc("process_post_content")



@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("wizard:"))
def wizard_callbacks(call):
    try:
        bot.answer_callback_query(call.id, "Working...")
        _, action, raw_uid = call.data.split(":", 2)
        uid = int(raw_uid)
        if call.from_user.id != uid and not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "This is not your session.", show_alert=True)
            return
        chat_id = call.message.chat.id
        msg_id = call.message.message_id
        if uid not in temp_data and action != "delete":
            _send_pe(chat_id, f"{P} Session expired.", use_main=False)
            return

        if action == "emojiauto":
            data = temp_data[uid]
            data["emoji_mode"] = "auto"
            data["manual_map"] = {}
            data["preserve_original_custom"] = False
            temp_data[uid] = data
            # Smart match ON: place the SAME premium emoji the user typed.
            rebuild_post_conversion(uid, randomize=False, allow_resolve=True)
            ask_add_button(chat_id, uid)
            return
        elif action == "emojikeep":
            data = temp_data[uid]
            data["emoji_mode"] = "keep"
            data["manual_map"] = {}
            data["preserve_original_custom"] = True
            temp_data[uid] = data
            rebuild_post_conversion(uid)
            ask_add_button(chat_id, uid)
            return
        elif action == "emojimanual":
            init_manual_emoji_selector(uid, keep_existing=True)
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action in ("epprevemoji", "epnextemoji"):
            data = temp_data[uid]
            items = data.get("emoji_items") or init_manual_emoji_selector(uid, keep_existing=True)
            if items:
                cur = int(data.get("emoji_pick_index", 0) or 0)
                data["emoji_pick_index"] = (cur + (-1 if action == "epprevemoji" else 1)) % len(items)
                temp_data[uid] = data
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action in ("epprevstyle", "epnextstyle"):
            change_manual_style(uid, -1 if action == "epprevstyle" else 1)
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action == "eprandomthis":
            change_manual_style(uid, random_this=True)
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action == "eprandomall":
            randomize_all_manual_styles(uid)
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action == "eporiginal":
            data = temp_data[uid]
            items = data.get("emoji_items") or []
            idx = int(data.get("emoji_pick_index", 0) or 0)
            if items:
                seq = items[idx]["emoji"]
                original_id = (data.get("original_custom_map") or {}).get(seq)
                if original_id:
                    data.setdefault("manual_map", {})[seq] = str(original_id)
                    data["emoji_mode"] = "manual"
                    temp_data[uid] = data
            show_emoji_picker(chat_id, uid, msg_id)
            return
        elif action == "epsave":
            data = temp_data[uid]
            data["emoji_mode"] = "manual"
            data["preserve_original_custom"] = True
            temp_data[uid] = data
            rebuild_post_conversion(uid)
            ask_add_button(chat_id, uid)
            return
        elif action == "epauto":
            data = temp_data[uid]
            data["emoji_mode"] = "auto"
            data["manual_map"] = {}
            data["preserve_original_custom"] = False
            temp_data[uid] = data
            rebuild_post_conversion(uid, randomize=False, allow_resolve=True)
            ask_add_button(chat_id, uid)
            return

        if action == "addbtn":
            ask_button_name(chat_id, uid)
        elif action == "skipbtn":
            ask_add_file(chat_id, uid)
        elif action.startswith("color"):
            colors = {"colorsuccess": "success", "colorprimary": "primary", "colordanger": "danger", "colornone": None}
            temp_data[uid]["btn_color"] = colors.get(action)
            ask_add_file(chat_id, uid)
        elif action == "addfile":
            sent = _send_pe(chat_id, f"{P} Send photo or document now.", use_main=False)
            if sent:
                bot.register_next_step_handler(sent, receive_file)
        elif action == "skipfile":
            send_preview_and_actions(chat_id, uid)
        elif action == "refresh":
            data = temp_data[uid]
            if data.get("emoji_mode") == "manual":
                # Manual mode protects the exact emojis chosen by the user.
                rebuild_post_conversion(uid)
            elif data.get("emoji_mode") == "keep":
                data["preserve_original_custom"] = True
                temp_data[uid] = data
                rebuild_post_conversion(uid)
            else:
                data["emoji_mode"] = "auto"
                data["manual_map"] = {}
                data["preserve_original_custom"] = False
                temp_data[uid] = data
                rebuild_post_conversion(uid, randomize=True)
            send_preview_and_actions(chat_id, uid)
        elif action == "aistudio":
            send_ai_studio(chat_id, uid)
        elif action == "aiemoji":
            data = temp_data[uid]
            base = data.get("original_text_pristine") or data.get("original_text") or ""
            data["ai_emoji_add"] = " ".join(ai_emoji_suggestions(base, limit=5))
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "Smart emojis added.")
            send_preview_and_actions(chat_id, uid)
        elif action == "aihook":
            data = temp_data[uid]
            base = data.get("original_text_pristine") or data.get("original_text") or ""
            data["ai_hook"] = ai_generate_hook(base, seed_shift=int(data.get("ai_seed", 0) or 0))
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "Hook line added.")
            send_preview_and_actions(chat_id, uid)
        elif action == "aisprinkle":
            data = temp_data[uid]
            data["ai_sprinkle"] = not bool(data.get("ai_sprinkle"))
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "Inline sprinkle toggled.")
            send_preview_and_actions(chat_id, uid)
        elif action == "aiboost":
            data = temp_data[uid]
            base = data.get("original_text_pristine") or data.get("original_text") or ""
            data["ai_hook"] = ai_generate_hook(base, seed_shift=int(data.get("ai_seed", 0) or 0))
            data["ai_emoji_add"] = " ".join(ai_emoji_suggestions(base, limit=6))
            data["ai_sprinkle"] = True
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "Max boost applied!")
            send_preview_and_actions(chat_id, uid)
        elif action == "airegen":
            data = temp_data[uid]
            data["ai_seed"] = int(data.get("ai_seed", 0) or 0) + 1
            base = data.get("original_text_pristine") or data.get("original_text") or ""
            if data.get("ai_hook"):
                data["ai_hook"] = ai_generate_hook(base, seed_shift=data["ai_seed"])
            if data.get("ai_emoji_add"):
                data["ai_emoji_add"] = " ".join(ai_emoji_suggestions(base, limit=5))
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "Regenerated.")
            send_preview_and_actions(chat_id, uid)
        elif action == "aiclear":
            data = temp_data[uid]
            data["ai_hook"] = None
            data["ai_emoji_add"] = ""
            data["ai_sprinkle"] = False
            temp_data[uid] = data
            ai_compose(uid)
            bot.answer_callback_query(call.id, "AI add-ons cleared.")
            send_preview_and_actions(chat_id, uid)
        elif action == "aiback":
            send_preview_and_actions(chat_id, uid)
        elif action == "delete":
            data = temp_data.pop(uid, {})
            for mid in (data.get("preview_msg_id"), data.get("action_msg_id")):
                if mid:
                    try:
                        bot.delete_message(chat_id, mid)
                    except Exception:
                        pass
            _send_pe(chat_id, f"{P} Post deleted.", use_main=False, reply_markup=user_keyboard(uid))
        elif action == "done":
            data = temp_data.pop(uid, {})
            inc_user(uid, "post_conversions", 1)
            inc_user(uid, "conversions", 1)
            inc_user(uid, "score", 1)
            track_event("post_done", uid, {"pack_slug": data.get("pack_slug"), "emoji_mode": data.get("emoji_mode")})
            track_event("conversion", uid, {"source": "make_post"})
            _send_pe(chat_id, f"{P} Done! Your premium emoji post is ready.", use_main=False, reply_markup=user_keyboard(uid))
    except Exception:
        log_exc("wizard_callbacks")


@bot.message_handler(commands=["cancel"])
def cancel_step(message):
    temp_data.pop(message.from_user.id, None)
    _send_pe(message.chat.id, f"{P} Cancelled successfully.", use_main=False, reply_markup=user_keyboard(message.from_user.id))

# ======================== ADMIN CALLBACKS + STEP HANDLERS ========================
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("tpl:"))
def template_callbacks(call):
    try:
        uid = call.from_user.id
        key = call.data.split(":", 1)[1]
        samples = {
            "sale": "LIMITED TIME OFFER 🔥\n\nPremium deal is live now ⚡\nGrab yours before stock ends 💎\n\nTap the button below and order now 🚀",
            "join": "JOIN OUR PREMIUM CHANNEL 🚀\n\nDaily updates, exclusive resources and VIP drops are waiting for you 💎\n\nBe part of the community today ✨",
            "giveaway": "MEGA GIVEAWAY ALERT 🎁\n\nComplete the steps and join the reward pool 🏆\nInvite friends for extra chance 💎\n\nWinners will be announced soon ⚡",
            "launch": "VIP LAUNCH IS LIVE 👑\n\nA new premium experience is ready for you 🚀\nFast, beautiful and powerful updates are inside 💎\n\nTry it now ✨",
        }
        raw = samples.get(key, samples["sale"])
        style = user_output_style(uid)
        styled = style_text(raw, style if style != "normal" else "bold")
        final_text, ents = process_text_with_duplicate_emojis(styled, [], get_user_pack_slug(uid))
        bot.answer_callback_query(call.id, "Template ready")
        bot.send_message(call.message.chat.id, final_text, entities=ents, parse_mode=None)
    except Exception:
        log_exc("template_callbacks")


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin:"))
def admin_callbacks(call):
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Admin only.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "Opening...")
        data = call.data
        chat_id, msg_id, uid = call.message.chat.id, call.message.message_id, call.from_user.id
        if data == "admin:home":
            send_admin_panel(chat_id, msg_id)
        elif data == "admin:health":
            try:
                _t0 = time.time()
                client.admin.command("ping")
                mongo_status = f"OK ({int((time.time() - _t0) * 1000)}ms)"
            except Exception:
                mongo_status = "ERROR"
            health_text = (
                f"{premium_header('LIVE STATUS')}\n\n"
                f"{P} Bot      : @{get_bot_username()}\n"
                f"{P} MongoDB  : {mongo_status}\n"
                f"{P} Uptime   : {fmt_uptime()}\n"
                f"{P} Updates  : {runtime_metrics.get('updates', 0)}\n"
                f"{P} Convert  : {runtime_metrics.get('conversions', 0)}\n"
                f"{P} Errors   : {runtime_metrics.get('errors', 0)}\n"
                f"{P} Scheduler: {'RUNNING' if scheduler.running else 'STOPPED'}\n"
                f"{P} Time     : {now_local().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{premium_footer()}"
            )
            m = types.InlineKeyboardMarkup(row_width=2)
            m.add(i_btn("Refresh", "admin:health", "success", "stats"), i_btn("BACK", "admin:home", "primary", "back"))
            _edit_pe(chat_id, msg_id, health_text, use_main=False, reply_markup=m)
        elif data == "admin:support":
            _edit_pe(chat_id, msg_id, support_overview_text(), use_main=False, reply_markup=support_overview_markup())
        elif data == "admin:analytics":
            _edit_pe(chat_id, msg_id, analytics_text(), use_main=False, reply_markup=back_markup())
        elif data == "admin:packs":
            _edit_pe(chat_id, msg_id, f"{P} EMOJI PACKS\n\n{P} Manage packs, emoji IDs, and bulk .txt imports.", use_main=False, reply_markup=packs_markup())
        elif data == "admin:pack_create":
            sent = _send_pe(chat_id, f"{P} Send: slug | Pack Name | description | keyword1,keyword2", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_pack_create)
        elif data.startswith("admin:pack_view:"):
            slug = data.split(":", 2)[2]
            pdoc = packs.find_one({"slug": slug})
            m = types.InlineKeyboardMarkup(row_width=2)
            m.add(i_btn("✅ Set Default", f"admin:pack_default:{slug}", "success", "success"), i_btn("📥 Import Here", f"admin:emoji_bulk_pack:{slug}", "primary", "emoji"))
            if slug != "default":
                m.add(i_btn("🗑 Delete Pack", f"admin:pack_delete:{slug}", "danger", "danger"))
            m.add(i_btn("BACK", "admin:packs", "primary", "back"))
            _edit_pe(chat_id, msg_id, f"{P} PACK DETAILS\n\n{P} Slug: {slug}\n{P} Name: {pdoc.get('name') if pdoc else slug}\n{P} Count: {refresh_pack_count(slug)}", use_main=False, reply_markup=m)
        elif data.startswith("admin:pack_default:"):
            slug = data.split(":", 2)[2]
            packs.update_many({}, {"$set": {"is_default": False}})
            packs.update_one({"slug": slug}, {"$set": {"is_default": True}})
            set_setting("bot", "default_pack_slug", slug)
            invalidate_emoji_cache()
            _edit_pe(chat_id, msg_id, f"{P} Default pack set: {slug}", use_main=False, reply_markup=packs_markup())
        elif data.startswith("admin:pack_delete:"):
            slug = data.split(":", 2)[2]
            if slug != "default":
                packs.update_one({"slug": slug}, {"$set": {"active": False, "deleted_at": now_utc()}})
                emojis_col.update_many({"pack_slug": slug}, {"$set": {"active": False}})
                users.update_many({"preferred_pack": slug}, {"$set": {"preferred_pack": get_default_pack_slug()}})
                invalidate_emoji_cache()
            _edit_pe(chat_id, msg_id, f"{P} Pack deleted.", use_main=False, reply_markup=packs_markup())
        elif data == "admin:emoji_add":
            sent = _send_pe(chat_id, f"{P} Send: pack_slug | emoji_id\nOr only emoji_id for default pack.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_emoji_add)
        elif data == "admin:emoji_remove":
            sent = _send_pe(chat_id, f"{P} Send emoji_id, or pack_slug | emoji_id.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_emoji_remove)
        elif data == "admin:emoji_bulk":
            temp_data[f"bulk_pack_{uid}"] = get_default_pack_slug()
            sent = _send_pe(chat_id, f"{P} Send/forward .txt file with emoji IDs. Target: {get_default_pack_slug()}", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_bulk_txt)
        elif data.startswith("admin:emoji_bulk_pack:"):
            slug = data.split(":", 2)[2]
            temp_data[f"bulk_pack_{uid}"] = slug
            sent = _send_pe(chat_id, f"{P} Send/forward .txt file with emoji IDs. Target: {slug}", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_bulk_txt)
        elif data == "admin:collector":
            _edit_pe(chat_id, msg_id, forwarded_collector_help_text(), use_main=False, reply_markup=collector_admin_markup())
        elif data == "admin:export_pack":
            sent = _send_pe(chat_id, f"{P} Send pack slug to export. Example: default", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_export_pack)
        elif data == "admin:export_backup":
            export_all_emoji_backup(chat_id, uid)
        elif data == "admin:channels":
            _edit_pe(chat_id, msg_id, f"{P} CHANNEL MANAGEMENT\n\n{P} Force Join: {'ON' if get_setting('bot', 'force_join_enabled', True) else 'OFF'}", use_main=False, reply_markup=channels_markup())
        elif data == "admin:channel_add":
            sent = _send_pe(chat_id, f"{P} Send: CHANNEL_ID | CHANNEL_NAME | CHANNEL_LINK", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_channel_add)
        elif data.startswith("admin:channel_remove:"):
            cid = data.split(":", 2)[2]
            channel_cache["expires"] = 0
            join_cache.clear()
            channels.update_one({"channel_id": cid}, {"$set": {"active": False, "deleted_at": now_utc()}})
            _edit_pe(chat_id, msg_id, f"{P} Channel removed.", use_main=False, reply_markup=channels_markup())
        elif data == "admin:force_toggle":
            set_setting("bot", "force_join_enabled", not get_setting("bot", "force_join_enabled", True))
            _edit_pe(chat_id, msg_id, f"{P} Force Join updated.", use_main=False, reply_markup=channels_markup())
        elif data == "admin:admins":
            _edit_pe(chat_id, msg_id, f"{P} ADMIN MANAGEMENT", use_main=False, reply_markup=admins_markup())
        elif data == "admin:add_admin":
            if not is_owner(uid):
                bot.answer_callback_query(call.id, "Owner only.", show_alert=True); return
            sent = _send_pe(chat_id, f"{P} Send Telegram User ID to add admin.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_add_admin)
        elif data.startswith("admin:remove_admin:"):
            if not is_owner(uid): return
            rid = int(data.split(":")[-1])
            if rid != MASTER_ADMIN_ID:
                admin_cache["expires"] = 0
            admins.update_one({"user_id": rid}, {"$set": {"active": False, "removed_at": now_utc()}})
            _edit_pe(chat_id, msg_id, f"{P} Admin removed.", use_main=False, reply_markup=admins_markup())
        elif data == "admin:list_admins":
            lines = [f"{'👑 OWNER' if a.get('is_master') else '⭐ ADMIN'} • {a.get('user_id')}" for a in admins.find({"active": True})]
            _edit_pe(chat_id, msg_id, f"{P} ADMIN LIST\n\n" + "\n".join(lines), use_main=False, reply_markup=admins_markup())
        elif data == "admin:spam":
            s = get_setting("spam", default={}) or {}
            _edit_pe(chat_id, msg_id, f"{P} ANTI SPAM\n\n{P} Enabled: {s.get('enabled')}\n{P} Max Actions: {s.get('max_actions')}\n{P} Window: {s.get('window_seconds')} sec\n{P} Mute: {s.get('mute_minutes')} min\n{P} Ban After: {s.get('ban_after_violations')}\n{P} Ban Minutes: {s.get('ban_minutes')}", use_main=False, reply_markup=spam_markup())
        elif data == "admin:spam_toggle":
            set_setting("spam", "enabled", not get_setting("spam", "enabled", True))
            _edit_pe(chat_id, msg_id, f"{P} Anti-spam toggled.", use_main=False, reply_markup=spam_markup())
        elif data == "admin:spam_set":
            sent = _send_pe(chat_id, f"{P} Send: max_actions | window_seconds | mute_minutes | ban_after | ban_minutes", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_spam_set)
        elif data == "admin:spam_reset_user":
            sent = _send_pe(chat_id, f"{P} Send user ID to reset spam.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_spam_reset)
        elif data == "admin:growth":
            g = get_setting("growth", default={}) or {}
            _edit_pe(chat_id, msg_id, f"{P} GROWTH & COINS\n\n{P} Coins: {g.get('coins_enabled')}\n{P} Start: {g.get('starting_coins')}\n{P} Cost: {g.get('conversion_cost')}\n{P} Daily: {g.get('daily_bonus')}\n{P} Referral: {g.get('referral_bonus')}", use_main=False, reply_markup=growth_markup())
        elif data == "admin:coins_toggle":
            set_setting("growth", "coins_enabled", not get_setting("growth", "coins_enabled", True))
            _edit_pe(chat_id, msg_id, f"{P} Coins toggled.", use_main=False, reply_markup=growth_markup())
        elif data == "admin:leaderboard_toggle":
            set_setting("growth", "leaderboard_enabled", not get_setting("growth", "leaderboard_enabled", True))
            _edit_pe(chat_id, msg_id, f"{P} Leaderboard toggled.", use_main=False, reply_markup=growth_markup())
        elif data == "admin:growth_set":
            sent = _send_pe(chat_id, f"{P} Send: starting_coins | conversion_cost | daily_bonus | referral_bonus | referred_user_bonus", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_growth_set)
        elif data == "admin:top_users":
            lines = []
            for u in users.find({}, {"user_id": 1, "username": 1, "score": 1, "coins": 1}).sort("score", DESCENDING).limit(10):
                lines.append(f"🏆 @{u.get('username') or u.get('user_id')} • score {u.get('score', 0)} • coins {u.get('coins', 0)}")
            _edit_pe(chat_id, msg_id, f"{P} TOP USERS\n\n" + ("\n".join(lines) or "No users yet."), use_main=False, reply_markup=growth_markup())
        elif data == "admin:settings":
            _edit_pe(chat_id, msg_id, f"{P} BOT SETTINGS\n\n{P} Status: {'ONLINE' if get_setting('bot', 'active', True) else 'OFFLINE'}\n{P} Inline: {get_setting('bot', 'inline_mode_enabled', True)}\n{P} Direct: {get_setting('bot', 'direct_convert_enabled', True)}", use_main=False, reply_markup=settings_markup())
        elif data == "admin:bot_toggle":
            set_setting("bot", "active", not get_setting("bot", "active", True)); send_admin_panel(chat_id, msg_id)
        elif data == "admin:inline_toggle":
            set_setting("bot", "inline_mode_enabled", not get_setting("bot", "inline_mode_enabled", True)); _edit_pe(chat_id, msg_id, f"{P} Inline updated.", use_main=False, reply_markup=settings_markup())
        elif data == "admin:direct_toggle":
            set_setting("bot", "direct_convert_enabled", not get_setting("bot", "direct_convert_enabled", True)); _edit_pe(chat_id, msg_id, f"{P} Direct convert updated.", use_main=False, reply_markup=settings_markup())
        elif data == "admin:set_welcome":
            sent = _send_pe(chat_id, f"{P} Send new welcome title.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_welcome)
        elif data == "admin:broadcasts":
            m = types.InlineKeyboardMarkup(row_width=2)
            m.add(i_btn("📢 Send Now", "admin:broadcast_now", "success", "broadcast"), i_btn("⏰ Schedule", "admin:broadcast_schedule", "primary", "broadcast"))
            for b in broadcasts.find({"status": "scheduled"}).sort("scheduled_at", ASCENDING).limit(10):
                bid = str(b["_id"])
                m.add(i_btn(f"⏰ {fmt_dt(b.get('scheduled_at'))}", "admin:broadcasts", "primary", "broadcast"), i_btn("Cancel", f"admin:broadcast_cancel:{bid}", "danger", "danger"))
            m.add(i_btn("BACK", "admin:home", "primary", "back"))
            _edit_pe(chat_id, msg_id, f"{P} BROADCASTS\n\n{P} Scheduled: {broadcasts.count_documents({'status': 'scheduled'})}", use_main=False, reply_markup=m)
        elif data == "admin:broadcast_now":
            sent = _send_pe(chat_id, f"{P} Send any message to broadcast now.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_broadcast_now)
        elif data == "admin:broadcast_schedule":
            sent = _send_pe(chat_id, f"{P} Send message to schedule.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_schedule_message)
        elif data.startswith("admin:broadcast_cancel:"):
            bid = data.split(":")[-1]
            try: scheduler.remove_job(f"broadcast_{bid}")
            except Exception: pass
            broadcasts.update_one({"_id": ObjectId(bid)}, {"$set": {"status": "cancelled", "cancelled_at": now_utc()}})
            _edit_pe(chat_id, msg_id, f"{P} Broadcast cancelled.", use_main=False, reply_markup=back_markup("admin:broadcasts"))
        elif data == "admin:users":
            _edit_pe(chat_id, msg_id, users_overview_text(), use_main=False, reply_markup=users_overview_markup())
        elif data == "admin:user_search":
            sent = _send_pe(chat_id, f"{P} Send a Telegram User ID or @username to manage.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_user_search)
        elif data.startswith("admin:users_recent:"):
            skip = safe_int(data.split(":")[-1], 0)
            _edit_pe(chat_id, msg_id, f"{P} {section_style('RECENT USERS')}\n\n{P} Tap a user to open their profile.", use_main=False, reply_markup=users_list_markup(skip, only_banned=False))
        elif data.startswith("admin:users_banned:"):
            skip = safe_int(data.split(":")[-1], 0)
            _edit_pe(chat_id, msg_id, f"{P} {section_style('BANNED USERS')}\n\n{P} Tap a user to review or unban.", use_main=False, reply_markup=users_list_markup(skip, only_banned=True))
        elif data.startswith("admin:user_view:"):
            tuid = safe_int(data.split(":")[-1], 0)
            _edit_pe(chat_id, msg_id, user_detail_text(get_user(tuid)), use_main=False, reply_markup=user_detail_markup(tuid))
        elif data.startswith("admin:user_ban:"):
            tuid = safe_int(data.split(":")[-1], 0)
            if tuid == MASTER_ADMIN_ID or is_admin(tuid):
                bot.answer_callback_query(call.id, "You cannot ban an admin.", show_alert=True)
            else:
                users.update_one({"user_id": tuid}, {"$set": {"banned": True, "banned_at": now_utc(), "banned_by": uid}})
                count_cache["expires"] = 0
                track_event("user_banned", uid, {"target": tuid})
                _edit_pe(chat_id, msg_id, user_detail_text(get_user(tuid)), use_main=False, reply_markup=user_detail_markup(tuid))
        elif data.startswith("admin:user_unban:"):
            tuid = safe_int(data.split(":")[-1], 0)
            users.update_one({"user_id": tuid}, {"$set": {"banned": False, "unbanned_at": now_utc(), "unbanned_by": uid}})
            count_cache["expires"] = 0
            track_event("user_unbanned", uid, {"target": tuid})
            _edit_pe(chat_id, msg_id, user_detail_text(get_user(tuid)), use_main=False, reply_markup=user_detail_markup(tuid))
        elif data.startswith("admin:user_resetspam:"):
            tuid = safe_int(data.split(":")[-1], 0)
            users.update_one({"user_id": tuid}, {"$set": {"spam.violations": 0, "spam.muted_until": None, "spam.banned_until": None}})
            rate_memory.pop(tuid, None)
            bot.answer_callback_query(call.id, "Spam status reset.")
            _edit_pe(chat_id, msg_id, user_detail_text(get_user(tuid)), use_main=False, reply_markup=user_detail_markup(tuid))
        elif data.startswith("admin:user_addcoins:") or data.startswith("admin:user_subcoins:"):
            tuid = safe_int(data.split(":")[-1], 0)
            sign = "add" if "addcoins" in data else "sub"
            temp_data[f"coins_target_{uid}"] = tuid
            temp_data[f"coins_sign_{uid}"] = sign
            verb = "add to" if sign == "add" else "remove from"
            sent = _send_pe(chat_id, f"{P} Send the number of coins to {verb} user {tuid}.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_user_coins)
        elif data.startswith("admin:user_dm:"):
            tuid = safe_int(data.split(":")[-1], 0)
            temp_data[f"dm_target_{uid}"] = tuid
            sent = _send_pe(chat_id, f"{P} Send the message to deliver to user {tuid}.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_user_dm)
    except Exception:
        log_exc("admin_callbacks")


def admin_receive_pack_create(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        parts = [x.strip() for x in (message.text or "").split("|")]
        if len(parts) < 2:
            sent = _send_pe(message.chat.id, f"{P} Invalid. Send: slug | name | description | keywords", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_pack_create)
            return
        slug = re.sub(r"[^a-z0-9_\-]", "", parts[0].lower().replace(" ", "_"))[:32]
        name = parts[1][:64]
        desc = parts[2][:200] if len(parts) > 2 else ""
        keywords = [x.strip().lower() for x in parts[3].split(",")] if len(parts) > 3 else []
        packs.update_one({"slug": slug}, {"$set": {"name": name, "description": desc, "keywords": keywords, "active": True, "is_default": False, "updated_at": now_utc()}, "$setOnInsert": {"slug": slug, "created_by": message.from_user.id, "created_at": now_utc()}}, upsert=True)
        refresh_pack_count(slug)
        _send_pe(message.chat.id, f"{P} Pack saved: {name} ({slug})", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_pack_create")


def admin_receive_user_search(message):
    try:
        if not is_admin(message.from_user.id):
            return
        if message.text and message.text.strip() == "/cancel":
            return cancel_step(message)
        u = find_user_doc(message.text)
        if not u:
            sent = _send_pe(message.chat.id, f"{P} No user found. Send a valid User ID or @username, or /cancel.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_user_search)
            return
        _send_pe(message.chat.id, user_detail_text(u), use_main=False, reply_markup=user_detail_markup(u.get("user_id")))
    except Exception:
        log_exc("admin_receive_user_search")


def admin_receive_user_coins(message):
    try:
        uid = message.from_user.id
        if not is_admin(uid):
            return
        if message.text and message.text.strip() == "/cancel":
            return cancel_step(message)
        target = temp_data.pop(f"coins_target_{uid}", None)
        sign = temp_data.pop(f"coins_sign_{uid}", "add")
        if not target:
            return
        amount = safe_int((message.text or "").strip(), 0)
        if amount <= 0:
            sent = _send_pe(message.chat.id, f"{P} Send a positive number, or /cancel.", use_main=False)
            if sent:
                temp_data[f"coins_target_{uid}"] = target
                temp_data[f"coins_sign_{uid}"] = sign
                bot.register_next_step_handler(sent, admin_receive_user_coins)
            return
        delta = amount if sign == "add" else -amount
        users.update_one({"user_id": int(target)}, {"$inc": {"coins": delta}})
        track_event("admin_coins_adjust", uid, {"target": target, "delta": delta})
        new_u = get_user(target) or {}
        verb = "added to" if delta > 0 else "removed from"
        _send_pe(message.chat.id, f"{P} {abs(delta)} coins {verb} user {target}.\n{P} New balance: {new_u.get('coins', 0)}", use_main=False)
        _send_pe(message.chat.id, user_detail_text(new_u), use_main=False, reply_markup=user_detail_markup(target))
        try:
            if delta > 0:
                _send_pe(int(target), f"{P} You received {delta} bonus coins from the team.", use_main=False)
        except Exception:
            pass
    except Exception:
        log_exc("admin_receive_user_coins")


def admin_receive_user_dm(message):
    try:
        uid = message.from_user.id
        if not is_admin(uid):
            return
        if message.text and message.text.strip() == "/cancel":
            return cancel_step(message)
        target = temp_data.pop(f"dm_target_{uid}", None)
        if not target:
            return
        try:
            bot.copy_message(int(target), message.chat.id, message.message_id)
            _send_pe(message.chat.id, f"{P} Message delivered to user {target}.", use_main=False, reply_markup=admin_menu())
            track_event("admin_dm", uid, {"target": target})
        except Exception as e:
            _send_pe(message.chat.id, f"{P} Could not deliver. The user may have blocked the bot.\n{P} ({str(e)[:80]})", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_user_dm")


def admin_receive_emoji_add(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        parts = [x.strip() for x in (message.text or "").split("|")]
        pack_slug, eid = (get_default_pack_slug(), parts[0]) if len(parts) == 1 else (parts[0], parts[1])
        if not valid_emoji_id(eid):
            sent = _send_pe(message.chat.id, f"{P} Invalid emoji ID. Try again:", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_emoji_add)
            return
        res = bulk_import_emoji_ids([eid], pack_slug, message.from_user.id, "manual")
        _send_pe(message.chat.id, f"{P} Emoji added.\nPack: {pack_slug}\nInserted: {res.get('inserted')}\nPack Total: {res.get('pack_count')}", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_emoji_add")


def admin_receive_emoji_remove(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        parts = [x.strip() for x in (message.text or "").split("|")]
        if len(parts) == 1:
            emojis_col.update_many({"emoji_id": parts[0]}, {"$set": {"active": False, "deleted_at": now_utc()}})
            for pdoc in packs.find({"active": True}): refresh_pack_count(pdoc.get("slug"))
        else:
            emojis_col.update_many({"pack_slug": parts[0], "emoji_id": parts[1]}, {"$set": {"active": False, "deleted_at": now_utc()}})
            refresh_pack_count(parts[0])
        invalidate_emoji_cache()
        _send_pe(message.chat.id, f"{P} Emoji removed/deactivated.", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_emoji_remove")


def admin_receive_bulk_txt(message):
    try:
        uid = message.from_user.id
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        if message.content_type != "document" or not message.document:
            sent = _send_pe(message.chat.id, f"{P} Please send a .txt document.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_bulk_txt)
            return
        if not (message.document.file_name or "").lower().endswith(".txt"):
            sent = _send_pe(message.chat.id, f"{P} Only .txt files accepted.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_bulk_txt)
            return
        pack_slug = temp_data.pop(f"bulk_pack_{uid}", get_default_pack_slug())
        status = _send_pe(message.chat.id, f"{P} Starting premium emoji import...", use_main=False)
        def cb(stage, done, total, force=False):
            edit_loading(status, "PREMIUM TXT IMPORT", stage, done, total, force)
        cb("Downloading TXT file", 5, 100, True)
        file_info = bot.get_file(message.document.file_id)
        raw = bot.download_file(file_info.file_path)
        cb("Reading TXT file", 12, 100, True)
        content = raw.decode("utf-8", errors="ignore")
        cb("Extracting premium emoji IDs", 18, 100, True)
        ids = extract_emoji_ids(content)
        res = bulk_import_emoji_ids(ids, pack_slug, uid, "txt_import", progress_callback=cb)
        final_text = (
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n"
            f"{P}      BULK IMPORT DONE      {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} Target Pack : {pack_slug}\n"
            f"{P} Found IDs    : {res.get('found')}\n"
            f"{P} Inserted     : {res.get('inserted')}\n"
            f"{P} Duplicates   : {res.get('duplicates')}\n"
            f"{P} Pack Total   : {res.get('pack_count')}\n\n"
            f"{P} Cache refreshed. New emojis are live now.\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}"
        )
        if status:
            _edit_pe(message.chat.id, status.message_id, final_text, use_main=False, reply_markup=admin_home_markup())
        else:
            _send_pe(message.chat.id, final_text, use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_bulk_txt")

def admin_receive_channel_add(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        parts = [x.strip() for x in (message.text or "").split("|")]
        if len(parts) != 3 or not parts[2].startswith(("https://t.me/", "http://t.me/", "tg://")):
            sent = _send_pe(message.chat.id, f"{P} Invalid. Use: CHANNEL_ID | NAME | LINK", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_channel_add)
            return
        cid, name, link = parts
        channel_cache["expires"] = 0
        join_cache.clear()
        channels.update_one({"channel_id": cid}, {"$set": {"name": name, "link": link, "active": True, "updated_at": now_utc()}, "$setOnInsert": {"channel_id": cid, "created_by": message.from_user.id, "created_at": now_utc()}}, upsert=True)
        _send_pe(message.chat.id, f"{P} Channel added: {name}", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_channel_add")


def admin_receive_add_admin(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        if not is_owner(message.from_user.id): return
        new_id = int((message.text or "").strip())
        if new_id == MASTER_ADMIN_ID:
            _send_pe(message.chat.id, f"{P} Master admin already exists.", use_main=False); return
        admin_cache["expires"] = 0
        admins.update_one({"user_id": new_id}, {"$set": {"role": "admin", "active": True, "is_master": False, "updated_at": now_utc()}, "$setOnInsert": {"user_id": new_id, "created_by": message.from_user.id, "created_at": now_utc()}}, upsert=True)
        _send_pe(message.chat.id, f"{P} Admin added: {new_id}", use_main=False, reply_markup=admin_menu())
    except Exception:
        _send_pe(message.chat.id, f"{P} Invalid user ID.", use_main=False)


def admin_receive_spam_set(message):
    try:
        parts = [safe_int(x.strip(), None) for x in (message.text or "").split("|")]
        if len(parts) != 5 or any(x is None for x in parts):
            sent = _send_pe(message.chat.id, f"{P} Invalid. Example: 8 | 10 | 3 | 5 | 60", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_spam_set)
            return
        set_settings_bulk("spam", {"max_actions": parts[0], "window_seconds": parts[1], "mute_minutes": parts[2], "ban_after_violations": parts[3], "ban_minutes": parts[4]})
        _send_pe(message.chat.id, f"{P} Anti-spam limits updated.", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_spam_set")


def admin_receive_spam_reset(message):
    try:
        target = int((message.text or "").strip())
        users.update_one({"user_id": target}, {"$set": {"spam": {"violations": 0, "muted_until": None, "banned_until": None}}})
        _send_pe(message.chat.id, f"{P} Spam reset for {target}.", use_main=False, reply_markup=admin_menu())
    except Exception:
        _send_pe(message.chat.id, f"{P} Invalid user ID.", use_main=False)


def admin_receive_growth_set(message):
    try:
        parts = [safe_int(x.strip(), None) for x in (message.text or "").split("|")]
        if len(parts) != 5 or any(x is None for x in parts):
            sent = _send_pe(message.chat.id, f"{P} Invalid. Example: 20 | 0 | 10 | 25 | 10", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_receive_growth_set)
            return
        set_settings_bulk("growth", {"starting_coins": parts[0], "conversion_cost": parts[1], "daily_bonus": parts[2], "referral_bonus": parts[3], "referred_user_bonus": parts[4]})
        _send_pe(message.chat.id, f"{P} Growth settings updated.", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_growth_set")


def admin_receive_welcome(message):
    title = (message.text or "").strip()[:120]
    if title:
        set_setting("bot", "welcome_title", title)
    _send_pe(message.chat.id, f"{P} Welcome title updated.", use_main=False, reply_markup=admin_menu())


def admin_receive_broadcast_now(message):
    if message.text and message.text.strip() == "/cancel": return cancel_step(message)
    if not is_admin(message.from_user.id): return
    _send_pe(message.chat.id, f"{P} Broadcasting started...", use_main=False)
    broadcast_to_all(message.chat.id, message.message_id, message.from_user.id)


def admin_receive_schedule_message(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        temp_data[f"schedule_msg_{message.from_user.id}"] = {"chat_id": message.chat.id, "message_id": message.message_id}
        sent = _send_pe(message.chat.id, f"{P} Send schedule time in Asia/Dhaka:\nYYYY-MM-DD HH:MM\nOr relative: +10m / +2h", use_main=False)
        if sent: bot.register_next_step_handler(sent, admin_receive_schedule_time)
    except Exception:
        log_exc("admin_receive_schedule_message")


def admin_receive_schedule_time(message):
    try:
        if message.text and message.text.strip() == "/cancel": return cancel_step(message)
        source = temp_data.pop(f"schedule_msg_{message.from_user.id}", None)
        run_at = parse_schedule_time(message.text)
        if not source or not run_at:
            sent = _send_pe(message.chat.id, f"{P} Invalid time. Try again.", use_main=False)
            if source:
                temp_data[f"schedule_msg_{message.from_user.id}"] = source
                if sent: bot.register_next_step_handler(sent, admin_receive_schedule_time)
            return
        doc = {"status": "scheduled", "from_chat_id": source["chat_id"], "message_id": source["message_id"], "scheduled_at": run_at, "created_by": message.from_user.id, "created_at": now_utc()}
        res = broadcasts.insert_one(doc)
        doc["_id"] = res.inserted_id
        schedule_broadcast_doc(doc)
        _send_pe(message.chat.id, f"{P} Broadcast scheduled for {fmt_dt(run_at)}.", use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_receive_schedule_time")


@bot.message_handler(commands=["collector", "emojicollector"])
@bot.message_handler(func=lambda m: m.text == "EMOJI COLLECTOR" and is_admin(m.from_user.id))
def emoji_collector_button(message):
    try:
        if not precheck(message, require_join=False):
            return
        _send_pe(message.chat.id, forwarded_collector_help_text(), use_main=False, reply_markup=collector_admin_markup())
    except Exception:
        log_exc("emoji_collector_button")


@bot.message_handler(commands=["exportemojis"])
@bot.message_handler(func=lambda m: m.text == "EXPORT EMOJIS" and is_admin(m.from_user.id))
def export_emojis_button(message):
    try:
        if not precheck(message, require_join=False):
            return
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) > 1 and parts[0].startswith("/"):
            export_pack_as_txt(message.chat.id, parts[1].strip(), message.from_user.id)
            return
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(i_btn("DEFAULT PACK", f"femoji:export:{get_default_pack_slug()}", "success", "pack"))
        m.add(i_btn("ALL PACKS BACKUP", "femoji:backup", "primary", "pack"))
        m.add(i_btn("TYPE PACK SLUG", "admin:export_pack", "primary", "settings"))
        _send_pe(message.chat.id, f"{P} Choose export option.\n\n{P} You can also use /exportemojis default", use_main=False, reply_markup=m)
    except Exception:
        log_exc("export_emojis_button")


@bot.message_handler(commands=["backupemojis"])
def backup_emojis_command(message):
    try:
        if not is_admin(message.from_user.id):
            return
        if not precheck(message, require_join=False):
            return
        export_all_emoji_backup(message.chat.id, message.from_user.id)
    except Exception:
        log_exc("backup_emojis_command")


@bot.message_handler(commands=["health"])
def admin_health_command(message):
    try:
        if not is_admin(message.from_user.id):
            return
        if not precheck(message, require_join=False):
            return
        try:
            _t0 = time.time()
            client.admin.command("ping")
            mongo_ms = int((time.time() - _t0) * 1000)
            mongo_status = f"OK ({mongo_ms}ms)"
        except Exception:
            mongo_status = "ERROR"
        text = (
            f"{premium_header('BOT HEALTH')}\n\n"
            f"{P} Telegram Bot : @{get_bot_username()}\n"
            f"{P} MongoDB      : {mongo_status}\n"
            f"{P} Uptime       : {fmt_uptime()}\n"
            f"{P} Updates      : {runtime_metrics.get('updates', 0)}\n"
            f"{P} Conversions  : {runtime_metrics.get('conversions', 0)}\n"
            f"{P} Errors       : {runtime_metrics.get('errors', 0)}\n"
            f"{P} Users        : {cached_count('users', users)}\n"
            f"{P} Emoji IDs    : {cached_count('emojis', emojis_col, {'active': True})}\n"
            f"{P} Packs        : {cached_count('packs', packs, {'active': True})}\n"
            f"{P} Server Time  : {now_local().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{P} Scheduler    : {'RUNNING' if scheduler.running else 'STOPPED'}\n"
            f"{premium_footer()}"
        )
        _send_pe(message.chat.id, text, use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("admin_health_command")


@bot.message_handler(func=lambda m: m.text == "BROADCAST" and is_admin(m.from_user.id))
def broadcast_button(message):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("📢 Send Now", "admin:broadcast_now", "success", "broadcast"), i_btn("⏰ Schedule", "admin:broadcast_schedule", "primary", "broadcast"))
    m.add(i_btn("🔙 Admin Panel", "admin:home", "primary", "back"))
    _send_pe(message.chat.id, f"{P} Choose broadcast mode.", use_main=False, reply_markup=m)


@bot.message_handler(commands=["broadcast"])
def broadcast_reply_command(message):
    if is_admin(message.from_user.id) and message.reply_to_message:
        _send_pe(message.chat.id, f"{P} Broadcasting started...", use_main=False)
        broadcast_to_all(message.chat.id, message.reply_to_message.message_id, message.from_user.id)
    elif is_admin(message.from_user.id):
        _send_pe(message.chat.id, f"{P} Reply to a message with /broadcast.", use_main=False)

# ======================== USER CALLBACKS ========================
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("user:"))
def user_callbacks(call):
    try:
        uid = call.from_user.id
        if call.data == "user:check_join":
            missing = check_joined(uid)
            if missing:
                bot.answer_callback_query(call.id, "Still missing channels.", show_alert=True)
                send_join_notice(call.message.chat.id, missing)
            else:
                bot.answer_callback_query(call.id, "Joined!")
                _send_pe(call.message.chat.id, f"{P} You joined all channels. Welcome!", use_main=False, reply_markup=user_keyboard(uid))
        elif call.data == "user:auto_pack":
            cur = bool((get_user(uid) or {}).get("auto_pack"))
            users.update_one({"user_id": uid}, {"$set": {"auto_pack": not cur}})
            bot.answer_callback_query(call.id, f"Auto Pack {'ON' if not cur else 'OFF'}")
            _edit_pe(call.message.chat.id, call.message.message_id, f"{P} Auto Smart Pack is now {'ON' if not cur else 'OFF'}.", use_main=False, reply_markup=back_markup("user:close"))
        elif call.data == "user:open_style":
            try:
                bot.answer_callback_query(call.id, "Opening Style Lab")
            except Exception:
                pass
            class _M: pass
            msg = _M(); msg.from_user = call.from_user; msg.chat = call.message.chat
            style_lab(msg)
        elif call.data.startswith("user:style:"):
            style = call.data.split(":", 2)[2]
            if style != "normal" and style not in STYLE_TABLES:
                style = "normal"
            users.update_one({"user_id": uid}, {"$set": {"text_style": style, "updated_at": now_utc()}})
            user_presence_cache.pop(uid, None)
            bot.answer_callback_query(call.id, f"Style set: {style.upper()}")
            # Refresh the Style Lab in-place so the active marker moves instantly.
            text, m = build_style_lab_view(uid)
            _edit_pe(call.message.chat.id, call.message.message_id, text, use_main=False, reply_markup=m)

        elif call.data.startswith("user:setpack:"):
            slug = call.data.split(":", 2)[2]
            if get_pack(slug):
                users.update_one({"user_id": uid}, {"$set": {"preferred_pack": slug}})
                bot.answer_callback_query(call.id, "Pack updated.")
                _edit_pe(call.message.chat.id, call.message.message_id, f"{P} Pack changed to {slug}.", use_main=False)
            else:
                bot.answer_callback_query(call.id, "Pack not found.", show_alert=True)
        elif call.data == "user:close":
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception: pass
    except Exception:
        log_exc("user_callbacks")


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("support:"))
def support_callbacks(call):
    try:
        uid = call.from_user.id
        data = call.data
        if data == "support:end":
            bot.answer_callback_query(call.id, "Support chat ended.")
            end_support_session(uid, notify=False, ask_rating=False)
            _send_pe(call.message.chat.id, f"{premium_header('SUPPORT CLOSED')}\n\n{P} Thanks for contacting us. Tap LIVE SUPPORT anytime.\n{premium_footer()}", use_main=False, reply_markup=user_keyboard(uid))
            send_rating_prompt(uid)
            return
        if data.startswith("support:rate:"):
            stars = safe_int(data.split(":")[-1], 0)
            if 1 <= stars <= 5:
                support_tickets.update_one({"user_id": int(uid)}, {"$set": {"rating": stars, "rated_at": now_utc()}}, upsert=True)
                track_event("support_rating", uid, {"stars": stars})
                bot.answer_callback_query(call.id, "Thanks for your feedback!")
                try:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                except Exception:
                    pass
                _send_pe(call.message.chat.id, f"{premium_header('THANK YOU')}\n\n{P} You rated us {'⭐' * stars} ({stars}/5).\n{P} We appreciate your feedback! 💛\n{premium_footer()}", use_main=False)
                assignee_id, _ = get_assignee(uid)
                if assignee_id:
                    try:
                        _send_pe(int(assignee_id), f"{P} ⭐ User {uid} rated your support {stars}/5.", use_main=False)
                    except Exception:
                        pass
            return
        # Admin-only actions below
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Admin only.", show_alert=True)
            return
        if data == "support:toggle":
            new_val = not support_enabled()
            set_setting("bot", "support_chat_enabled", new_val)
            bot.answer_callback_query(call.id, f"Live chat {'OPEN' if new_val else 'CLOSED'}.")
            _edit_pe(call.message.chat.id, call.message.message_id, support_overview_text(), use_main=False, reply_markup=support_overview_markup())
        elif data.startswith("support:reply:"):
            target = safe_int(data.split(":")[-1], 0)
            ok, assignee = claim_ticket(target, uid)
            if not ok and assignee and int(assignee) != uid:
                bot.answer_callback_query(call.id, f"⚠️ This ticket is being handled by {admin_label(assignee)}. Use Take Over if needed.", show_alert=True)
                try:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=support_admin_markup(target, assignee, uid))
                except Exception:
                    pass
                return
            temp_data[f"support_reply_{uid}"] = target
            bot.answer_callback_query(call.id, "Ticket claimed. Send your reply now.")
            sent = _send_pe(call.message.chat.id, f"{P} You are now handling user {target}. Type your reply (text, photo, file...). Send /cancel to abort.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_deliver_support_reply)
        elif data.startswith("support:takeover:"):
            target = safe_int(data.split(":")[-1], 0)
            takeover_ticket(target, uid)
            temp_data[f"support_reply_{uid}"] = target
            bot.answer_callback_query(call.id, "You have taken over this ticket.")
            sent = _send_pe(call.message.chat.id, f"{P} You took over user {target}. Type your reply now, or /cancel.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_deliver_support_reply)
        elif data.startswith("support:release:"):
            target = safe_int(data.split(":")[-1], 0)
            release_ticket(target, uid)
            temp_data.pop(f"support_reply_{uid}", None)
            bot.answer_callback_query(call.id, "Ticket released. Any admin can now claim it.")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=support_admin_markup(target, None, uid))
            except Exception:
                pass
        elif data.startswith("support:close:"):
            target = safe_int(data.split(":")[-1], 0)
            release_ticket(target, uid)
            end_support_session(target, notify=True, by_admin=True)
            bot.answer_callback_query(call.id, f"Ticket {target} closed.")
            _send_pe(call.message.chat.id, f"{P} Ticket for user {target} marked as closed.", use_main=False)
        elif data.startswith("support:quick:"):
            target = safe_int(data.split(":")[-1], 0)
            bot.answer_callback_query(call.id, "Pick a template.")
            _send_pe(call.message.chat.id, f"{premium_header('QUICK REPLIES')}\n\n{P} Choose a template to send to user {target}.\n{premium_footer()}", use_main=False, reply_markup=quick_reply_menu_markup(target))
        elif data.startswith("support:qsend:"):
            parts = data.split(":")
            idx = safe_int(parts[2], -1)
            target = safe_int(parts[3], 0)
            replies = get_quick_replies()
            if 0 <= idx < len(replies):
                ok, assignee = claim_ticket(target, uid)
                if not ok and assignee and int(assignee) != uid:
                    bot.answer_callback_query(call.id, f"⚠️ Handled by {admin_label(assignee)}.", show_alert=True)
                    return
                try:
                    body = f"{premium_header('🎧 SUPPORT REPLY 🎧')}\n\n{P} {replies[idx]}\n{premium_footer()}"
                    _send_pe(int(target), body, use_main=False, reply_markup=support_user_markup())
                    support_tickets.update_one({"user_id": int(target)}, {"$set": {"last_admin_at": now_utc(), "status": "open"}, "$inc": {"admin_msgs": 1}}, upsert=True)
                    support_messages.insert_one({"user_id": int(target), "from": "admin", "admin_id": uid, "type": "text", "text": replies[idx], "at": now_utc()})
                    track_event("support_quick_reply", uid, {"target": target})
                    bot.answer_callback_query(call.id, "Template sent.")
                    _send_pe(call.message.chat.id, f"{P} Template delivered to user {target}.", use_main=False, reply_markup=support_admin_markup(target, uid, uid))
                except Exception as e:
                    bot.answer_callback_query(call.id, "Delivery failed.", show_alert=True)
                    _send_pe(call.message.chat.id, f"{P} Could not deliver. ({str(e)[:60]})", use_main=False)
        elif data.startswith("support:transcript:"):
            target = safe_int(data.split(":")[-1], 0)
            bot.answer_callback_query(call.id, "Loading transcript...")
            _send_pe(call.message.chat.id, support_transcript_text(target), use_main=False, reply_markup=support_admin_markup(target, uid, uid))
        elif data == "support:qr_manage":
            _edit_pe(call.message.chat.id, call.message.message_id, quick_reply_manage_text(), use_main=False, reply_markup=quick_reply_manage_markup())
        elif data == "support:qr_add":
            bot.answer_callback_query(call.id, "Send the new template text.")
            sent = _send_pe(call.message.chat.id, f"{P} Send the new quick reply text. /cancel to abort.", use_main=False)
            if sent: bot.register_next_step_handler(sent, admin_add_quick_reply)
        elif data.startswith("support:qr_del:"):
            idx = safe_int(data.split(":")[-1], -1)
            items = get_quick_replies()
            if 0 <= idx < len(items):
                items.pop(idx)
                save_quick_replies(items)
            bot.answer_callback_query(call.id, "Template removed.")
            _edit_pe(call.message.chat.id, call.message.message_id, quick_reply_manage_text(), use_main=False, reply_markup=quick_reply_manage_markup())
        elif data == "support:qr_reset":
            save_quick_replies(list(DEFAULT_QUICK_REPLIES))
            bot.answer_callback_query(call.id, "Templates reset to defaults.")
            _edit_pe(call.message.chat.id, call.message.message_id, quick_reply_manage_text(), use_main=False, reply_markup=quick_reply_manage_markup())
    except Exception:
        log_exc("support_callbacks")


def admin_add_quick_reply(message):
    try:
        uid = message.from_user.id
        if not is_admin(uid):
            return
        txt = (message.text or "").strip()
        if txt == "/cancel" or not txt:
            return cancel_step(message)
        items = get_quick_replies()
        items.append(txt)
        save_quick_replies(items)
        _send_pe(message.chat.id, f"{P} Quick reply saved.", use_main=False, reply_markup=quick_reply_manage_markup())
    except Exception:
        log_exc("admin_add_quick_reply")

# ======================== INLINE MODE ========================
@bot.inline_handler(func=lambda query: True)
def inline_convert(query):
    try:
        uid = query.from_user.id
        if not get_setting("bot", "inline_mode_enabled", True):
            bot.answer_inline_query(query.id, [], switch_pm_text="Inline mode disabled", switch_pm_parameter="start", cache_time=1)
            return
        text = (query.query or "").strip()
        if not text:
            result = types.InlineQueryResultArticle(
                id="hint",
                title="Type text with emojis",
                description="Example: Hello [emoji] World",
                input_message_content=types.InputTextMessageContent(message_text=f"Type @{get_bot_username()} Hello to convert premium emojis."),
            )
            bot.answer_inline_query(query.id, [result], cache_time=1, is_personal=True)
            return
        # Register inline user lightly.
        users.update_one({"user_id": uid}, {"$setOnInsert": {"user_id": uid, "joined_at": now_utc(), "preferred_pack": get_default_pack_slug(), "text_style": "normal", "coins": int((get_setting('growth', default={}) or {}).get('starting_coins', 20)), "referral_code": make_ref_code(uid)}, "$set": {"last_seen": now_utc()}}, upsert=True)
        pack_slug = smart_pack_for_text(text, uid) if user_auto_pack(uid) else get_user_pack_slug(uid)
        styled_text, _did_style = apply_output_style(text, uid)
        final_text, entities = process_text_with_duplicate_emojis(styled_text, [], pack_slug)
        sug = "".join(smart_emoji_suggestions(text))
        styled_alt, _ = apply_output_style(text + " " + sug, uid)
        alt_text, alt_entities = process_text_with_duplicate_emojis(styled_alt, [], pack_slug)
        r1 = types.InlineQueryResultArticle(id="convert", title="Premium Emoji Convert", description=f"Pack: {pack_slug}", input_message_content=types.InputTextMessageContent(message_text=final_text, entities=entities, parse_mode=None))
        r2 = types.InlineQueryResultArticle(id="smart", title="AI Smart Emoji Suggest", description="Adds smart premium emoji hooks", input_message_content=types.InputTextMessageContent(message_text=alt_text, entities=alt_entities, parse_mode=None))
        bot.answer_inline_query(query.id, [r1, r2], cache_time=1, is_personal=True)
        inc_user(uid, "inline_conversions", 1)
        inc_user(uid, "conversions", 1)
        inc_user(uid, "score", 1)
        track_event("inline_conversion", uid, {"pack_slug": pack_slug})
        track_event("conversion", uid, {"source": "inline"})
    except Exception:
        log_exc("inline_convert")
        try: bot.answer_inline_query(query.id, [], cache_time=1)
        except Exception: pass

# ======================== ADVANCED FORWARDED PREMIUM EMOJI COLLECTOR ========================
EMOJI_SAVE_DIR = "premium_emoji_files"
os.makedirs(EMOJI_SAVE_DIR, exist_ok=True)


def sanitize_pack_slug(slug):
    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", str(slug or "default").strip().lower())
    return slug[:60] or "default"


def is_forwarded_message(message):
    return bool(
        getattr(message, "forward_from_chat", None)
        or getattr(message, "forward_from", None)
        or getattr(message, "forward_sender_name", None)
        or getattr(message, "forward_date", None)
        or getattr(message, "forward_origin", None)
    )


def iter_message_entities(message):
    entities = []
    try:
        if getattr(message, "entities", None):
            entities.extend(message.entities or [])
        if getattr(message, "caption_entities", None):
            entities.extend(message.caption_entities or [])
    except Exception:
        pass
    return entities


def capture_bases_from_message(message):
    """When a premium message is forwarded/sent, its text plus custom_emoji entities
    let us learn the real emoji behind each premium id FOR FREE (no API call).
    Stores base_emoji so Smart Match works instantly for collected emojis."""
    try:
        text = getattr(message, "text", None) or getattr(message, "caption", None) or ""
        if not text:
            return
        units = text.encode("utf-16-le")
        for ent in iter_message_entities(message):
            try:
                if ent.type != "custom_emoji" or not getattr(ent, "custom_emoji_id", None):
                    continue
                off = int(ent.offset) * 2
                ln = int(ent.length) * 2
                grapheme = units[off:off + ln].decode("utf-16-le", "ignore")
                base = _norm_emoji(grapheme)
                cid = str(ent.custom_emoji_id)
                if cid and base and base.strip():
                    if CUSTOM_EMOJI_BASE.get(cid) != base:
                        CUSTOM_EMOJI_BASE[cid] = base
                        try:
                            emojis_col.update_many(
                                {"emoji_id": cid},
                                {"$set": {"base_emoji": base, "base_resolved_at": now_utc()}},
                            )
                        except Exception:
                            pass
                        emoji_base_map_cache["expires"] = 0
            except Exception:
                pass
    except Exception:
        log_exc("capture_bases_from_message")


def extract_forwarded_premium_ids(message):
    """Extract premium custom emoji IDs and numeric IDs from forwarded posts or normal admin messages."""
    found = []
    try:
        capture_bases_from_message(message)
        text = getattr(message, "text", None) or getattr(message, "caption", None) or ""
        found.extend(extract_emoji_ids(text))
        for ent in iter_message_entities(message):
            try:
                if ent.type == "custom_emoji" and getattr(ent, "custom_emoji_id", None):
                    found.append(str(ent.custom_emoji_id))
            except Exception:
                pass
        if getattr(message, "reply_to_message", None):
            found.extend(extract_forwarded_premium_ids(message.reply_to_message))
    except Exception:
        log_exc("extract_forwarded_premium_ids")
    clean, seen = [], set()
    for eid in found:
        eid = str(eid).strip()
        if valid_emoji_id(eid) and eid not in seen:
            seen.add(eid)
            clean.append(eid)
    return clean


def save_ids_to_txt(ids, pack_slug="default"):
    pack_slug = sanitize_pack_slug(pack_slug)
    os.makedirs(EMOJI_SAVE_DIR, exist_ok=True)
    path = os.path.join(EMOJI_SAVE_DIR, f"{pack_slug}_premium_emoji_ids.txt")
    existing_order = []
    existing = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                eid = line.strip()
                if valid_emoji_id(eid) and eid not in existing:
                    existing.add(eid)
                    existing_order.append(eid)
    new_ids = []
    for eid in ids or []:
        eid = str(eid).strip()
        if valid_emoji_id(eid) and eid not in existing:
            existing.add(eid)
            existing_order.append(eid)
            new_ids.append(eid)
    with open(path, "w", encoding="utf-8") as f:
        for eid in existing_order:
            f.write(eid + "\n")
    return path, len(new_ids), len(existing_order)


def build_pack_txt_from_db(pack_slug="default"):
    pack_slug = sanitize_pack_slug(pack_slug)
    ids = [d.get("emoji_id") for d in emojis_col.find({"pack_slug": pack_slug, "active": True}, {"emoji_id": 1}).sort("created_at", ASCENDING)]
    ids = [str(x) for x in ids if valid_emoji_id(x)]
    return save_ids_to_txt(ids, pack_slug)[0], len(ids)


def collector_admin_markup():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(i_btn("EXPORT DEFAULT", f"femoji:export:{get_default_pack_slug()}", "success", "pack"), i_btn("BACKUP ALL", "femoji:backup", "primary", "pack"))
    m.add(i_btn("PACKS", "admin:packs", "primary", "pack"), i_btn("ADMIN PANEL", "admin:home", "primary", "back"))
    return m


def forwarded_save_markup(token, pack_slug=None):
    pack_slug = sanitize_pack_slug(pack_slug or get_default_pack_slug())
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(i_btn("SAVE PREMIUM EMOJIS", f"femoji:save:{token}", "success", "emoji"))
    m.add(i_btn(f"SAVE TO {pack_slug.upper()}", f"femoji:save:{token}", "success", "pack"))
    m.add(i_btn("CANCEL", f"femoji:cancel:{token}", "danger", "danger"))
    return m


def forwarded_collector_help_text():
    return (
        f"{premium_header('FORWARD EMOJI COLLECTOR')}\n\n"
        f"{P} Forward any post from your Premium Emoji IDs channel to this bot.\n"
        f"{P} The bot will detect numeric IDs and custom emoji entities.\n\n"
        f"{P} {section_style('Manual Safe Mode')}\n"
        f"{P} 1. Forward the channel post here.\n"
        f"{P} 2. Preview detected IDs.\n"
        f"{P} 3. Click SAVE PREMIUM EMOJIS.\n"
        f"{P} 4. Bot saves TXT file and imports to MongoDB pack.\n\n"
        f"{P} Default Pack : {get_default_pack_slug()}\n"
        f"{P} Save Folder  : {EMOJI_SAVE_DIR}/\n\n"
        f"{P} Commands: /exportemojis default, /backupemojis, /health\n"
        f"{premium_footer()}"
    )


def _send_collector_exact_preview(chat_id, source_label, ids, pack_slug, reply_markup=None):
    """Send collector preview without random UI emoji replacement.
    Each preview icon is mapped to its own detected custom_emoji_id, so it shows the SAME emoji.
    """
    try:
        ids = [str(x).strip() for x in (ids or []) if valid_emoji_id(str(x).strip())]
        shown = ids[:25]
        parts = []
        entities = []

        def add(line=""):
            parts.append(str(line) + "\n")

        def add_exact_row(eid):
            offset = _utf16_len_str("".join(parts))
            parts.append(f"{PLACEHOLDER} {eid}\n")
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=offset,
                length=_utf16_len(PLACEHOLDER),
                custom_emoji_id=str(eid),
            ))

        add("╭━━━━━━━━━━━━━━━━━━━━╮")
        add("     PREMIUM IDS DETECTED")
        add("╰━━━━━━━━━━━━━━━━━━━━╯")
        add("")
        add(f"Source      : {source_label}")
        add(f"Found IDs    : {len(ids)}")
        add(f"Target Pack  : {pack_slug}")
        add("")
        add("PREVIEW — SAME EMOJI, SAME ID")
        add("━━━━━━━━━━━━━━━━━━━━")
        for eid in shown:
            add_exact_row(eid)
        if len(ids) > len(shown):
            add(f"...and {len(ids) - len(shown)} more")
        add("")
        add("Nothing is saved yet. Click SAVE PREMIUM EMOJIS to import.")
        add("━━━━━━━━━━━━━━━━━━━━")

        text = "".join(parts).rstrip()
        try:
            return bot.send_message(
                chat_id,
                text,
                entities=entities or None,
                reply_markup=reply_markup,
                parse_mode=None,
                disable_web_page_preview=True,
            )
        except Exception:
            # Fallback: if Telegram rejects any custom emoji ID, send plain IDs without random replacement.
            plain_rows = "\n".join(str(eid) for eid in shown)
            more = f"\n...and {len(ids) - len(shown)} more" if len(ids) > len(shown) else ""
            plain_text = (
                "╭━━━━━━━��━━━━━━━━━━━━╮\n"
                "     PREMIUM IDS DETECTED\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"Source      : {source_label}\n"
                f"Found IDs    : {len(ids)}\n"
                f"Target Pack  : {pack_slug}\n\n"
                "PREVIEW\n"
                f"{plain_rows}{more}\n\n"
                "Nothing is saved yet. Click SAVE PREMIUM EMOJIS to import.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            return bot.send_message(chat_id, plain_text, reply_markup=reply_markup, parse_mode=None, disable_web_page_preview=True)
    except Exception:
        log_exc("_send_collector_exact_preview")
        return _send_pe(chat_id, f"{P} Preview failed. Detected {len(ids or [])} IDs.", use_main=False, reply_markup=reply_markup)


def show_forwarded_emoji_preview(message, ids, pack_slug=None):
    try:
        pack_slug = sanitize_pack_slug(pack_slug or temp_data.get(f"bulk_pack_{message.from_user.id}") or get_default_pack_slug())
        token = str(uuid.uuid4()).replace("-", "")[:10]
        temp_data[f"femoji_{token}"] = {
            "admin_id": int(message.from_user.id),
            "chat_id": int(message.chat.id),
            "ids": list(ids),
            "pack_slug": pack_slug,
            "created_at": time.time(),
            "source_message_id": getattr(message, "message_id", None),
        }
        source_label = "Forwarded post" if is_forwarded_message(message) else "Admin message"
        _send_collector_exact_preview(
            message.chat.id,
            source_label,
            ids,
            pack_slug,
            reply_markup=forwarded_save_markup(token, pack_slug),
        )
    except Exception:
        log_exc("show_forwarded_emoji_preview")

def export_pack_as_txt(chat_id, pack_slug, admin_id=None):
    try:
        pack_slug = sanitize_pack_slug(pack_slug or get_default_pack_slug())
        status = _send_pe(chat_id, f"{P} Preparing export for pack: {pack_slug}", use_main=False)
        path, count = build_pack_txt_from_db(pack_slug)
        if count <= 0:
            if status:
                _edit_pe(chat_id, status.message_id, f"{P} No active emoji IDs found for pack: {pack_slug}", use_main=False, reply_markup=admin_home_markup())
            else:
                _send_pe(chat_id, f"{P} No active emoji IDs found for pack: {pack_slug}", use_main=False)
            return
        with open(path, "rb") as f:
            bot.send_document(chat_id, f, caption=f"Premium emoji export: {pack_slug} | IDs: {count}")
        if status:
            _edit_pe(chat_id, status.message_id, f"{P} Export complete.\n\n{P} Pack: {pack_slug}\n{P} IDs : {count}", use_main=False, reply_markup=admin_home_markup())
        track_event("emoji_export", admin_id, {"pack_slug": pack_slug, "count": count})
    except Exception:
        log_exc("export_pack_as_txt")
        _send_pe(chat_id, f"{P} Export failed.", use_main=False)


def export_all_emoji_backup(chat_id, admin_id=None):
    try:
        os.makedirs(EMOJI_SAVE_DIR, exist_ok=True)
        stamp = now_local().strftime("%Y%m%d_%H%M%S")
        zip_path = os.path.join(EMOJI_SAVE_DIR, f"gadget_premium_emoji_backup_{stamp}.zip")
        active_packs = list(packs.find({"active": True}, {"slug": 1, "name": 1}).sort("slug", ASCENDING))
        status = _send_pe(chat_id, f"{P} Building full emoji backup...", use_main=False)
        total_ids = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            readme = [
                "GADGET Premium Emoji Backup",
                f"Created: {now_local().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Packs: {len(active_packs)}",
                "",
            ]
            for pdoc in active_packs:
                slug = sanitize_pack_slug(pdoc.get("slug") or "default")
                ids = [d.get("emoji_id") for d in emojis_col.find({"pack_slug": slug, "active": True}, {"emoji_id": 1}).sort("created_at", ASCENDING)]
                ids = [str(x) for x in ids if valid_emoji_id(x)]
                total_ids += len(ids)
                zf.writestr(f"{slug}_premium_emoji_ids.txt", "\n".join(ids) + ("\n" if ids else ""))
                readme.append(f"{slug}: {len(ids)} IDs")
            zf.writestr("README.txt", "\n".join(readme) + "\n")
        with open(zip_path, "rb") as f:
            bot.send_document(chat_id, f, caption=f"Full premium emoji backup | Packs: {len(active_packs)} | IDs: {total_ids}")
        if status:
            _edit_pe(chat_id, status.message_id, f"{P} Backup complete.\n\n{P} Packs: {len(active_packs)}\n{P} IDs  : {total_ids}", use_main=False, reply_markup=admin_home_markup())
        track_event("emoji_backup", admin_id, {"packs": len(active_packs), "ids": total_ids})
    except Exception:
        log_exc("export_all_emoji_backup")
        _send_pe(chat_id, f"{P} Backup failed.", use_main=False)


def admin_receive_export_pack(message):
    try:
        if message.text and message.text.strip() == "/cancel":
            return cancel_step(message)
        if not is_admin(message.from_user.id):
            return
        slug = sanitize_pack_slug((message.text or "").strip() or get_default_pack_slug())
        export_pack_as_txt(message.chat.id, slug, message.from_user.id)
    except Exception:
        log_exc("admin_receive_export_pack")


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("femoji:"))
def forwarded_premium_emoji_callback(call):
    try:
        uid = int(call.from_user.id)
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "Admin only.", show_alert=True)
            return
        parts = call.data.split(":", 2)
        action = parts[1] if len(parts) > 1 else ""
        token = parts[2] if len(parts) > 2 else ""
        if action == "backup":
            bot.answer_callback_query(call.id, "Creating backup...")
            export_all_emoji_backup(call.message.chat.id, uid)
            return
        if action == "export":
            bot.answer_callback_query(call.id, "Exporting...")
            export_pack_as_txt(call.message.chat.id, token or get_default_pack_slug(), uid)
            return
        key = f"femoji_{token}"
        data = temp_data.get(key)
        if not data:
            bot.answer_callback_query(call.id, "Expired. Forward the post again.", show_alert=True)
            return
        if int(data.get("admin_id", uid)) != uid and not is_owner(uid):
            bot.answer_callback_query(call.id, "This import belongs to another admin.", show_alert=True)
            return
        if action == "cancel":
            temp_data.pop(key, None)
            bot.answer_callback_query(call.id, "Cancelled")
            _edit_pe(call.message.chat.id, call.message.message_id, f"{P} Forwarded emoji import cancelled.", use_main=False, reply_markup=admin_home_markup())
            return
        if action != "save":
            bot.answer_callback_query(call.id, "Unknown action.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "Saving premium emojis...")
        ids = data.get("ids") or []
        pack_slug = sanitize_pack_slug(data.get("pack_slug") or get_default_pack_slug())
        status = call.message
        def cb(stage, done, total, force=False):
            edit_loading(status, "FORWARDED EMOJI IMPORT", stage, done, total, force)
        cb("Preparing forwarded premium emoji IDs", 5, 100, True)
        file_path, new_file_ids, total_file_ids = save_ids_to_txt(ids, pack_slug)
        cb("Saved IDs into local TXT vault", 22, 100, True)
        res = bulk_import_emoji_ids(ids, pack_slug, uid, "forwarded_channel", progress_callback=cb)
        temp_data.pop(key, None)
        final_text = (
            f"{premium_header('IMPORT COMPLETE')}\n\n"
            f"{P} Target Pack    : {pack_slug}\n"
            f"{P} Found IDs      : {res.get('found', 0)}\n"
            f"{P} New DB IDs     : {res.get('inserted', 0)}\n"
            f"{P} Duplicate IDs  : {res.get('duplicates', 0)}\n"
            f"{P} Pack Total     : {res.get('pack_count', 0)}\n\n"
            f"{P} TXT New IDs    : {new_file_ids}\n"
            f"{P} TXT Total IDs  : {total_file_ids}\n"
            f"{P} Local File     : {file_path}\n\n"
            f"{P} These premium emojis are now live in your bot.\n"
            f"{premium_footer()}"
        )
        _edit_pe(call.message.chat.id, call.message.message_id, final_text, use_main=False, reply_markup=admin_home_markup())
    except Exception:
        log_exc("forwarded_premium_emoji_callback")
        try:
            bot.answer_callback_query(call.id, "Import failed.", show_alert=True)
        except Exception:
            pass


# ======================== LIVE SUPPORT (TWO-WAY CHAT) ========================
def support_enabled():
    return bool(get_setting("bot", "support_chat_enabled", True))


def in_support_mode(uid):
    return bool(temp_data.get(f"support_mode_{int(uid)}"))


def support_intro_text():
    return (
        f"{premium_header('🎧 LIVE SUPPORT 🎧')}\n\n"
        f"{P} You are now connected to our support team.\n"
        f"{P} Send your question, screenshot, or file and a human\n"
        f"{P} will reply right here in this chat.\n\n"
        f"{P} {section_style('TIPS')}\n"
        f"{P} • Describe your issue clearly.\n"
        f"{P} • You can send photos, videos and documents.\n"
        f"{P} • Tap END CHAT when your issue is solved.\n"
        f"{premium_footer()}"
    )


def support_user_markup():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(i_btn("End Chat", "support:end", "danger", "danger"))
    return m


def admin_label(admin_id):
    """Readable name for an admin Telegram ID."""
    try:
        u = get_user(admin_id) or {}
        name = _user_display_name(u)
        uname = ("@" + u.get("username")) if u.get("username") else None
        if uname and name != "Unknown":
            return f"{name} ({uname})"
        return uname or (name if name != "Unknown" else str(admin_id))
    except Exception:
        return str(admin_id)


def claim_ticket(user_id, admin_id):
    """
    Atomically assign a ticket to an admin only if it is currently unassigned.
    Returns (success, current_assignee_id).
    """
    user_id = int(user_id)
    admin_id = int(admin_id)
    res = support_tickets.update_one(
        {"user_id": user_id, "$or": [{"assigned_to": None}, {"assigned_to": {"$exists": False}}]},
        {"$set": {"assigned_to": admin_id, "assigned_name": admin_label(admin_id), "assigned_at": now_utc(), "status": "open"}},
    )
    if res.modified_count == 1:
        return True, admin_id
    doc = support_tickets.find_one({"user_id": user_id}, {"assigned_to": 1}) or {}
    return False, doc.get("assigned_to")


def takeover_ticket(user_id, admin_id):
    """Force-reassign a ticket to a new admin, notifying the previous one."""
    user_id = int(user_id)
    admin_id = int(admin_id)
    doc = support_tickets.find_one({"user_id": user_id}, {"assigned_to": 1}) or {}
    prev = doc.get("assigned_to")
    support_tickets.update_one(
        {"user_id": user_id},
        {"$set": {"assigned_to": admin_id, "assigned_name": admin_label(admin_id), "assigned_at": now_utc(), "status": "open"}},
    )
    if prev and int(prev) != admin_id:
        try:
            _send_pe(int(prev), f"{P} ⚠️ Ticket for user {user_id} was taken over by {admin_label(admin_id)}.", use_main=False)
        except Exception:
            pass
    return prev


def release_ticket(user_id, admin_id=None):
    user_id = int(user_id)
    support_tickets.update_one(
        {"user_id": user_id},
        {"$set": {"assigned_to": None, "assigned_name": None, "released_at": now_utc()}},
    )


def get_assignee(user_id):
    doc = support_tickets.find_one({"user_id": int(user_id)}, {"assigned_to": 1, "assigned_name": 1}) or {}
    return doc.get("assigned_to"), doc.get("assigned_name")


# ---- Quick reply templates (canned responses) ----
DEFAULT_QUICK_REPLIES = [
    "Hello! 👋 Thanks for reaching out. How can I help you today?",
    "Please send a screenshot of the issue so we can check it faster. 📸",
    "Your issue has been resolved. ✅ Is there anything else we can help with?",
    "Thanks for your patience! 🙏 We are working on it right now.",
    "This feature is coming soon. 🚀 Stay tuned for updates!",
]


def get_quick_replies():
    val = get_setting("bot", "quick_replies", None)
    if not isinstance(val, list) or not val:
        return list(DEFAULT_QUICK_REPLIES)
    return val


def save_quick_replies(items):
    set_setting("bot", "quick_replies", items[:20])


def quick_reply_menu_markup(target):
    m = types.InlineKeyboardMarkup(row_width=1)
    for idx, txt in enumerate(get_quick_replies()):
        label = (txt[:42] + "…") if len(txt) > 43 else txt
        m.add(i_btn(label, f"support:qsend:{idx}:{target}", "primary", "broadcast"))
    m.add(i_btn("Cancel", f"support:reply:{target}", "danger", "back"))
    return m


def quick_reply_manage_text():
    lines = []
    for idx, txt in enumerate(get_quick_replies()):
        short = (txt[:50] + "…") if len(txt) > 51 else txt
        lines.append(f"{P} {idx + 1}. {short}")
    body = "\n".join(lines) if lines else f"{P} No templates yet."
    return (
        f"{premium_header('⚡ QUICK REPLIES ⚡')}\n\n"
        f"{P} {section_style('SAVED TEMPLATES')}\n"
        f"{body}\n\n"
        f"{P} Tap a number to delete it, or ADD NEW to create one.\n"
        f"{premium_footer()}"
    )


def quick_reply_manage_markup():
    m = types.InlineKeyboardMarkup(row_width=4)
    btns = [i_btn(str(idx + 1), f"support:qr_del:{idx}", "danger", "danger") for idx in range(len(get_quick_replies()))]
    for i in range(0, len(btns), 4):
        m.add(*btns[i:i + 4])
    m.add(i_btn("Add New", "support:qr_add", "success", "broadcast"))
    m.add(i_btn("Reset Defaults", "support:qr_reset", "primary", "back"), i_btn("BACK", "admin:support", "primary", "back"))
    return m


# ---- Support rating ----
def send_rating_prompt(uid):
    try:
        m = types.InlineKeyboardMarkup(row_width=5)
        m.add(*[i_btn("⭐" * n if n <= 2 else str(n), f"support:rate:{n}", "primary", "stats") for n in range(1, 6)])
        _send_pe(int(uid), f"{premium_header('RATE OUR SUPPORT')}\n\n{P} How was your support experience?\n{P} Tap 1 (poor) to 5 (excellent).\n{premium_footer()}", use_main=False, reply_markup=m)
    except Exception:
        pass


def support_rating_stats():
    try:
        cur = support_tickets.aggregate([
            {"$match": {"rating": {"$gte": 1}}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
        ])
        doc = next(cur, None)
        if not doc:
            return None, 0
        return round(doc.get("avg", 0), 2), doc.get("count", 0)
    except Exception:
        return None, 0


def start_support_session(message):
    uid = message.from_user.id
    if not support_enabled():
        url = _support_url()
        mk = types.InlineKeyboardMarkup()
        if url:
            mk.add(i_btn("Contact Admin", url=url, style="success", emoji_key="admin_panel"))
        _send_pe(message.chat.id, f"{premium_header('SUPPORT')}\n\n{P} Live chat is currently closed.\n{P} Please reach us directly via the button below.\n{premium_footer()}", use_main=False, reply_markup=mk if url else None)
        return
    temp_data[f"support_mode_{uid}"] = True
    u = get_user(uid) or {}
    support_tickets.update_one(
        {"user_id": int(uid)},
        {"$set": {"user_id": int(uid), "status": "open", "username": u.get("username"),
                  "name": _user_display_name(u), "last_user_at": now_utc(),
                  "assigned_to": None, "assigned_name": None},
         "$setOnInsert": {"opened_at": now_utc()},
         "$inc": {"sessions": 1}},
        upsert=True,
    )
    track_event("support_open", uid)
    _send_pe(message.chat.id, support_intro_text(), use_main=False, reply_markup=support_user_markup())


def end_support_session(uid, notify=True, by_admin=False, ask_rating=True):
    uid = int(uid)
    temp_data.pop(f"support_mode_{uid}", None)
    had_chat = bool(support_tickets.find_one({"user_id": uid, "user_msgs": {"$gte": 1}}, {"_id": 1}))
    support_tickets.update_one({"user_id": uid}, {"$set": {"status": "closed", "closed_at": now_utc()}})
    if notify:
        try:
            who = "an agent" if by_admin else "you"
            _send_pe(uid, f"{premium_header('SUPPORT CLOSED')}\n\n{P} This support chat was ended by {who}.\n{P} Tap LIVE SUPPORT anytime to start again.\n{premium_footer()}", use_main=False, reply_markup=user_keyboard(uid))
        except Exception:
            pass
    if ask_rating and had_chat:
        send_rating_prompt(uid)


def support_admin_markup(uid, assignee_id, viewer_id):
    """Build per-admin action buttons based on who owns the ticket."""
    uid = int(uid)
    mk = types.InlineKeyboardMarkup(row_width=2)
    if not assignee_id:
        mk.add(i_btn("Reply (Claim)", f"support:reply:{uid}", "success", "broadcast"),
               i_btn("Quick Reply", f"support:quick:{uid}", "primary", "broadcast"))
        mk.add(i_btn("Close", f"support:close:{uid}", "danger", "danger"))
    elif int(assignee_id) == int(viewer_id):
        mk.add(i_btn("Reply", f"support:reply:{uid}", "success", "broadcast"),
               i_btn("Quick Reply", f"support:quick:{uid}", "primary", "broadcast"))
        mk.add(i_btn("Transcript", f"support:transcript:{uid}", "primary", "stats"),
               i_btn("Release", f"support:release:{uid}", "primary", "back"))
        mk.add(i_btn("Close", f"support:close:{uid}", "danger", "danger"))
    else:
        mk.add(i_btn("Take Over", f"support:takeover:{uid}", "danger", "spam"))
    mk.add(i_btn("View Profile", f"admin:user_view:{uid}", "primary", "users_list"))
    return mk


def support_transcript_text(uid, limit=12):
    uid = int(uid)
    rows = list(support_messages.find({"user_id": uid}).sort("at", DESCENDING).limit(limit))
    rows.reverse()
    if not rows:
        return f"{premium_header('TRANSCRIPT')}\n\n{P} No messages logged yet.\n{premium_footer()}"
    lines = []
    for r in rows:
        who = "USER" if r.get("from") == "user" else "AGENT"
        body = r.get("text")
        if not body:
            body = f"[{r.get('type', 'media')}]"
        body = body if len(body) <= 60 else body[:57] + "…"
        lines.append(f"{P} {who}: {body}")
    return (
        f"{premium_header('🗂 CHAT TRANSCRIPT 🗂')}\n\n"
        f"{P} Last {len(rows)} messages with user {uid}\n\n"
        + "\n".join(lines)
        + f"\n{premium_footer()}"
    )


def relay_user_to_admins(message):
    uid = message.from_user.id
    u = get_user(uid) or {}
    uname = ("@" + u.get("username")) if u.get("username") else "—"
    support_tickets.update_one({"user_id": int(uid)}, {"$set": {"last_user_at": now_utc(), "status": "open"}, "$inc": {"user_msgs": 1}}, upsert=True)
    try:
        support_messages.insert_one({"user_id": int(uid), "from": "user", "type": message.content_type, "text": getattr(message, "text", None) or getattr(message, "caption", None), "at": now_utc()})
    except Exception:
        pass
    assignee_id, assignee_name = get_assignee(uid)
    if assignee_id:
        assign_line = f"{P} Handled by : {assignee_name or admin_label(assignee_id)}\n"
    else:
        assign_line = f"{P} Status   : 🟡 Unclaimed — first admin to reply claims it\n"
    header = (
        f"{premium_header('📩 SUPPORT MESSAGE 📩')}\n\n"
        f"{P} From : {_user_display_name(u)} ({uname})\n"
        f"{P} ID   : {uid}\n"
        f"{P} Time : {fmt_dt(now_utc())}\n"
        f"{assign_line}"
        f"{premium_footer()}"
    )
    # If a ticket is already claimed, only the owner gets the follow-up messages
    # so two admins never reply to the same person at once.
    if assignee_id:
        targets = [int(assignee_id)]
    else:
        targets = get_all_admin_ids()
    delivered = 0
    for aid in targets:
        try:
            _send_pe(aid, header, use_main=False)
            bot.copy_message(aid, message.chat.id, message.message_id)
            _send_pe(aid, f"{P} Actions for this ticket:", use_main=False, reply_markup=support_admin_markup(uid, assignee_id, aid))
            delivered += 1
        except Exception:
            continue
    if not delivered:
        _send_pe(message.chat.id, f"{P} Message received. Our team will reply soon.", use_main=False, reply_markup=support_user_markup())


def admin_deliver_support_reply(message):
    try:
        aid = message.from_user.id
        if not is_admin(aid):
            return
        if message.text and message.text.strip() == "/cancel":
            return cancel_step(message)
        target = temp_data.pop(f"support_reply_{aid}", None)
        if not target:
            return
        # Make sure this admin still owns the ticket (another admin may have taken over).
        assignee_id, assignee_name = get_assignee(target)
        if assignee_id and int(assignee_id) != int(aid):
            _send_pe(message.chat.id, f"{P} ⚠️ This ticket was taken over by {assignee_name or admin_label(assignee_id)}. Your reply was NOT sent.", use_main=False)
            return
        if not assignee_id:
            claim_ticket(target, aid)
        try:
            if message.content_type == "text":
                # Render the human reply with the premium emoji engine so the user
                # only ever sees premium emojis (never plain ones).
                reply_body = (
                    f"{premium_header('🎧 SUPPORT REPLY 🎧')}\n\n"
                    f"{P} {message.text}\n"
                    f"{premium_footer()}"
                )
                _send_pe(int(target), reply_body, use_main=False, reply_markup=support_user_markup())
            else:
                _send_pe(int(target), f"{premium_header('🎧 SUPPORT REPLY 🎧')}\n{premium_footer()}", use_main=False, reply_markup=support_user_markup())
                bot.copy_message(int(target), message.chat.id, message.message_id)
            support_tickets.update_one({"user_id": int(target)}, {"$set": {"last_admin_at": now_utc(), "status": "open"}, "$inc": {"admin_msgs": 1}}, upsert=True)
            support_messages.insert_one({"user_id": int(target), "from": "admin", "admin_id": aid, "type": message.content_type, "text": getattr(message, "text", None) or getattr(message, "caption", None), "at": now_utc()})
            track_event("support_reply", aid, {"target": target})
            mk_again = types.InlineKeyboardMarkup(row_width=2)
            mk_again.add(i_btn("Reply Again", f"support:reply:{target}", "success", "broadcast"),
                         i_btn("Release", f"support:release:{target}", "primary", "back"))
            mk_again.add(i_btn("Close Ticket", f"support:close:{target}", "danger", "danger"))
            _send_pe(message.chat.id, f"{P} Reply delivered to user {target}. Use the buttons below for the next action.", use_main=False, reply_markup=mk_again)
        except Exception as e:
            _send_pe(message.chat.id, f"{P} Could not deliver. User may have blocked the bot.\n{P} ({str(e)[:80]})", use_main=False)
    except Exception:
        log_exc("admin_deliver_support_reply")


def support_overview_text():
    open_count = cached_count("support_open", support_tickets, {"status": "open"}, ttl=10)
    total = cached_count("support_total", support_tickets, ttl=20)
    closed = cached_count("support_closed", support_tickets, {"status": "closed"}, ttl=20)
    status = "🟢 OPEN" if support_enabled() else "🔴 CLOSED"
    unclaimed = cached_count("support_unclaimed", support_tickets, {"status": "open", "$or": [{"assigned_to": None}, {"assigned_to": {"$exists": False}}]}, ttl=8)
    avg, rcount = support_rating_stats()
    rating_line = f"{avg}/5 from {rcount} ratings" if avg else "no ratings yet"
    return (
        f"{premium_header('🎧 LIVE SUPPORT CENTER 🎧')}\n\n"
        f"{P} {section_style('SUPPORT MATRIX')}\n"
        f"{P} Live Chat   : {status}\n"
        f"{P} Open Tickets: {open_count}\n"
        f"{P} Unclaimed   : {unclaimed}\n"
        f"{P} Closed      : {closed}\n"
        f"{P} Total       : {total}\n"
        f"{P} Satisfaction: ⭐ {rating_line}\n\n"
        f"{P} Open tickets appear below. Tap one to reply.\n"
        f"{premium_footer()}"
    )


def support_overview_markup():
    m = types.InlineKeyboardMarkup(row_width=1)
    rows = list(support_tickets.find({"status": "open"}).sort("last_user_at", DESCENDING).limit(10))
    for t in rows:
        tag = t.get("username") and ("@" + t["username"]) or (t.get("name") or str(t.get("user_id")))
        if t.get("assigned_to"):
            short = (t.get("assigned_name") or str(t.get("assigned_to"))).split(" (")[0]
            flag = f"[busy: {short}]"
        else:
            flag = "[free]"
        m.add(i_btn(f"{tag} - {flag}"[:60], f"support:reply:{t.get('user_id')}", "primary", "broadcast"))
    toggle = "Close Live Chat" if support_enabled() else "Open Live Chat"
    tstyle = "danger" if support_enabled() else "success"
    m.add(i_btn(toggle, "support:toggle", tstyle, "settings"), i_btn("Quick Replies", "support:qr_manage", "primary", "broadcast"))
    m.add(i_btn("Refresh", "admin:support", "primary", "back"), i_btn("BACK", "admin:home", "primary", "back"))
    return m


@bot.message_handler(commands=["support"])
@bot.message_handler(func=lambda m: m.text == "LIVE SUPPORT")
def support_command(message):
    if not precheck(message, require_join=False):
        return
    if is_admin(message.from_user.id):
        _send_pe(message.chat.id, support_overview_text(), use_main=False, reply_markup=support_overview_markup())
        return
    start_support_session(message)


@bot.message_handler(
    content_types=["text", "photo", "video", "animation", "document", "sticker", "voice", "audio", "video_note"],
    func=lambda m: not is_admin(m.from_user.id) and in_support_mode(m.from_user.id)
)
def support_relay_handler(message):
    try:
        uid = message.from_user.id
        txt = (message.text or "").strip()
        if txt in ("/cancel", "/end") or txt.upper() == "END CHAT":
            end_support_session(uid)
            return
        if txt == "/start":
            temp_data.pop(f"support_mode_{uid}", None)
            return welcome(message)
        if not precheck(message, require_join=False):
            return
        relay_user_to_admins(message)
    except Exception:
        log_exc("support_relay_handler")


@bot.message_handler(
    content_types=["text", "photo", "video", "animation", "document", "sticker"],
    func=lambda m: is_admin(m.from_user.id) and not (
        m.content_type == "document" and getattr(m, "document", None) and (m.document.file_name or "").lower().endswith(".txt")
    ) and bool(extract_forwarded_premium_ids(m))
)
def forwarded_premium_emoji_preview(message):
    try:
        if not precheck(message, require_join=False):
            return
        ids = extract_forwarded_premium_ids(message)
        if not ids:
            _send_pe(message.chat.id, f"{P} No premium emoji IDs found. Forward a Premium Emoji IDs post to this bot.", use_main=False, reply_markup=admin_menu())
            return
        show_forwarded_emoji_preview(message, ids)
    except Exception:
        log_exc("forwarded_premium_emoji_preview")


# ======================== BULK TXT DIRECT + DIRECT CONVERT ========================
@bot.message_handler(content_types=["document"], func=lambda m: is_admin(m.from_user.id) and (m.document.file_name or "").lower().endswith(".txt"))
def direct_admin_txt_import(message):
    try:
        if not precheck(message, require_join=False): return
        pack_slug = temp_data.pop(f"bulk_pack_{message.from_user.id}", get_default_pack_slug())
        status = _send_pe(message.chat.id, f"{P} Starting premium emoji import...", use_main=False)
        def cb(stage, done, total, force=False):
            edit_loading(status, "PREMIUM TXT IMPORT", stage, done, total, force)
        cb("Downloading TXT file", 5, 100, True)
        file_info = bot.get_file(message.document.file_id)
        raw = bot.download_file(file_info.file_path)
        cb("Reading and extracting IDs", 15, 100, True)
        content = raw.decode("utf-8", errors="ignore")
        ids = extract_emoji_ids(content)
        res = bulk_import_emoji_ids(ids, pack_slug, message.from_user.id, "direct_txt_import", progress_callback=cb)
        final_text = (
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n"
            f"{P}      BULK IMPORT DONE      {P}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}\n\n"
            f"{P} Target Pack : {pack_slug}\n"
            f"{P} Found IDs    : {res.get('found')}\n"
            f"{P} Inserted     : {res.get('inserted')}\n"
            f"{P} Duplicates   : {res.get('duplicates')}\n"
            f"{P} Pack Total   : {res.get('pack_count')}\n"
            f"{P}━━━━━━━━━━━━━━━━━━━━{P}"
        )
        if status:
            _edit_pe(message.chat.id, status.message_id, final_text, use_main=False, reply_markup=admin_home_markup())
        else:
            _send_pe(message.chat.id, final_text, use_main=False, reply_markup=admin_menu())
    except Exception:
        log_exc("direct_admin_txt_import")

@bot.message_handler(commands=["syncemojis", "resolveemojis"])
def sync_emojis_command(message):
    """Admin: force-resolve the real emoji behind every premium id so Smart Match
    places the SAME emoji users type. Runs in the background with live progress."""
    try:
        uid = message.from_user.id
        if not is_admin(uid):
            return
        pending = emojis_col.count_documents(
            {"active": True, "$or": [{"base_emoji": {"$exists": False}}, {"base_emoji": None}, {"base_emoji": ""}]}
        )
        if pending == 0:
            _send_pe(message.chat.id, f"{premium_header('EMOJI SYNC')}\n\n{P} All emojis are already synced for Smart Match.\n{premium_footer()}", use_main=False)
            return
        status = _send_pe(
            message.chat.id,
            f"{premium_header('EMOJI SYNC')}\n\n{P} Syncing {pending} emojis for Smart Match...\n{P} You can keep using the bot.\n{premium_footer()}",
            use_main=False,
        )
        chat_id = message.chat.id
        msg_id = status.message_id if status else None

        def _run():
            last = {"t": 0}

            def _progress(done, total):
                now = time.time()
                if msg_id and (now - last["t"] > 4 or done >= total):
                    last["t"] = now
                    try:
                        _edit_pe(chat_id, msg_id, f"{premium_header('EMOJI SYNC')}\n\n{P} Progress : {done}/{total}\n{premium_footer()}", use_main=False)
                    except Exception:
                        pass

            gained = resolve_all_emoji_bases(silent=True, progress_cb=_progress)
            if msg_id:
                try:
                    _edit_pe(chat_id, msg_id, f"{premium_header('EMOJI SYNC DONE')}\n\n{P} Newly matched : {gained}\n{P} Smart Match is now sharper.\n{premium_footer()}", use_main=False)
                except Exception:
                    pass

        threading.Thread(target=_run, daemon=True).start()
    except Exception:
        log_exc("sync_emojis_command")


@bot.message_handler(commands=["ping", "uptime"])
def ping_command(message):
    """Lightweight live status: round-trip latency, uptime and DB ping."""
    try:
        if not precheck(message, require_join=False):
            return
        t0 = time.time()
        probe = _send_pe(message.chat.id, f"{P} Pinging...", use_main=False)
        rtt_ms = int((time.time() - t0) * 1000)
        try:
            d0 = time.time()
            client.admin.command("ping")
            db_ms = f"{int((time.time() - d0) * 1000)}ms"
        except Exception:
            db_ms = "ERROR"
        text = (
            f"{premium_header('LIVE STATUS')}\n\n"
            f"{P} Status   : ONLINE\n"
            f"{P} Latency  : {rtt_ms}ms\n"
            f"{P} Database : {db_ms}\n"
            f"{P} Uptime   : {fmt_uptime()}\n"
            f"{premium_footer()}"
        )
        if probe:
            _edit_pe(message.chat.id, probe.message_id, text, use_main=False)
        else:
            _send_pe(message.chat.id, text, use_main=False)
    except Exception:
        log_exc("ping_command")


@bot.message_handler(content_types=["text"])
def direct_text_converter(message):
    try:
        if not precheck(message): return
        if not get_setting("bot", "direct_convert_enabled", True): return
        text = message.text or ""
        if text.startswith("/"): return
        if not has_unicode_emoji(text):
            _send_pe(message.chat.id, f"{P} Send text with emojis, or tap MAKE POST.", use_main=False, reply_markup=user_keyboard(message.from_user.id))
            return
        uid = message.from_user.id
        if not charge_conversion(uid, "direct_convert"):
            _send_pe(message.chat.id, f"{P} Not enough coins. Use DAILY BONUS or REFERRAL.", use_main=False)
            return
        pack_slug = smart_pack_for_text(text, uid) if user_auto_pack(uid) else get_user_pack_slug(uid)
        styled_text, did_style = apply_output_style(text, uid)
        final_text, ents = process_text_with_duplicate_emojis(styled_text, [] if did_style else (message.entities or []), pack_slug)
        bot.send_message(message.chat.id, final_text, entities=ents, parse_mode=None)
        inc_user(uid, "conversions", 1)
        inc_user(uid, "score", 1)
        runtime_metrics["conversions"] = runtime_metrics.get("conversions", 0) + 1
        track_event("conversion", uid, {"source": "direct", "pack_slug": pack_slug})
    except Exception:
        log_exc("direct_text_converter")


@bot.message_handler(content_types=["photo", "video", "audio", "voice", "sticker", "animation", "document", "contact", "location"])
def fallback_non_text(message):
    try:
        if precheck(message):
            _send_pe(message.chat.id, f"{P} Tap MAKE POST first to convert media captions or attach files.", use_main=False, reply_markup=user_keyboard(message.from_user.id))
    except Exception:
        log_exc("fallback_non_text")

# ======================== MAIN ========================
def start_bot():
    bootstrap_database()
    try:
        get_bot_username()
    except Exception:
        pass
    try:
        scheduler.start()
        schedule_pending_broadcasts()
    except Exception:
        log_exc("scheduler_start")

    # Warm up Smart Emoji Match in the background so 'Make Post' gets more
    # accurate over time without ever blocking the bot at startup.
    try:
        threading.Thread(target=resolve_all_emoji_bases, kwargs={"silent": True}, daemon=True).start()
    except Exception:
        log_exc("startup_resolve")

    print("╔═══════════════════════════════════════��═══════════════════���══╗")
    print("║ 🔥 GADGET PREMIUM EMOJI ULTIMATE ADVANCED v20.0             ║")
    print("║ Forward Collector + TXT Vault + Backup + Dynamic Premium Engine          ║")
    print("║ Self-healing polling • Live status • Smarter admin tools     ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # Self-healing polling: exponential backoff on failure, auto-reset on success,
    # MongoDB re-ping before each restart so the bot recovers from network drops.
    backoff = 3
    max_backoff = 60
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20, skip_pending=True)
            backoff = 3  # clean exit -> reset backoff
        except KeyboardInterrupt:
            log.info("Shutdown requested. Stopping bot.")
            break
        except ApiTelegramException as e:
            if getattr(e, "error_code", None) == 401 or "Unauthorized" in str(e):
                log.error(
                    "Telegram API returned 401 Unauthorized. Your TOKEN is invalid, revoked, or copied incorrectly. "
                    "Generate a new token in @BotFather and paste it into the TOKEN = \"...\" line."
                )
                break
            log_exc("polling_crash_restart")
            try:
                client.admin.command("ping")
            except Exception:
                log.warning("MongoDB unreachable during restart; will keep retrying.")
            log.warning("Polling restarting in %ss...", backoff)
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
        except Exception:
            log_exc("polling_crash_restart")
            log.warning("Polling restarting in %ss...", backoff)
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)


if __name__ == "__main__":
    start_bot()
