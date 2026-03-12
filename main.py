import asyncio
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# =========================================
# CONFIG
# =========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7713470997:AAEvpPQK_aw5A4REz7HLPXKKWtmT-kFoSzU")
BASE_URL = os.getenv("BASE_URL", "https://ai-trade-terminal-bot-production.up.railway.app")
PORT = int(os.getenv("PORT", "8080"))

router = Router()


# =========================================
# BOT KEYBOARD
# =========================================
def main_keyboard() -> ReplyKeyboardMarkup:
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


# =========================================
# BOT START
# =========================================
@router.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "💎 <b>Добро пожаловать в Chrome Trade Terminal</b>\n\n"
        "Премиальный торговый mini app нового поколения внутри Telegram.\n\n"
        "⚡ Сигналы по нескольким рынкам\n"
        "📈 Встроенный анализ активов\n"
        "🧠 Обучение и торговые стратегии\n"
        "🛟 Поддержка внутри терминала\n\n"
        "Открой терминал и начни работу в интерфейсе уровня 2026.\n\n"
        "<b>Нажми кнопку ниже:</b>\n"
        "🚀 <b>Открыть терминал</b>"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# =========================================
# HTML TERMINAL
# =========================================
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
      --bg2:#15181d;
      --card:#181c22;
      --card2:#232832;
      --card3:#11151b;
      --line:rgba(255,255,255,.10);
      --text:#f4f7fb;
      --muted:#b4bcc8;
      --silver1:#f2f5f8;
      --silver2:#d4d9e0;
      --silver3:#a0a8b4;
      --silver4:#7f8792;
      --green:#7df0b2;
      --red:#ff9d9d;
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
      padding:22px 18px;
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
      font-size:27px;
      font-weight:900;
      line-height:1.14;
      margin-bottom:10px;
      color:#f8fbff;
      max-width:360px;
    }

    .hero-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.62;
      max-width:430px;
    }

    .hero-grid{
      display:grid;
      grid-template-columns:repeat(3,1fr);
      gap:10px;
      margin-top:16px;
    }

    .hero-stat{
      padding:12px;
      border-radius:18px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02)),
        #131821;
      border:1px solid rgba(255,255,255,.08);
    }

    .hero-stat-label{
      font-size:11px;
      color:var(--muted);
      margin-bottom:6px;
      font-weight:800;
      text-transform:uppercase;
      letter-spacing:.35px;
    }

    .hero-stat-value{
      font-size:18px;
      font-weight:900;
      color:#f8fbff;
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
    .lesson-box{
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

    <!-- HOME -->
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
          Премиальный стиль, быстрый выбор рынков и удобная логика навигации.
        </div>

        <div class="hero-grid">
          <div class="hero-stat">
            <div class="hero-stat-label">Markets</div>
            <div class="hero-stat-value">4</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-label">Сигналы</div>
            <div class="hero-stat-value">Live</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-label">Format</div>
            <div class="hero-stat-value">Mini App</div>
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
            <div class="menu-desc">Психология, понимание рынка и правила торговли в формате мини-курса.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('support')">
            <div class="menu-title">3. Поддержка</div>
            <div class="menu-desc">Помощь по терминалу, ответы на частые вопросы и связь с менеджером.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('home')">
            <div class="menu-title">4. Торговые стратегии</div>
            <div class="menu-desc">Раздел пока можно оставить в отдельной версии. Сейчас основной фокус — premium UX и сигнальный flow.</div>
          </button>
        </div>
      </div>
    </div>

    <!-- TRADE MENU -->
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
            <div class="menu-desc">Официальные валютные пары с поиском, таймфреймами и генерацией сигнала.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('stocks')">
            <div class="menu-title">3. Торговля Акциями</div>
            <div class="menu-desc">Популярные акции с быстрым переходом к анализу и выбором времени входа.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('crypto')">
            <div class="menu-title">4. Торговля криптовалютой</div>
            <div class="menu-desc">Криптоактивы с поиском, таймфреймами и генерацией сигнала.</div>
          </button>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <!-- MARKET LIST -->
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

    <!-- ANALYSIS -->
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

    <!-- EDUCATION MENU -->
    <div id="screen-education-menu" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">🎓</div>
          <div>
            <div class="title">Обучение</div>
            <div class="subtitle">Мини-курс внутри терминала</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Разделы обучения</div>
        <div class="section-sub">Изучи основу, без которой стабильная торговля невозможна.</div>

        <div class="menu-grid">
          <button class="menu-btn primary" onclick="openLesson('psychology', 0)">
            <div class="menu-title">1. Психология</div>
            <div class="menu-desc">Эмоции, дисциплина, страх, жадность, правильное состояние перед торговлей.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('market', 0)">
            <div class="menu-title">2. Что такое рынок</div>
            <div class="menu-desc">Импульс, откат, тренд, флет, уровни, волатильность и логика движения цены.</div>
          </button>

          <button class="menu-btn" onclick="openLesson('rules', 0)">
            <div class="menu-title">3. Правила торговли</div>
            <div class="menu-desc">Когда входить, когда не входить, как фильтровать сделки и сохранять депозит.</div>
          </button>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <!-- LESSON -->
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

    <!-- SUPPORT -->
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
      <button id="tab-strategies" class="tab-btn" onclick="showScreen('home')">Стратегии</button>
      <button id="tab-support" class="tab-btn" onclick="showScreen('support')">Поддержка</button>
    </div>
  </div>

  <script>
    if (window.Telegram && window.Telegram.WebApp) {
      Telegram.WebApp.ready();
      Telegram.WebApp.expand();
    }

    const OTC_ASSETS = [
      "AED/CNY",
      "USD/BDT OTC",
      "EUR/USD OTC",
      "GBP/USD OTC",
      "USD/JPY OTC",
      "AUD/USD OTC",
      "NZD/JPY OTC"
    ];

    const OFFICIAL_ASSETS = [
      "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF",
      "NZD/USD", "EUR/JPY", "EUR/GBP", "EUR/CHF", "EUR/AUD", "EUR/CAD",
      "GBP/JPY", "GBP/CHF", "GBP/AUD", "GBP/CAD", "AUD/JPY", "AUD/CAD",
      "AUD/CHF", "CAD/JPY", "CHF/JPY", "NZD/JPY", "NZD/CAD", "NZD/CHF",
      "EUR/NZD", "GBP/NZD", "AUD/NZD", "USD/SGD", "USD/MXN", "USD/NOK",
      "USD/SEK", "USD/TRY", "USD/ZAR", "EUR/SEK", "EUR/NOK", "EUR/TRY"
    ];

    const STOCK_ASSETS = [
      "Apple", "Tesla", "Amazon", "Google", "Meta", "Microsoft",
      "NVIDIA", "Netflix", "Intel", "AMD", "Coca-Cola", "McDonald's",
      "Nike", "Disney", "Boeing", "Alibaba", "Uber", "Pfizer"
    ];

    const CRYPTO_ASSETS = [
      "Bitcoin", "Ethereum", "Litecoin", "Dash", "Chainlink",
      "BCH/EUR", "BCH/GBP", "BCH/JPY", "BTC/GBP", "BTC/JPY",
      "Bitcoin OTC", "Ethereum OTC", "Litecoin OTC", "Solana OTC",
      "Polkadot OTC", "BNB OTC", "Dogecoin OTC", "Cardano OTC",
      "Avalanche OTC", "TRON OTC", "Toncoin OTC", "Polygon OTC",
      "Bitcoin ETF OTC"
    ];

    const LESSONS = {
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
          text: "Страх заставляет пропускать хорошие входы. Жадность заставляет входить без подтверждения и брать лишние сделки. Оба состояния мешают торговле, потому что в этот момент решение принимает не система, а эмоция.",
          main: "Главная мысль: страх и жадность всегда ломают дисциплину, если ты не умеешь замечать их вовремя."
        },
        {
          kicker: "Психология • Урок 3",
          title: "Почему новички сливают депозит",
          text: "Основные причины: торговля без плана, завышенные суммы, попытка быстро отбить минус, входы без фильтра и хаотичное нажатие кнопок. Проблема не всегда в стратегии — чаще проблема в поведении самого трейдера.",
          main: "Главная мысль: депозит чаще сливают не из-за рынка, а из-за отсутствия дисциплины."
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
          text: "Импульс — это сильное движение цены в одну сторону. Откат — это временное движение против основного импульса. Очень важно не путать эти два состояния, иначе можно войти в рынок в самый неудобный момент.",
          main: "Главная мысль: не входи в конец импульса и учись видеть, где цена уже перегрета."
        },
        {
          kicker: "Рынок • Урок 3",
          title: "Поддержка и сопротивление",
          text: "Поддержка — зона, где цена часто удерживается от падения. Сопротивление — зона, где цена часто удерживается от роста. Это одни из самых сильных ориентиров в торговле, потому что у уровней часто скапливается реакция рынка.",
          main: "Главная мысль: уровни — это основа понимания, где цена может остановиться или развернуться."
        }
      ],
      rules: [
        {
          kicker: "Правила • Урок 1",
          title: "Не входи без причины",
          text: "Каждая сделка должна иметь логичную причину: уровень, импульс, подтверждение, структура движения. Если причина входа звучит как 'мне кажется', значит это слабая сделка.",
          main: "Главная мысль: хорошая сделка всегда объяснима."
        },
        {
          kicker: "Правила • Урок 2",
          title: "Не торгуй на эмоциях",
          text: "После минуса у многих появляется желание сразу открыть следующую сделку, чтобы отбиться. Это одна из главных ошибок. Сделка после эмоции редко бывает сильной.",
          main: "Главная мысль: эмоция не может быть основанием для входа."
        },
        {
          kicker: "Правила • Урок 3",
          title: "Лучше пропустить, чем залететь случайно",
          text: "Пропущенная плохая сделка — это не потеря, а сохранённый депозит. Торговля строится не только на хороших входах, но и на умении отказаться от слабых.",
          main: "Главная мысль: умение не входить — это часть профессионализма."
        }
      ]
    };

    let currentMarket = "otc";
    let currentTf = "30 сек";
    let currentSelectedAsset = null;
    let currentLessonGroup = "psychology";
    let currentLessonIndex = 0;
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

      const title = document.getElementById("marketTitle");
      const sub = document.getElementById("marketSub");
      const search = document.getElementById("assetSearch");

      search.value = "";

      if (type === "otc") {
        title.innerText = "Торговля ОТС";
        sub.innerText = "Выбор OTC актива";
      } else if (type === "official") {
        title.innerText = "Торговля Официалов";
        sub.innerText = "Выбор официального актива";
      } else if (type === "stocks") {
        title.innerText = "Торговля Акциями";
        sub.innerText = "Выбор акции";
      } else {
        title.innerText = "Торговля криптовалютой";
        sub.innerText = "Выбор криптоактива";
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
      const marketAssets = getMarketAssets();
      const filtered = marketAssets.filter(a => a.toLowerCase().includes(searchValue));

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

      const loadingBox = document.getElementById("loadingBox");
      const analysisBox = document.getElementById("analysisBox");
      const loadingFill = document.getElementById("loadingFill");
      const loadingText = document.getElementById("loadingText");

      loadingBox.style.display = "none";
      analysisBox.style.display = "none";
      loadingFill.style.width = "0%";
      loadingText.innerText = "Подготавливаем торговый сигнал";

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
      const textUp = [
        `Сценарий по активу ${asset} указывает на возможное движение вверх. Расчётная сила сигнала — ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вверх. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вверх. Сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const textDown = [
        `Сценарий по активу ${asset} указывает на возможное движение вниз. Расчётная сила сигнала — ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вниз. Сигнал оценивается как ${strength}% и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вниз. Сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const arr = direction === "ВВЕРХ" ? textUp : textDown;
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
      const analysisBox = document.getElementById("analysisBox");
      const signalAsset = document.getElementById("signalAsset");
      const signalDirection = document.getElementById("signalDirection");
      const signalTime = document.getElementById("signalTime");
      const signalType = document.getElementById("signalType");
      const signalCommentText = document.getElementById("signalComment");
      const signalMarketLine = document.getElementById("signalMarketLine");
      const signalStrength = document.getElementById("signalStrength");

      signalAsset.innerText = asset;
      signalDirection.innerText = direction;
      signalDirection.className = "chip " + (direction === "ВВЕРХ" ? "dir-up" : "dir-down");
      signalTime.innerText = currentTf;
      signalType.innerText = getMarketLabel();
      signalCommentText.innerText = signalComment(direction, asset, currentTf, strength);
      signalMarketLine.innerText = `${getMarketLabel()} • ${currentTf}`;
      signalStrength.innerText = `${strength}%`;

      analysisBox.style.display = "block";
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
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(W, y);
          ctx.stroke();
        }

        for (let i = 0; i < 8; i++) {
          const x = (W / 8) * i;
          ctx.strokeStyle = "rgba(255,255,255,0.04)";
          ctx.lineWidth = 1;
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

      const categoryTitle = document.getElementById("lessonCategoryTitle");
      const categorySub = document.getElementById("lessonCategorySub");
      const kicker = document.getElementById("lessonKicker");
      const title = document.getElementById("lessonTitle");
      const text = document.getElementById("lessonText");
      const main = document.getElementById("lessonMain");
      const nextBtn = document.getElementById("lessonNextBtn");

      if (currentLessonGroup === "psychology") {
        categoryTitle.innerText = "Психология";
        categorySub.innerText = "Контроль эмоций и дисциплина";
      } else if (currentLessonGroup === "market") {
        categoryTitle.innerText = "Что такое рынок";
        categorySub.innerText = "Понимание структуры движения цены";
      } else {
        categoryTitle.innerText = "Правила торговли";
        categorySub.innerText = "Фильтрация входов и защита депозита";
      }

      kicker.innerText = lesson.kicker;
      title.innerText = lesson.title;
      text.innerText = lesson.text;
      main.innerText = lesson.main;

      if (currentLessonIndex >= LESSONS[currentLessonGroup].length - 1) {
        nextBtn.innerText = "Вернуться в обучение";
      } else {
        nextBtn.innerText = "Следующий урок ➜";
      }
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
  </script>
</body>
</html>
"""

# =========================================
# WEB ROUTES
# =========================================
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
    return app

# =========================================
# STARTUP
# =========================================
async def start_web():
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"WEB STARTED ON PORT {PORT}")

async def start_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN":
        raise RuntimeError("Укажи BOT_TOKEN")
    if not BASE_URL or BASE_URL == "https://your-domain.up.railway.app":
        raise RuntimeError("Укажи BASE_URL")

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