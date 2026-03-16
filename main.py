import asyncio
import hashlib
import hmac
import json
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qsl

import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7713470997:AAG0jqwe0fiYb1Qn-lSRVvvgrePcuAyeZ4M")
BASE_URL = os.getenv("BASE_URL", "https://ai-trade-terminal-bot-production.up.railway.app")
PORT = int(os.getenv("PORT", "8080"))

PARTNER_ID = os.getenv("PARTNER_ID", "51641")
API_TOKEN = os.getenv("API_TOKEN", "AdrPoT7UjHjggMAJNda3")

REF_LINK = os.getenv("REF_LINK", "https://u3.shortink.io/smart/ROGGOnnWSoGn5O")
REVIEWS_GROUP_LINK = os.getenv("REVIEWS_GROUP_LINK", "https://t.me/+6jtb0MDtb_A0YTQy")

AUTO_CHECK_EVERY_SEC = int(os.getenv("AUTO_CHECK_EVERY_SEC", str(10 * 60)))
AUTO_CHECK_TOTAL_SEC = int(os.getenv("AUTO_CHECK_TOTAL_SEC", str(3 * 60 * 60)))
AUTO_CHECK_MAX_RUNS = max(1, AUTO_CHECK_TOTAL_SEC // AUTO_CHECK_EVERY_SEC)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ALLOWED_USERS_FILE = DATA_DIR / "allowed_users.json"

router = Router()
WAITING_ID = set()
PENDING: Dict[int, Dict[str, Any]] = {}

# ================== ТЕКСТИ ==================
VIP_CAPTION = (
    "☑️ <b>ВАРИАНТЫ VIP ПОДПИСКИ</b>\n"
    "Пожалуйста выберите вариант,\n"
    "по которому хотите попасть в закрытый доступ 👇🏻"
)

FREE_TEXT = (
    "🎁 <b>БОТ БЕСПЛАТНО</b>\n\n"
    "<b>Чтобы получить доступ, сделай 3 простых шага:</b>\n\n"
    "1️⃣ <b>Зарегистрируйся по моей ссылке</b>\n"
    f"👉 {REF_LINK}\n\n"
    "⚠️ <b>ВАЖНО</b>\n"
    "Если у тебя уже есть аккаунт Pocket Option — старый аккаунт нужно удалить.\n"
    "Торговать можно только на аккаунте, который зарегистрирован по моей ссылке.\n\n"
    "2️⃣ <b>Внеси депозит</b>\n"
    "Рекомендую от <b>50$</b> для комфортной работы.\n\n"
    "3️⃣ <b>Нажми «Скинуть ID для проверки»</b> ✅"
)

ACCESS_TEXT = (
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


# ================== КНОПКИ ==================
def kb_want_team() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 ХОЧУ В КОМАНДУ", callback_data="open_vip")]
        ]
    )


def vip_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="БЕСПЛАТНО — реферальная ссылка", callback_data="free_info")],
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


def terminal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚀 Открыть терминал",
                    web_app=WebAppInfo(url=f"{BASE_URL}/app")
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Нажми кнопку, чтобы открыть терминал"
    )


# ================== ХРАНЕНИЕ ДОСТУПА ==================
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
        encoding="utf-8"
    )


def allow_user(user_id: int) -> None:
    users = load_allowed_users()
    users.add(int(user_id))
    save_allowed_users(users)


def is_user_allowed(user_id: int) -> bool:
    return int(user_id) in load_allowed_users()


# ================== TELEGRAM WEBAPP VERIFY ==================
def verify_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
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
        hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if calculated_hash != received_hash:
        return None

    auth_date = pairs.get("auth_date")
    if auth_date:
        try:
            if time.time() - int(auth_date) > 86400:
                return None
        except Exception:
            return None

    user_raw = pairs.get("user")
    if not user_raw:
        return None

    try:
        return json.loads(user_raw)
    except Exception:
        return None


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


def normalize_id(text: str) -> str:
    return (text or "").strip().replace(" ", "")


def looks_like_id(text: str) -> bool:
    return text.isdigit() and 4 <= len(text) <= 20


# ================== AUTO CHECK ==================
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

                    await bot.send_message(chat_id, ACCESS_TEXT, parse_mode="HTML")
                    await bot.send_message(
                        chat_id,
                        "🚀 <b>Открыть терминал</b>",
                        parse_mode="HTML",
                        reply_markup=terminal_keyboard()
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
            reply_markup=deposit_check_kb()
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
        "runs_left": AUTO_CHECK_MAX_RUNS
    }


