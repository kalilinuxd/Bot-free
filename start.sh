#!/bin/bash
echo "🚀 بدء تشغيل بوت Free Fire..."
pip install -r requirements.txt
while true; do
    echo "🔄 تشغيل البوت..."
    python bot.py
    echo "⚠️ البوت توقف. إعادة التشغيل خلال 5 ثوان..."
    sleep 5
done
