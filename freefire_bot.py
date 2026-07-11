#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import random

def main():
    # قراءة الإعدادات من المتغيرات البيئية
    matches = int(os.getenv("MATCHES", "5"))
    auto_mode = os.getenv("AUTO_MODE", "true").lower() == "true"
    delay_min = float(os.getenv("DELAY_MIN", "0.3"))
    delay_max = float(os.getenv("DELAY_MAX", "1.5"))
    
    print("🚀 بدء تشغيل بوت Free Fire (تعليمي)")
    print(f"🎯 عدد المباريات: {matches}")
    print(f"🤖 الوضع التلقائي: {auto_mode}")
    print(f"⏱️ التأخير: {delay_min}-{delay_max} ثانية")
    
    for i in range(matches):
        print(f"🏃 المباراة {i+1}/{matches} جارية...")
        time.sleep(random.uniform(delay_min, delay_max))
        print(f"✅ انتهت المباراة {i+1}")
    
    print("✅ انتهى عمل البوت")

if __name__ == "__main__":
    main()
