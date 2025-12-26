# plugins/update.py
"""
🔄 نظام التحديث المتكامل
✅ يدعم جميع المحركات - بدون مشاكل - استمرارية كاملة
"""

import os
import sys
import asyncio
import subprocess
import time
import importlib
import shutil
import json
from datetime import datetime
from pathlib import Path

from telethon import events, Button
from __main__ import client, bot_info, load_plugins

# ==================== الإعدادات ====================
SECTION_NAME = "🔄 نظام التحديث"
COMMANDS = """• `.تحديث` - تحديث السورس من GitHub
• `.فحص تحديث` - فحص التحديثات المتاحة
• `.اعادة تشغيل` - إعادة تشغيل البوت
• `.تحديث الاضافات` - تحديث الإضافات فقط
• `.نسخ احتياطي` - نسخ احتياطي للجلسة
• `.حالة النظام` - معلومات النظام"""

# ==================== المتغيرات العالمية ====================
UPDATE_LOG_FILE = "update_log.json"
BACKUP_DIR = "backups"
REPO_URL = "https://github.com/your-username/comun-pro.git"

# ==================== دوال المساعدة ====================
def log_update(action: str, status: str, details: str = ""):
    """تسجيل عمليات التحديث"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "details": details[:500]
    }
    
    try:
        if os.path.exists(UPDATE_LOG_FILE):
            with open(UPDATE_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_data)
        if len(logs) > 50:  # حفظ آخر 50 عملية فقط
            logs = logs[-50:]
        
        with open(UPDATE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except:
        pass

def create_backup():
    """إنشاء نسخة احتياطية"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        backup_name = f"backup_{int(time.time())}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # نسخ الملفات المهمة
        important_files = [
            "main.py",
            "plugins/",
            "requirements.txt",
            "session.txt" if os.path.exists("session.txt") else None,
            "comun_session.txt" if os.path.exists("comun_session.txt") else None
        ]
        
        os.makedirs(backup_path, exist_ok=True)
        
        for item in important_files:
            if item and os.path.exists(item):
                if item.endswith('/'):
                    shutil.copytree(item, os.path.join(backup_path, item), 
                                  dirs_exist_ok=True)
                else:
                    shutil.copy2(item, backup_path)
        
        return backup_path, backup_name
    except Exception as e:
        return None, str(e)

def run_git_command(cmd):
    """تنفيذ أمر git بأمان"""
    try:
        result = subprocess.run(
            cmd,
            shell=True if isinstance(cmd, str) else False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "المهلة انتهت"
    except Exception as e:
        return -1, "", str(e)

def check_git_status():
    """فحص حالة Git"""
    try:
        # التحقق من وجود Git
        returncode, stdout, stderr = run_git_command(["git", "--version"])
        if returncode != 0:
            return False, "Git غير مثبت"
        
        # التحقق من كون المجلد مخزن Git
        returncode, stdout, stderr = run_git_command(["git", "status"])
        if returncode != 0:
            return False, "المجلد ليس مخزن Git"
        
        return True, "Git جاهز"
    except Exception as e:
        return False, str(e)

# ==================== الأحداث الرئيسية ====================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تحديث$'))
async def update_command(event):
    """تحديث كامل للسورس"""
    msg = await event.edit("🔄 **جاري التحضير للتحديث...**")
    
    # التحقق من Git
    git_ready, git_msg = check_git_status()
    if not git_ready:
        await msg.edit(f"❌ **خطأ في Git:**\n`{git_msg}`")
        return
    
    # المرحلة 1: إنشاء نسخة احتياطية
    await msg.edit("🔄 **جاري التحضير للتحديث...**\n"
                   "📦 **المرحلة 1:** إنشاء نسخة احتياطية")
    
    backup_path, backup_result = create_backup()
    if backup_path:
        log_update("backup", "success", f"Backup created: {backup_result}")
    else:
        log_update("backup", "failed", backup_result)
    
    # المرحلة 2: جلب التحديثات
    await msg.edit("🔄 **جاري التحضير للتحديث...**\n"
                   "📥 **المرحلة 2:** جلب التحديثات من GitHub")
    
    returncode, stdout, stderr = run_git_command(["git", "fetch", "--all"])
    if returncode != 0:
        await msg.edit(f"❌ **فشل في جلب التحديثات:**\n```\n{stderr[:300]}\n```")
        log_update("fetch", "failed", stderr[:200])
        return
    
    # المرحلة 3: تطبيق التحديثات
    await msg.edit("🔄 **جاري التحضير للتحديث...**\n"
                   "⚡ **المرحلة 3:** تطبيق التحديثات")
    
    returncode, stdout, stderr = run_git_command(["git", "pull", "--rebase"])
    if returncode != 0:
        await msg.edit(f"❌ **فشل في تطبيق التحديثات:**\n```\n{stderr[:300]}\n```")
        log_update("pull", "failed", stderr[:200])
        return
    
    pull_output = stdout.strip()
    
    # التحقق إذا كان السورس محدث بالفعل
    if "Already up to date" in pull_output or "Already up-to-date" in pull_output:
        await msg.edit("✅ **السورس محدث بالفعل!**\n"
                       "🎯 **أنت على آخر إصدار**")
        log_update("update", "already_updated")
        return
    
    # المرحلة 4: تحديث الإضافات
    await msg.edit("🔄 **جاري التحضير للتحديث...**\n"
                   "🔌 **المرحلة 4:** تحديث الإضافات")
    
    try:
        old_plugins = len([f for f in os.listdir("plugins") if f.endswith('.py')])
        load_plugins()
        new_plugins = len([f for f in os.listdir("plugins") if f.endswith('.py')])
    except Exception as e:
        await msg.edit(f"⚠️ **تم التحديث ولكن حدث خطأ في الإضافات:**\n```\n{str(e)[:200]}\n```")
        log_update("plugins", "error", str(e)[:200])
        return
    
    # المرحلة 5: تثبيت المتطلبات
    await msg.edit("🔄 **جاري التحضير للتحديث...**\n"
                   "📦 **المرحلة 5:** تثبيت المتطلبات الجديدة")
    
    if os.path.exists("requirements.txt"):
        returncode, stdout, stderr = run_git_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"]
        )
        if returncode != 0:
            log_update("requirements", "warning", stderr[:200])
    
    # النتيجة النهائية
    update_summary = f"""
✅ **تم التحديث بنجاح!**

📊 **ملخص التحديث:**
📥 **السحب:** {pull_output[:100]}...
🔌 **الإضافات:** {old_plugins} → {new_plugins}
📦 **النسخة الاحتياطية:** {'✅' if backup_path else '⚠️'}

🔄 **جاري إعادة التشغيل خلال 3 ثواني...**
"""
    
    await msg.edit(update_summary)
    log_update("complete_update", "success", f"Plugins: {old_plugins}->{new_plugins}")
    
    # إعادة التشغيل بعد 3 ثواني
    await asyncio.sleep(3)
    await restart_bot(event, silent=True)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.فحص تحديث$'))
