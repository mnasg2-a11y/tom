import os
import yt_dlp
import asyncio
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🎬 قـسـم الـفـيـديـو الـمـطـور"
COMMANDS = (
    "• `.تحميل_فيد` <رابط> : تـحـمـيل فـيـديـو مـن أي مـنـصـة (TikTok, YT, IG)\n"
    "• `.بحث_فيد` <اسم> : الـبـحث عـن فـيـديـو وتـحـمـيـلـه تـلـقـائـيـاً"
)

# إعدادات المحرك لتحميل الفيديو بأفضل جودة
def get_video_opts():
    return {
        "format": "best",
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
    }

# 1. أمر تحميل الفيديو عبر الرابط (أي منصة)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحميل_فيد (.*)'))
async def vid_downloader(event):
    url = event.pattern_match.group(1)
    if not url:
        return await event.edit("⚠️ **الـرجـاء وضـع رابـط الـفـيـديـو الـمـطلـوب.**")
    
    await event.edit("🎬 **جـارِ تـحـلـيـل الـرابـط وجـلـب الـفـيـديـو...**")
    
    try:
        with yt_dlp.YoutubeDL(get_video_opts()) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            await event.edit("📤 **جـارِ رفـع الـفـيـديـو بـأعـلـى جـودة...**")
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **تـم تـحـمـيل الـفـيـديـو بـنـجـاح**\n📌 **الـعنوان:** `{info.get('title', 'Video')}`\n🔗 **الـمنصة:** {info.get('extractor_key', 'Unknown')}",
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ أثـنـاء الـتـحـمـيل:**\n`{str(e)[:150]}`")

# 2. أمر البحث عن فيديو وتحميله بالاسم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def vid_searcher(event):
    query = event.pattern_match.group(1)
    if not query:
        return await event.edit("⚠️ **يـرجـى كـتـابـة اسـم الـفـيـديـو للـبـحـث عـنـه.**")
    
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن `{query}` وتـحـمـيـلـه...**")
    
    try:
        # البحث في يوتيوب وجلب أول نتيجة
        search_url = f"ytsearch1:{query}"
        with yt_dlp.YoutubeDL(get_video_opts()) as ydl:
            info = ydl.extract_info(search_url, download=True)['entries'][0]
            file_path = ydl.prepare_filename(info)
            
            await event.edit("📤 **جـد الـفـيـديـو! جـارِ الـرفـع الآن...**")
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **نـتـيـجـة الـبـحث والـتـحـمـيل:**\n📌 `{info.get('title')}`",
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **لـم يـتـم الـعـثـور عـلى نـتـائـج:**\n`{str(e)[:150]}`")
