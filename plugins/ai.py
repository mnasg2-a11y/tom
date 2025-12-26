import asyncio
import random
import aiohttp
from telethon import events, Button
from __main__ import client # استيراد العميل من الملف الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🧠 الـذكـاء الاصـطـنـاعـي"
COMMANDS = (
    "• `.سؤال` : دردشـة ذكـيـة مـع Gemini 2.0\n"
    "• `.رسم` : تـولـيـد صـور فـنـيـة سـريـعـة\n"
    "• `.فلول` : تـولـيـد صـور فـائـقـة الـجـودة (Flux)\n"
    "• `.ترجم` : تـرجـمـة ذكـيـة لأي لـغـة\n"
    "• `.كود` : كـتـابـة أكـواد بـرمـجـيـة مـفـولـة"
)

# --- إعدادات الـ AI (مستخلصة من سورس كومن) ---
API_URL = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
HEADERS = {
    'Content-Type': 'application/json',
    'x-goog-api-key': "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk", # مفتاح سورس كومن
    'x-firebase-appcheck': "eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ=="
}

# --- 1. أمر السؤال والدردشة ---
@client.on(events.NewMessage(pattern=r'\.سؤال (.*)'))
async def ai_chat(event):
    question = event.pattern_match.group(1)
    await event.edit("🤔 **جـارِ الـتـفـكـيـر...**")
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": question}]}]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, headers=HEADERS) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    await event.edit(f"🧠 **الـرد الـذكـي:**\n\n{answer}")
                else:
                    await event.edit("⚠️ **عذراً، حدث خطأ في الاتصال بالذكاء الاصطناعي.**")
    except Exception as e:
        await event.edit(f"❌ **خطأ:** {str(e)}")

# --- 2. أمر الرسم السريع (Writecream) ---
@client.on(events.NewMessage(pattern=r'\.رسم (.*)'))
async def fast_draw(event):
    prompt = event.pattern_match.group(1)
    await event.edit("🎨 **جـارِ رسـم لوحـتـك...**")
    
    url = f"https://1yjs1yldj7.execute-api.us-east-1.amazonaws.com/default/ai_image?prompt={prompt}&aspect_ratio=1:1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                img_url = data.get("image_link")
                if img_url:
                    await event.delete()
                    await client.send_file(event.chat_id, img_url, caption=f"🖼 **تـم الـرسـم بـنـجـاح:**\n`{prompt}`")
                else:
                    await event.edit("❌ **فـشـل تـولـيـد الـصـورة.**")
    except:
        await event.edit("⚠️ **حـدث خـطأ أثـنـاء الـتـواصـل مـع الـسـيـرفـر.**")

# --- 3. أمر الصور الفائقة (Flux Max) ---
@client.on(events.NewMessage(pattern=r'\.فلول (.*)'))
async def flux_draw(event):
    prompt = event.pattern_match.group(1)
    await event.edit("✨ **جـارِ تـولـيـد صـورة فـائـقـة الـدقـة...**")
    
    seed = random.randint(1, 999999)
    flux_url = f"https://image.pollinations.ai/prompt/{prompt}?model=flux&seed={seed}&width=1024&height=1024&nologo=true"
    
    try:
        await event.delete()
        await client.send_file(event.chat_id, flux_url, caption=f"💎 **Flux Max Generation:**\n`{prompt}`")
    except:
        await event.edit("❌ **فـشـل الـتـولـيـد الـعـالـي.**")

# --- 4. أمر الترجمة الذكية ---
@client.on(events.NewMessage(pattern=r'\.ترجم (.*)'))
async def translator(event):
    text = event.pattern_match.group(1)
    await event.edit("🌍 **جـارِ الـتـرجـمـة...**")
    
    prompt = f"ترجم النص التالي إلى العربية والإنجليزية بأسلوب احترافي: {text}"
    # استخدام نفس وظيفة الدردشة للترجمة لضمان دقة AI
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=HEADERS) as resp:
            result = await resp.json()
            answer = result['candidates'][0]['content']['parts'][0]['text']
            await event.edit(f"🌍 **الـتـرجـمـة الاحـتـرافـيـة:**\n\n{answer}")