# ================== HANDLERS ==================
@router.message(CommandStart())
async def start_handler(message: Message):
    if is_user_allowed(message.from_user.id):
        await message.answer(ACCESS_TEXT, parse_mode="HTML", reply_markup=terminal_keyboard())
        return

    await message.answer(make_recruit_text(), parse_mode="HTML", reply_markup=kb_want_team())


@router.message(Command("strat"))
async def strat_handler(message: Message):
    await message.answer(make_recruit_text(), parse_mode="HTML", reply_markup=kb_want_team())


@router.callback_query(F.data == "open_vip")
async def open_vip(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(VIP_CAPTION, parse_mode="HTML", reply_markup=vip_buttons())


@router.callback_query(F.data == "free_info")
async def free_info_handler(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text(FREE_TEXT, parse_mode="HTML", reply_markup=free_kb())
    except Exception:
        await callback.message.answer(FREE_TEXT, parse_mode="HTML", reply_markup=free_kb())


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
    try:
        await callback.message.edit_text(VIP_CAPTION, parse_mode="HTML", reply_markup=vip_buttons())
    except Exception:
        await callback.message.answer(VIP_CAPTION, parse_mode="HTML", reply_markup=vip_buttons())


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
                "❌ <b>Не найдено</b>\n\n"
                "Проверь, правильный ли ID.\n"
                "Если ты только что зарегистрировался — подожди 2-5 минут и отправь ID снова ✅",
                parse_mode="HTML",
            )
            return

        if is_ftd:
            allow_user(message.from_user.id)

            await wait_msg.edit_text(ACCESS_TEXT, parse_mode="HTML")
            await message.answer(
                "🚀 <b>Открыть терминал</b>",
                parse_mode="HTML",
                reply_markup=terminal_keyboard()
            )

            if message.from_user.id in PENDING:
                PENDING.pop(message.from_user.id, None)
        else:
            start_or_refresh_auto_check(message.from_user.id, trader_id, message.chat.id, message.bot)

            minutes = AUTO_CHECK_EVERY_SEC // 60
            hours = AUTO_CHECK_TOTAL_SEC // 3600
            await wait_msg.edit_text(
                "✅ <b>Регистрация подтверждена</b>\n\n"
                "💳 Теперь сделай депозит (FTD) — после этого выдадим полный доступ ✅\n\n"
                f"🤖 Я буду проверять FTD автоматически каждые <b>{minutes} мин</b> "
                f"(до <b>{hours} часов</b>) и открою доступ сразу, как депозит отобразится.",
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


# ================== WEB TERMINAL ==================
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

    .chart-card{
      margin:14px 0;
      border-radius:18px;
      padding:12px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01)),
        #11161d;
      border:1px solid rgba(255,255,255,.07);
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

    .action-btn,.next-btn,.back-btn{
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

    .action-btn.primary,.next-btn{
      color:#111318;
      background:
        linear-gradient(135deg, #8b95a1 0%, #d8dde4 38%, #9da5b0 62%, #f1f4f7 100%);
      border:1px solid rgba(255,255,255,.12);
    }

    .action-btn.secondary,.back-btn{
      color:#fff;
      background:#1a2029;
      border:1px solid rgba(255,255,255,.08);
    }

    .lesson-box,.support-item{
      padding:14px;
      border-radius:18px;
      background:#141a22;
      border:1px solid rgba(255,255,255,.07);
      margin-bottom:10px;
    }

    .lesson-kicker{
      color:#d9dde3;
      font-size:11px;
      font-weight:900;
      letter-spacing:.4px;
      margin-bottom:8px;
      text-transform:uppercase;
    }

    .lesson-title{
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
          Современный рабочий интерфейс с сигналами, анализом, обучением и поддержкой.
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
            <div class="menu-desc">Курс по бинарным опционам, психологии, рынку, свечам и индикаторам.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('support')">
            <div class="menu-title">3. Поддержка</div>
            <div class="menu-desc">Помощь по терминалу и ответы на частые вопросы.</div>
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
            <div class="menu-desc">OTC активы, поиск, таймфреймы и выдача сигнала после анализа.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('official')">
            <div class="menu-title">2. Торговля Официалов</div>
            <div class="menu-desc">Официальные валютные пары с поиском и генерацией сигнала.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('stocks')">
            <div class="menu-title">3. Торговля Акциями</div>
            <div class="menu-desc">Популярные акции с переходом к анализу.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('crypto')">
            <div class="menu-title">4. Торговля криптовалютой</div>
            <div class="menu-desc">Криптоактивы с поиском и анализом.</div>
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
            <div class="subtitle">Короткий учебный блок</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="lesson-box">
          <div class="lesson-kicker">Основы</div>
          <div class="lesson-title">Что важно помнить</div>
          <div class="lesson-text">
            Не входи в рынок без плана. Следи за импульсом, откатом, волатильностью и не торгуй в тильте.
            Любой сигнал — это вероятность, а не гарантия.
          </div>
          <div class="lesson-main">
            Главная мысль: дисциплина важнее эмоций.
          </div>
        </div>
        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
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
          Если у тебя возникли вопросы по работе терминала, настройкам или сигналам — обратись в поддержку.
        </div>
        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

  </div>

  <div class="bottom-tabs">
    <div class="bottom-tabs-inner">
      <button id="tab-home" class="tab-btn active" onclick="showScreen('home')">Главная</button>
      <button id="tab-education" class="tab-btn" onclick="showScreen('education-menu')">Обучение</button>
      <button id="tab-support" class="tab-btn" onclick="showScreen('support')">Поддержка</button>
      <button class="tab-btn" onclick="showScreen('trade-menu')">Торговля</button>
    </div>
  </div>

  <script>
    if (window.Telegram && window.Telegram.WebApp) {
      Telegram.WebApp.ready();
      Telegram.WebApp.expand();
    }

    const OTC_ASSETS = [
      "AED/CNY","USD/BDT OTC","EUR/USD OTC","GBP/USD OTC","USD/JPY OTC","AUD/USD OTC","NZD/JPY OTC"
    ];

    const OFFICIAL_ASSETS = [
      "EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","USD/CHF","NZD/USD","EUR/JPY","EUR/GBP",
      "EUR/CHF","EUR/AUD","EUR/CAD","GBP/JPY","GBP/CHF","GBP/AUD","GBP/CAD","AUD/JPY","AUD/CAD"
    ];

    const STOCK_ASSETS = [
      "Apple","Tesla","Amazon","Google","Meta","Microsoft","NVIDIA","Netflix","Intel","AMD"
    ];

    const CRYPTO_ASSETS = [
      "Bitcoin","Ethereum","Litecoin","Dash","Chainlink","BTC/JPY","Bitcoin OTC","Ethereum OTC","Solana OTC","Dogecoin OTC"
    ];

    let currentMarket = "otc";
    let currentTf = "30 сек";
    let currentSelectedAsset = null;
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
      if (name === "education-menu") setBottomTab("education");
      if (name === "support") setBottomTab("support");
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
        `По активу ${asset} сохраняется приоритет движения вверх. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`
      ];
      const down = [
        `Сценарий по активу ${asset} указывает на возможное движение вниз. Расчётная сила сигнала — ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вниз. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`
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
  </script>
</body>
</html>
"""


def build_denied_html() -> str:
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Доступ закрыт</title>
  <style>
    body{
      margin:0;
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      background:#0f1115;
      color:#fff;
      font-family:Arial,sans-serif;
    }
    .box{
      max-width:420px;
      padding:24px;
      border-radius:18px;
      background:#171b22;
      border:1px solid rgba(255,255,255,.08);
      text-align:center;
    }
    .title{
      font-size:24px;
      font-weight:700;
      margin-bottom:12px;
    }
    .text{
      font-size:15px;
      line-height:1.6;
      color:#c9d1d9;
    }
  </style>
</head>
<body>
  <div class="box">
    <div class="title">⛔ Доступ закрыт</div>
    <div class="text">
      Торговый терминал доступен только после успешной регистрации и подтвержденного FTD.
      Вернись в Telegram-бот и пройди проверку доступа.
    </div>
  </div>
</body>
</html>
"""


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Chrome Trade Terminal is running", content_type="text/plain")


async def auth_webapp(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "reason": "bad_json"}, status=400)

    init_data = data.get("initData", "")
    user = verify_telegram_init_data(init_data, BOT_TOKEN)

    if not user:
        return web.json_response({"ok": False, "reason": "invalid_init_data"}, status=403)

    user_id = user.get("id")
    if not user_id or not is_user_allowed(int(user_id)):
        return web.json_response({"ok": False, "reason": "access_denied"}, status=403)

    return web.json_response({"ok": True, "user_id": int(user_id)})


async def app_page(request: web.Request) -> web.Response:
    return web.Response(text=build_html(), content_type="text/html")


async def denied_page(request: web.Request) -> web.Response:
    return web.Response(text=build_denied_html(), content_type="text/html", status=403)


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def create_web_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/app", app_page)
    app.router.add_post("/auth", auth_webapp)
    app.router.add_get("/denied", denied_page)
    app.router.add_get("/health", health)
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
    if not BASE_URL:
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
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
