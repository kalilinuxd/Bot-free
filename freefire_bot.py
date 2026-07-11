# هذا هو بوت Free Fire التعليمي
# يمكنك استخدام الكود من الردود السابقة
# أو أي كود بوت تريد التحكم به

import time
import random
import os

def main():
    print("🚀 بدء تشغيل بوت Free Fire (تعليمي)")
    
    # قراءة الإعدادات من ملف config.json إن وجد
    try:
        import json
        with open("bot_config.json", "r") as f:
            config = json.load(f)
            matches = config.get("matches_per_session", 5)
    except:
        matches = 5
    
    print(f"🎯 عدد المباريات: {matches}")
    print("🤖 البوت يعمل... (للتعليم فقط)")
    
    # محاكاة عمل البوت
    for i in range(matches):
        print(f"🏃 المباراة {i+1}/{matches} جارية...")
        time.sleep(random.randint(2, 5))
        print(f"✅ انتهت المباراة {i+1}")
    
    print("✅ انتهى عمل البوت")

if __name__ == "__main__":
    main()
