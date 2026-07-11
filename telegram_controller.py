#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================================
# ⚙️ الإعدادات - التوكن من المتغيرات البيئية
# ============================================================

TOKEN = os.getenv("8960077800:AAEj8H729UQnN2uaqa8mBceJ78XbhIndUzk")
if not TOKEN:
    print("❌ خطأ: لم يتم تعيين TOKEN في المتغيرات البيئية")
    sys.exit(1)

# ============================================================
# المتغيرات العامة
# ============================================================

BOT_PROCESS = None
BOT_RUNNING = False
BOT_LOGS = []

CONFIG = {
    "matches_per_session": 5,
    "auto_mode": True,
    "delay_min": 0.3,
    "delay_max": 1.5
}

# ============================================================
# خادم Flask (للإبقاء على الخدمة نشطة)
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot_running": BOT_RUNNING,
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "logs_count": len(BOT_LOGS)
    })

@app.route('/status')
def status():
    return jsonify({
        "bot_running": BOT_RUNNING,
        "config": CONFIG,
        "pid": BOT_PROCESS.pid if BOT_PROCESS else None
    })

@app.route('/logs')
def logs():
    return jsonify({"logs": BOT_LOGS[-50:]})

# ============================================================
# دوال بوت Free Fire
# ============================================================

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    BOT_LOGS.append(f"[{timestamp}] {msg}")
    if len(BOT_LOGS) > 200:
        BOT_LOGS.pop(0)
    print(msg)

def run_freefire_bot():
    global BOT_PROCESS, BOT_RUNNING
    
    if BOT_RUNNING:
        log_message("⚠️ البوت يعمل بالفعل")
        return
    
    log_message("🚀 بدء تشغيل بوت Free Fire...")
    
    env = os.environ.copy()
    env["MATCHES"] = str(CONFIG['matches_per_session'])
    env["AUTO_MODE"] = str(CONFIG['auto_mode'])
    env["DELAY_MIN"] = str(CONFIG['delay_min'])
    env["DELAY_MAX"] = str(CONFIG['delay_max'])
    
    try:
        BOT_PROCESS = subprocess.Popen(
            [sys.executable, "freefire_bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        BOT_RUNNING = True
        log_message(f"✅ البوت يعمل (PID: {BOT_PROCESS.pid})")
        
        def read_output():
            for line in BOT_PROCESS.stdout:
                log_message(f"[بوت] {line.strip()}")
        
        threading.Thread(target=read_output, daemon=True).start()
        
    except Exception as e:
        log_message(f"❌ فشل التشغيل: {e}")
        BOT_RUNNING = False
        BOT_PROCESS = None

def stop_freefire_bot():
    global BOT_PROCESS, BOT_RUNNING
    
    if not BOT_RUNNING or BOT_PROCESS is None:
        log_message("⚠️ البوت متوقف بالفعل")
        return
    
    log_message("⏹ إيقاف بوت Free Fire...")
    
    try:
        BOT_PROCESS.terminate()
        time.sleep(2)
        if BOT_PROCESS.poll() is None:
            BOT_PROCESS.kill()
        BOT_RUNNING = False
        BOT_PROCESS = None
        log_message("✅ تم إيقاف البوت")
    except Exception as e:
        log_message(f"❌ فشل الإيقاف: {e}")

def restart_freefire_bot():
    log_message("🔄 إعادة تشغيل البوت...")
    stop_freefire_bot()
    time.sleep(2)
    run_freefire_bot()

# ============================================================
# أوامر تيليجرام
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("▶️ تشغيل البوت", callback_data="run")],
        [InlineKeyboardButton("⏹ إيقاف البوت", callback_data="stop")],
        [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart")],
        [InlineKeyboardButton("📊 الحالة", callback_data="status")],
        [InlineKeyboardButton("📜 السجلات", callback_data="logs")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
        [InlineKeyboardButton("🗑 مسح السجلات", callback_data="clear_logs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *مركز التحكم - بوت Free Fire*\n\n"
        "اختر أمراً من القائمة للتحكم بالبوت.\n\n"
        f"📌 الحالة: {'🟢 يعمل' if BOT_RUNNING else '🔴 متوقف'}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "run":
        if BOT_RUNNING:
            await query.edit_message_text("⚠️ البوت يعمل بالفعل.")
            return
        run_freefire_bot()
        await query.edit_message_text("✅ تم تشغيل البوت.")
    
    elif action == "stop":
        if not BOT_RUNNING:
            await query.edit_message_text("⚠️ البوت متوقف بالفعل.")
            return
        stop_freefire_bot()
        await query.edit_message_text("⏹ تم إيقاف البوت.")
    
    elif action == "restart":
        await query.edit_message_text("🔄 جاري إعادة التشغيل...")
        restart_freefire_bot()
        await query.edit_message_text("✅ تم إعادة التشغيل.")
    
    elif action == "status":
        status = "🟢 يعمل" if BOT_RUNNING else "🔴 متوقف"
        pid = BOT_PROCESS.pid if BOT_PROCESS and BOT_PROCESS.poll() is None else "لا يوجد"
        await query.edit_message_text(
            f"📊 *الحالة*\n\nالحالة: {status}\nPID: {pid}\nالمباريات: {CONFIG['matches_per_session']}",
            parse_mode="Markdown"
        )
    
    elif action == "logs":
        if not BOT_LOGS:
            await query.edit_message_text("📜 لا توجد سجلات.")
            return
        logs_text = "\n".join(BOT_LOGS[-20:])
        await query.edit_message_text(f"📜 *السجلات*\n```\n{logs_text}\n```", parse_mode="Markdown")
    
    elif action == "clear_logs":
        BOT_LOGS.clear()
        await query.edit_message_text("✅ تم مسح السجلات.")
    
    elif action == "settings":
        keyboard = [
            [InlineKeyboardButton(f"🎯 المباريات: {CONFIG['matches_per_session']}", callback_data="edit_matches")],
            [InlineKeyboardButton(f"🤖 التلقائي: {'ON' if CONFIG['auto_mode'] else 'OFF'}", callback_data="toggle_auto")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚙️ *الإعدادات*", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif action.startswith("set_matches_"):
        value = int(action.split("_")[2])
        CONFIG['matches_per_session'] = value
        await query.edit_message_text(f"✅ تم ضبط المباريات إلى {value}.")
    
    elif action == "toggle_auto":
        CONFIG['auto_mode'] = not CONFIG['auto_mode']
        await query.edit_message_text(f"✅ الوضع التلقائي: {'ON' if CONFIG['auto_mode'] else 'OFF'}")
    
    elif action == "back":
        keyboard = [
            [InlineKeyboardButton("▶️ تشغيل", callback_data="run")],
            [InlineKeyboardButton("⏹ إيقاف", callback_data="stop")],
            [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart")],
            [InlineKeyboardButton("📊 الحالة", callback_data="status")],
            [InlineKeyboardButton("📜 السجلات", callback_data="logs")],
            [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🤖 *مركز التحكم*", reply_markup=reply_markup, parse_mode="Markdown")

# ============================================================
# التشغيل الرئيسي
# ============================================================

def run_telegram_bot():
    """تشغيل بوت تيليجرام في خيط منفصل"""
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CallbackQueryHandler(button_handler))
    
    log_message("🤖 بوت تيليجرام يعمل...")
    app_tg.run_polling()

if __name__ == "__main__":
    # تشغيل بوت تيليجرام في الخلفية
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    log_message("🌐 تشغيل خادم الويب على المنفذ 10000...")
    
    # تشغيل خادم Flask (يبقي الخدمة نشطة)
    app.run(host='0.0.0.0', port=10000)
