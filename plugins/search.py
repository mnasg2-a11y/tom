import aiohttp
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🔍 قـسـم الـبـحـث والـروابـط"
COMMANDS = (
    "• `.ويكي` : بـحـث سـريـع فـي مـوسـوعـة ويـكـيـبـيـديـا\n"
    "• `.قصر` : تـقـصـيـر الـروابـط الـطـويـلـة بـلـمـسـة واحدة"
)

# 1. البحث في ويكيبيديا
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ويكي (.*)'))
async def wiki_search(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن `{query}` فـي ويـكـيـبـيـديـا...**")
    
    # استخدام API ويكيبيديا الرسمي
    wiki_url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(wiki_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    summary = data.get("extract", "لـم يـتـم الـعـثـور عـلى مـعـلـومـات كـافـيـة.")
                    title = data.get("title", query)
                    
                    wiki_res = (
                        f"📚 **الـمـوسـوعـة الـحـرة: {title}**\n"
                        "───━━━━─ ● ─━━━━───\n\n"
                        f"{summary}\n\n"
                        "───━━━━─ ● ─━━━━───\n"
                        "✨ **تـم الـبـحـث بـواسطـة Common Pro**"
                    )
                    await event.edit(wiki_res)
                else:
                    await event.edit("⚠️ **عـذراً، لـم يـتـم الـعـثـور عـلـى نـتـائـج لهذا الـبـحث.**")
    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ أثـنـاء الـبـحث:** {str(e)}")

# 2. تقصير الروابط (نظام مزدوج)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.قصر (.*)'))
async def link_shortener(event):
    long_url = event.pattern_match.group(1)
    await event.edit("🔗 **جـارِ تـقـصـيـر الـرابـط...**")
    
    # استخدام API مجاني لتقصير الروابط
    api_url = f"https://is.gd/create.php?format=json&url={long_url}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    short_url = data.get("shorturl")
                    
                    short_res = (
                        "✅ **تـم تـقـصـيـر الـرابـط بـنـجـاح!**\n\n"
                        f"🔗 **الـرابـط الأصـلي:** `{long_url}`\n"
                        f"🚀 **الـرابـط الـمـقـصّر:** {short_url}\n\n"
                        "💎 **S O U R C E  C O M M O N**"
                    )
                    await event.edit(short_res)
                else:
                    await event.edit("❌ **فـشـل تـقـصـيـر الـرابـط، تـأكـد مـن صـحـتـه.**")
    except:
        await event.edit("⚠️ **حـدث خـطأ فـي الاتـصال بـسـيرفـر الـتـقـصير.**")
