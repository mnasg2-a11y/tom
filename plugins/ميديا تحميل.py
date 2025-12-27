import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events
from __main__ import client #

os.environ['SSL_CERT_FILE'] = certifi.where()

SECTION_NAME = "🚀 مـحـرك الـتـحـمـيـل الـعـالـمـي الصاروخي"
COMMANDS = "• `.ميديا` : لـوحـة الـتـحـمـيـل الـشـامـلـة"

def get_pro_opts(is_audio=False, hook=None):
    # إعدادات البحث الدقيق لكل شيء
    return {
        'format': 'bestaudio/best' if is_audio else 'best[height<=1080]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'source_address': '0.0.0.0',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'progress_hooks': [hook] if hook else [],
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash'],
            }
        },
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if not is_audio else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'concurrent_fragment_downloads': 10,  # زيادة السرعة
    }

def progress_bar(current, total, speed="", width=20):
    """شريط تحميل احترافي"""
    percentage = min(100, (current * 100) / total) if total > 0 else 0
    filled = int(width * percentage // 100)
    
    # ألوان وزخارف للشريط
    bar_chars = ["⬜", "⬛", "🟨", "🟧", "🟥", "🟪", "🟦", "🟩"]
    filled_char = bar_chars[min(filled % len(bar_chars), len(bar_chars)-1)]
    empty_char = "▫️"
    
    bar = filled_char * filled + empty_char * (width - filled)
    
    # إضافة مؤشرات
    indicators = ""
    if percentage < 30:
        indicators = "🟢"
    elif percentage < 70:
        indicators = "🟡"
    elif percentage < 90:
        indicators = "🟠"
    else:
        indicators = "🔴"
    
    # إضافة سرعة
    speed_display = f"│ ⚡ {speed}" if speed else ""
    
    return f"{indicators} {bar} {percentage:.1f}%{speed_display}"

def pro_hook(d, event, loop, last_upd, start_time):
    """دالة التحديث مع شريط احترافي"""
    if d['status'] == 'downloading':
        curr = time.time()
        if curr - last_upd[0] > 1.0:  # تحديث أسرع
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total and total > 0:
                speed = d.get('_speed_str', '')
                elapsed = curr - start_time
                
                # حساب الوقت المتبقي
                if '_speed_str' in d and 'MiB/s' in d['_speed_str']:
                    try:
                        speed_num = float(d['_speed_str'].split()[0])
                        if speed_num > 0:
                            remaining = (total - downloaded) / (speed_num * 1024 * 1024)
                            time_str = f"⏳ {remaining:.1f}s"
                        else:
                            time_str = "⏳ ..."
                    except:
                        time_str = "⏳ ..."
                else:
                    time_str = "⏳ ..."
                
                bar = progress_bar(downloaded, total, speed)
                
                # رسالة احترافية
                msg = f"""
┌─────────────────────────
│ 🚀 **محرك التحميل العالمي**
├─────────────────────────
│ 📊 **الشريط:** {bar}
│ 📦 **الحجم:** {downloaded/1024/1024:.1f}MB / {total/1024/1024:.1f}MB
│ ⚡ **السرعة:** `{speed}`
│ {time_str}
│ 🔍 **الحالة:** جاري التحميل...
└─────────────────────────
                """
                loop.create_task(event.edit(msg.strip()))
                last_upd[0] = curr

async def universal_downloader(event, url, is_audio=False, is_search=False):
    """دالة التحميل الرئيسية مع بحث شامل"""
    start_time = time.time()
    
    # إذا كان بحث (حتى لو رابط) أو كلمات
    if " " in url or not url.startswith(('http://', 'https://', 'www.')):
        is_search = True
        search_query = url
        await event.edit(f"🔍 **جاري البحث الدقيق عن:**\n`{search_query[:50]}`")
    else:
        await event.edit("📡 **جاري فحص الرابط وتجاوز الحماية...**")
    
    last_upd = [start_time]
    loop = asyncio.get_event_loop()
    
    try:
        def start():
            # إعداد البحث الشامل
            if is_search:
                # بحث شامل في كل المنصات
                if " " in url or not url.startswith('http'):
                    target = f"ytsearch3:{url}"  # البحث في أول 3 نتائج
                else:
                    target = url
            else:
                target = url
            
            hook = lambda d: pro_hook(d, event, loop, last_upd, start_time)
            
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio, hook)) as ydl:
                # إضافة مستخرجين إضافيين
                ydl.params['extract_flat'] = False
                
                # البحث في مصادر متعددة
                info = ydl.extract_info(target, download=True)
                
                # إذا كان بحث، نختار أفضل نتيجة
                if is_search and 'entries' in info:
                    # اختيار أفضل نتيجة
                    entries = [e for e in info['entries'] if e]
                    if entries:
                        # اختيار الأكثر مشاهدة/شهرة
                        info = max(entries, key=lambda x: x.get('view_count', 0) or x.get('like_count', 0) or 0)
                    else:
                        info = info['entries'][0]
                elif 'entries' in info:
                    info = info['entries'][0]
                
                path = ydl.prepare_filename(info)
                
                # تأكد من الصيغة الصحيحة
                if is_audio and not path.endswith('.mp3'):
                    new_path = path.rsplit(".", 1)[0] + ".mp3"
                    if os.path.exists(path): 
                        os.rename(path, new_path)
                    path = new_path
                
                return path, info

        file_path, info = await asyncio.to_thread(start)
        
        # حساب الوقت الإجمالي
        total_time = time.time() - start_time
        
        # رسالة النجاح
        success_msg = f"""
┌─────────────────────────
│ ✅ **تم التحميل بنجاح!**
├─────────────────────────
│ 📌 **العنوان:** `{info.get('title', 'غير معروف')[:60]}`
│ ⏱️ **الوقت:** {total_time:.1f} ثانية
│ 💾 **الصيغة:** {'🎵 MP3' if is_audio else '🎬 MP4'}
│ 🚀 **جاري الرفع الآن...**
└─────────────────────────
        """
        await event.edit(success_msg.strip())
        
        # الحصول على العنوان
        title = info.get('title', 'ميديا')
        if title and len(title) > 50:
            title = title[:47] + "..."
        
        # **الإرسال النهائي**
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **{title}**\n\n💎 **S O U R C E  C O M M O N**\n⚡ **الوقت:** {total_time:.1f} ثانية",
            video=not is_audio,
            supports_streaming=True,
            attributes=None,
            force_document=False
        )
        
        await event.delete()
        if os.path.exists(file_path): 
            os.remove(file_path)
            
    except Exception as e:
        error_msg = f"""
┌─────────────────────────
│ ❌ **حدث خطأ!**
├─────────────────────────
│ 🔧 **السبب:** `{str(e)[:100]}`
│ 
│ 💡 **حلول مقترحة:**
│ 1. تأكد من الرابط
│ 2. حاول مجدداً
│ 3. جرب رابط مختلف
└─────────────────────────
        """
        await event.edit(error_msg.strip())

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def v_d(event): 
    await universal_downloader(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def a_d(event): 
    await universal_downloader(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def s_v(event): 
    await universal_downloader(event, event.pattern_match.group(1), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def s_a(event): 
    await universal_downloader(event, event.pattern_match.group(1), True, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def m_m(event):
    help_text = """
┌─────────────────────────
│ 🚀 **محرك تحميل كومن الاحترافي**
├─────────────────────────
│ **🎬 التحميل من أي منصة:**
│ `.فيديو` + الرابط
│ `.صوت` + الرابط
│ 
│ **🔍 البحث الدقيق:**
│ `.بحث_فيد` + أي كلمة
│ `.بحث_صوت` + أي كلمة
│ 
│ **⚡ المميزات:**
│ • بحث شامل في كل المنصات
│ • شريط تحميل احترافي
│ • تحميل سريع جداً
│ • دعم جميع الصيغ
└─────────────────────────
    """
    await event.edit(help_text.strip())
