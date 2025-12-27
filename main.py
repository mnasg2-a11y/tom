#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 سورس كومن Pro - النسخة الأساسية
✅ جلسة دائمة - بدون أوامر - استمرارية كاملة
"""

import os
import sys
import asyncio
import time
import signal
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# ==================== الإعدادات الأساسية ====================
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION_FILE = "comun_session.txt"

# ==================== إدارة الجلسة ====================
def load_session():
    """تحميل الجلسة من الملف"""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                session_str = f.read().strip()
                if session_str and len(session_str) > 50:
                    print(f"✅ تم تحميل الجلسة من {SESSION_FILE}")
                    return session_str
    except Exception as e:
        print(f"❌ خطأ في تحميل الجلسة: {e}")
    return None

def save_session(session_str: str):
    """حفظ الجلسة في الملف"""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            f.write(session_str)
        print("✅ تم حفظ الجلسة")
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الجلسة: {e}")
        return False

async def create_new_session():
    """إنشاء جلسة جديدة مرة واحدة فقط"""
    print("\n" + "="*50)
    print("🔐 **المرة الأولى - تسجيل الدخول**")
    print("="*50)
    print("⚠️ هذه العملية مرة واحدة فقط")
    print("📱 ستحتاج إلى إدخال رقم الهاتف والكود")
    print("="*50)
    
    try:
        client_temp = TelegramClient(StringSession(), API_ID, API_HASH)
        await client_temp.start()
        
        # التحقق إذا كان الحساب محمي بكلمة سر
        try:
            me = await client_temp.get_me()
        except SessionPasswordNeededError:
            print("🔒 الحساب محمي بكلمة سر")
            password = input("🔑 أدخل كلمة السر: ")
            await client_temp.start(password=password)
            me = await client_temp.get_me()
        
        session_str = client_temp.session.save()
        
        if save_session(session_str):
            print(f"\n✅ **تم التسجيل بنجاح!**")
            print(f"👤 **الاسم:** {me.first_name}")
            print(f"🆔 **الايدي:** {me.id}")
            print(f"📞 **المستخدم:** @{me.username if me.username else 'لا يوجد'}")
            print("💾 **تم حفظ الجلسة للأبد**")
            print("="*50)
            print("🚀 **لن تحتاج لإدخال الرقم مرة أخرى**")
            print("="*50)
            
            # إرسال رسالة تأكيد
            await client_temp.send_message(
                "me",
                f"✅ **تم حفظ الجلسة بنجاح!**\n"
                f"👤 **الحساب:** {me.first_name}\n"
                f"📅 **التاريخ:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"🔐 **لن تحتاج لإدخال الرقم مرة أخرى**"
            )
            
            await client_temp.disconnect()
            return session_str
        
        await client_temp.disconnect()
        return None
        
    except KeyboardInterrupt:
        print("\n❌ تم إلغاء العملية")
        return None
    except Exception as e:
        print(f"❌ خطأ في إنشاء الجلسة: {e}")
        return None

# ==================== العميل الرئيسي ====================
SESSION_STR = load_session()

if not SESSION_STR:
    SESSION_STR = asyncio.run(create_new_session())
    if not SESSION_STR:
        print("❌ فشل في إنشاء الجلسة!")
        sys.exit(1)

# إنشاء العميل
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

# ==================== وظائف البوت ====================
async def check_connection():
    """التحقق من الاتصال"""
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ الجلسة منتهية الصلاحية!")
            return False
        
        me = await client.get_me()
        return me
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

async def send_startup_message():
    """إرسال رسالة بدء التشغيل"""
    try:
        me = await client.get_me()
        message = f"""
✅ **البوت يعمل الآن!**
👤 **الحساب:** {me.first_name}
🆔 **الايدي:** {me.id}
⏰ **الوقت:** {time.strftime('%Y-%m-%d %H:%M:%S')}
🔥 **الجلسة دائمة ولا تحتاج لتسجيل**
"""
        await client.send_message("me", message)
        return True
    except:
        return False

async def keep_alive():
    """الحفاظ على اتصال البوت نشطاً"""
    print("🔄 جاري تشغيل البوت...")
    
    # التحقق من الاتصال
    me = await check_connection()
    if not me:
        print("❌ فشل في الاتصال!")
        return False
    
    print(f"✅ **اتصال ناجح:** {me.first_name}")
    
    # إرسال رسالة البدء
    await send_startup_message()
    
    # حفظ الجلسة الحالية
    save_session(SESSION_STR)
    
    print("\n" + "="*50)
    print("🎯 **البوت يعمل بنجاح!**")
    print("🔐 **الجلسة محفوظة ومستمرة**")
    print("⚡ **لن ينقطع الاتصال أبداً**")
    print("="*50)
    print("\n📌 **المميزات:**")
    print("• ✅ جلسة دائمة لا تنتهي")
    print("• ✅ اتصال مستمر 24/7")
    print("• ✅ لا حاجة لإعادة التسجيل")
    print("• ✅ يعمل في الخلفية")
    print("="*50)
    
    return True

async def run_bot():
    """تشغيل البوت الرئيسي"""
    try:
        # تشغيل البوت
        success = await keep_alive()
        if not success:
            return False
        
        # تشغيل العميل بشكل دائم
        await client.run_until_disconnected()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹ تم إيقاف البوت بواسطة المستخدم")
        return True
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        return False
    finally:
        # حفظ الجلسة قبل الخروج
        save_session(SESSION_STR)
        print("💾 تم حفظ الجلسة")

# ==================== تشغيل البوت ====================
async def main():
    """الدالة الرئيسية"""
    while True:
        try:
            print("\n" + "="*50)
            print("🚀 بدء تشغيل سورس كومن Pro")
            print("="*50)
            
            # تشغيل البوت
            success = await run_bot()
            
            if success:
                print("\n🔄 جاري إعادة التشغيل...")
                await asyncio.sleep(5)  # انتظار 5 ثواني
            else:
                print("\n❌ فشل في التشغيل، إعادة المحاولة...")
                await asyncio.sleep(10)  # انتظار 10 ثواني
                
        except KeyboardInterrupt:
            print("\n\n⏹ إيقاف نهائي للبوت")
            break
        except Exception as e:
            print(f"\n⚠️ خطأ غير متوقع: {e}")
            await asyncio.sleep(10)

# ==================== نقطة الدخول ====================
if __name__ == "__main__":
    # معالجة إشارات الإيقاف
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    
    # تشغيل البوت
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ نهائي: {e}")
    finally:
        # التأكد من حفظ الجلسة
        if 'SESSION_STR' in globals() and SESSION_STR:
            save_session(SESSION_STR)
        print("\n🔥 جلسة كومن Pro محفوظة للأبد!")
