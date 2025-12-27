#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 سورس كومن Pro - مع محرك التحديثات الذكي
✅ اكتشاف تلقائي - تثبيت تلقائي - تنظيم تلقائي
"""

import os
import sys
import asyncio
import time
import signal
import importlib
from pathlib import Path

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==================== الإعدادات الأساسية ====================
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION_FILE = "comun_session.txt"
PLUGINS_DIR = Path("plugins")

# ==================== إدارة الجلسة ====================
def load_session():
    """تحميل الجلسة"""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
    except:
        pass
    return None

def save_session(session_str: str):
    """حفظ الجلسة"""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            f.write(session_str)
        return True
    except:
        return False

async def create_new_session():
    """إنشاء جلسة جديدة"""
    print("\n" + "="*50)
    print("🔐 **تسجيل الدخول الأول**")
    print("="*50)
    
    try:
        client_temp = TelegramClient(StringSession(), API_ID, API_HASH)
        await client_temp.start()
        session_str = client_temp.session.save()
        
        me = await client_temp.get_me()
        print(f"✅ **تم التسجيل كـ:** {me.first_name}")
        
        save_session(session_str)
        await client_temp.disconnect()
        
        print("💾 **تم حفظ الجلسة للأبد!**")
        print("="*50)
        
        return session_str
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None

# ==================== نظام الإضافات ====================
PLUGINS_HELP = {}

def load_plugins():
    """تحميل جميع الإضافات"""
    global PLUGINS_HELP
    PLUGINS_HELP.clear()
    
    # إنشاء مجلد الإضافات
    PLUGINS_DIR.mkdir(exist_ok=True)
    
    # تحميل الإضافات
    sys.path.insert(0, str(PLUGINS_DIR))
    
    for plugin_file in PLUGINS_DIR.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue
            
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem,
                str(plugin_file)
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_file.stem] = module
            spec.loader.exec_module(module)
            
            if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
                PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
                
            print(f"✅ تم تحميل: {plugin_file.stem}")
            
        except Exception as e:
            print(f"❌ خطأ في {plugin_file.name}: {e}")

# ==================== العميل الرئيسي ====================
SESSION_STR = load_session()

if not SESSION_STR:
    SESSION_STR = asyncio.run(create_new_session())
    if not SESSION_STR:
        print("❌ فشل في إنشاء الجلسة!")
        sys.exit(1)

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

# ==================== الأوامر الأساسية ====================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.الاوامر$'))
async def help_command(event):
    """عرض الأوامر"""
    if not PLUGINS_HELP:
        await event.edit("📭 **لا توجد أوامر مثبتة!**")
        return
    
    help_text = "🚀 **سورس كومن Pro - الأوامر**\n" + "═"*30 + "\n"
    
    for section, commands in PLUGINS_HELP.items():
        help_text += f"\n**{section}:**\n{commands}\n"
    
    help_text += f"\n📊 **عدد الإضافات:** {len(PLUGINS_HELP)}"
    help_text += f"\n⏰ **الوقت:** {time.strftime('%H:%M:%S')}"
    
    await event.edit(help_text)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.الحالة$'))
async def status_command(event):
    """حالة البوت"""
    try:
        me = await client.get_me()
        plugins_count = len(list(PLUGINS_DIR.glob("*.py")))
        
        status = f"""
🤖 **حالة سورس كومن Pro**

👤 **الحساب:** {me.first_name}
🆔 **الايدي:** {me.id}
📁 **الإضافات:** {plugins_count}
⏰ **الوقت:** {time.strftime('%Y-%m-%d %H:%M:%S')}
🔥 **الجلسة:** ✅ دائمة

💡 **النظام جاهز لاكتشاف التحديثات تلقائياً**
"""
        await event.edit(status)
    except:
        await event.edit("✅ **البوت يعمل بنجاح!**")

# ==================== بدء التشغيل ====================
async def startup():
    """بدء تشغيل البوت"""
    print("\n" + "="*50)
    print("🚀 بدء تشغيل سورس كومن Pro")
    print("="*50)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ الجلسة غير صالحة!")
        return False
    
    # تحميل الإضافات
    print("📁 جاري تحميل الإضافات...")
    load_plugins()
    print(f"✅ تم تحميل {len(PLUGINS_HELP)} إضافة")
    
    # معلومات الحساب
    me = await client.get_me()
    print(f"👤 **الحساب:** {me.first_name}")
    print(f"🔥 **الجلسة دائمة ومستمرة**")
    print("="*50)
    print("🎯 النظام جاهز لاكتشاف التحديثات تلقائياً!")
    print("="*50)
    
    return True

async def main():
    """الدالة الرئيسية"""
    while True:
        try:
            success = await startup()
            if success:
                await client.run_until_disconnected()
            else:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n⏹ تم إيقاف البوت")
            break
        except Exception as e:
            print(f"\n⚠️ خطأ: {e}")
            await asyncio.sleep(5)

# ==================== التشغيل ====================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔥 تم حفظ الجلسة!")
    finally:
        if 'SESSION_STR' in globals():
            save_session(SESSION_STR)
