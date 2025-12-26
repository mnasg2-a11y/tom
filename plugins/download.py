import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client # استيراد العميل الأساسي

# --- بيانات القسم للوحة التلقائية ---
SECTION_NAME = "🎬 مـركـز الـمـيـديـا الاحـتـرافـي"
COMMANDS = "• `.ميديا` : لـعـرض لـوحـة الـتـحـمـيـل الـذكـيـة"

# إعدادات المحرك (نفس القوة بدون تغيير)
def get_pro_opts(is_audio=False):
    return {
        'format': 'bestaudio/best' if is_audio else 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'no_warnings': True,
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

# 1. الواجهة الاحترافية الرئيسية
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def pro_media_menu(event):
    menu_text = (
        "╔════════════════════╗\n"
        "      **💎 C O M M O N  -  M E D I A**\n"
        "╚════════════════════╝\n\n"
        "🎬 **الـتـحـمـيـل عـبـر الـروابـط:**\n"
        "• `.فيديو` <رابط>\n"
        "• `.صوت` <رابط>\n\n"
        "🔍 **الـبـحـث الـذكـي (يـوتـيـوب):**\n"
        "• `.بحث_فيد` <اسـم>\n"
        "• `.بحث_صوت` <اسـم>\n"
        "───━━━━─ ● ─━━━━───\n"
        "🚀 **الـحـالـة:** جـاهـز لـلـتـحـمـيـل الـفـوري"
    )
    await event.edit(menu_text)

# دالة التحميل الاحترافية (مع تأثيرات بصرية)
async def pro_downloader(event, url, is_audio=False, is_search=False):
    # شكل احترافي للتحميل
    loading_ui = "⏳ **جـارِ الـتـحـضـيـر...**\n" + ("🎵" if is_audio else "🎬") + " [▒▒▒▒▒▒▒▒▒▒] 0%"
    await event.edit(loading_ui)
    
    try:
        def run_ydl():
            target_url = f"ytsearch1:{url}" if is_search else url
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio)) as ydl:
                info = ydl.extract_info(target_url, download=True)
                if is_search: info = info['entries'][0]
                path = ydl.prepare_filename(info)
                if is_audio: path = path.rsplit(".", 1)[0] + ".mp3"
                return path, info
        
        # تنفيذ التحميل
        file_path, info = await asyncio.to_thread(run_ydl)
        
        # تحديث الحالة بشكل احترافي
        await event.edit("📤 **جـارِ الـرفـع إلـى الـسـحـابـة...**\n" + ("🎵" if is_audio else "🎬") + " [██████████] 100%")
        
        # تصميم الكابشن (وصف الملف) الاحترافي
        caption = (
            f"✅ **تـم الـتـحـمـيـل بـواسطـة Common Pro**\n"
            f"───━━━━─ ● ─━━━━───\n"
            f"📌 **الـعـنـوان:** `{info.get('title')[:50]}`\n"
            f"⏱ **الـمـدة:** `{info.get('duration_string', 'Unknown')}`\n"
            f"🎬 **الـمـنـصـة:** {info.get('extractor_key', 'Link')}\n"
            f"───━━━━─ ● ─━━━━───\n"
            f"💎 **المطور:** @iomk0 | **القناة:** @iomk3"
        )
        
        await client.send_file(event.chat_id, file_path, caption=caption, reply_to=event.reply_to_msg_id)
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ فـي الـمـحـرك:**\n`{str(e)[:100]}`")

# --- محركات التشغيل (بقيت كما هي للسرعة) ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def d_v(event): await pro_downloader(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def d_a(event): await pro_downloader(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def s_v(event): await pro_downloader(event, event.pattern_match.group(1), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def s_a(event): await pro_downloader(event, event.pattern_match.group(1), True, True)