async def check_update_command(event):
    """فحص التحديثات المتاحة"""
    msg = await event.edit("🔍 **جاري فحص التحديثات...**")
    
    git_ready, git_msg = check_git_status()
    if not git_ready:
        await msg.edit(f"❌ **خطأ في Git:**\n`{git_msg}`")
        return
    
    # جلب أحدث التحديثات
    returncode, stdout, stderr = run_git_command(["git", "fetch"])
    if returncode != 0:
        await msg.edit(f"❌ **فشل في جلب المعلومات:**\n```\n{stderr[:200]}\n```")
        return
    
    # مقارنة مع الفرع الحالي
    returncode, stdout, stderr = run_git_command([
        "git", "log", "HEAD..origin/main", "--oneline", "--no-merges"
    ])
    
    if returncode != 0:
        await msg.edit("❌ **فشل في مقارنة الفروع**")
        return
    
    commits = [c for c in stdout.strip().split('\n') if c]
    
    if not commits:
        await msg.edit("✅ **أنت على آخر إصدار!**\n"
                       "🎯 **لا توجد تحديثات جديدة**")
    else:
        commits_count = len(commits)
        last_commits = "\n".join([f"• {c[:60]}..." for c in commits[:5]])
        
        response = f"""
📥 **يوجد {commits_count} تحديث جديد!**

📋 **آخر {min(5, commits_count)} تحديث:**
{last_commits}

💡 **استخدم `.تحديث` لتنزيل التحديثات**
        """
        
        if commits_count > 5:
            response += f"\n📌 **و {commits_count - 5} تحديثات أخرى...**"
        
        await msg.edit(response)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اعادة تشغيل$'))
