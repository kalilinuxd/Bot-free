#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import time
import signal
import threading
import subprocess
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================================
# ⚙️ الإعدادات الأساسية - فقط التوكن
# ============================================================

TOKEN = "8960077800:AAEj8H729UQnN2uaqa8mBceJ78XbhIndUzk"  # سيُقرأ من المتغير البيئي إن وُجد

# محاولة قراءة التوكن من البيئة أولاً
if os.getenv("TOKEN"):
    TOKEN = os.getenv("TOKEN")

# ============================================================
# المتغيرات العامة (تُضبط عبر تيليجرام فقط)
# ============================================================

BOT_PROCESS = None
BOT_RUNNING = False
BOT_LOGS = []

# الإعدادات الافتراضية (تُعدّل عبر تيليجرام)
CONFIG = {
    "matches_per_session": 5,
    "auto_mode": True,
    "delay_min": 0.3,
    "delay_max": 1.5
}

# ============================================================
# دوال المساعدة
# ============================================================

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    BOT_LOGS.append(f"[{timestamp}] {msg}")
    if len(BOT_LOGS) > 200:
        BOT_LOGS.pop(0)
    print(msg)

def get_status_text():
    status = "🟢 يعمل" if BOT_RUNNING else "🔴 متوقف"
    pid = BOT_PROCESS.pid if BOT_PROCESS and BOT_PROCESS.poll() is None else "لا يوجد"
    return f"""📊 *حالة البوت*

📌 الحالة: {status}
🆔 PID: {pid}
🎯 المباريات لكل جلسة: {CONFIG['matches_per_session']}
🤖 الوضع التلقائي: {'✅' if CONFIG['auto_mode'] else '❌'}
⏱️ التأخير: {CONFIG['delay_min']}-{CONFIG['delay_max']} ثانية
📅 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# ============================================================
# دوال تشغيل البوت
# ============================================================

def run_freefire_bot():
    global BOT_PROCESS, BOT_RUNNING
    
    if BOT_RUNNING:
        log_message("⚠️ البوت يعمل بالفعل")
        return
    
    log_message("🚀 بدء تشغيل بوت Free Fire...")
    
    # تمرير الإعدادات للبوت عبر متغيرات بيئية مؤقتة
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
    
    # ===== تشغيل =====
    if action == "run":
        if BOT_RUNNING:
            await query.edit_message_text("⚠️ البوت يعمل بالفعل.")
            return
        run_freefire_bot()
        await query.edit_message_text(
            f"✅ تم تشغيل البوت.\n\n{get_status_text()}",
            parse_mode="Markdown"
        )
    
    # ===== إيقاف =====
    elif action == "stop":
        if not BOT_RUNNING:
            await query.edit_message_text("⚠️ البوت متوقف بالفعل.")
            return
        stop_freefire_bot()
        await query.edit_message_text(
            f"⏹ تم إيقاف البوت.\n\n{get_status_text()}",
            parse_mode="Markdown"
        )
    
    # ===== إعادة تشغيل =====
    elif action == "restart":
        await query.edit_message_text("🔄 جاري إعادة التشغيل...")
        restart_freefire_bot()
        await query.edit_message_text(
            f"✅ تم إعادة التشغيل.\n\n{get_status_text()}",
            parse_mode="Markdown"
        )
    
    # ===== الحالة =====
    elif action == "status":
        await query.edit_message_text(
            get_status_text(),
            parse_mode="Markdown"
        )
    
    # ===== السجلات =====
    elif action == "logs":
        if not BOT_LOGS:
            await query.edit_message_text("📜 لا توجد سجلات.")
            return
        logs_text = "\n".join(BOT_LOGS[-30:])
        if len(logs_text) > 4000:
            logs_text = logs_text[-4000:]
        await query.edit_message_text(
            f"📜 *آخر السجلات:*\n```\n{logs_text}\n```",
            parse_mode="Markdown"
        )
    
    # ===== مسح السجلات =====
    elif action == "clear_logs":
        BOT_LOGS.clear()
        log_message("🗑 تم مسح السجلات بواسطة المستخدم")
        await query.edit_message_text("✅ تم مسح جميع السجلات.")
    
    # ===== الإعدادات =====
    elif action == "settings":
        keyboard = [
            [InlineKeyboardButton(f"🎯 المباريات: {CONFIG['matches_per_session']}", callback_data="edit_matches")],
            [InlineKeyboardButton(f"🤖 الوضع التلقائي: {'ON' if CONFIG['auto_mode'] else 'OFF'}", callback_data="toggle_auto")],
            [InlineKeyboardButton(f"⏱️ التأخير: {CONFIG['delay_min']}-{CONFIG['delay_max']}", callback_data="edit_delay")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚙️ *الإعدادات*\n\nاختر إعداداً لتغييره:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # ===== تعديل المباريات =====
    elif action == "edit_matches":
        keyboard = [
            [InlineKeyboardButton("3 مباريات", callback_data="set_matches_3")],
            [InlineKeyboardButton("5 مباريات", callback_data="set_matches_5")],
            [InlineKeyboardButton("10 مباريات", callback_data="set_matches_10")],
            [InlineKeyboardButton("20 مباراة", callback_data="set_matches_20")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="settings")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🎯 *عدد المباريات لكل جلسة*\n\nالحالي: {CONFIG['matches_per_session']}\n\nاختر قيمة جديدة:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # ===== ضبط عدد المباريات =====
    elif action.startswith("set_matches_"):
        value = int(action.split("_")[2])
        CONFIG['matches_per_session'] = value
        log_message(f"✅ تم ضبط المباريات إلى {value}")
        await query.edit_message_text(
            f"✅ تم ضبط عدد المباريات إلى {value}.",
            parse_mode="Markdown"
        )
        await show_settings(query)
    
    # ===== تبديل الوضع التلقائي =====
    elif action == "toggle_auto":
        CONFIG['auto_mode'] = not CONFIG['auto_mode']
        log_message(f"✅ الوضع التلقائي: {'ON' if CONFIG['auto_mode'] else 'OFF'}")
        await query.edit_message_text(
            f"✅ تم {'تفعيل' if CONFIG['auto_mode'] else 'إيقاف'} الوضع التلقائي.",
            parse_mode="Markdown"
        )
        await show_settings(query)
    
    # ===== تعديل التأخير =====
    elif action == "edit_delay":
        keyboard = [
            [InlineKeyboardButton("0.3 - 1.5 ثانية", callback_data="set_delay_0.3_1.5")],
            [InlineKeyboardButton("1 - 3 ثواني", callback_data="set_delay_1_3")],
            [InlineKeyboardButton("3 - 5 ثواني", callback_data="set_delay_3_5")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="settings")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"⏱️ *التأخير بين الإجراءات*\n\nالحالي: {CONFIG['delay_min']}-{CONFIG['delay_max']} ثانية\n\nاختر نطاقاً جديداً:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # ===== ضبط التأخير =====
    elif action.startswith("set_delay_"):
        parts = action.split("_")
        min_delay = float(parts[2])
        max_delay = float(parts[3])
        CONFIG['delay_min'] = min_delay
        CONFIG['delay_max'] = max_delay
        log_message(f"✅ تم ضبط التأخير إلى {min_delay}-{max_delay}")
        await query.edit_message_text(
            f"✅ تم ضبط التأخير إلى {min_delay}-{max_delay} ثانية.",
            parse_mode="Markdown"
        )
        await show_settings(query)
    
    # ===== رجوع =====
    elif action == "back":
        await show_main_menu(query)

async def show_settings(query):
    keyboard = [
        [InlineKeyboardButton(f"🎯 المباريات: {CONFIG['matches_per_session']}", callback_data="edit_matches")],
        [InlineKeyboardButton(f"🤖 الوضع التلقائي: {'ON' if CONFIG['auto_mode'] else 'OFF'}", callback_data="toggle_auto")],
        [InlineKeyboardButton(f"⏱️ التأخير: {CONFIG['delay_min']}-{CONFIG['delay_max']}", callback_data="edit_delay")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "⚙️ *الإعدادات*\n\nاختر إعداداً لتغييره:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_main_menu(query):
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
    await query.edit_message_text(
        "🤖 *مركز التحكم - بوت Free Fire*\n\nاختر أمراً:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ============================================================
# التشغيل الرئيسي
# ============================================================

def main():
    if not TOKEN or TOKEN == "ضع_التوكن_هنا":
        print("❌ خطأ: لم يتم تعيين توكن بوت تيليجرام.")
        print("💡 ضع التوكن في المتغير البيئي TOKEN أو في السطر المناسب.")
        sys.exit(1)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    log_message("🚀 بدء تشغيل بوت التحكم عبر تيليجرام...")
    app.run_polling()

if __name__ == "__main__":
    main()
