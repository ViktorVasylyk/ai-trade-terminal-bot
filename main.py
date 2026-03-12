import asyncio
import os
import random

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# =========================================
# CONFIG
# =========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7713470997:AAFhROBNs4LE0EDCCqsyjkJ7SPrC1dDFuo4")
BASE_URL = os.getenv("BASE_URL", "https://your-domain.up.railway.app")
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
        "Этот терминал создан на базе современных технологий анализа рынка и интеллектуальной логики принятия решений.\n\n"
        "⚡ Быстро\n"
        "🧠 Умно\n"
        "📈 Удобно\n"
        "💎 Профессионально\n\n"
        "Это современный торговый продукт с удобным терминалом, обучением и поддержкой внутри Telegram.\n\n"
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
  <title>AI Trade Terminal</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root{
      --bg:#070b14;
      --bg2:#0d1322;
      --card:#10192c;
      --card2:#131f36;
      --line:rgba(255,255,255,.08);
      --text:#ffffff;
      --muted:#9db0d2;
      --blue:#3b82f6;
      --blue2:#2563eb;
      --green:#22c55e;
      --red:#ef4444;
      --gold:#d4af37;
      --shadow:0 12px 40px rgba(0,0,0,.35);
      --radius:20px;
    }

    *{
      box-sizing:border-box;
      margin:0;
      padding:0;
      font-family:Inter,Arial,sans-serif;
      -webkit-tap-highlight-color: transparent;
    }

    body{
      background:
        radial-gradient(circle at top right, rgba(59,130,246,.15), transparent 25%),
        radial-gradient(circle at bottom left, rgba(37,99,235,.12), transparent 25%),
        linear-gradient(180deg, #060913 0%, #0b1220 100%);
      color:var(--text);
      min-height:100vh;
    }

    .wrap{
      max-width:560px;
      margin:0 auto;
      padding:16px 16px 95px;
    }

    .screen{
      display:none;
      animation:fade .2s ease;
    }

    .screen.active{
      display:block;
    }

    @keyframes fade{
      from{opacity:.5; transform:translateY(6px);}
      to{opacity:1; transform:translateY(0);}
    }

    .topbar{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:16px;
      gap:12px;
    }

    .brand{
      display:flex;
      align-items:center;
      gap:12px;
    }

    .logo{
      width:44px;
      height:44px;
      border-radius:14px;
      background:linear-gradient(135deg, var(--blue), var(--blue2));
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:20px;
      box-shadow:var(--shadow);
    }

    .title{
      font-size:22px;
      font-weight:800;
      letter-spacing:.2px;
    }

    .subtitle{
      color:var(--muted);
      font-size:12px;
      margin-top:3px;
    }

    .vip{
      background:linear-gradient(135deg,#19315d,#244eb0);
      border:1px solid rgba(255,255,255,.08);
      color:#e9f1ff;
      border-radius:14px;
      padding:9px 12px;
      font-weight:700;
      font-size:12px;
      white-space:nowrap;
    }

    .card{
      background:linear-gradient(180deg,var(--card),var(--card2));
      border:1px solid var(--line);
      border-radius:var(--radius);
      padding:16px;
      box-shadow:var(--shadow);
      margin-bottom:14px;
    }

    .hero{
      padding:18px;
    }

    .hero-title{
      font-size:24px;
      font-weight:800;
      line-height:1.2;
      margin-bottom:8px;
    }

    .hero-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.55;
    }

    .glow{
      background:
        linear-gradient(135deg, rgba(59,130,246,.16), rgba(37,99,235,.05)),
        linear-gradient(180deg,var(--card),var(--card2));
    }

    .section-title{
      font-size:18px;
      font-weight:800;
      margin-bottom:12px;
    }

    .section-sub{
      color:var(--muted);
      font-size:13px;
      margin-bottom:12px;
      line-height:1.5;
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
      border-radius:18px;
      padding:16px;
      text-align:left;
      color:#fff;
      background:linear-gradient(135deg,#152543,#1d335b);
      border:1px solid rgba(255,255,255,.08);
      box-shadow:var(--shadow);
    }

    .menu-btn.primary{
      background:linear-gradient(135deg,#2450b7,#2f6df6);
    }

    .menu-btn .menu-title{
      font-size:16px;
      font-weight:800;
      margin-bottom:4px;
    }

    .menu-btn .menu-desc{
      color:#d6e2ff;
      opacity:.82;
      font-size:12px;
      line-height:1.45;
    }

    .back-btn{
      width:100%;
      border:none;
      cursor:pointer;
      border-radius:16px;
      padding:14px;
      text-align:center;
      color:#fff;
      background:#18243d;
      border:1px solid rgba(255,255,255,.08);
      font-weight:700;
      margin-top:8px;
    }

    .search{
      width:100%;
      background:#0b1425;
      color:#fff;
      border:1px solid rgba(255,255,255,.08);
      border-radius:16px;
      padding:14px 14px;
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
      background:#172238;
      color:#dbe7ff;
      border:1px solid rgba(255,255,255,.06);
      font-size:12px;
      font-weight:700;
    }

    .tf-btn.active{
      background:linear-gradient(135deg,#2759cf,#3b82f6);
      color:white;
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
      border-radius:16px;
      background:#0f182b;
      border:1px solid rgba(255,255,255,.06);
      cursor:pointer;
    }

    .asset-name{
      font-size:15px;
      font-weight:800;
    }

    .asset-meta{
      margin-top:4px;
      color:var(--muted);
      font-size:12px;
    }

    .badge-mini{
      font-size:11px;
      font-weight:800;
      border-radius:12px;
      padding:8px 10px;
      background:rgba(59,130,246,.14);
      color:#cfe0ff;
      white-space:nowrap;
    }

    .signal-box{
      margin-top:12px;
      border-radius:18px;
      padding:16px;
      background:
        linear-gradient(135deg, rgba(59,130,246,.10), rgba(255,255,255,.02)),
        #0d1729;
      border:1px solid rgba(255,255,255,.08);
    }

    .signal-label{
      color:var(--muted);
      font-size:12px;
      margin-bottom:8px;
    }

    .signal-asset{
      font-size:22px;
      font-weight:900;
      margin-bottom:10px;
    }

    .signal-row{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      margin-bottom:10px;
    }

    .chip{
      padding:10px 12px;
      border-radius:14px;
      background:#15233d;
      border:1px solid rgba(255,255,255,.06);
      font-size:12px;
      font-weight:800;
    }

    .dir-up{
      color:#7df7a6;
    }

    .dir-down{
      color:#ff8f8f;
    }

    .generate-btn{
      width:100%;
      border:none;
      cursor:pointer;
      border-radius:16px;
      padding:15px;
      margin-top:12px;
      font-size:15px;
      font-weight:800;
      color:#fff;
      background:linear-gradient(135deg,#2d61df,#3b82f6);
      box-shadow:var(--shadow);
    }

    .support-item{
      padding:14px;
      border-radius:16px;
      background:#101a2d;
      border:1px solid rgba(255,255,255,.06);
      margin-bottom:10px;
    }

    .support-title{
      font-size:15px;
      font-weight:800;
      margin-bottom:5px;
    }

    .support-text{
      color:var(--muted);
      font-size:13px;
      line-height:1.5;
    }

    .bottom-tabs{
      position:fixed;
      left:0;
      right:0;
      bottom:0;
      background:rgba(8,11,19,.95);
      backdrop-filter:blur(12px);
      border-top:1px solid rgba(255,255,255,.08);
      padding:10px 12px 14px;
      z-index:99;
    }

    .bottom-tabs-inner{
      max-width:560px;
      margin:0 auto;
      display:grid;
      grid-template-columns:repeat(3,1fr);
      gap:8px;
    }

    .tab-btn{
      border:none;
      cursor:pointer;
      border-radius:16px;
      padding:12px 8px;
      text-align:center;
      background:#11182a;
      color:#9db0d2;
      border:1px solid rgba(255,255,255,.06);
      font-size:12px;
      font-weight:800;
    }

    .tab-btn.active{
      color:#fff;
      background:linear-gradient(135deg,#234eb3,#3271f6);
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
            <div class="title">AI Trade Terminal</div>
            <div class="subtitle">Профессиональный торговый интерфейс</div>
          </div>
        </div>
        <div class="vip">2026 EDITION</div>
      </div>

      <div class="card hero glow">
        <div class="hero-title">Добро пожаловать в торговый терминал</div>
        <div class="hero-text">
          Современный интерфейс для удобной работы с торговыми сигналами, обучением и поддержкой.
          Всё собрано в одном красивом терминале внутри Telegram.
        </div>
      </div>

      <div class="card">
        <div class="section-title">Главное меню</div>
        <div class="section-sub">Выбери раздел, с которого хочешь начать работу.</div>

        <div class="menu-grid">
          <button class="menu-btn primary" onclick="openTradeMenu()">
            <div class="menu-title">1. Начать торговлю</div>
            <div class="menu-desc">ОТС, официальные валюты, акции, поиск активов, таймфреймы и генерация сигнала.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('education')">
            <div class="menu-title">2. Обучение</div>
            <div class="menu-desc">Базовые принципы работы с сигналами, фильтрация входов и дисциплина.</div>
          </button>

          <button class="menu-btn" onclick="showScreen('support')">
            <div class="menu-title">3. Поддержка</div>
            <div class="menu-desc">Связь с поддержкой, помощь по терминалу и ответы на частые вопросы.</div>
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
            <div class="menu-desc">Топовые OTC активы, быстрый поиск, таймфреймы и сигнал в 1 клик.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('official')">
            <div class="menu-title">2. Торговля Официалов</div>
            <div class="menu-desc">Официальные валютные пары с поиском, таймфреймами и генерацией сигнала.</div>
          </button>

          <button class="menu-btn" onclick="openMarket('stocks')">
            <div class="menu-title">3. Торговля Акциями</div>
            <div class="menu-desc">Популярные акции с быстрым переходом к сигналу и выбором времени входа.</div>
          </button>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
      </div>
    </div>

    <!-- MARKET -->
    <div id="screen-market" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">💹</div>
          <div>
            <div class="title" id="marketTitle">Рынок</div>
            <div class="subtitle" id="marketSub">Выбор актива и генерация сигнала</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Выбор актива</div>
        <input id="assetSearch" class="search" type="text" placeholder="Введи актив, например EUR/USD" oninput="renderAssets()" />

        <div class="tf-row" id="timeframeRow">
          <button class="tf-btn active" data-tf="30 сек" onclick="selectTf('30 сек')">30 сек</button>
          <button class="tf-btn" data-tf="1 мин" onclick="selectTf('1 мин')">1 мин</button>
          <button class="tf-btn" data-tf="2 мин" onclick="selectTf('2 мин')">2 мин</button>
          <button class="tf-btn" data-tf="3 мин" onclick="selectTf('3 мин')">3 мин</button>
        </div>

        <div class="asset-list" id="assetList"></div>

        <div class="signal-box" id="signalBox" style="display:none;">
          <div class="signal-label">Торговый сигнал</div>
          <div class="signal-asset" id="signalAsset">EUR/USD</div>
          <div class="signal-row">
            <div class="chip" id="signalDirection">ВВЕРХ</div>
            <div class="chip" id="signalTime">30 сек</div>
            <div class="chip" id="signalType">OTC</div>
          </div>
          <div class="section-sub" id="signalComment" style="margin:0;">
            Сигнал сгенерирован для тестового режима терминала.
          </div>
          <button class="generate-btn" onclick="generateCurrentSignal()">🔁 Сгенерировать ещё сигнал</button>
        </div>

        <button class="back-btn" onclick="showScreen('trade-menu')">⬅ Назад</button>
      </div>
    </div>

    <!-- EDUCATION -->
    <div id="screen-education" class="screen">
      <div class="topbar">
        <div class="brand">
          <div class="logo">🎓</div>
          <div>
            <div class="title">Обучение</div>
            <div class="subtitle">Базовые правила и дисциплина</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">Основы работы</div>
        <div class="support-item">
          <div class="support-title">1. Не входи хаотично</div>
          <div class="support-text">Всегда смотри на общий ритм рынка и не открывай сделки без логики и плана.</div>
        </div>
        <div class="support-item">
          <div class="support-title">2. Не гонись за рынком</div>
          <div class="support-text">Если движение уже прошло — лучше пропустить вход, чем залететь в конец импульса.</div>
        </div>
        <div class="support-item">
          <div class="support-title">3. Уважай риск</div>
          <div class="support-text">Фиксированная сумма на вход и контроль эмоций всегда важнее случайной удачи.</div>
        </div>
        <div class="support-item">
          <div class="support-title">4. Сначала фильтр, потом вход</div>
          <div class="support-text">Сигнал — это ориентир. Лучший результат даёт сигнал + здравый фильтр рынка.</div>
        </div>

        <button class="back-btn" onclick="showScreen('home')">⬅ Назад</button>
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
      <button id="tab-education" class="tab-btn" onclick="showScreen('education')">Обучение</button>
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

    let currentScreen = "home";
    let currentMarket = "otc";
    let currentTf = "30 сек";
    let currentSelectedAsset = null;

    function setBottomTab(id) {
      document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
      const tab = document.getElementById("tab-" + id);
      if (tab) tab.classList.add("active");
    }

    function showScreen(name) {
      currentScreen = name;
      document.querySelectorAll(".screen").forEach(el => el.classList.remove("active"));

      const target = document.getElementById("screen-" + name);
      if (target) target.classList.add("active");

      if (name === "home") setBottomTab("home");
      if (name === "education") setBottomTab("education");
      if (name === "support") setBottomTab("support");
      if (name === "trade-menu" || name === "market") {
        document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
      }
    }

    function openTradeMenu() {
      showScreen("trade-menu");
    }

    function getMarketAssets() {
      if (currentMarket === "otc") return OTC_ASSETS;
      if (currentMarket === "official") return OFFICIAL_ASSETS;
      return STOCK_ASSETS;
    }

    function getMarketLabel() {
      if (currentMarket === "otc") return "OTC";
      if (currentMarket === "official") return "OFFICIAL";
      return "STOCKS";
    }

    function openMarket(type) {
      currentMarket = type;
      currentSelectedAsset = null;

      const title = document.getElementById("marketTitle");
      const sub = document.getElementById("marketSub");
      const search = document.getElementById("assetSearch");
      const signalBox = document.getElementById("signalBox");

      signalBox.style.display = "none";
      search.value = "";

      if (type === "otc") {
        title.innerText = "Торговля ОТС";
        sub.innerText = "Топовые OTC активы и быстрые сигналы";
      } else if (type === "official") {
        title.innerText = "Торговля Официалов";
        sub.innerText = "Официальные валютные пары";
      } else {
        title.innerText = "Торговля Акциями";
        sub.innerText = "Популярные акции для тестового режима";
      }

      showScreen("market");
      renderAssets();
    }

    function selectTf(tf) {
      currentTf = tf;
      document.querySelectorAll(".tf-btn").forEach(btn => btn.classList.remove("active"));
      const active = document.querySelector(`.tf-btn[data-tf="${tf}"]`);
      if (active) active.classList.add("active");

      if (currentSelectedAsset) {
        generateSignal(currentSelectedAsset);
      }
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
            <div class="asset-meta">Нажми для генерации сигнала</div>
          </div>
          <div class="badge-mini">${getMarketLabel()}</div>
        `;
        el.onclick = () => generateSignal(asset);
        list.appendChild(el);
      });
    }

    function randomDirection() {
      return Math.random() > 0.5 ? "ВВЕРХ" : "ВНИЗ";
    }

    function signalComment(direction, asset, tf) {
      const textUp = [
        `Сигнал по активу ${asset}: возможное движение вверх на ${tf}.`,
        `Импульсный сценарий по ${asset}: приоритет вверх на ${tf}.`,
        `Потенциальный вход по ${asset}: направление вверх, время ${tf}.`
      ];
      const textDown = [
        `Сигнал по активу ${asset}: возможное движение вниз на ${tf}.`,
        `Импульсный сценарий по ${asset}: приоритет вниз на ${tf}.`,
        `Потенциальный вход по ${asset}: направление вниз, время ${tf}.`
      ];
      const arr = direction === "ВВЕРХ" ? textUp : textDown;
      return arr[Math.floor(Math.random() * arr.length)];
    }

    function generateSignal(asset) {
      currentSelectedAsset = asset;
      const direction = randomDirection();
      const signalBox = document.getElementById("signalBox");
      const signalAsset = document.getElementById("signalAsset");
      const signalDirection = document.getElementById("signalDirection");
      const signalTime = document.getElementById("signalTime");
      const signalType = document.getElementById("signalType");
      const signalCommentText = document.getElementById("signalComment");

      signalAsset.innerText = asset;
      signalDirection.innerText = direction;
      signalDirection.className = "chip " + (direction === "ВВЕРХ" ? "dir-up" : "dir-down");
      signalTime.innerText = currentTf;
      signalType.innerText = getMarketLabel();
      signalCommentText.innerText = signalComment(direction, asset, currentTf);

      signalBox.style.display = "block";
      signalBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function generateCurrentSignal() {
      if (!currentSelectedAsset) {
        const marketAssets = getMarketAssets();
        generateSignal(marketAssets[0]);
        return;
      }
      generateSignal(currentSelectedAsset);
    }
  </script>
</body>
</html>
"""

# =========================================
# WEB ROUTES
# =========================================
async def index(request: web.Request) -> web.Response:
    return web.Response(text="AI Trade Terminal is running", content_type="text/plain")

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