async def restart_command(event, silent=False):
    """إعادة تشغيل البوت"""
    if not silent:
        msg = await event.edit("🔄 **جاري إعادة التشغيل...**")
    else:
        try:
            msg = await event.client.send_message(event.chat_id, "🔄 **إعادة تشغيل تلقائية...**")
        except:
            return
    
    try:
        # حفظ الجلسة إذا كانت موجودة
        session_files = ["session.txt", "comun_session.txt"]
        for session_file in session_files:
            if os.path.exists(session_file):
                backup_file = f"{session_file}.backup_{int(time.time())}"
                shutil.copy2(session_file, backup_file)
        
        # رسالة الانتظار
        if not silent:
            await msg.edit("✅ **تم حفظ الجلسة!\n🔄 جاري إعادة التشغيل...**")
        
        # إعادة التشغيل بعد تأخير قصير
        await asyncio.sleep(2)
        
        # إعادة التشغيل النظيفة
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    except Exception as e:
        if not silent:
            await msg.edit(f"❌ **خطأ في إعادة التشغيل:**\n`{str(e)[:200]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.تحديث الاضافات$'))
async def update_plugins_command(event):
    """تحديث الإضافات فقط"""
    msg = await event.edit("🔌 **جاري تحديث الإضافات...**")
    
    try:
        # تعداد الإضافات قبل التحديث
        plugins_before = []
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            plugins_before = [f.name for f in plugins_dir.iterdir() if f.suffix == '.py']
        
        # إعادة تحميل الإضافات
        from __main__ import load_plugins
        load_plugins()
        
        # تعداد الإضافات بعد التحديث
        plugins_after = []
        if plugins_dir.exists():
            plugins_after = [f.name for f in plugins_dir.iterdir() if f.suffix == '.py']
        
        # تحليل النتيجة
        updated = len(plugins_after) - len(plugins_before)
        
        if updated > 0:
            message = f"✅ **تم تحديث الإضافات!**\n📁 **إضافة {updated} إضافات جديدة**"
        elif updated < 0:
            message = f"⚠️ **تم تحديث الإضافات**\n📁 **تمت إزالة {abs(updated)} إضافات**"
        else:
            message = "✅ **تم تحديث الإضافات!**\n📁 **عدد الإضافات لم يتغير**"
        
        # عرض الإضافات الجديدة إن وجدت
        new_plugins = set(plugins_after) - set(plugins_before)
        if new_plugins:
            message += f"\n\n✨ **الإضافات الجديدة:**\n"
            for plugin in list(new_plugins)[:5]:
                message += f"• `{plugin}`\n"
            if len(new_plugins) > 5:
                message += f"• و {len(new_plugins) - 5} أكثر..."
        
        await msg.edit(message)
        log_update("plugins_update", "success", f"Plugins: {len(plugins_before)}->{len(plugins_after)}")
        
    except Exception as e:
        await msg.edit(f"❌ **خطأ في تحديث الإضافات:**\n`{str(e)[:200]}`")
        log_update("plugins_update", "failed", str(e)[:200])

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.نسخ احتياطي$'))
async def backup_command(event):
    """إنشاء نسخة احتياطية"""
    msg = await event.edit("💾 **جاري إنشاء نسخة احتياطية...**")
    
    backup_path, backup_result = create_backup()
    
    if backup_path:
        # حساب حجم النسخة الاحتياطية
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        
        size_mb = total_size / (1024 * 1024)
        
        await msg.edit(f"""
✅ **تم إنشاء النسخة الاحتياطية!**

📁 **المعلومات:**
• **الاسم:** `{backup_result}`
• **المسار:** `{backup_path}`
• **الحجم:** `{size_mb:.2f} MB`
• **الوقت:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

💡 **النسخة محفوظة في مجلد `backups/`**
""")
        log_update("manual_backup", "success", backup_result)
    else:
        await msg.edit(f"❌ **فشل في إنشاء النسخة الاحتياطية:**\n`{backup_result}`")
        log_update("manual_backup", "failed", backup_result)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.حالة النظام$'))
async def system_status_command(event):
    """عرض حالة النظام"""
    try:
        # جمع المعلومات
        import platform
        import psutil
        
        # معلومات النظام
        system_info = {
            "النظام": platform.system(),
            "الإصدار": platform.release(),
            "المعالج": platform.processor(),
            "بايثون": platform.python_version(),
        }
        
        # معلومات الذاكرة
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # معلومات البوت
        bot_dir = Path(".")
        plugins_count = len([f for f in bot_dir.glob("plugins/*.py") if f.is_file()])
        session_files = len([f for f in bot_dir.glob("*.txt") if "session" in f.name])
        
        # معلومات التحديث
        update_logs = []
        if os.path.exists(UPDATE_LOG_FILE):
            with open(UPDATE_LOG_FILE, "r", encoding="utf-8") as f:
                update_logs = json.load(f)
        
        last_update = update_logs[-1]["timestamp"] if update_logs else "لا يوجد"
        
        # بناء الرسالة
        status_msg = f"""
🖥 **حالة النظام - {BOT_NAME}**

📊 **معلومات النظام:**
"""
        for key, value in system_info.items():
            status_msg += f"• **{key}:** `{value}`\n"
        
        status_msg += f"""
💾 **الذاكرة والقرص:**
• **الذاكرة:** `{memory.percent}%` مستخدم
• **القرص:** `{disk.percent}%` مستخدم
• **المساحة الحرة:** `{disk.free / (1024**3):.1f} GB`

🤖 **معلومات البوت:**
• **الإصدار:** `{VERSION}`
• **عدد الإضافات:** `{plugins_count}`
• **ملفات الجلسة:** `{session_files}`
• **آخر تحديث:** `{last_update[:19]}`

🔄 **استخدم `.تحديث` للتحديث**
"""
        
        await event.edit(status_msg)
        
    except ImportError:
        # إذا لم يكن psutil مثبتاً
        await event.edit("""
📊 **حالة النظام الأساسية:**

⚠️ **لتثبيت المميزات الكاملة:**
```bash
pip install psutil
