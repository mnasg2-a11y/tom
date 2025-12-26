# plugins/update.py
import os, sys, subprocess, asyncio, time, shutil
from telethon import events
from __main__ import client

SECTION_NAME = "🔄 قـسـم الـتـحـديـث"
COMMANDS = """• `.تحديث` : لـتـحـديـث الـسـورس مـن الـمـسـتـودع
• `.اعادة تشغيل` : إعـادة تـشـغـيـل الـبـوت
• `.اصلاح جيت` : إصـلاح مـشـاكـل Git
• `.فحص تحديث` : فـحـص الـتـحـديـثـات"""

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث$'))
async def update_bot(event):
    """تحديث السورس من جيت هاب"""
    msg = await event.edit("🔄 **جـارِ الـتـحـديـث...**\n"
                          "⏳ **سـيـسـتـغـرق ذلـك بـضـعـة ثـوانـي**")
    
    try:
        # التحقق من وجود Git
        if not shutil.which("git"):
            await msg.edit("❌ **Git غـيـر مـثـبـت!**\n"
                          "📥 يـرجـى تـثـبـيـت Git أولاً:\n"
                          "`apt install git` أو `pkg install git`")
            return
        
        # التحقق من أننا في مستودع Git
        if not os.path.exists(".git"):
            await msg.edit("❌ **لـيـس مـسـتـودع Git!**\n"
                          "📁 إسـتـخـدم `.اصلاح جيت` لـحـل الـمـشـكـلـة")
            return
        
        # 1. حفظ التغييرات المحلية
        await msg.edit("🔄 **جـارِ الـتـحـديـث...**\n"
                      "💾 **حـفـظ الـتـغـيـيـرات الـمـحـلـيـة...**")
        
        try:
            subprocess.run(["git", "stash"], 
                          capture_output=True, 
                          text=True, 
                          check=True)
        except:
            pass  # تجاهل إذا لا توجد تغييرات
        
        # 2. جلب التحديثات
        await msg.edit("🔄 **جـارِ الـتـحـديـث...**\n"
                      "📥 **جـلـب الـتـحـديـثـات الـجـديـدة...**")
        
        start_time = time.time()
        
        # جلب آخر التحديثات
        fetch_result = subprocess.run(["git", "fetch", "origin"],
                                     capture_output=True,
                                     text=True,
                                     encoding='utf-8')
        
        if fetch_result.returncode != 0:
            await msg.edit(f"❌ **فـشـل فـي جـلـب الـتـحـديـثـات:**\n"
                          f"```\n{fetch_result.stderr[:300]}\n```")
            return
        
        # 3. دمج التحديثات (بدون تعارضات)
        await msg.edit("🔄 **جـارِ الـتـحـديـث...**\n"
                      "🔀 **دمـج الـتـحـديـثـات...**")
        
        # استخدام reset --hard للتأكد من المزامنة
        reset_result = subprocess.run(["git", "reset", "--hard", "origin/main"],
                                     capture_output=True,
                                     text=True,
                                     encoding='utf-8')
        
        if reset_result.returncode != 0:
            # محاولة pull عادي
            pull_result = subprocess.run(["git", "pull", "--no-rebase"],
                                        capture_output=True,
                                        text=True,
                                        encoding='utf-8')
            
            if pull_result.returncode != 0:
                error_msg = pull_result.stderr or pull_result.stdout
                await msg.edit(f"❌ **فـشـل فـي تـحـديـث الـسـورس:**\n"
                              f"```\n{error_msg[:400]}\n```"
                              f"\n🛠 **حـاول إسـتـخـدام:** `.اصلاح جيت`")
                return
            else:
                output = pull_result.stdout
        else:
            output = reset_result.stdout
        
        end_time = time.time()
        elapsed = round(end_time - start_time, 2)
        
        # 4. تحديث الإضافات
        await msg.edit("✅ **تـم تـحـديـث الـكـود!**\n"
                      "🔄 **جـارِ تـحـديـث الإضـافـات...**")
        
        # إعادة تحميل الإضافات
        from __main__ import load_plugins
        try:
            load_plugins()
            plugins_count = len([f for f in os.listdir("plugins") if f.endswith(".py")])
        except:
            plugins_count = 0
        
        # عرض النتيجة
        if "Already up to date" in output or "Already up-to-date" in output:
            await msg.edit(f"✅ **الـسـورس مـتـاحـث إلـى أحـدث إصـدار!**\n"
                          f"⏱ **الـوقـت:** `{elapsed} ثـانـيـة`\n"
                          f"📁 **الإضـافـات:** {plugins_count}")
        else:
            await msg.edit(f"✅ **تـم الـتـحـديـث بـنـجـاح!**\n"
                          f"📊 **الـمـخـرج:** `{output[:150]}...`\n"
                          f"⏱ **الـوقـت:** `{elapsed} ثـانـيـة`\n"
                          f"📁 **الإضـافـات:** {plugins_count}")
        
        # استعادة التغييرات المحلية
        try:
            subprocess.run(["git", "stash", "pop"], 
                          capture_output=True, 
                          text=True)
        except:
            pass
        
    except FileNotFoundError:
        await msg.edit("❌ **Git غـيـر مـثـبـت!**\n"
                      "📥 يـرجـى تـثـبـيـت Git أولاً")
    except Exception as e:
        await msg.edit(f"❌ **خـطـأ غـيـر مـتـوقـع:**\n"
                      f"```\n{str(e)[:400]}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.اصلاح جيت$'))
async def fix_git(event):
    """إصلاح مشاكل Git"""
    msg = await event.edit("🔧 **جـارِ إصـلاح مـشـاكـل Git...**")
    
    steps = []
    
    try:
        # 1. تهيئة Git إذا لم تكن موجودة
        if not os.path.exists(".git"):
            steps.append("📁 **إنـشـاء مـسـتـودع جـديـد...**")
            result = subprocess.run(["git", "init"],
                                  capture_output=True,
                                  text=True,
                                  encoding='utf-8')
            if result.returncode == 0:
                steps.append("✅ تـم إنـشـاء الـمـسـتـودع")
        
        # 2. إضافة remote إذا لم يكن موجوداً
        remote_result = subprocess.run(["git", "remote", "-v"],
                                     capture_output=True,
                                     text=True,
                                     encoding='utf-8')
        
        if "origin" not in remote_result.stdout:
            steps.append("🔗 **إضـافـة الـمـسـتـودع الأصـلـي...**")
            # سيحتاج المستخدم لتعيين رابط المستودع
            await msg.edit("🔧 **يـجـب عـيـيـن رابـط الـمـسـتـودع:**\n"
                          "استخدم:\n"
                          "`git remote add origin <رابط_المستودع>`\n\n"
                          "ثم حاول `.تحديث` مرة أخرى")
            return
        
        # 3. إصلاح أذونات الملفات
        steps.append("🔒 **تـصـحـيـح أخـلاصـيـة الـمـلـفـات...**")
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".sh") or file == "config.py":
                    try:
                        os.chmod(os.path.join(root, file), 0o755)
                    except:
                        pass
        
        steps.append("✅ **تـم الإصـلاح بـنـجـاح!**")
        
        await msg.edit(f"🔧 **تـقـريـر الإصـلاح:**\n\n" + "\n".join(steps))
        
    except Exception as e:
        await msg.edit(f"❌ **فـشـل فـي الإصـلاح:**\n"
                      f"```\n{str(e)[:300]}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فحص تحديث$'))
async def check_update(event):
    """فحص التحديثات المتوفرة"""
    msg = await event.edit("🔍 **جـارِ فـحـص الـتـحـديـثـات...**")
    
    try:
        if not os.path.exists(".git"):
            await msg.edit("❌ **لـيـس مـسـتـودع Git!**\n"
                          "إسـتـخـدم `.اصلاح جيت` أولاً")
            return
        
        # جلب آخر التحديثات
        subprocess.run(["git", "fetch"], 
                      capture_output=True, 
                      text=True)
        
        # مقارنة الفروع
        result = subprocess.run(["git", "log", "HEAD..origin/main", "--oneline"],
                              capture_output=True,
                              text=True,
                              encoding='utf-8')
        
        commits = [c for c in result.stdout.strip().split('\n') if c]
        
        if not commits:
            await msg.edit("✅ **أنـت عـلـى آخـر إصـدار!**\n"
                          "🎯 **لا تـوجـد تـحـديـثـات جـديـدة**")
        else:
            updates_count = len(commits)
            last_updates = "\n".join(commits[:5])
            
            await msg.edit(f"📥 **يـوجـد {updates_count} تـحـديـث جـديـد!**\n\n"
                          f"**آخـر {min(5, updates_count)} تـحـديـث:**\n"
                          f"```\n{last_updates}\n```\n\n"
                          f"🎯 اسـتـخـدم `.تحديث` لـتـنـزيـل الـتـحـديـثـات")
        
    except Exception as e:
        await msg.edit(f"❌ **خـطـأ فـي فـحـص الـتـحـديـثـات:**\n"
                      f"```\n{str(e)[:300]}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.اعادة تشغيل$'))
async def restart_bot(event):
    """إعادة تشغيل البوت"""
    msg = await event.edit("🔄 **جـارِ إعـادة الـتـشـغـيـل...**")
    
    try:
        # حفظ الجلسة
        from __main__ import save_session, SESSION_STR
        if SESSION_STR:
            save_session(SESSION_STR)
        
        await asyncio.sleep(2)
        await msg.edit("✅ **تـم إعـادة الـتـشـغـيـل!**")
        
        # إعادة التشغيل
        python = sys.executable
        os.execl(python, python, *sys.argv)
        
    except Exception as e:
        await msg.edit(f"❌ **فـشـل إعـادة الـتـشـغـيـل:**\n`{str(e)[:200]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.حالة النظام$'))
async def system_status(event):
    """عرض حالة النظام"""
    import psutil
    
    msg = await event.edit("📊 **جـارِ جـمـع مـعـلـومـات الـنـظـام...**")
    
    try:
        # معلومات النظام
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # معلومات Git
        git_status = "❌ غير مثبت"
        git_version = ""
        
        if shutil.which("git"):
            git_status = "✅ مثبت"
            result = subprocess.run(["git", "--version"],
                                  capture_output=True,
                                  text=True)
            git_version = result.stdout.strip()
        
        # معلومات Python
        python_version = sys.version.split()[0]
        
        status_text = (
            f"📊 **حـالـة الـنـظـام:**\n"
            f"═══════════════════\n"
            f"**💻 الـمـعـالـج:** {cpu_percent}%\n"
            f"**🧠 الـذاكـرة:** {memory.percent}%\n"
            f"**💾 الـتـخـزيـن:** {disk.percent}%\n"
            f"═══════════════════\n"
            f"**🐍 Python:** {python_version}\n"
            f"**🔄 Git:** {git_status}\n"
            f"{git_version}\n"
            f"═══════════════════\n"
            f"**📁 الـمـلـفـات:** {len(os.listdir('.'))}\n"
            f"**🔌 الإضـافـات:** {len([f for f in os.listdir('plugins') if f.endswith('.py')]) if os.path.exists('plugins') else 0}"
        )
        
        await msg.edit(status_text)
        
    except ImportError:
        await msg.edit("❌ **يـجـب تـثـبـيـت psutil:**\n`pip install psutil`")
    except Exception as e:
        await msg.edit(f"❌ **خـطـأ:**\n`{str(e)[:300]}`")
