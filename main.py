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
        "🤖 <b>Добро пожаловать в торгового бота нового поколения</b>\n\n"
        "Этот терминал объединяет сигналы, обучение, стратегии и поддержку внутри Telegram.\n\n"
        "⚡ Премиальный интерфейс\n"
        "📈 Рынки и сигналы\n"
        "🧠 Обучение и стратегии\n"
        "💎 Современный стиль 2026\n\n"
        "Чтобы начать работу, нажми кнопку ниже:\n"
        "<b>🚀 Открыть терминал</b>"
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
      --accent:#d9dde4;
      --accentDark:#8b95a1;
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
      padding:18px;
      background:
        radial-gradient(circle at top right, rgba(255,255,255,.12), transparent 25%),
        linear-gradient(135deg, #20242b, #151920 65%, #262b34);
    }

    .hero-title{
      font-size:24px;
      font-weight:900;
      line-height:1.2;
      margin-bottom:8px;
      color:#f8fbff;
    }

    .hero-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.62;
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

    .mini-stats{
      display:grid;
      grid-template-columns:repeat(3,1fr);
      gap:10px;
      margin-top:10px;
    }

    .stat-card{
      padding:12px;
      border-radius:18px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02)),
        #161b22;
      border:1px solid rgba(255,255,255,.08);
      text-align:center;
    }

    .stat-label{
      font-size:11px;
      color:var(--muted);
      margin-bottom:6px;
      font-weight:800;
      text-transform:uppercase;
      letter-spacing:.4px;
    }

    .stat-value{
      font-size:18px;
      font-weight:900;
      color:#f8fbff;
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
      transition:width .25s linear;
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
      min-width:90px;
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
    .lesson-box,
    .strategy-card{
      padding:14px;
      border-radius:18px;
      background:#141a22;
      border:1px solid rgba(255,255,255,.07);
      margin-bottom:10px;
    }

    .support-title,
    .strategy-title{
      font-size:15px;
      font-weight:900;
      margin-bottom:5px;
    }

    .support-text,
    .strategy-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.65;
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

    .strategy-kicker{
      color:#d9dde3;
      font-size:11px;
      font-weight:900;
      letter-spacing:.4px;
      margin-bottom:8px;
      text-transform:uppercase;
    }

    .strategy-title-big{
      font-size:20px;
      font-weight:900;
      margin-bottom:10px;
      line-height:1.25;
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
        <div class="hero-title">Добро пожаловать в профессиональный терминал</div>
        <div class="hero-text">
          Современный trading mini app с сигналами, обучением, стратегиями и поддержкой.
          Серебристо-хромовый стиль, быстрый доступ к рынкам и удобная навигация.
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

          <button class="menu-btn" onclick="showScreen('strategies-menu')">
            <div class="menu-title">4. Торговые стратегии</div>
            <div class="menu-desc">Подборка из 15 детально расписанных стратегий с логикой, фильтрами и ошибками новичков.</div>
          </button>
        </div>

        <div class="mini-stats">
          <div class="stat-card">
            <div class="stat-label">Markets</div>
            <div class="stat-value">4</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Стратегий</div>
            <div class="stat-value">15</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Обучение</div>
            <div class="stat-value">PRO</div>
          </div>
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
            <div class="menu-desc">Топовые OTC активы, поиск, таймфреймы и выдача сигнала после 5-секундного анализа.</div>
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

    <!-- STRATEGIES MENU -->
    <div id="screen-strategies-menu" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">♟</div>
          <div>
            <div class="title">Торговые стратегии</div>
            <div class="subtitle">Подборка систем и логики входа</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Выбери стратегию</div>
        <div class="section-sub">Ни одна стратегия не даёт гарантий. Это обучающий раздел для понимания логики входа и фильтрации рынка.</div>
        <div class="menu-grid" id="strategiesList"></div>
        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <!-- STRATEGY DETAIL -->
    <div id="screen-strategy-detail" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">📘</div>
          <div>
            <div class="title">Стратегия</div>
            <div class="subtitle">Подробное описание</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="strategy-card">
          <div class="strategy-kicker" id="strategyKicker">Стратегия 1</div>
          <div class="strategy-title-big" id="strategyTitleBig">Название стратегии</div>

          <div class="strategy-section">
            <div class="strategy-section-title">Суть стратегии</div>
            <div class="strategy-section-text" id="strategyCore"></div>
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
      <button id="tab-strategies" class="tab-btn" onclick="showScreen('strategies-menu')">Стратегии</button>
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
        },
        {
          kicker: "Психология • Урок 4",
          title: "Дисциплина",
          text: "Сильный трейдер отличается не количеством сделок, а качеством решений. Иногда лучший ход — это пропустить вход. Если ты не умеешь ждать, ты будешь входить в слабые ситуации и отдавать деньги рынку.",
          main: "Главная мысль: лучше 2 точных входа, чем 15 хаотичных."
        },
        {
          kicker: "Психология • Урок 5",
          title: "Правильное состояние перед торговлей",
          text: "Перед сессией ты должен быть спокойным, собранным и готовым пропускать плохие сигналы. Если ты раздражён, уставший или хочешь быстро заработать любой ценой — это уже плохое состояние для торговли.",
          main: "Главная мысль: сначала состояние, потом рынок. Нервный трейдер почти всегда принимает плохие решения."
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
          title: "Почему цена движется",
          text: "Цена движется из-за спроса, предложения, новостей, волатильности и активности участников. Иногда движение плавное, иногда резкое. Чтобы торговать лучше, нужно понимать не просто направление, а контекст движения.",
          main: "Главная мысль: цена не двигается просто так — у любого движения есть причина."
        },
        {
          kicker: "Рынок • Урок 3",
          title: "Импульс и откат",
          text: "Импульс — это сильное движение цены в одну сторону. Откат — это временное движение против основного импульса. Очень важно не путать эти два состояния, иначе можно войти в рынок в самый неудобный момент.",
          main: "Главная мысль: не входи в конец импульса и учись видеть, где цена уже перегрета."
        },
        {
          kicker: "Рынок • Урок 4",
          title: "Тренд и флет",
          text: "Тренд — это устойчивое направленное движение цены. Флет — это боковое движение без явного лидера. Одни входы хорошо работают в тренде, другие — во флете. Если не понимать фазу рынка, входы будут случайными.",
          main: "Главная мысль: сначала определи фазу рынка, потом ищи вход."
        },
        {
          kicker: "Рынок • Урок 5",
          title: "Поддержка и сопротивление",
          text: "Поддержка — зона, где цена часто удерживается от падения. Сопротивление — зона, где цена часто удерживается от роста. Это одни из самых сильных ориентиров в торговле, потому что у уровней часто скапливается реакция рынка.",
          main: "Главная мысль: уровни — это основа понимания, где цена может остановиться или развернуться."
        },
        {
          kicker: "Рынок • Урок 6",
          title: "Волатильность",
          text: "Волатильность — это скорость и сила движения цены. Когда рынок слишком резкий, короткие входы становятся опаснее. Высокая волатильность без понимания структуры часто приводит к хаотичным сделкам.",
          main: "Главная мысль: не каждый быстрый рынок подходит для входа."
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
          title: "Работай с фиксированной суммой",
          text: "На маленьком депозите не увеличивай сумму хаотично. Торговля должна быть стабильной. Один неправильный шаг на завышенной сумме может перечеркнуть всё, что заработано до этого.",
          main: "Главная мысль: стабильность важнее агрессии."
        },
        {
          kicker: "Правила • Урок 4",
          title: "Не входи в длинные тени",
          text: "Если свечи рваные, с большими тенями и рынок дёргается, вход становится слабее. Такой рынок труднее читать, особенно на коротких таймфреймах.",
          main: "Главная мысль: если рынок выглядит грязно — лучше пропустить."
        },
        {
          kicker: "Правила • Урок 5",
          title: "Не входи в конец импульса",
          text: "Когда движение уже прошло большую часть пути, вход часто становится поздним. Новички любят влетать именно туда, где движение уже выдохлось.",
          main: "Главная мысль: чем позже вход, тем слабее вероятность."
        },
        {
          kicker: "Правила • Урок 6",
          title: "Лучше пропустить, чем залететь случайно",
          text: "Пропущенная плохая сделка — это не потеря, а сохранённый депозит. Торговля строится не только на хороших входах, но и на умении отказаться от слабых.",
          main: "Главная мысль: умение не входить — это часть профессионализма."
        },
        {
          kicker: "Правила • Урок 7",
          title: "После серии минусов — пауза",
          text: "Несколько неудач подряд часто ломают психологию. В этот момент решения становятся всё хуже. Лучше остановиться, выдохнуть и вернуться позже, чем продолжать ломать депозит.",
          main: "Главная мысль: пауза после эмоциональной просадки — это сила, а не слабость."
        }
      ]
    };

    const STRATEGIES = [
      {
        title: "Отбой от уровня поддержки или сопротивления",
        core: "Это одна из самых базовых и сильных стратегий. Суть в том, что цена часто реагирует на области, где ранее уже останавливалась. Если актив подходит к сильной зоне поддержки или сопротивления и показывает замедление, отклонение или слабость пробоя, появляется идея входа в обратную сторону.",
        entry: "Сначала находишь визуально понятный уровень, где цена уже делала реакцию раньше. Затем ждёшь повторного подхода. На подходе смотришь, есть ли замедление, маленькие свечи, длинные тени, отказ идти дальше или резкий откат от зоны. После этого ищешь короткий вход в сторону отбоя.",
        filters: "Лучше всего работает, когда уровень уже подтверждался ранее. Хорошо, если подход к уровню не хаотичный, а плавный. Дополнительный плюс — если рынок не слишком рваный и нет сильного новостного импульса.",
        mistakes: "Главная ошибка — входить просто потому, что цена коснулась линии. Само касание ещё не равно сильному отскоку. Вторая ошибка — брать отбой против мощного импульса без признаков замедления.",
        markets: "Подходит для ОТС, официалов и части крипты. Лучше всего на коротких и средних таймфреймах, когда рынок читается визуально."
      },
      {
        title: "Пробой уровня с подтверждением",
        core: "Это стратегия не на отбой, а на продолжение движения. Если цена долго упиралась в уровень и затем уверенно его прошла, часто начинается новая волна движения. Но входить нужно не в первую секунду пробоя, а после подтверждения силы.",
        entry: "Смотришь, где цена несколько раз не могла пройти зону. Затем ждёшь уверенный пробой сильной свечой или серией свечей. После пробоя можно входить либо сразу при явной силе, либо после небольшого возврата к пробитой зоне, если рынок не потерял импульс.",
        filters: "Сильный пробой — это не просто укол, а движение с телом свечи. Объективно лучше, когда после выхода за уровень цена не возвращается назад мгновенно. Полезно смотреть, есть ли запас пространства до следующей зоны.",
        mistakes: "Самая частая ошибка — путать ложный пробой с настоящим. Если цена только проколола уровень тенью и сразу вернулась, это слабый сценарий. Вторая ошибка — прыгать в перегретое движение уже после длинной свечи без оценки контекста.",
        markets: "Лучше работает на трендовых движениях официалов, крипты и активных ОТС периодах."
      },
      {
        title: "Продолжение тренда после отката",
        core: "Одна из самых логичных стратегий. Если рынок уже идёт вверх или вниз, лучшая идея часто не ловить разворот, а дождаться отката и войти по тренду. Так ты торгуешь вместе с основным движением, а не против него.",
        entry: "Сначала определяешь тренд по структуре: серия более высоких максимумов и минимумов или наоборот. Потом ждёшь откат против тренда. Если после отката цена снова начинает возвращаться по основному направлению, ищешь вход.",
        filters: "Подтверждением может быть слабость отката, короткие свечи против тренда, возврат к поддержке/сопротивлению, ускорение в сторону основного движения. Важно, чтобы тренд был визуально понятным.",
        mistakes: "Ошибка — принимать любой хаос за тренд. Если рынок пилит туда-сюда, это не тренд. Вторая ошибка — входить слишком рано, когда откат ещё не закончился.",
        markets: "Сильнее всего работает на официалах и крипте, но на ОТС тоже можно использовать, если рынок направленный."
      },
      {
        title: "Ложный пробой уровня",
        core: "Ложный пробой — мощный паттерн, когда цена как будто проходит уровень, привлекает толпу в одну сторону, а затем резко возвращается назад. Часто это даёт хороший контрдвижущийся вход.",
        entry: "Находишь сильную зону. Ждёшь пробой уровня не телом подтверждения, а скорее уколом или резким выносом. Если после этого цена быстро возвращается обратно за уровень, можно рассматривать вход против ложного пробоя.",
        filters: "Лучше, если возврат назад происходит быстро. Также хорошо, если на уровне уже была реакция раньше. Важен контекст: ложный пробой сильнее у границ диапазона, чем посреди хаоса.",
        mistakes: "Ошибка — заранее угадывать ложный пробой до подтверждения. Нужно дождаться возврата цены, а не думать, что любой вынос обязательно окажется ложным.",
        markets: "Подходит почти везде, особенно на ОТС и валютах во флете."
      },
      {
        title: "Торговля во флете от границ диапазона",
        core: "Когда цена не трендит, а двигается в коридоре, можно работать от верхней и нижней границы этого диапазона. Это стратегия не для сильного импульса, а для спокойного рынка.",
        entry: "Определи границы, где цена уже минимум дважды реагировала. Вход ищется на подходе к верхней границе вниз или к нижней вверх, но только при наличии реакции, а не заранее вслепую.",
        filters: "Лучше всего, когда диапазон широкий и читаемый. Слабые свечи на краях диапазона, длинные тени и отказ идти дальше усиливают идею.",
        mistakes: "Ошибка — путать флет с накоплением перед пробоем. Если рынок начинает резко сжиматься и давление на одну из сторон растёт, возможен выход из диапазона.",
        markets: "Хорошо работает на ОТС и части официальных валют в спокойные часы."
      },
      {
        title: "Импульс после консолидации",
        core: "После узкого накопления цена часто делает резкое движение. Эта стратегия строится на том, что период сжатия волатильности часто заканчивается импульсом.",
        entry: "Находишь участок, где свечи маленькие, диапазон узкий и цена сжалась. Затем ждёшь выноса из этой зоны и входишь по направлению сильного движения, если пробой выглядит уверенно.",
        filters: "Полезно, если перед консолидацией уже было движение — тогда чаще идёт продолжение. Слабый ложный вынос не подходит. Нужна сила и понятная направленность.",
        mistakes: "Ошибка — торговать любой боковик. Не всякий боковик даёт качественный импульс. Также опасно входить в момент, когда цена уже ушла слишком далеко от зоны.",
        markets: "Часто даёт хорошие движения на крипте и официалах."
      },
      {
        title: "Свечной разворот у уровня",
        core: "Это стратегия, где основной упор делается на реакцию свечей у важной зоны. Не просто уровень, а уровень плюс форма поведения цены на нём.",
        entry: "Ждёшь подход к уровню. Смотришь на свечи: длинная тень, резкий откат, серия отказов идти дальше, поглощение или мощная ответная свеча. После этого берёшь вход в сторону разворота.",
        filters: "Лучше не брать такую модель посреди пустого места. Свечной разворот сильнее у поддержки, сопротивления, после затухания импульса или на границе диапазона.",
        mistakes: "Ошибка — считать любую красивую свечу самостоятельным сигналом. Без контекста она может ничего не значить.",
        markets: "Подходит для всех рынков, где есть читаемая реакция на зону."
      },
      {
        title: "Возврат после сильного выноса",
        core: "Иногда рынок делает слишком агрессивное движение и временно перегревается. После таких выносов можно искать короткий обратный откат, если видно, что импульс выдохся.",
        entry: "Смотришь на резкое сильное движение одной или несколькими большими свечами. Если после этого цена начинает терять скорость, появляются тени, замедление или короткая консолидация, можно искать краткий вход против выноса.",
        filters: "Работает лучше, если вынос пришёл в сильную зону или после длинного одностороннего движения. Чем больше перегрев, тем выше шанс на локальную разгрузку.",
        mistakes: "Главная ошибка — лезть против свежего сильного импульса слишком рано. Сначала должен появиться хотя бы минимальный признак слабости.",
        markets: "Наиболее полезно на ОТС и крипте, где часто бывают резкие короткие всплески."
      },
      {
        title: "Стратегия после ретеста пробитой зоны",
        core: "После пробоя цена нередко возвращается проверить пробитый уровень с обратной стороны. Это называется ретест. Если уровень выдерживает, возникает хорошая точка продолжения движения.",
        entry: "Ждёшь пробой уровня. Не входишь сразу в хаос. Затем смотришь, вернётся ли цена к пробитой области. Если ретест слабый и цена снова идёт по направлению пробоя — можно входить.",
        filters: "Ретест должен быть аккуратным. Если цена слишком глубоко вернулась назад и колеблется возле уровня, пробой уже выглядит слабее.",
        mistakes: "Ошибка — считать любой возврат хорошим ретестом. Если возврат слишком тяжёлый и идёт с силой, рынок может просто отменить пробой.",
        markets: "Хорошо подходит для официалов и крипты, особенно на движениях с понятной структурой."
      },
      {
        title: "Трендовая линия как фильтр входа",
        core: "Трендовая линия сама по себе не магия, но она полезна как визуальный фильтр структуры. Если цена уважает диагональ и продолжает движение, можно использовать это как дополнительный ориентир.",
        entry: "Проводишь линию по минимумам восходящего движения или максимумам нисходящего. Ждёшь откат к линии и смотришь, сохраняется ли реакция. Если цена не ломает структуру и снова идёт по тренду — ищешь вход.",
        filters: "Трендовая линия должна быть построена не по одной случайной точке, а по нескольким касаниям. Её лучше использовать вместе с уровнями и реакцией свечей.",
        mistakes: "Ошибка — натягивать линию на любой график и верить в неё без подтверждений. Она работает как фильтр, а не как абсолютный сигнал.",
        markets: "Полезна на трендовых рынках, особенно на валютах и криптовалюте."
      },
      {
        title: "Смена характера движения",
        core: "Иногда рынок долго шёл в одну сторону, а потом начинает вести себя иначе: теряет скорость, не обновляет экстремумы, даёт слабые продолжения. Это может быть ранним сигналом на смену сценария.",
        entry: "Смотришь на последовательность движения. Если актив перестал обновлять структуру, импульсы стали слабее, а откаты глубже, можно искать контртрендовую идею после подтверждения разворота.",
        filters: "Важно наличие уровня, зоны или визуальной причины, а не просто чувство, что рынок 'устал'. Подтверждение разворота всегда сильнее догадки.",
        mistakes: "Ошибка — пытаться словить каждую вершину или дно. Смена характера должна быть видна не по одной свече, а по изменению ритма.",
        markets: "Подходит опытным пользователям на всех рынках."
      },
      {
        title: "Вход после двойной реакции",
        core: "Если цена дважды реагирует на одну область, это усиливает значимость зоны. Двойная реакция часто надёжнее единичного касания.",
        entry: "Находишь зону, где уже был первый отбой. Когда цена подходит к ней второй раз, смотришь, появляется ли снова замедление, тени, отклонение. При наличии подтверждения можно брать вход.",
        filters: "Чем чище зона и чем понятнее первая реакция, тем лучше. Также важно, чтобы между первым и вторым подходом структура рынка не успела полностью поменяться.",
        mistakes: "Ошибка — входить только потому, что это 'второе касание'. Всегда нужно смотреть, есть ли фактическая реакция.",
        markets: "Хорошо работает во флете и на понятных уровнях."
      },
      {
        title: "Контекст + свеча подтверждения",
        core: "Это не одна конкретная модель, а более профессиональный подход. Сначала оценивается общий контекст: тренд, уровень, волатильность, направление импульса. И только потом ищется свеча-подтверждение.",
        entry: "Например, цена пришла в сильную область поддержки в рамках общего роста. После этого появляется свеча с сильным отбоем вверх. Вход ищется не на самой зоне вслепую, а после видимого подтверждения.",
        filters: "Контекст должен предшествовать свече. Если есть только одна свеча без общей логики рынка, этого мало.",
        mistakes: "Ошибка — смотреть только на свечной паттерн и игнорировать рыночную картину вокруг.",
        markets: "Это универсальный подход, который уместен почти в любой стратегии."
      },
      {
        title: "Короткий вход после слабого отката",
        core: "Если после сильного движения откат получился очень слабым, это может говорить о силе основного направления. Тогда есть смысл искать продолжение движения.",
        entry: "Смотришь на мощный импульс. Потом ждёшь небольшой откат. Если он вялый, медленный и не ломает структуру, при возвращении силы по основному направлению ищешь вход.",
        filters: "Подтверждает идею ситуация, когда рынок будто бы не хочет идти против основного импульса. Также полезно, если откат происходит в районе локальной зоны.",
        mistakes: "Ошибка — считать любой короткий откат признаком силы. Иногда рынок просто делает паузу перед резким разворотом.",
        markets: "Эффективно на направленных рынках."
      },
      {
        title: "Стратегия 'лучше пропустить, чем залететь'",
        core: "Это скорее профессиональный подход, чем паттерн. Его суть — входить только в самые понятные ситуации и сознательно пропускать слабые. В долгосрочной перспективе это часто работает лучше, чем постоянная торговля без отбора.",
        entry: "Ты не ищешь вход любой ценой. Ты фильтруешь рынок: есть ли уровень, есть ли структура, понятна ли волатильность, не перегрето ли движение, есть ли подтверждение. Только после этого рассматриваешь сделку.",
        filters: "Всё, что выглядит спорно, рвано, импульсивно, запоздало или слишком красиво только на первый взгляд, лучше не брать. Сильный трейдер умеет ждать.",
        mistakes: "Главная ошибка новичка — думать, что чем больше сделок, тем больше заработок. На практике часто работает наоборот.",
        markets: "Подходит абсолютно для всех рынков и должен быть базой поведения трейдера."
      }
    ];

    let currentMarket = "otc";
    let currentTf = "30 сек";
    let currentSelectedAsset = null;

    let currentLessonGroup = "psychology";
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

      if (currentMarket === "otc") {
        startOtcLoading(asset);
      } else {
        renderSignalNow(asset);
      }
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
        `Сценарий по активу ${asset} указывает на возможное движение вверх. Текущая модель выглядит сильнее среднего, а расчётная сила сигнала составляет ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вверх. Сигнал оценивается как ${strength}% по внутренней модели фильтрации и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вверх. Вероятностная сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const textDown = [
        `Сценарий по активу ${asset} указывает на возможное движение вниз. Текущая модель выглядит сильнее среднего, а расчётная сила сигнала составляет ${strength}%. Рабочий интервал — ${tf}.`,
        `По активу ${asset} сохраняется приоритет движения вниз. Сигнал оценивается как ${strength}% по внутренней модели фильтрации и подходит под таймфрейм ${tf}.`,
        `На ${asset} зафиксирован сценарий на движение вниз. Вероятностная сила модели — ${strength}%, рабочее окно входа — ${tf}.`
      ];
      const arr = direction === "ВВЕРХ" ? textUp : textDown;
      return arr[Math.floor(Math.random() * arr.length)];
    }

    function startOtcLoading(asset) {
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

      const totalMs = 5000;
      const intervalMs = 250;
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

      if (currentMarket === "otc") {
        startOtcLoading(currentSelectedAsset);
      } else {
        renderSignalNow(currentSelectedAsset);
      }
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

    function renderStrategiesList() {
      const list = document.getElementById("strategiesList");
      list.innerHTML = "";

      STRATEGIES.forEach((item, index) => {
        const btn = document.createElement("button");
        btn.className = index === 0 ? "menu-btn primary" : "menu-btn";
        btn.innerHTML = `
          <div class="menu-title">${index + 1}. ${item.title}</div>
          <div class="menu-desc">${item.core.slice(0, 150)}...</div>
        `;
        btn.onclick = () => openStrategy(index);
        list.appendChild(btn);
      });
    }

    function openStrategy(index) {
      currentStrategyIndex = index;
      renderStrategy();
      showScreen("strategy-detail");
    }

    function renderStrategy() {
      const strategy = STRATEGIES[currentStrategyIndex];
      document.getElementById("strategyKicker").innerText = `Стратегия ${currentStrategyIndex + 1} из ${STRATEGIES.length}`;
      document.getElementById("strategyTitleBig").innerText = strategy.title;
      document.getElementById("strategyCore").innerText = strategy.core;
      document.getElementById("strategyEntry").innerText = strategy.entry;
      document.getElementById("strategyFilters").innerText = strategy.filters;
      document.getElementById("strategyMistakes").innerText = strategy.mistakes;
      document.getElementById("strategyMarkets").innerText = strategy.markets;

      const nextBtn = document.getElementById("strategyNextBtn");
      if (currentStrategyIndex >= STRATEGIES.length - 1) {
        nextBtn.innerText = "Вернуться к списку стратегий";
      } else {
        nextBtn.innerText = "Следующая стратегия ➜";
      }
    }

    function nextStrategy() {
      if (currentStrategyIndex >= STRATEGIES.length - 1) {
        showScreen("strategies-menu");
        return;
      }
      currentStrategyIndex += 1;
      renderStrategy();
    }

    renderStrategiesList();
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