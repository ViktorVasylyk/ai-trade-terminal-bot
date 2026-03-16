import asyncio
import hashlib
import hmac
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qsl

import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

# ================== ENV / SETTINGS ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7713470997:AAG0jqwe0fiYb1Qn-lSRVvvgrePcuAyeZ4M")
BASE_URL = os.getenv("BASE_URL", "https://your-domain.up.railway.app")
PORT = int(os.getenv("PORT", "8080"))

PARTNER_ID = os.getenv("PARTNER_ID", "51641")
API_TOKEN = os.getenv("API_TOKEN", "AdrPoT7UjHjggMAJNda3")

REF_LINK = os.getenv("REF_LINK", "https://u3.shortink.io/smart/ROGGOnnWSoGn5O")
REVIEWS_GROUP_LINK = os.getenv("REVIEWS_GROUP_LINK", "https://t.me/+6jtb0MDtb_A0YTQy")

BASE_DIR = Path(__file__).resolve().parent
BANNER_PATH = BASE_DIR / "vip_banner.png"
ALLOWED_USERS_FILE = BASE_DIR / "allowed_users.json"

AUTO_CHECK_EVERY_SEC = 10 * 60
AUTO_CHECK_TOTAL_SEC = 3 * 60 * 60
AUTO_CHECK_MAX_RUNS = max(1, AUTO_CHECK_TOTAL_SEC // AUTO_CHECK_EVERY_SEC)

router = Router()

# ================== ACCESS STORAGE ==================
def load_allowed_users() -> set[int]:
    if not ALLOWED_USERS_FILE.exists():
        return set()
    try:
        data = json.loads(ALLOWED_USERS_FILE.read_text(encoding="utf-8"))
        return {int(x) for x in data}
    except Exception:
        return set()


def save_allowed_users(users: set[int]) -> None:
    ALLOWED_USERS_FILE.write_text(
        json.dumps(sorted(list(users)), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def allow_user(user_id: int) -> None:
    users = load_allowed_users()
    users.add(int(user_id))
    save_allowed_users(users)


def is_user_allowed(user_id: int) -> bool:
    return int(user_id) in load_allowed_users()


def verify_telegram_init_data(init_data: str, bot_token: str) -> Optional[dict]:
    if not init_data:
        return None

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if calculated_hash != received_hash:
        return None

    user_raw = pairs.get("user")
    if not user_raw:
        return None

    try:
        return json.loads(user_raw)
    except Exception:
        return None


# ================== TEXTS ==================
VIP_CAPTION = (
    "☑️ <b>ВАРИАНТЫ VIP ПОДПИСКИ</b>\n"
    "Пожалуйста выберите вариант\n"
    "по которому хотите попасть в закрытый чат 👇🏻"
)

FREE_TEXT = (
    "🎁 <b>БОТ БЕСПЛАТНО</b>\n\n"
    "<b>Чтобы получить доступ, сделай 3 простых шага:</b>\n\n"
    "1️⃣ <b>Зарегистрируйся по моей ссылке</b>\n"
    f"👉 {REF_LINK}\n\n"
    "⚠️ <b>ВАЖНО</b>\n"
    "Если у тебя уже есть аккаунт Pocket Option — старый аккаунт нужно удалить.\n"
    "Торговать можно только на аккаунте, который зарегистрирован по моей ссылке.\n\n"
    "Если этого не сделать — пароль будет изменён, и ты потеряешь доступ к боту.\n\n"
    "2️⃣ <b>Внеси депозит</b>\n"
    "Рекомендую от <b>50$</b> для комфортной работы.\n\n"
    "3️⃣ <b>Нажми «Скинуть ID для проверки»</b> ✅"
)

BOT_ACCESS_TEXT = (
    "💎 <b>Доступ открыт</b>\n\n"
    "Нажми кнопку ниже, чтобы открыть торговый терминал.\n\n"
    "⚠️ <b>ВАЖНО</b>\n"
    "Торговать можно только на аккаунте, который зарегистрирован по моей ссылке.\n"
    "Если будешь торговать на старом/другом аккаунте —\n"
    "ты потеряешь доступ к боту."
)


def make_recruit_text() -> str:
    online = random.randint(120, 210)
    left_slots = random.randint(3, 9)
    today_profit = random.randint(900, 5800)
    return (
        "🔥 <b>ОТКРЫТ НАБОР В VIP</b>\n\n"
        f"👥 Онлайн сейчас: <b>{online}</b>\n"
        f"🎯 Осталось мест: <b>{left_slots}</b>\n"
        f"📈 Сегодня в чате: <b>+${today_profit}</b>\n\n"
        "Успей попасть в команду 🚀"
    )


# ================== KEYBOARDS ==================
def terminal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚀 Открыть терминал",
                    web_app=WebAppInfo(url=f"{BASE_URL}/app"),
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Нажми кнопку, чтобы открыть терминал",
    )


def kb_want_team() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 ХОЧУ В КОМАНДУ", callback_data="open_vip")]
        ]
    )


def vip_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="БЕСПЛАТНО-реферальная ссылка", callback_data="free_info")],
            [InlineKeyboardButton(text="ОТЗЫВЫ УЧАСТНИКОВ", url=REVIEWS_GROUP_LINK)],
        ]
    )


def free_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔗 Перейти по ссылке", url=REF_LINK),
                InlineKeyboardButton(text="📨 Скинуть ID для проверки", callback_data="send_id"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_vip")],
        ]
    )


def deposit_check_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 ДЕПОЗИТ СДЕЛАЛ — СКИНУТЬ ID НА ПРОВЕРКУ",
                    callback_data="send_id",
                )
            ]
        ]
    )


# ================== AFFILIATE API ==================
def make_hash(user_id: str, partner_id: str, api_token: str) -> str:
    raw = f"{user_id}:{partner_id}:{api_token}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


async def fetch_user_info(trader_id: str) -> Dict[str, Any]:
    h = make_hash(trader_id, PARTNER_ID, API_TOKEN)
    url = f"https://affiliate.pocketoption.com/api/user-info/{trader_id}/{PARTNER_ID}/{h}"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PocketAffiliateBot/1.0)",
        "Accept": "application/json,text/plain,*/*",
    }

    async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=headers) as client:
        r = await client.get(url)

        if r.status_code != 200:
            try:
                return {"_http_status": r.status_code, "_error_json": r.json()}
            except Exception:
                return {"_http_status": r.status_code, "_error_text": r.text[:800]}

        return r.json()


def _to_number(v: Any) -> Optional[float]:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None
    return None


def find_ftd_anywhere(obj: Any) -> bool:
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_low = str(k).lower()

            if k_low == "sum_ftd":
                num = _to_number(v)
                if num is not None and num > 0:
                    return True

            if k_low in {"ftd", "is_ftd", "has_ftd", "first_deposit", "first_deposit_done"}:
                if v in (1, True, "1", "true", "True", "yes", "YES"):
                    return True

            if k_low in {"ftd_amount", "ftd_sum", "first_deposit_amount", "deposits_sum", "deposit_sum", "total_deposits"}:
                num = _to_number(v)
                if num is not None and num > 0:
                    return True

            if "ftd" in k_low or ("first" in k_low and "deposit" in k_low):
                if v in (1, True, "1", "true", "True"):
                    return True
                num = _to_number(v)
                if num is not None and num > 0:
                    return True

        return any(find_ftd_anywhere(x) for x in obj.values())

    if isinstance(obj, list):
        return any(find_ftd_anywhere(x) for x in obj)

    return False


def parse_status(data: Dict[str, Any]) -> Tuple[bool, bool]:
    if not isinstance(data, dict):
        return False, False

    if "_http_status" in data:
        return False, False

    if data.get("error") is True:
        return False, False

    is_registered = any(
        k in data and data.get(k) not in (None, "", False, 0)
        for k in ("user_id", "trader_id", "id", "status", "email", "country", "currency", "sum_ftd")
    )

    is_ftd = find_ftd_anywhere(data)
    return is_registered, is_ftd


# ================== AUTO CHECK ==================
PENDING: Dict[int, Dict[str, Any]] = {}
WAITING_ID = set()


async def send_terminal_access(message: Message):
    await message.answer(
        BOT_ACCESS_TEXT,
        parse_mode="HTML",
        reply_markup=terminal_keyboard(),
    )


async def auto_check_loop(tg_id: int, trader_id: str, chat_id: int, bot: Bot):
    runs_left = AUTO_CHECK_MAX_RUNS
    await asyncio.sleep(random.randint(10, 45))

    while runs_left > 0:
        state = PENDING.get(tg_id)
        if not state:
            return

        trader_id = state.get("trader_id", trader_id)
        chat_id = state.get("chat_id", chat_id)

        try:
            data = await fetch_user_info(trader_id)
            if "_http_status" not in data:
                is_reg, is_ftd = parse_status(data)
                if is_reg and is_ftd:
                    allow_user(tg_id)
                    PENDING.pop(tg_id, None)
                    await bot.send_message(
                        chat_id,
                        "✅ <b>FTD подтвержден!</b>\n🔥 Доступ активирован 🚀",
                        parse_mode="HTML",
                    )
                    await bot.send_message(
                        chat_id,
                        BOT_ACCESS_TEXT,
                        parse_mode="HTML",
                        reply_markup=terminal_keyboard(),
                    )
                    return
        except Exception:
            pass

        runs_left -= 1
        if PENDING.get(tg_id):
            PENDING[tg_id]["runs_left"] = runs_left

        await asyncio.sleep(AUTO_CHECK_EVERY_SEC + random.randint(0, 30))

    PENDING.pop(tg_id, None)
    try:
        await bot.send_message(
            chat_id,
            "⏳ Я проверял FTD автоматически, но депозит ещё не отобразился.\n\n"
            "Если депозит уже сделал — нажми кнопку и скинь ID ещё раз ✅",
            parse_mode="HTML",
            reply_markup=deposit_check_kb(),
        )
    except Exception:
        pass


def start_or_refresh_auto_check(tg_id: int, trader_id: str, chat_id: int, bot: Bot):
    if tg_id in PENDING and PENDING[tg_id].get("task") and not PENDING[tg_id]["task"].done():
        PENDING[tg_id]["trader_id"] = trader_id
        PENDING[tg_id]["chat_id"] = chat_id
        return

    task = asyncio.create_task(auto_check_loop(tg_id, trader_id, chat_id, bot))
    PENDING[tg_id] = {
        "task": task,
        "trader_id": trader_id,
        "chat_id": chat_id,
        "runs_left": AUTO_CHECK_MAX_RUNS,
    }


# ================== HELPERS ==================
async def send_vip_screen(message: Message):
    if not BANNER_PATH.exists():
        await message.answer(f"❌ Не найден vip_banner.png\nПуть:\n{BANNER_PATH}")
        return

    banner = FSInputFile(str(BANNER_PATH))
    await message.answer_photo(
        photo=banner,
        caption=VIP_CAPTION,
        parse_mode="HTML",
        reply_markup=vip_buttons(),
    )


def normalize_id(text: str) -> str:
    return (text or "").strip().replace(" ", "")


def looks_like_id(text: str) -> bool:
    return text.isdigit() and 4 <= len(text) <= 20


# ================== BOT HANDLERS ==================
@router.message(Command("start"))
async def start_handler(message: Message):
    if is_user_allowed(message.from_user.id):
        await message.answer(
            "💎 <b>Доступ уже открыт</b>\n\n"
            "Нажми кнопку ниже, чтобы открыть торговый терминал.",
            parse_mode="HTML",
            reply_markup=terminal_keyboard(),
        )
        return

    await message.answer(
        make_recruit_text(),
        parse_mode="HTML",
        reply_markup=kb_want_team(),
    )


