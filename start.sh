#!/bin/bash
echo "🚀 بدء تشغيل بوت Free Fire..."
pip install -r requirements.txt
while true; do
    echo "🔄 تشغيل البوت..."
    # 1. ضع التوكن في السطر TOKEN داخل telegram_controller.py

# 2. تأكد من وجود freefire_bot.py في نفس المجلد

# 3. شغل بوت التحكم
python telegram_controller.py
    echo "⚠️ البوت توقف. إعادة التشغيل خلال 5 ثوان..."
    sleep 5
done