@router.message(Command("strat"))
async def strat_handler(message: Message):
    if is_user_allowed(message.from_user.id):
        await message.answer(
            "💎 <b>Доступ уже открыт</b>\n\n"
            "Нажми кнопку ниже, чтобы открыть торговый терминал.",
            parse_mode="HTML",
            reply_markup=terminal_keyboard(),
        )
        return

    await message.answer(
        make_recruit_text(),
        parse_mode="HTML",
        reply_markup=kb_want_team(),
    )


@router.message(Command("terminal"))
async def terminal_handler(message: Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer(
            "⛔ <b>Доступ закрыт</b>\n\n"
            "Сначала пройди регистрацию и FTD.",
            parse_mode="HTML",
        )
        return

    await message.answer(
        "🚀 <b>Открытие терминала</b>",
        parse_mode="HTML",
        reply_markup=terminal_keyboard(),
    )


@router.callback_query(F.data == "open_vip")
async def open_vip(callback: CallbackQuery):
    await callback.answer()
    await send_vip_screen(callback.message)


@router.callback_query(F.data == "free_info")
async def free_info_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption=FREE_TEXT,
        parse_mode="HTML",
        reply_markup=free_kb(),
    )


@router.callback_query(F.data == "send_id")
async def send_id_handler(callback: CallbackQuery):
    await callback.answer()
    WAITING_ID.add(callback.from_user.id)
    await callback.message.answer(
        "🆔 <b>Скиньте ваш ID торгового аккаунта в чат</b> 👇\n\n"
        "⏳ <b>Проверка</b> займет от <b>1</b> минуты до <b>30</b> минут ✅",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_vip")
async def back_to_vip(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_caption(
        caption=VIP_CAPTION,
        parse_mode="HTML",
        reply_markup=vip_buttons(),
    )


@router.message(F.text)
async def catch_id_message(message: Message):
    if message.from_user.id not in WAITING_ID:
        return

    trader_id = normalize_id(message.text)
    if not looks_like_id(trader_id):
        await message.answer("❌ ID должен быть только цифрами. Отправь ID ещё раз ✅")
        return

    WAITING_ID.discard(message.from_user.id)
    wait_msg = await message.answer("⏳ <b>Проверяем…</b> Подожди пару секунд ✅", parse_mode="HTML")

    try:
        data = await fetch_user_info(trader_id)

        if "_http_status" in data:
            status = data.get("_http_status")
            err_txt = ""
            if "_error_json" in data:
                err_txt = json.dumps(data["_error_json"], ensure_ascii=False)[:800]
            else:
                err_txt = str(data.get("_error_text", ""))[:800]

            if status == 404:
                await wait_msg.edit_text(
                    "❌ <b>ID не найдено</b>\n\n"
                    "Проверь правильность ID.\n"
                    "Важно: аккаунт должен быть зарегистрирован по моей ссылке ✅",
                    parse_mode="HTML",
                )
                return

            await wait_msg.edit_text(
                "⚠️ <b>Ошибка проверки</b>\n\n"
                f"Сервис вернул статус: <code>{status}</code>\n"
                f"<code>{err_txt}</code>\n\n"
                "Попробуй снова через пару минут ✅",
                parse_mode="HTML",
            )
            return

        is_reg, is_ftd = parse_status(data)

        if not is_reg:
            await wait_msg.edit_text(
                "❌ <b>ID не найдено</b>\n\n"
                "Проверь правильность ID.\n"
                "Важно: аккаунт должен быть зарегистрирован по моей ссылке ✅",
                parse_mode="HTML",
            )
            return

        if is_ftd:
            allow_user(message.from_user.id)

            await wait_msg.edit_text(
                "✅ <b>FTD подтвержден</b>\n\n"
                "🔥 Доступ активирован. Добро пожаловать в VIP 🚀",
                parse_mode="HTML",
            )

            if message.from_user.id in PENDING:
                PENDING.pop(message.from_user.id, None)

            await send_terminal_access(message)

        else:
            start_or_refresh_auto_check(message.from_user.id, trader_id, message.chat.id, message.bot)

            minutes = AUTO_CHECK_EVERY_SEC // 60
            hours = AUTO_CHECK_TOTAL_SEC // 3600
            await wait_msg.edit_text(
                "✅ <b>Регистрация подтверждена</b>\n\n"
                "💳 Теперь сделай депозит (FTD) — после этого выдадим полный доступ ✅\n\n"
                f"🤖 Я буду проверять FTD автоматически каждые <b>{minutes} мин</b> (до <b>{hours} часов</b>) и открою доступ сразу, как депозит отобразится.",
                parse_mode="HTML",
                reply_markup=deposit_check_kb(),
            )

    except Exception as ex:
        await wait_msg.edit_text(
            "⚠️ <b>Ошибка проверки</b>\n\n"
            "Попробуй снова через пару минут ✅",
            parse_mode="HTML",
        )
        print("ERROR:", repr(ex))


# ================== TERMINAL HTML ==================
def build_html() -> str:
    return r"""
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Chrome Trade Terminal</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root{
      --bg:#0d0f13;
      --card:#181c22;
      --card2:#232832;
      --line:rgba(255,255,255,.10);
      --text:#f4f7fb;
      --muted:#b4bcc8;
      --silver1:#f2f5f8;
      --silver2:#d4d9e0;
      --silver3:#a0a8b4;
      --green:#7df0b2;
      --red:#ff9d9d;
      --blue:#9fd0ff;
      --gold:#f0d89f;
      --shadow:0 14px 50px rgba(0,0,0,.35);
      --radius:22px;
    }

    *{
      box-sizing:border-box;
      margin:0;
      padding:0;
      font-family:Inter,Arial,sans-serif;
      -webkit-tap-highlight-color:transparent;
    }

    body{
      min-height:100vh;
      color:var(--text);
      background:
        radial-gradient(circle at top right, rgba(255,255,255,.07), transparent 20%),
        radial-gradient(circle at bottom left, rgba(205,210,220,.08), transparent 25%),
        linear-gradient(180deg, #0b0d11 0%, #14181e 50%, #0b0e12 100%);
    }

    .wrap{
      max-width:560px;
      margin:0 auto;
      padding:16px 16px 104px;
    }

    .screen{display:none; animation:fade .22s ease;}
    .screen.active{display:block;}

    @keyframes fade{
      from{opacity:.45; transform:translateY(8px);}
      to{opacity:1; transform:translateY(0);}
    }

    .topbar{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
      margin-bottom:16px;
    }

    .brand{
      display:flex;
      align-items:center;
      gap:12px;
    }

    .logo{
      width:48px;
      height:48px;
      border-radius:16px;
      background:
        linear-gradient(135deg, #6b7380 0%, #e3e8ee 30%, #8e97a3 55%, #f4f7fb 100%);
      color:#111318;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:20px;
      font-weight:900;
      box-shadow:var(--shadow);
      border:1px solid rgba(255,255,255,.22);
    }

    .title{
      font-size:22px;
      font-weight:900;
      color:var(--silver1);
      letter-spacing:.2px;
    }

    .subtitle{
      color:var(--muted);
      font-size:12px;
      margin-top:3px;
    }

    .vip{
      border-radius:14px;
      padding:9px 12px;
      font-weight:900;
      font-size:12px;
      color:#111318;
      white-space:nowrap;
      background:
        linear-gradient(135deg, #808995 0%, #d8dde4 35%, #9ea7b1 60%, #f5f8fb 100%);
      border:1px solid rgba(255,255,255,.16);
      box-shadow:var(--shadow);
    }

    .card{
      margin-bottom:14px;
      padding:16px;
      border-radius:var(--radius);
      background:
        linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02)),
        linear-gradient(180deg, var(--card), var(--card2));
      border:1px solid var(--line);
      box-shadow:var(--shadow);
      backdrop-filter:blur(12px);
    }

    .hero{
      padding:24px 18px;
      background:
        radial-gradient(circle at top right, rgba(255,255,255,.16), transparent 24%),
        radial-gradient(circle at bottom left, rgba(255,255,255,.05), transparent 22%),
        linear-gradient(135deg, #21262e, #11161d 60%, #2b313a);
      overflow:hidden;
      position:relative;
    }

    .hero::before{
      content:"";
      position:absolute;
      top:-40px;
      right:-40px;
      width:120px;
      height:120px;
      border-radius:50%;
      background:radial-gradient(circle, rgba(255,255,255,.14), transparent 70%);
      filter:blur(6px);
    }

    .hero::after{
      content:"";
      position:absolute;
      left:-30px;
      bottom:-30px;
      width:160px;
      height:160px;
      border-radius:50%;
      background:radial-gradient(circle, rgba(255,255,255,.05), transparent 70%);
      filter:blur(10px);
    }

    .hero-badge{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:8px 12px;
      border-radius:999px;
      font-size:11px;
      font-weight:900;
      color:#111318;
      margin-bottom:12px;
      background:
        linear-gradient(135deg, #8b95a1 0%, #d9dee5 38%, #9fa8b2 60%, #f3f6fa 100%);
      box-shadow:var(--shadow);
      border:1px solid rgba(255,255,255,.14);
    }

    .hero-title{
      font-size:28px;
      font-weight:900;
      line-height:1.1;
      margin-bottom:10px;
      color:#f8fbff;
      max-width:390px;
    }

    .hero-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.65;
      max-width:450px;
    }

    .hero-panel{
      margin-top:16px;
      padding:14px;
      border-radius:18px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02)),
        #12171f;
      border:1px solid rgba(255,255,255,.08);
    }

    .hero-panel-title{
      font-size:13px;
      font-weight:900;
      margin-bottom:8px;
      color:#f3f6fa;
    }

    .hero-panel-text{
      font-size:13px;
      line-height:1.6;
      color:var(--muted);
    }

    .section-title{
      font-size:18px;
      font-weight:900;
      margin-bottom:12px;
      color:#f4f7fb;
    }

    .section-sub{
      color:var(--muted);
      font-size:13px;
      margin-bottom:12px;
      line-height:1.55;
    }

    .menu-grid{
      display:grid;
      grid-template-columns:1fr;
      gap:12px;
    }

    .menu-btn{
      width:100%;
      border:none;
      cursor:pointer;
      border-radius:20px;
      padding:16px;
      text-align:left;
      color:#fff;
      background:
        linear-gradient(135deg, rgba(255,255,255,.09), rgba(255,255,255,.02)),
        linear-gradient(135deg, #1a1f27, #2b313a 55%, #161a21);
      border:1px solid rgba(255,255,255,.10);
      box-shadow:var(--shadow);
    }

    .menu-btn.primary{
      color:#111318;
      background:
        linear-gradient(135deg, #88919d 0%, #d7dce3 35%, #9fa8b3 60%, #f3f6fa 100%);
      border:1px solid rgba(255,255,255,.15);
    }

    .menu-title{
      font-size:16px;
      font-weight:900;
      margin-bottom:4px;
    }

    .menu-desc{
      font-size:12px;
      line-height:1.5;
      color:#d8dee7;
      opacity:.95;
    }

    .menu-btn.primary .menu-desc{
      color:#2f363f;
    }

    .search{
      width:100%;
      background:#12161c;
      color:#fff;
      border:1px solid rgba(255,255,255,.10);
      border-radius:16px;
      padding:14px;
      outline:none;
      font-size:14px;
      margin-bottom:12px;
    }

    .tf-row{
      display:flex;
      gap:8px;
      flex-wrap:wrap;
      margin-bottom:14px;
    }

    .tf-btn{
      border:none;
      cursor:pointer;
      padding:10px 12px;
      border-radius:14px;
      background:#1b212a;
      color:#d9dfe7;
      border:1px solid rgba(255,255,255,.08);
      font-size:12px;
      font-weight:800;
    }

    .tf-btn.active{
      color:#101216;
      background:
        linear-gradient(135deg, #8c95a2 0%, #d8dde4 38%, #9da6b1 62%, #eef2f6 100%);
    }

    .asset-list{
      display:flex;
      flex-direction:column;
      gap:10px;
      margin-bottom:8px;
    }

    .asset-item{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
      padding:14px;
      border-radius:18px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01)),
        #131820;
      border:1px solid rgba(255,255,255,.07);
      cursor:pointer;
      box-shadow:var(--shadow);
    }

    .asset-name{
      font-size:15px;
      font-weight:900;
    }

    .asset-meta{
      margin-top:4px;
      color:var(--muted);
      font-size:12px;
    }

    .badge-mini{
      font-size:11px;
      font-weight:900;
      border-radius:12px;
      padding:8px 10px;
      background:rgba(255,255,255,.08);
      color:#edf1f6;
      white-space:nowrap;
      border:1px solid rgba(255,255,255,.08);
    }

    .loading-box{
      margin-top:12px;
      border-radius:20px;
      padding:18px;
      background:
        linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.02)),
        #151a22;
      border:1px solid rgba(255,255,255,.08);
      display:none;
    }

    .loading-title{
      font-size:16px;
      font-weight:900;
      margin-bottom:8px;
    }

    .loading-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.6;
      margin-bottom:12px;
    }

    .loading-bar{
      width:100%;
      height:10px;
      background:#1a212b;
      border-radius:999px;
      overflow:hidden;
      border:1px solid rgba(255,255,255,.06);
    }

    .loading-fill{
      height:100%;
      width:0%;
      background:
        linear-gradient(135deg, #8d96a3 0%, #d4d9e0 35%, #a2abb5 65%, #eef2f6 100%);
      transition:width .2s linear;
    }

    .analysis-box{
      margin-top:12px;
      border-radius:20px;
      padding:16px;
      background:
        linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.02)),
        #141a23;
      border:1px solid rgba(255,255,255,.08);
      box-shadow:var(--shadow);
    }

    .analysis-head{
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:12px;
      margin-bottom:14px;
    }

    .analysis-label{
      color:var(--muted);
      font-size:12px;
      margin-bottom:6px;
    }

    .analysis-asset{
      font-size:24px;
      font-weight:900;
      margin-bottom:4px;
    }

    .analysis-market{
      font-size:12px;
      color:var(--muted);
    }

    .strength-badge{
      min-width:92px;
      text-align:center;
      padding:10px 12px;
      border-radius:16px;
      color:#111318;
      font-weight:900;
      font-size:14px;
      background:
        linear-gradient(135deg, #8a93a0 0%, #dde2e8 38%, #9ea7b2 60%, #f5f8fb 100%);
      border:1px solid rgba(255,255,255,.14);
      box-shadow:var(--shadow);
    }

    .signal-row{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      margin-bottom:12px;
    }

    .chip{
      padding:10px 12px;
      border-radius:14px;
      background:#18202b;
      border:1px solid rgba(255,255,255,.06);
      font-size:12px;
      font-weight:900;
    }

    .dir-up{color:var(--green);}
    .dir-down{color:var(--red);}

    .analysis-comment{
      color:#dce3ec;
      font-size:14px;
      line-height:1.65;
      margin-bottom:12px;
    }

    .chart-card,.scheme-card{
      margin:14px 0;
      border-radius:18px;
      padding:12px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01)),
        #11161d;
      border:1px solid rgba(255,255,255,.07);
    }

    .chart-head{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:8px;
    }

    .chart-title{
      font-size:13px;
      font-weight:900;
      color:#f0f4f9;
    }

    .chart-sub{
      font-size:11px;
      color:var(--muted);
    }

    .chart-wrap{
      height:180px;
      width:100%;
      border-radius:14px;
      overflow:hidden;
      background:
        linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.00)),
        #0d1218;
      border:1px solid rgba(255,255,255,.05);
      position:relative;
    }

    #liveChart{
      width:100%;
      height:100%;
      display:block;
    }

    .action-btn,
    .next-btn,
    .back-btn{
      width:100%;
      border:none;
      cursor:pointer;
      border-radius:16px;
      padding:14px;
      font-size:14px;
      font-weight:900;
      margin-top:10px;
      box-shadow:var(--shadow);
    }

    .action-btn.primary,
    .next-btn{
      color:#111318;
      background:
        linear-gradient(135deg, #8b95a1 0%, #d8dde4 38%, #9da5b0 62%, #f1f4f7 100%);
      border:1px solid rgba(255,255,255,.12);
    }

    .action-btn.secondary,
    .back-btn{
      color:#fff;
      background:#1a2029;
      border:1px solid rgba(255,255,255,.08);
    }

    .support-item,
    .lesson-box,
    .strategy-box{
      padding:14px;
      border-radius:18px;
      background:#141a22;
      border:1px solid rgba(255,255,255,.07);
      margin-bottom:10px;
    }

    .support-title{
      font-size:15px;
      font-weight:900;
      margin-bottom:5px;
    }

    .support-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.6;
    }

    .lesson-kicker,.strategy-kicker{
      color:#d9dde3;
      font-size:11px;
      font-weight:900;
      letter-spacing:.4px;
      margin-bottom:8px;
      text-transform:uppercase;
    }

    .lesson-title,.strategy-title-big{
      font-size:20px;
      font-weight:900;
      margin-bottom:10px;
      line-height:1.25;
    }

    .lesson-text{
      color:#dce3ec;
      font-size:14px;
      line-height:1.75;
      margin-bottom:12px;
    }

    .lesson-main{
      padding:12px;
      border-radius:14px;
      background:rgba(255,255,255,.06);
      border:1px solid rgba(255,255,255,.10);
      color:#f0f4f9;
      font-size:13px;
      line-height:1.6;
    }

    .strategy-section{
      margin-bottom:14px;
    }

    .strategy-section-title{
      font-size:14px;
      font-weight:900;
      margin-bottom:6px;
      color:#f2f5f8;
    }

    .strategy-section-text{
      color:#dbe2ea;
      font-size:14px;
      line-height:1.72;
    }

    .scheme-wrap{
      width:100%;
      border-radius:14px;
      overflow:hidden;
      border:1px solid rgba(255,255,255,.06);
      background:#0f141a;
    }

    .scheme-wrap svg{
      width:100%;
      height:auto;
      display:block;
    }

    .bottom-tabs{
      position:fixed;
      left:0;
      right:0;
      bottom:0;
      background:rgba(11,13,17,.96);
      backdrop-filter:blur(12px);
      border-top:1px solid rgba(255,255,255,.08);
      padding:10px 12px 14px;
      z-index:99;
    }

    .bottom-tabs-inner{
      max-width:560px;
      margin:0 auto;
      display:grid;
      grid-template-columns:repeat(4,1fr);
      gap:8px;
    }

    .tab-btn{
      border:none;
      cursor:pointer;
      border-radius:16px;
      padding:12px 6px;
      text-align:center;
      background:#171b22;
      color:#b8bec8;
      border:1px solid rgba(255,255,255,.06);
      font-size:11px;
      font-weight:900;
      line-height:1.2;
    }

    .tab-btn.active{
      color:#101216;
      background:
        linear-gradient(135deg, #8e98a4 0%, #d8dde4 38%, #9ba4af 60%, #eef2f6 100%);
    }

    .empty{
      color:var(--muted);
      text-align:center;
      padding:18px;
      font-size:13px;
    }
  </style>
</head>
<body>
  <div id="access-overlay" style="
    position:fixed;
    inset:0;
    z-index:99999;
    background:#0b0d11;
    color:#fff;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:24px;
    font-family:Arial,sans-serif;
  ">
    <div>
      <div style="font-size:22px;font-weight:700;margin-bottom:12px;">Проверка доступа...</div>
      <div style="font-size:14px;opacity:.8;">Подожди пару секунд</div>
    </div>
  </div>

  <div class="wrap">

    <div id="screen-home" class="screen active">
      <div class="topbar">
        <div class="brand">
          <div class="logo">⚡</div>
          <div>
            <div class="title">Chrome Trade Terminal</div>
            <div class="subtitle">Loft style • premium interface</div>
          </div>
        </div>
        <div class="vip">2026 PRO</div>
      </div>

      <div class="card hero">
        <div class="hero-badge">● PREMIUM TRADING WORKSPACE</div>
        <div class="hero-title">Торговый терминал нового поколения внутри Telegram</div>
        <div class="hero-text">
          Современный рабочий интерфейс с сигналами, анализом, обучением, стратегиями и поддержкой.
          Премиальный стартовый экран и единая логика работы внутри mini app.
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">Что внутри</div>
          <div class="hero-panel-text">
            4 рынка, быстрый выбор активов, 3-секундный анализ перед сигналом, живой демо-график,
            большой курс по бинарным опционам, психологический блок, технический анализ,
            smart money, японские свечи и набор логичных торговых стратегий со схемами.
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Главное меню</div>
        <div class="section-sub">Выбери раздел, с которого хочешь начать работу.</div>

        <div class="menu-grid">
          <button class="menu-btn primary" onclick="openTradeMenu()">
            <div class="menu-title">1. Начать торговлю</div>
            <div class="menu-desc">ОТС, официальные активы, акции, криптовалюта, поиск активов, таймфреймы и сигналы.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('education-menu')">
            <div class="menu-title">2. Обучение</div>
            <div class="menu-desc">Большой курс: что такое бинарные опционы, психология, рынок, теханализ, свечи, индикаторы, smart money, risk management.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('support')">
            <div class="menu-title">3. Поддержка</div>
            <div class="menu-desc">Помощь по терминалу, ответы на частые вопросы и связь с менеджером.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('strategies-menu')">
            <div class="menu-title">4. Торговые стратегии</div>
            <div class="menu-desc">10 подробно расписанных стратегий с логикой входа, фильтрами, ошибками новичков и схемами.</div>
          </button>
        </div>
      </div>
    </div>

    <div id="screen-trade-menu" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">📈</div>
          <div>
            <div class="title">Начать торговлю</div>
            <div class="subtitle">Выбери нужный рынок</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Рынки</div>

        <div class="menu-grid">
          <button class="menu-btn primary" onclick="openMarket('otc')">
            <div class="menu-title">1. Торговля ОТС</div>
            <div class="menu-desc">Топовые OTC активы, поиск, таймфреймы и выдача сигнала после 3-секундного анализа.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('official')">
            <div class="menu-title">2. Торговля Официалов</div>
            <div class="menu-desc">Официальные валютные пары с поиском, таймфреймами и генерацией сигнала после 3-секундного анализа.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('stocks')">
            <div class="menu-title">3. Торговля Акциями</div>
            <div class="menu-desc">Популярные акции с быстрым переходом к анализу и выдачей сигнала после 3 секунд загрузки.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('crypto')">
            <div class="menu-title">4. Торговля криптовалютой</div>
            <div class="menu-desc">Криптоактивы с поиском, таймфреймами и генерацией сигнала после 3 секунд анализа.</div>
          </button>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-market-list" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">💹</div>
          <div>
            <div class="title" id="marketTitle">Рынок</div>
            <div class="subtitle" id="marketSub">Выбор актива</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Выбор актива</div>
        <input id="assetSearch" class="search" type="text" placeholder="Введи актив, например EUR/USD" oninput="renderAssets()" />

        <div class="tf-row">
          <button class="tf-btn active" data-tf="30 сек" onclick="selectTf('30 сек')">30 сек</button>
          <button class="tf-btn" data-tf="1 мин" onclick="selectTf('1 мин')">1 мин</button>
          <button class="tf-btn" data-tf="2 мин" onclick="selectTf('2 мин')">2 мин</button>
          <button class="tf-btn" data-tf="3 мин" onclick="selectTf('3 мин')">3 мин</button>
        </div>

        <div class="asset-list" id="assetList"></div>

        <button class="back-btn" onclick="showScreen('trade-menu')">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-analysis" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">🧠</div>
          <div>
            <div class="title">Анализ актива</div>
            <div class="subtitle">Подготовка и генерация сигнала</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="loading-box" id="loadingBox">
          <div class="loading-title">Анализируем актив...</div>
          <div class="loading-text" id="loadingText">Подготавливаем торговый сигнал</div>
          <div class="loading-bar">
            <div class="loading-fill" id="loadingFill"></div>
          </div>
        </div>

        <div class="analysis-box" id="analysisBox" style="display:none;">
          <div class="analysis-head">
            <div>
              <div class="analysis-label">Актив</div>
              <div class="analysis-asset" id="signalAsset">EUR/USD</div>
              <div class="analysis-market" id="signalMarketLine">OTC • 30 сек</div>
            </div>
            <div class="strength-badge">
              <div id="signalStrength">87%</div>
            </div>
          </div>

          <div class="signal-row">
            <div class="chip" id="signalDirection">ВВЕРХ</div>
            <div class="chip" id="signalTime">30 сек</div>
            <div class="chip" id="signalType">OTC</div>
          </div>

          <div class="analysis-comment" id="signalComment">
            Сигнал сгенерирован для тестового режима терминала.
          </div>

          <div class="chart-card">
            <div class="chart-head">
              <div>
                <div class="chart-title">Живой график</div>
                <div class="chart-sub">Демо-визуализация движения цены</div>
              </div>
            </div>
            <div class="chart-wrap">
              <canvas id="liveChart"></canvas>
            </div>
          </div>

          <button class="action-btn primary" onclick="generateCurrentSignal()">🔁 Сгенерировать еще сигнал</button>
          <button class="action-btn secondary" onclick="backToAssets()">📂 Выбрать другой актив</button>
        </div>

        <button class="back-btn" onclick="backToAssets()">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-education-menu" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">🎓</div>
          <div>
            <div class="title">Обучение</div>
            <div class="subtitle">Большой курс внутри терминала</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Разделы курса</div>
        <div class="section-sub">Пройди учебный блок по бинарным опционам, рынку, психологии и стратегиям принятия решений.</div>

        <div class="menu-grid">
          <button class="menu-btn primary" onclick="openLesson('binary', 0)">
            <div class="menu-title">1. Что такое бинарные опционы</div>
            <div class="menu-desc">Как работает контракт, экспирация, выплата, риски и типичные ошибки новичков.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('psychology', 0)">
            <div class="menu-title">2. Психология</div>
            <div class="menu-desc">Страх, жадность, тильт, дисциплина, пауза после минусов и правильное состояние перед сессией.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('market', 0)">
            <div class="menu-title">3. Что такое рынок</div>
            <div class="menu-desc">Импульс, откат, тренд, флет, волатильность, ликвидность, уровни.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('tech', 0)">
            <div class="menu-title">4. Технический анализ</div>
            <div class="menu-desc">Уровни, пробои, ложные пробои, трендовые линии, структура движения.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('candles', 0)">
            <div class="menu-title">5. Японские свечи</div>
            <div class="menu-desc">Пин-бар, поглощение, доджи, чтение тела и теней свечи в контексте рынка.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('indicators', 0)">
            <div class="menu-title">6. Индикаторы</div>
            <div class="menu-desc">EMA, RSI, Stochastic, MACD, Bollinger, ATR и как не перегрузить график.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('smartmoney', 0)">
            <div class="menu-title">7. Smart Money</div>
            <div class="menu-desc">Ликвидность, equal highs/lows, sweep, imbalance, displacement, order block.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('risk', 0)">
            <div class="menu-title">8. Risk Management</div>
            <div class="menu-desc">Фиксированная сумма, остановка сессии, серия убытков, контроль рисков и поведения.</div>
          </button>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-lesson" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">📚</div>
          <div>
            <div class="title" id="lessonCategoryTitle">Обучение</div>
            <div class="subtitle" id="lessonCategorySub">Теория и практика</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="lesson-box">
          <div class="lesson-kicker" id="lessonKicker">Урок 1</div>
          <div class="lesson-title" id="lessonTitle">Название урока</div>
          <div class="lesson-text" id="lessonText">Текст урока</div>
          <div class="lesson-main" id="lessonMain">Главная мысль</div>
        </div>

        <button class="next-btn" id="lessonNextBtn" onclick="nextLesson()">Следующий урок ➜</button>
        <button class="back-btn" onclick="backFromLesson()">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-strategies-menu" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">♟</div>
          <div>
            <div class="title">Торговые стратегии</div>
            <div class="subtitle">Практические модели входа</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Выбери стратегию</div>
        <div class="section-sub">Это обучающий раздел. Все стратегии надо применять только с фильтрацией рынка, а не механически.</div>
        <div class="menu-grid" id="strategiesList"></div>
        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-strategy-detail" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">📘</div>
          <div>
            <div class="title">Стратегия</div>
            <div class="subtitle">Подробное описание и схема</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="strategy-box">
          <div class="strategy-kicker" id="strategyKicker">Стратегия 1</div>
          <div class="strategy-title-big" id="strategyTitleBig">Название стратегии</div>

          <div class="strategy-section">
            <div class="strategy-section-title">Суть стратегии</div>
            <div class="strategy-section-text" id="strategyCore"></div>
          </div>

          <div class="scheme-card">
            <div class="chart-title" style="margin-bottom:10px;">Схема</div>
            <div class="scheme-wrap" id="strategyScheme"></div>
          </div>

          <div class="strategy-section">
            <div class="strategy-section-title">Как искать вход</div>
            <div class="strategy-section-text" id="strategyEntry"></div>
          </div>

          <div class="strategy-section">
            <div class="strategy-section-title">Фильтры и подтверждения</div>
            <div class="strategy-section-text" id="strategyFilters"></div>
          </div>

          <div class="strategy-section">
            <div class="strategy-section-title">Главные ошибки</div>
            <div class="strategy-section-text" id="strategyMistakes"></div>
          </div>

          <div class="strategy-section">
            <div class="strategy-section-title">Для каких рынков и таймфреймов</div>
            <div class="strategy-section-text" id="strategyMarkets"></div>
          </div>
        </div>

        <button class="next-btn" id="strategyNextBtn" onclick="nextStrategy()">Следующая стратегия ➜</button>
        <button class="back-btn" onclick="showScreen('strategies-menu')">⬅ Назад</button>
      </div>
    </div>

    <div id="screen-support" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">🛟</div>
          <div>
            <div class="title">Поддержка</div>
            <div class="subtitle">Помощь и связь</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="support-item">
          <div class="support-title">Поддержка терминала</div>
          <div class="support-text">Если у тебя возникли вопросы по работе терминала, настройкам или сигналам — напиши в поддержку.</div>
        </div>

        <div class="support-item">
          <div class="support-title">Техническая помощь</div>
          <div class="support-text">Проблемы с открытием терминала, интерфейсом или отображением меню решаются через техподдержку.</div>
        </div>

        <div class="support-item">
          <div class="support-title">Связь</div>
          <div class="support-text">Сюда потом можно вставить username менеджера, ссылку на Telegram-чат или кнопку на канал.</div>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

  </div>

  <div class="bottom-tabs">
    <div class="bottom-tabs-inner">
      <button id="tab-home" class="tab-btn active" onclick="showScreen('home')">Главная</button>
      <button id="tab-education" class="tab-btn" onclick="showScreen('education-menu')">Обучение</button>
      <button id="tab-strategies" class="tab-btn" onclick="showScreen('strategies-menu')">Стратегии</button>
      <button id="tab-support" class="tab-btn" onclick="showScreen('support')">Поддержка</button>
    </div>
  </div>

  <script>
    const OTC_ASSETS = [
      "AED/CNY","USD/BDT OTC","EUR/USD OTC","GBP/USD OTC","USD/JPY OTC","AUD/USD OTC","NZD/JPY OTC"
    ];

    const OFFICIAL_ASSETS = [
      "EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","USD/CHF","NZD/USD","EUR/JPY","EUR/GBP",
      "EUR/CHF","EUR/AUD","EUR/CAD","GBP/JPY","GBP/CHF","GBP/AUD","GBP/CAD","AUD/JPY","AUD/CAD",
      "AUD/CHF","CAD/JPY","CHF/JPY","NZD/JPY","NZD/CAD","NZD/CHF","EUR/NZD","GBP/NZD","AUD/NZD",
      "USD/SGD","USD/MXN","USD/NOK","USD/SEK","USD/TRY","USD/ZAR","EUR/SEK","EUR/NOK","EUR/TRY"
    ];

    const STOCK_ASSETS = [
      "Apple","Tesla","Amazon","Google","Meta","Microsoft","NVIDIA","Netflix","Intel","AMD",
      "Coca-Cola","McDonald's","Nike","Disney","Boeing","Alibaba","Uber","Pfizer"
    ];

    const CRYPTO_ASSETS = [
      "Bitcoin","Ethereum","Litecoin","Dash","Chainlink","BCH/EUR","BCH/GBP","BCH/JPY","BTC/GBP","BTC/JPY",
      "Bitcoin OTC","Ethereum OTC","Litecoin OTC","Solana OTC","Polkadot OTC","BNB OTC","Dogecoin OTC",
      "Cardano OTC","Avalanche OTC","TRON OTC","Toncoin OTC","Polygon OTC","Bitcoin ETF OTC"
    ];

    const LESSONS = {
      binary: [
        {
          kicker: "Binary Options • Урок 1",
          title: "Что такое бинарные опционы",
          text: "Бинарный опцион — это контракт с фиксированным исходом. Ты не покупаешь сам актив, а прогнозируешь, будет ли цена выше или ниже определённого уровня к моменту экспирации. Если прогноз совпадает с итоговым результатом, платформа начисляет фиксированную выплату. Если нет — сделка закрывается в минус. Главная особенность бинарных опционов в том, что здесь важен не размер движения, а сам факт правильного направления на определённый промежуток времени.",
          main: "Главная мысль: в бинарных опционах ты торгуешь не активом, а вероятностью правильного направления к моменту экспирации."
        },
        {
          kicker: "Binary Options • Урок 2",
          title: "Экспирация и выплата",
          text: "Экспирация — это срок жизни сделки. Она может быть короткой, например 30 секунд, или длиннее — 1, 2, 3 минуты и больше. В бинарных опционах мало просто угадать, куда идёт цена. Нужно ещё понимать, подходит ли выбранный таймфрейм под текущую фазу рынка. Слишком короткая экспирация часто делает даже хороший анализ уязвимым к рыночному шуму.",
          main: "Главная мысль: направление и время должны совпасть. Хорошая идея на неправильной экспирации легко ломается."
        },
        {
          kicker: "Binary Options • Урок 3",
          title: "Чем бинарные опционы отличаются от обычного трейдинга",
          text: "В классическом трейдинге ты можешь сопровождать позицию, двигать стоп, фиксировать прибыль частями. В бинарных опционах логика жёстче: есть заранее заданный исход, фиксированный риск и фиксированный результат. Поэтому качество входа и выбор момента здесь ещё важнее, чем в обычной торговле.",
          main: "Главная мысль: в бинарных опционах вход и тайминг критичнее, потому что гибкости управления сделкой почти нет."
        },
        {
          kicker: "Binary Options • Урок 4",
          title: "Типичные ошибки новичков",
          text: "Новички часто думают, что бинарные опционы — это быстрый способ постоянно забирать деньги у рынка. Из-за этого они торгуют без плана, лезут в любую свечу, увеличивают сумму после минуса, пытаются отбиться и быстро сливают депозит. Проблема обычно не в кнопках выше/ниже, а в полном отсутствии системы.",
          main: "Главная мысль: основная ошибка новичка — искать лёгкие деньги вместо дисциплины и повторяемой модели."
        },
        {
          kicker: "Binary Options • Урок 5",
          title: "Как подходить к binary options правильно",
          text: "Нормальный подход — это не поиск волшебной схемы, а работа с вероятностями. Нужно понимать рынок, фильтровать входы, использовать понятные модели, ограничивать количество сделок и соблюдать контроль суммы. Тогда binary options превращаются не в хаос, а в дисциплинарную среду, где важны структура и качество исполнения.",
          main: "Главная мысль: правильный подход к бинарным опционам строится на отборе ситуаций, а не на постоянной игре в угадайку."
        }
      ],
      psychology: [
        {
          kicker: "Психология • Урок 1",
          title: "Эмоции трейдера",
          text: "Рынок не любит спешку, азарт и желание отыграться. Главная задача трейдера — сохранять спокойствие и принимать решения по системе, а не по эмоциям. Когда человек торгует на нервах, он перестаёт видеть рынок и начинает реагировать импульсивно.",
          main: "Главная мысль: сильный трейдер не тот, кто торгует много, а тот, кто умеет сохранять контроль над собой."
        },
        {
          kicker: "Психология • Урок 2",
          title: "Страх и жадность",
          text: "Страх заставляет пропускать хорошие входы. Жадность заставляет входить без подтверждения и брать лишние сделки. Оба состояния ломают дисциплину и приводят к слабым решениям. Если трейдер не замечает эти состояния, он начинает торговать эмоциональным фоном, а не логикой.",
          main: "Главная мысль: страх и жадность нельзя убрать полностью, но ими можно научиться управлять."
        },
        {
          kicker: "Психология • Урок 3",
          title: "Тильт после минусов",
          text: "После серии неудач у многих включается желание срочно вернуть деньги. В этот момент начинается тильт: человек открывает сделки быстрее, хуже читает рынок и отказывается от своих же правил. Это одна из самых опасных фаз. Именно в тильте сливаются депозиты, которые до этого можно было сохранить.",
          main: "Главная мысль: после эмоционального удара не нужно ускоряться — нужно остановиться."
        },
        {
          kicker: "Психология • Урок 4",
          title: "Дисциплина важнее мотивации",
          text: "Мотивация нестабильна: сегодня она есть, завтра её нет. Дисциплина работает иначе. Это привычка соблюдать правила даже тогда, когда не хочется. Именно дисциплина позволяет трейдеру переживать плохие дни без разрушения счёта.",
          main: "Главная мысль: не мотивация делает систему рабочей, а дисциплина повторять правильные действия."
        },
        {
          kicker: "Психология • Урок 5",
          title: "Как мыслить сериями сделок",
          text: "Одна сделка почти ничего не значит. Трейдинг нужно оценивать сериями: 20, 30, 50 входов. Когда человек зациклен на одной позиции, он эмоционально перегружает себя. Когда он мыслит серией, он видит статистику, а не драму одной кнопки.",
          main: "Главная мысль: профессионал оценивает не одну сделку, а повторяемость результата на дистанции."
        }
      ],
      market: [
        {
          kicker: "Рынок • Урок 1",
          title: "Что такое рынок простыми словами",
          text: "Рынок — это постоянное движение цены вверх и вниз под влиянием покупателей и продавцов. Цена меняется потому, что одна сторона сильнее другой. Задача трейдера — не угадывать всё подряд, а найти момент, где вероятность движения выше.",
          main: "Главная мысль: рынок — это борьба сторон, а не случайный хаос."
        },
        {
          kicker: "Рынок • Урок 2",
          title: "Импульс и откат",
          text: "Импульс — это сильное движение цены в одну сторону. Откат — это временное движение против основного импульса. Очень важно не путать эти состояния. Новички часто входят в конец импульса, когда движение уже выдохлось, и получают плохой тайминг.",
          main: "Главная мысль: хороший вход часто появляется не в момент паники, а после оценки структуры движения."
        },
        {
          kicker: "Рынок • Урок 3",
          title: "Тренд и флет",
          text: "Тренд — это устойчивое направленное движение. Флет — это боковой диапазон без ярко выраженного лидера. Одни модели работают в тренде, другие во флете. Если не различать эти состояния, можно применять правильную идею в неправильной фазе рынка.",
          main: "Главная мысль: сначала определи фазу рынка, потом ищи вход."
        },
        {
          kicker: "Рынок • Урок 4",
          title: "Волатильность",
          text: "Волатильность — это скорость и сила движения цены. На высокой волатильности короткие экспирации становятся опаснее, потому что случайный шум растёт. На очень низкой волатильности движения может не хватить даже для хорошей идеи. Поэтому волатильность надо учитывать до входа, а не после.",
          main: "Главная мысль: хороший сигнал без подходящей волатильности может не реализоваться."
        },
        {
          kicker: "Рынок • Урок 5",
          title: "Поддержка и сопротивление",
          text: "Поддержка — это зона, где продавцам становится труднее давить цену ниже. Сопротивление — область, где покупателям становится труднее продолжать рост. Эти зоны не являются магическими линиями, но они помогают понимать, где рынок может тормозить, разворачиваться или накапливать ликвидность.",
          main: "Главная мысль: уровни — это не точка, а зона реакции цены."
        }
      ],
      tech: [
        {
          kicker: "Технический анализ • Урок 1",
          title: "Как читать структуру движения",
          text: "Технический анализ начинается не с индикаторов, а с понимания структуры. Если цена делает более высокие минимумы и максимумы — рынок выглядит сильнее вверх. Если обновляются минимумы и ломаются откаты — рынок слабее. Это базовая логика, без которой любые индикаторы превращаются в декорацию.",
          main: "Главная мысль: структура движения важнее красивых линий и стрелок."
        },
        {
          kicker: "Технический анализ • Урок 2",
          title: "Пробой и ложный пробой",
          text: "Пробой — это ситуация, когда цена уверенно проходит важную зону и показывает готовность двигаться дальше. Ложный пробой — это вынос за уровень с быстрым возвратом назад. Обе модели полезны, но их нельзя путать. Именно путаница между настоящим пробоем и ложным чаще всего ломает вход.",
          main: "Главная мысль: важен не сам факт выхода за уровень, а то, что цена делает после него."
        },
        {
          kicker: "Технический анализ • Урок 3",
          title: "Трендовые линии",
          text: "Трендовая линия не должна быть магической палкой. Это лишь визуальный фильтр, который помогает увидеть направление и качество откатов. Если цена уважает линию несколько раз, это усиливает идею. Но сам по себе контакт с линией без контекста ничего не гарантирует.",
          main: "Главная мысль: трендовая линия — это помощник, а не самостоятельный грааль."
        },
        {
          kicker: "Технический анализ • Урок 4",
          title: "Консолидация и накопление",
          text: "Когда цена сжимается и диапазон становится узким, рынок часто готовится к более сильному движению. Но консолидация не всегда означает немедленный выстрел. Нужно смотреть, куда давит рынок, сохраняется ли структура и есть ли признаки выхода одной из сторон.",
          main: "Главная мысль: консолидация ценна тем, что готовит почву для импульса."
        }
      ],
      candles: [
        {
          kicker: "Свечи • Урок 1",
          title: "Тело и тени свечи",
          text: "Тело показывает, где цена открылась и закрылась. Тени показывают, где цена была, но не смогла удержаться. Длинная тень часто указывает на борьбу и отказ от дальнейшего движения. Но отдельно от контекста свеча мало что значит.",
          main: "Главная мысль: свеча всегда читается вместе с местом, где она появилась."
        },
        {
          kicker: "Свечи • Урок 2",
          title: "Пин-бар",
          text: "Пин-бар — это свеча с маленьким телом и длинной тенью, которая указывает на агрессивное отклонение цены от зоны. Сильнее всего пин-бар работает на уровне поддержки или сопротивления, а не в случайном месте графика.",
          main: "Главная мысль: хороший пин-бар — это реакция на важную область, а не просто красивая свеча."
        },
        {
          kicker: "Свечи • Урок 3",
          title: "Поглощение",
          text: "Поглощение появляется, когда новая свеча своим телом перекрывает предыдущую и показывает смену краткосрочного баланса сил. Это часто бывает полезно после отката или у уровня. Но если рынок рваный и хаотичный, даже красивое поглощение может не отработать.",
          main: "Главная мысль: поглощение хорошо работает в контексте, а не само по себе."
        },
        {
          kicker: "Свечи • Урок 4",
          title: "Доджи и нерешительность",
          text: "Доджи часто показывает неопределённость и отсутствие явного лидера в моменте. На сильном уровне такая свеча может указывать на остановку движения. Но в середине слабого рынка доджи часто просто отражает шум и не даёт полезной информации.",
          main: "Главная мысль: доджи — это не сигнал входа, а сигнал присмотреться к контексту."
        }
      ],
      indicators: [
        {
          kicker: "Индикаторы • Урок 1",
          title: "EMA и SMA",
          text: "Скользящие средние помогают понимать направление и среднюю цену рынка. EMA реагирует быстрее, SMA мягче. Их можно использовать как фильтр тренда, динамическую зону отката или визуальную рамку движения.",
          main: "Главная мысль: средние полезны как фильтр, но не должны подменять чтение рынка."
        },
        {
          kicker: "Индикаторы • Урок 2",
          title: "RSI",
          text: "RSI показывает скорость и силу текущего движения. Многие используют его для оценки перекупленности и перепроданности, но на практике RSI лучше работает как дополнительный фильтр, а не как самостоятельная кнопка входа.",
          main: "Главная мысль: RSI становится сильнее, когда используется вместе с уровнем и контекстом."
        },
        {
          kicker: "Индикаторы • Урок 3",
          title: "Stochastic",
          text: "Stochastic похож по идее на RSI, но реагирует иначе и часто быстрее показывает локальное перегревание. Он может быть полезен во флете, но в мощном тренде ранние сигналы стохастика часто вводят новичка в заблуждение.",
          main: "Главная мысль: быстрый индикатор без понимания фазы рынка даёт много ложных входов."
        },
        {
          kicker: "Индикаторы • Урок 4",
          title: "MACD, Bollinger и ATR",
          text: "MACD помогает оценить импульс и смену темпа. Bollinger Bands позволяют видеть расширение и сжатие волатильности. ATR не показывает направление, но отлично помогает понять, насколько рынок активен. Каждый индикатор решает свою задачу, и перегружать ими график не нужно.",
          main: "Главная мысль: индикаторы полезны только тогда, когда каждый из них отвечает за конкретную функцию."
        }
      ],
      smartmoney: [
        {
          kicker: "Smart Money • Урок 1",
          title: "Что трейдеры называют ликвидностью",
          text: "Под ликвидностью в практическом трейдинге часто понимают зоны, где сконцентрированы стопы, заявки и очевидные ожидания толпы. Это могут быть equal highs, equal lows, границы диапазона, экстремумы и сильные уровни.",
          main: "Главная мысль: цена часто идёт не туда, где всем удобно, а туда, где можно собрать ликвидность."
        },
        {
          kicker: "Smart Money • Урок 2",
          title: "Equal highs / equal lows",
          text: "Когда на графике видны почти одинаковые вершины или почти одинаковые минимумы, многие трейдеры считают эти области зонами ликвидности. Часто рынок сначала выносит такую область, а потом показывает обратную реакцию.",
          main: "Главная мысль: одинаковые вершины и минимумы часто становятся магнитом для цены."
        },
        {
          kicker: "Smart Money • Урок 3",
          title: "Liquidity sweep",
          text: "Sweep — это вынос очевидной зоны с быстрым продолжением или возвратом. Он может использоваться как элемент сценария на ложный пробой или на ускорение после сбора ликвидности. Главное — не угадывать sweep заранее, а дождаться реакции после него.",
          main: "Главная мысль: сначала должен случиться сбор ликвидности, и только потом ищется логика входа."
        },
        {
          kicker: "Smart Money • Урок 4",
          title: "Imbalance и displacement",
          text: "Imbalance — это зона, где цена прошла слишком быстро и оставила неравномерное движение. Displacement — это сильный агрессивный импульс. Эти элементы помогают видеть, где рынок показал реальную силу одной из сторон.",
          main: "Главная мысль: быстрые и чистые импульсы часто указывают, где рынок действительно был силён."
        }
      ],
      risk: [
        {
          kicker: "Risk Management • Урок 1",
          title: "Фиксированная сумма входа",
          text: "Когда размер сделки меняется хаотично, трейдер теряет контроль над статистикой. Фиксированная сумма позволяет спокойно оценивать результат сериями, а не зависеть от одной неудачной попытки.",
          main: "Главная мысль: контроль риска начинается с одинакового подхода к размеру сделки."
        },
        {
          kicker: "Risk Management • Урок 2",
          title: "Когда остановить сессию",
          text: "Если у тебя несколько подряд плохих решений, это уже не просто рынок, а изменение твоего состояния. Иногда лучшая защита депозита — не найти новый вход, а закрыть терминал и вернуться позже.",
          main: "Главная мысль: пауза — это инструмент профессионала, а не слабость."
        },
        {
          kicker: "Risk Management • Урок 3",
          title: "Не пытайся отбиться",
          text: "Желание срочно вернуть потерянное — одна из самых дорогих эмоций в трейдинге. Оно толкает увеличивать сумму, ускорять сделки и ломать систему. Отбивание почти всегда превращает контролируемый минус в неконтролируемую серию.",
          main: "Главная мысль: задача после убытка — не отбиться, а не потерять контроль."
        },
        {
          kicker: "Risk Management • Урок 4",
          title: "Оценивай день, а не одну сделку",
          text: "Торговая сессия должна оцениваться по качеству решений, а не по эмоциям после одной позиции. Если ты отработал по системе, но получил случайный минус — это не трагедия. Если ты нарушил правила и случайно повезло — это тоже плохой день.",
          main: "Главная мысль: хороший день — это день дисциплины, а не только день плюса."
        }
      ]
    };

    const STRATEGIES = [
      {
        title: "Отбой от уровня",
        scheme: "level",
        core: "Стратегия строится на реакции цены от зоны поддержки или сопротивления. Ты ищешь не просто касание уровня, а сам факт замедления, отказа идти дальше, появления теней или разворотных свечей у сильной области.",
        entry: "Сначала выделяется зона, от которой цена уже делала реакцию в прошлом. Потом ждёшь повторного подхода. Если на подходе свечи теряют силу, появляются тени, замедление или поглощение в обратную сторону, можно рассматривать вход на отбой.",
        filters: "Лучше всего работает, когда уровень уже был проверен хотя бы один раз. Полезно, если рынок не находится в сильном новостном импульсе. Дополнительным фильтром могут быть свечные модели или слабость пробоя.",
        mistakes: "Главная ошибка — входить просто от линии без реакции. Второй частый промах — ловить отбой против очень мощного импульса, когда рынок ещё не выдохся.",
        markets: "ОТС, официальные валюты, крипта. Подходит для коротких и средних экспираций, если уровень читается визуально."
      },
      {
        title: "Пробой уровня с подтверждением",
        scheme: "breakout",
        core: "Суть стратегии — работать не против уровня, а по направлению его уверенного пробоя. Хороший пробой — это не просто тень за зону, а сила, за которой стоит реальное продолжение.",
        entry: "Находишь зону, которую рынок несколько раз не мог пройти. Затем ждёшь уверенный выход за неё. Вход возможен либо сразу после явной силы, либо после короткого возврата к зоне, если рынок не теряет импульс.",
        filters: "Нужен чистый пробой телом, а не уколом. Дополнительный плюс — если после выхода цена не возвращается обратно сразу же. Хорошо, когда до следующего уровня есть пространство.",
        mistakes: "Частая ошибка — прыгать в ложный пробой. Ещё одна ошибка — входить слишком поздно, когда движение уже растянуто.",
        markets: "Лучше работает на трендовых участках официальных валют и криптовалют."
      },
      {
        title: "Ложный пробой",
        scheme: "falsebreak",
        core: "Ложный пробой появляется, когда рынок сначала выносит очевидную зону, а потом резко возвращается назад. Часто это связано со сбором ликвидности и ловушкой для тех, кто входит слишком прямолинейно.",
        entry: "Ищешь сильный уровень. Ждёшь вынос за него. Если после этого цена быстро возвращается назад и показывает отказ закрепляться за зоной, можно искать вход в обратную сторону.",
        filters: "Лучше, когда возврат назад происходит быстро. Дополнительный плюс — если перед этим уровень был очевиден многим участникам рынка.",
        mistakes: "Ошибка — угадывать ложный пробой заранее. Сначала должен случиться вынос и только потом появиться подтверждение слабости.",
        markets: "Хорошо работает на ОТС и во флете на валютах."
      },
      {
        title: "Продолжение тренда после отката",
        scheme: "trendpullback",
        core: "Это одна из самых логичных стратегий: не ловить разворот, а входить по направлению уже существующего движения после коррекции. Так ты работаешь вместе с доминирующей стороной.",
        entry: "Определяешь тренд по структуре. Затем ждёшь откат против основного движения. Когда откат теряет силу и цена снова показывает готовность двигаться по тренду, ищешь вход.",
        filters: "Лучше всего работает при понятном тренде. Подтверждение — слабые откатные свечи, реакция на уровень или возврат силы основной стороны.",
        mistakes: "Ошибка — путать боковик с трендом. Ещё одна ошибка — входить, пока откат ещё не завершился.",
        markets: "Сильнее всего на официальных парах и крипте."
      },
      {
        title: "Флет от границ диапазона",
        scheme: "range",
        core: "Когда рынок не идёт направленно, а колеблется в диапазоне, можно искать входы от верхней и нижней границы. Это не стратегия для импульса, а для спокойной цикличной реакции.",
        entry: "Определи диапазон, где цена уже несколько раз разворачивалась. У верхней границы ищи признаки слабости для входа вниз, у нижней — признаки силы для входа вверх.",
        filters: "Важно, чтобы диапазон был визуально чистым. Длинные тени и отказ идти дальше усиливают идею. Лучше не брать такие входы, если рынок уже сжимается под явный пробой.",
        mistakes: "Главная ошибка — считать любой боковик флэтом для торговли. Иногда это просто накопление перед сильным выходом.",
        markets: "ОТС и спокойные валютные периоды."
      },
      {
        title: "Импульс после консолидации",
        scheme: "squeeze",
        core: "После узкого накопления цена часто делает резкое движение. Эта стратегия работает на переходе от сжатия к расширению волатильности.",
        entry: "Находишь участок, где диапазон узкий, свечи маленькие и рынок сжался. Потом ждёшь выход из этой зоны и работаешь в сторону силы.",
        filters: "Хорошо, если до консолидации уже был импульс. Важен именно уверенный выход, а не случайный укол.",
        mistakes: "Ошибка — входить в середине накопления без реального пробоя. Вторая ошибка — запрыгивать в движение, когда цена уже очень далеко ушла от зоны.",
        markets: "Крипта и активные официальные пары."
      },
      {
        title: "Свечной разворот у уровня",
        scheme: "candle",
        core: "Сильный уровень плюс разворотная свеча — одна из самых понятных моделей. Это может быть пин-бар, поглощение или серия свечей, показывающих отказ от продолжения движения.",
        entry: "Цена подходит к поддержке или сопротивлению. Ты ждёшь не только касание, но и реакцию: длинную тень, резкий отказ, поглощение или сильную ответную свечу. После этого ищешь вход в сторону разворота.",
        filters: "Свечная модель должна появляться на понятной зоне. Без контекста красивые свечи часто дают ложное ощущение сигнала.",
        mistakes: "Ошибка — торговать любую разворотную свечу в центре хаоса без уровня и структуры.",
        markets: "Подходит почти для всех рынков."
      },
      {
        title: "EMA + трендовый откат",
        scheme: "ema",
        core: "EMA используется как фильтр тренда и динамическая зона отката. Смысл не в том, чтобы торговать каждое касание средней, а в том, чтобы работать по тренду, когда цена возвращается к справедливой области и снова восстанавливает движение.",
        entry: "Определи направление по EMA. Если рынок выше средней и сохраняет структуру роста, ждёшь откат к EMA и реакцию вверх. В нисходящем сценарии — наоборот.",
        filters: "EMA должна использоваться вместе со структурой, а не сама по себе. Подтверждением может быть слабый откат, свечная реакция или уровень рядом.",
        mistakes: "Ошибка — думать, что средняя всегда удержит цену. На хаотичном рынке EMA часто режется без пользы.",
        markets: "Официальные валюты и крипта."
      },
      {
        title: "RSI + уровень",
        scheme: "rsi",
        core: "RSI лучше работает не как отдельный сигнал, а как фильтр. Если цена пришла в сильную зону и при этом RSI показывает перегрев или дивергенцию, это усиливает идею на реакцию.",
        entry: "Сначала находишь уровень. Затем смотришь, не указывает ли RSI на перекупленность, перепроданность или расхождение с ценой. Только после этого ищешь подтверждение по самой цене.",
        filters: "RSI должен усиливать контекст, а не заменять его. Особенно полезен во флете и на локальных выносах.",
        mistakes: "Ошибка — входить только по RSI без уровня и подтверждения. В тренде RSI может долго оставаться в зоне перегрева.",
        markets: "Флетовые и умеренно трендовые участки."
      },
      {
        title: "Liquidity sweep + возврат",
        scheme: "smart",
        core: "Это smart money модель, где цена сначала снимает очевидную ликвидность, а потом показывает возврат назад. Логика в том, что после сбора стопов и заявок рынок часто даёт обратную реакцию или ускорение по новому направлению.",
        entry: "Ищешь equal highs или equal lows, границу диапазона или очевидный экстремум. После выноса ждёшь подтверждение возврата: быструю реакцию, сильную свечу обратно, отсутствие закрепления за зоной. Затем входишь по подтверждённому возврату.",
        filters: "Чем очевиднее ликвидная зона, тем лучше. Важна скорость возврата и отсутствие продолжения за выносом.",
        mistakes: "Ошибка — пытаться угадать вынос до его завершения. Сначала должен быть сбор ликвидности, потом — реакция.",
        markets: "ОТС, крипта, активные валютные сессии."
      }
    ];

    let currentMarket = "otc";
    let currentTf = "30 сек";
    let currentSelectedAsset = null;
    let currentLessonGroup = "binary";
    let currentLessonIndex = 0;
    let currentStrategyIndex = 0;
    let chartTimer = null;

    function setBottomTab(id) {
      document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
      const tab = document.getElementById("tab-" + id);
      if (tab) tab.classList.add("active");
    }

    function showScreen(name) {
      document.querySelectorAll(".screen").forEach(el => el.classList.remove("active"));
      const target = document.getElementById("screen-" + name);
      if (target) target.classList.add("active");

      if (name === "home") setBottomTab("home");
      if (name === "education-menu" || name === "lesson") setBottomTab("education");
      if (name === "strategies-menu" || name === "strategy-detail") setBottomTab("strategies");
      if (name === "support") setBottomTab("support");
      if (name === "trade-menu" || name === "market-list" || name === "analysis") {
        document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
      }
    }

    function openTradeMenu() {
      showScreen("trade-menu");
    }

    function getMarketAssets() {
      if (currentMarket === "otc") return OTC_ASSETS;
      if (currentMarket === "official") return OFFICIAL_ASSETS;
      if (currentMarket === "stocks") return STOCK_ASSETS;
      return CRYPTO_ASSETS;
    }

    function getMarketLabel() {
      if (currentMarket === "otc") return "OTC";
      if (currentMarket === "official") return "OFFICIAL";
      if (currentMarket === "stocks") return "STOCKS";
      return "CRYPTO";
    }

    function openMarket(type) {
      currentMarket = type;
      currentSelectedAsset = null;
      document.getElementById("assetSearch").value = "";

      if (type === "otc") {
        document.getElementById("marketTitle").innerText = "Торговля ОТС";
        document.getElementById("marketSub").innerText = "Выбор OTC актива";
      } else if (type === "official") {
        document.getElementById("marketTitle").innerText = "Торговля Официалов";
        document.getElementById("marketSub").innerText = "Выбор официального актива";
      } else if (type === "stocks") {
        document.getElementById("marketTitle").innerText = "Торговля Акциями";
        document.getElementById("marketSub").innerText = "Выбор акции";
      } else {
        document.getElementById("marketTitle").innerText = "Торговля криптовалютой";
        document.getElementById("marketSub").innerText = "Выбор криптоактива";
      }

      showScreen("market-list");
      renderAssets();
    }

    function selectTf(tf) {
      currentTf = tf;
      document.querySelectorAll(".tf-btn").forEach(btn => btn.classList.remove("active"));
      const active = document.querySelector(`.tf-btn[data-tf="${tf}"]`);
      if (active) active.classList.add("active");
    }

    function renderAssets() {
      const list = document.getElementById("assetList");
      const searchValue = document.getElementById("assetSearch").value.toLowerCase().trim();
      const filtered = getMarketAssets().filter(a => a.toLowerCase().includes(searchValue));
      list.innerHTML = "";

      if (!filtered.length) {
        list.innerHTML = `<div class="empty">Ничего не найдено</div>`;
        return;
      }

      filtered.forEach(asset => {
        const el = document.createElement("div");
        el.className = "asset-item";
        el.innerHTML = `
          <div>
            <div class="asset-name">${asset}</div>
            <div class="asset-meta">Нажми для открытия анализа</div>
          </div>
          <div class="badge-mini">${getMarketLabel()}</div>
        `;
        el.onclick = () => openAnalysis(asset);
        list.appendChild(el);
      });
    }

    function openAnalysis(asset) {
      currentSelectedAsset = asset;
      document.getElementById("loadingBox").style.display = "none";
      document.getElementById("analysisBox").style.display = "none";
      document.getElementById("loadingFill").style.width = "0%";
      document.getElementById("loadingText").innerText = "Подготавливаем торговый сигнал";
      showScreen("analysis");
      startSignalLoading(asset);
    }

    function backToAssets() {
      stopChart();
      showScreen("market-list");
    }

    function randomDirection() {
      return Math.random() > 0.5 ? "ВВЕРХ" : "ВНИЗ";
    }

    function randomStrength() {
      return Math.floor(Math.random() * 16) + 80;
    }

    function signalComment(direction, asset, tf, strength) {
      const up = [
        `Сценарий по активу ${asset} указывает на возможное движение вверх. Расчётная сила сигнала — ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вверх. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вверх. Сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const down = [
        `Сценарий по активу ${asset} указывает на возможное движение вниз. Расчётная сила сигнала — ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вниз. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вниз. Сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const arr = direction === "ВВЕРХ" ? up : down;
      return arr[Math.floor(Math.random() * arr.length)];
    }

    function startSignalLoading(asset) {
      const loadingBox = document.getElementById("loadingBox");
      const loadingFill = document.getElementById("loadingFill");
      const loadingText = document.getElementById("loadingText");
      const analysisBox = document.getElementById("analysisBox");

      analysisBox.style.display = "none";
      loadingBox.style.display = "block";
      loadingFill.style.width = "0%";

      const loadingMessages = [
        "Сканируем структуру движения...",
        "Проверяем волатильность...",
        "Формируем направление входа...",
        "Подготавливаем итоговый сигнал..."
      ];

      let step = 0;
      loadingText.innerText = loadingMessages[0];

      const totalMs = 3000;
      const intervalMs = 150;
      const totalSteps = totalMs / intervalMs;
      let current = 0;

      const timer = setInterval(() => {
        current += 1;
        const percent = Math.min(100, Math.round((current / totalSteps) * 100));
        loadingFill.style.width = percent + "%";

        const msgIndex = Math.min(
          loadingMessages.length - 1,
          Math.floor((current / totalSteps) * loadingMessages.length)
        );

        if (msgIndex !== step) {
          step = msgIndex;
          loadingText.innerText = loadingMessages[msgIndex];
        }

        if (current >= totalSteps) {
          clearInterval(timer);
          loadingBox.style.display = "none";
          renderSignalNow(asset);
        }
      }, intervalMs);
    }

    function renderSignalNow(asset) {
      const direction = randomDirection();
      const strength = randomStrength();

      document.getElementById("signalAsset").innerText = asset;
      document.getElementById("signalDirection").innerText = direction;
      document.getElementById("signalDirection").className = "chip " + (direction === "ВВЕРХ" ? "dir-up" : "dir-down");
      document.getElementById("signalTime").innerText = currentTf;
      document.getElementById("signalType").innerText = getMarketLabel();
      document.getElementById("signalComment").innerText = signalComment(direction, asset, currentTf, strength);
      document.getElementById("signalMarketLine").innerText = `${getMarketLabel()} • ${currentTf}`;
      document.getElementById("signalStrength").innerText = `${strength}%`;

      document.getElementById("analysisBox").style.display = "block";
      startChart(direction);
    }

    function generateCurrentSignal() {
      if (!currentSelectedAsset) return;
      startSignalLoading(currentSelectedAsset);
    }

    function startChart(direction) {
      stopChart();
      const canvas = document.getElementById("liveChart");
      if (!canvas) return;

      const wrap = canvas.parentElement;
      const rect = wrap.getBoundingClientRect();
      canvas.width = Math.max(300, Math.floor(rect.width * 2));
      canvas.height = Math.max(180, Math.floor(rect.height * 2));

      const ctx = canvas.getContext("2d");
      const W = canvas.width;
      const H = canvas.height;

      let points = [];
      let value = H * 0.58;

      for (let i = 0; i < 60; i++) {
        value += (Math.random() - 0.5) * 18;
        value = Math.max(24, Math.min(H - 24, value));
        points.push(value);
      }

      function draw() {
        ctx.clearRect(0, 0, W, H);

        for (let i = 0; i < 6; i++) {
          const y = (H / 6) * i;
          ctx.strokeStyle = "rgba(255,255,255,0.06)";
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(W, y);
          ctx.stroke();
        }

        for (let i = 0; i < 8; i++) {
          const x = (W / 8) * i;
          ctx.strokeStyle = "rgba(255,255,255,0.04)";
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, H);
          ctx.stroke();
        }

        ctx.beginPath();
        for (let i = 0; i < points.length; i++) {
          const x = (W / (points.length - 1)) * i;
          const y = points[i];
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }

        ctx.strokeStyle = direction === "ВВЕРХ" ? "#7df0b2" : "#ff9d9d";
        ctx.lineWidth = 4;
        ctx.shadowBlur = 12;
        ctx.shadowColor = direction === "ВВЕРХ" ? "#7df0b2" : "#ff9d9d";
        ctx.stroke();
        ctx.shadowBlur = 0;

        const gradient = ctx.createLinearGradient(0, 0, 0, H);
        if (direction === "ВВЕРХ") {
          gradient.addColorStop(0, "rgba(125,240,178,0.20)");
          gradient.addColorStop(1, "rgba(125,240,178,0.01)");
        } else {
          gradient.addColorStop(0, "rgba(255,157,157,0.20)");
          gradient.addColorStop(1, "rgba(255,157,157,0.01)");
        }

        ctx.beginPath();
        for (let i = 0; i < points.length; i++) {
          const x = (W / (points.length - 1)) * i;
          const y = points[i];
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.lineTo(W, H);
        ctx.lineTo(0, H);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();
      }

      function tick() {
        let last = points[points.length - 1];
        let drift = direction === "ВВЕРХ" ? -2.2 : 2.2;
        let next = last + drift + (Math.random() - 0.5) * 16;
        next = Math.max(22, Math.min(H - 22, next));
        points.push(next);
        if (points.length > 65) points.shift();
        draw();
      }

      draw();
      chartTimer = setInterval(tick, 600);
    }

    function stopChart() {
      if (chartTimer) {
        clearInterval(chartTimer);
        chartTimer = null;
      }
    }

    function openLesson(group, index) {
      currentLessonGroup = group;
      currentLessonIndex = index;
      renderLesson();
      showScreen("lesson");
    }

    function renderLesson() {
      const lesson = LESSONS[currentLessonGroup][currentLessonIndex];
      const names = {
        binary: ["Что такое бинарные опционы", "Базовая механика и риски"],
        psychology: ["Психология", "Контроль эмоций и дисциплина"],
        market: ["Что такое рынок", "Понимание структуры движения цены"],
        tech: ["Технический анализ", "Структура, уровни, пробои"],
        candles: ["Японские свечи", "Свечные модели и контекст"],
        indicators: ["Индикаторы", "EMA, RSI, MACD и фильтры"],
        smartmoney: ["Smart Money", "Ликвидность и выносы"],
        risk: ["Risk Management", "Защита депозита и контроль сессии"]
      };

      document.getElementById("lessonCategoryTitle").innerText = names[currentLessonGroup][0];
      document.getElementById("lessonCategorySub").innerText = names[currentLessonGroup][1];
      document.getElementById("lessonKicker").innerText = lesson.kicker;
      document.getElementById("lessonTitle").innerText = lesson.title;
      document.getElementById("lessonText").innerText = lesson.text;
      document.getElementById("lessonMain").innerText = lesson.main;

      const lessons = LESSONS[currentLessonGroup];
      document.getElementById("lessonNextBtn").innerText =
        currentLessonIndex >= lessons.length - 1 ? "Вернуться в обучение" : "Следующий урок ➜";
    }

    function nextLesson() {
      const lessons = LESSONS[currentLessonGroup];
      if (currentLessonIndex >= lessons.length - 1) {
        showScreen("education-menu");
        return;
      }
      currentLessonIndex += 1;
      renderLesson();
    }

    function backFromLesson() {
      showScreen("education-menu");
    }

    function renderStrategiesList() {
      const list = document.getElementById("strategiesList");
      list.innerHTML = "";
      STRATEGIES.forEach((s, i) => {
        const btn = document.createElement("button");
        btn.className = i === 0 ? "menu-btn primary" : "menu-btn";
        btn.innerHTML = `
          <div class="menu-title">${i + 1}. ${s.title}</div>
          <div class="menu-desc">${s.core.slice(0, 170)}...</div>
        `;
        btn.onclick = () => openStrategy(i);
        list.appendChild(btn);
      });
    }

    function openStrategy(index) {
      currentStrategyIndex = index;
      renderStrategy();
      showScreen("strategy-detail");
    }

    function nextStrategy() {
      if (currentStrategyIndex >= STRATEGIES.length - 1) {
        showScreen("strategies-menu");
        return;
      }
      currentStrategyIndex += 1;
      renderStrategy();
    }

    function renderStrategy() {
      const s = STRATEGIES[currentStrategyIndex];
      document.getElementById("strategyKicker").innerText = `Стратегия ${currentStrategyIndex + 1} из ${STRATEGIES.length}`;
      document.getElementById("strategyTitleBig").innerText = s.title;
      document.getElementById("strategyCore").innerText = s.core;
      document.getElementById("strategyEntry").innerText = s.entry;
      document.getElementById("strategyFilters").innerText = s.filters;
      document.getElementById("strategyMistakes").innerText = s.mistakes;
      document.getElementById("strategyMarkets").innerText = s.markets;
      document.getElementById("strategyScheme").innerHTML = getSchemeSvg(s.scheme);

      document.getElementById("strategyNextBtn").innerText =
        currentStrategyIndex >= STRATEGIES.length - 1 ? "Вернуться к списку стратегий" : "Следующая стратегия ➜";
    }

    function getSchemeSvg(type) {
      const commonTop = `<svg viewBox="0 0 600 260" xmlns="http://www.w3.org/2000/svg">
        <rect width="600" height="260" fill="#0f141a"/>
        <g stroke="rgba(255,255,255,.06)">
          <line x1="0" y1="40" x2="600" y2="40"/>
          <line x1="0" y1="90" x2="600" y2="90"/>
          <line x1="0" y1="140" x2="600" y2="140"/>
          <line x1="0" y1="190" x2="600" y2="190"/>
          <line x1="80" y1="0" x2="80" y2="260"/>
          <line x1="160" y1="0" x2="160" y2="260"/>
          <line x1="240" y1="0" x2="240" y2="260"/>
          <line x1="320" y1="0" x2="320" y2="260"/>
          <line x1="400" y1="0" x2="400" y2="260"/>
          <line x1="480" y1="0" x2="480" y2="260"/>
        </g>`;

      if (type === "level") {
        return commonTop + `
          <line x1="40" y1="120" x2="560" y2="120" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <polyline points="60,70 110,85 160,95 210,110 260,118 300,150 345,135 390,122 440,98 500,88 550,80"
            fill="none" stroke="#7df0b2" stroke-width="4"/>
          <text x="365" y="112" fill="#f2f5f8" font-size="16" font-weight="700">Отбой от уровня</text>
          <circle cx="300" cy="150" r="6" fill="#ff9d9d"/>
        </svg>`;
      }

      if (type === "breakout") {
        return commonTop + `
          <line x1="40" y1="140" x2="560" y2="140" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <polyline points="50,150 100,148 150,145 200,147 250,144 300,146 350,130 400,95 460,78 520,60"
            fill="none" stroke="#7df0b2" stroke-width="4"/>
          <text x="350" y="130" fill="#f2f5f8" font-size="16" font-weight="700">Пробой</text>
        </svg>`;
      }

      if (type === "falsebreak") {
        return commonTop + `
          <line x1="40" y1="120" x2="560" y2="120" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <polyline points="60,95 120,100 180,108 240,116 300,125 340,105 380,140 430,150 490,145 550,138"
            fill="none" stroke="#ff9d9d" stroke-width="4"/>
          <text x="350" y="98" fill="#f2f5f8" font-size="16" font-weight="700">Ложный пробой</text>
        </svg>`;
      }

      if (type === "trendpullback") {
        return commonTop + `
          <polyline points="50,190 100,170 150,160 200,145 250,135 300,150 350,140 400,115 460,100 530,78"
            fill="none" stroke="#7df0b2" stroke-width="4"/>
          <line x1="40" y1="178" x2="560" y2="90" stroke="#9fd0ff" stroke-width="2" stroke-dasharray="10 8"/>
          <text x="315" y="160" fill="#f2f5f8" font-size="16" font-weight="700">Откат по тренду</text>
        </svg>`;
      }

      if (type === "range") {
        return commonTop + `
          <line x1="40" y1="70" x2="560" y2="70" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <line x1="40" y1="180" x2="560" y2="180" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <polyline points="60,170 110,120 160,95 210,150 260,175 310,130 360,88 420,150 470,175 530,125"
            fill="none" stroke="#f0d89f" stroke-width="4"/>
          <text x="390" y="63" fill="#f2f5f8" font-size="16" font-weight="700">Флет</text>
        </svg>`;
      }

      if (type === "squeeze") {
        return commonTop + `
          <polyline points="60,145 110,143 160,141 210,139 260,138 300,137 340,120 390,92 450,70 520,55"
            fill="none" stroke="#7df0b2" stroke-width="4"/>
          <path d="M70 155 L280 130" stroke="#9fd0ff" stroke-width="2"/>
          <path d="M70 120 L280 130" stroke="#9fd0ff" stroke-width="2"/>
          <text x="300" y="118" fill="#f2f5f8" font-size="16" font-weight="700">Выход из сжатия</text>
        </svg>`;
      }

      if (type === "candle") {
        return commonTop + `
          <line x1="40" y1="150" x2="560" y2="150" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <rect x="245" y="112" width="28" height="36" fill="#ff9d9d"/>
          <line x1="259" y1="75" x2="259" y2="178" stroke="#f2f5f8" stroke-width="3"/>
          <rect x="310" y="145" width="28" height="18" fill="#7df0b2"/>
          <line x1="324" y1="118" x2="324" y2="176" stroke="#f2f5f8" stroke-width="3"/>
          <text x="350" y="135" fill="#f2f5f8" font-size="16" font-weight="700">Свечной разворот</text>
        </svg>`;
      }

      if (type === "ema") {
        return commonTop + `
          <path d="M40 175 C120 160, 160 150, 220 145 S340 135, 400 118 S500 95, 560 85" stroke="#7df0b2" stroke-width="4" fill="none"/>
          <path d="M40 185 C120 178, 180 165, 240 154 S360 138, 420 126 S510 105, 560 96" stroke="#f0d89f" stroke-width="3" fill="none"/>
          <text x="390" y="120" fill="#f2f5f8" font-size="16" font-weight="700">EMA + откат</text>
        </svg>`;
      }

      if (type === "rsi") {
        return commonTop + `
          <line x1="40" y1="125" x2="560" y2="125" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
          <polyline points="60,95 120,105 180,115 240,130 300,145 360,138 420,120 480,98 540,88"
            fill="none" stroke="#f0d89f" stroke-width="4"/>
          <text x="355" y="150" fill="#f2f5f8" font-size="16" font-weight="700">RSI + уровень</text>
        </svg>`;
      }

      return commonTop + `
        <line x1="40" y1="115" x2="560" y2="115" stroke="#9fd0ff" stroke-width="3" stroke-dasharray="8 8"/>
        <polyline points="60,120 120,118 180,117 240,116 300,105 350,125 400,145 470,120 540,98"
          fill="none" stroke="#ff9d9d" stroke-width="4"/>
        <text x="335" y="98" fill="#f2f5f8" font-size="16" font-weight="700">Liquidity sweep</text>
      </svg>`;
    }

    function initUI() {
      renderStrategiesList();
    }

    async function verifyAccess() {
      try {
        if (!window.Telegram || !window.Telegram.WebApp) {
          document.getElementById("access-overlay").innerHTML = `
            <div>
              <div style="font-size:22px;font-weight:700;margin-bottom:12px;">Доступ запрещён</div>
              <div style="font-size:14px;opacity:.8;">Открой терминал только через Telegram-бота</div>
            </div>
          `;
          return;
        }

        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        const resp = await fetch("/auth/check", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ init_data: tg.initData || "" })
        });

        const data = await resp.json();

        if (resp.ok && data.ok) {
          const overlay = document.getElementById("access-overlay");
          if (overlay) overlay.style.display = "none";
          initUI();
        } else {
          document.getElementById("access-overlay").innerHTML = `
            <div>
              <div style="font-size:22px;font-weight:700;margin-bottom:12px;">Доступ запрещён</div>
              <div style="font-size:14px;opacity:.8;">Сначала пройди регистрацию и FTD</div>
            </div>
          `;
        }
      } catch (e) {
        document.getElementById("access-overlay").innerHTML = `
          <div>
            <div style="font-size:22px;font-weight:700;margin-bottom:12px;">Ошибка доступа</div>
            <div style="font-size:14px;opacity:.8;">Попробуй открыть терминал снова через бота</div>
          </div>
        `;
      }
    }

    verifyAccess();
  </script>
</body>
</html>
"""


# ================== WEB ROUTES ==================
async def auth_check(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "bad_json"}, status=400)

    init_data = data.get("init_data", "")
    user = verify_telegram_init_data(init_data, BOT_TOKEN)

    if not user:
        return web.json_response({"ok": False, "error": "unauthorized"}, status=403)

    user_id = user.get("id")
    if not user_id or not is_user_allowed(int(user_id)):
        return web.json_response({"ok": False, "error": "access_denied"}, status=403)

    return web.json_response({"ok": True})


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Chrome Trade Terminal is running", content_type="text/plain")


async def app_page(request: web.Request) -> web.Response:
    return web.Response(text=build_html(), content_type="text/html")


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def create_web_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/app", app_page)
    app.router.add_get("/health", health)
    app.router.add_post("/auth/check", auth_check)
    return app


async def start_web():
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"WEB STARTED ON PORT {PORT}")


async def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("Укажи BOT_TOKEN")
    if not BASE_URL or BASE_URL == "https://your-domain.up.railway.app":
        raise RuntimeError("Укажи BASE_URL")
    if not PARTNER_ID:
        raise RuntimeError("Укажи PARTNER_ID")
    if not API_TOKEN:
        raise RuntimeError("Укажи API_TOKEN")

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("BOT STARTED")
    await dp.start_polling(bot)


async def main():
    await asyncio.gather(
        start_web(),
        start_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
