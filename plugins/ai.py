# plugins/ai_pro.py
from telethon import events
import aiohttp
import json
import random
import os
from __main__ import client # استيراد العميل الأساسي للفهرسة

# --- بيانات الفهرسة لظهور الأوامر في قائمة السورس ---
SECTION_NAME = "🧠 قسم الذكاء الاصطناعي المطور"
COMMANDS = (
    "• `.ذكاء` : قائمة جميع الأوامر الذكية\n"
    "• `.سؤال` : محادثة ذكية فورية\n"
    "• `.كود` : برمجة وتصحيح ذكي\n"
    "• `.رسم` : إنشاء وصف للصور\n"
    "• `.مقال` : كتابة محتوى طويل\n"
    "• `.ترجم` : ترجمة احترافية\n"
    "• `.لخص` : تلخيص النصوص\n"
    "• `.حل` : حل المشكلات البرمجية\n"
    "• `.افكار` : توليد أفكار إبداعية\n"
    "• `.حكمة` : حكمة اليوم الذكية"
)

# =========================================================
# 🎯 محرك Gemini 2.0 Flash Lite الأساسي
# =========================================================

async def ask_gemini(prompt):
    api_url = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
    headers = {
        'User-Agent': "Ktor client", 
        'Accept': "application/json", 
        'Content-Type': "application/json", 
        'x-goog-api-key': "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk", 
        'x-goog-api-client': "gl-kotlin/2.2.0-ai fire/16.5.0", 
        'x-firebase-appid': "1:652803432695:android:c4341db6033e62814f33f2", 
        'x-firebase-appversion': "79", 
        'x-firebase-appcheck': "eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ=="
    }
    payload = {
        "model": "projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite", 
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'candidates' in result and result['candidates']:
                        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except: return None
    return None

# =========================================================
# 🛠 الأوامر المباشرة (تعمل بدون كلمة ذكاء)
# =========================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ذكاء$'))
async def ai_menu(event):
    """عرض قائمة التعليمات"""
    menu = """
🧠 **🛠 سورس كـومـن - نـظـام الـذكـاء الـمـتـكـامـل 🛠**

**📋 الأوامر المباشرة المتاحة:**
• `.سؤال [نص]` ← محادثة ذكية
• `.رسم [وصف]` ← إنشاء وصف صورة
• `.كود [لغة] [وصف]` ← كتابة كود
• `.مقال [موضوع]` ← كتابة مقال
• `.ترجم [لغة] [نص]` ← ترجمة
• `.لخص [نص]` ← تلخيص
• `.حل [مشكلة]` ← حل المشاكل
• `.افكار [موضوع]` ← أفكار إبداعية
• `.تعلم [موضوع]` ← شرح تعليمي
• `.قصة [فكرة]` ← كتابة قصة
• `.شعر [موضوع]` ← قصيدة شعرية
• `.تصميم [وصف]` ← تصميمات
• `.خطط [هدف]` ← تخطيط
• `.اختبر [موضوع]` ← اختبار
• `.حكمة` ← حكمة عشوائية

**👤 المطور:** @iomk0 | **📢 القناة:** @iomk3
    """
    await event.edit(menu)

# دالة المعالجة الموحدة للأوامر المباشرة
async def process_ai_cmd(event, mode, prompt_prefix):
    if len(event.text.split()) < 2 and mode != 'حكمة':
        return await event.edit(f"⚠️ **يرجى كتابة نص بعد الأمر.**\nمثال: `.{mode} كيف حالك؟`")
    
    user_input = event.text.split(maxsplit=1)[1] if mode != 'حكمة' else ""
    await event.edit(f"🤔 **جـارِ مـعـالجة '{mode}' عبر Gemini...**")
    
    if mode == 'حكمة':
        wisdoms = ["الصبر مفتاح الفرج.", "العلم في الصغر كالنقش في الحجر.", "الوقت كالسيف إن لم تقطعه قطعك."]
        return await event.edit(f"💭 **حكمة اليوم:**\n\n{random.choice(wisdoms)}")
    
    response = await ask_gemini(f"{prompt_prefix}: {user_input}")
    if response:
        await event.edit(f"🧠 **نـتـيـجـة الـذكاء ({mode}):**\n\n{response}")
    else:
        await event.edit("❌ **فشل الاتصال بمحرك Gemini، حاول لاحقاً.**")

# تسجيل الأوامر الـ 15 المباشرة
@client.on(events.NewMessage(outgoing=True, pattern=r'\.سؤال (.*)'))
async def ai_s(event): await process_ai_cmd(event, 'سؤال', 'أجب على هذا السؤال بالعربية')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.رسم (.*)'))
async def ai_r(event): await process_ai_cmd(event, 'رسم', 'صف صورة تفصيلية احترافية لـ')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.كود (.*)'))
async def ai_c(event): await process_ai_cmd(event, 'كود', 'اكتب كود برمجي نظيف مع شرح لـ')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.مقال (.*)'))
async def ai_m(event): await process_ai_cmd(event, 'مقال', 'اكتب مقالاً طويلاً ومنسقاً عن')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ترجم (.*)'))
async def ai_t(event): await process_ai_cmd(event, 'ترجم', 'ترجم النص التالي للعربية بدقة')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.لخص (.*)'))
async def ai_l(event): await process_ai_cmd(event, 'لخص', 'لخص النص التالي بأسلوب نقاط')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.حل (.*)'))
async def ai_h(event): await process_ai_cmd(event, 'حل', 'حل المشكلة التالية برمجياً ومنطقياً')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.افكار (.*)'))
async def ai_f(event): await process_ai_cmd(event, 'افكار', 'قدم 5 أفكار إبداعية ومبتكرة عن')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تعلم (.*)'))
async def ai_e(event): await process_ai_cmd(event, 'تعلم', 'اشرح لي هذا الموضوع بطريقة مبسطة')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.قصة (.*)'))
async def ai_q(event): await process_ai_cmd(event, 'قصة', 'اكتب قصة قصيرة ومشوقة عن')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.شعر (.*)'))
async def ai_sh(event): await process_ai_cmd(event, 'شعر', 'اكتب قصيدة شعرية فصيحة عن')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تصميم (.*)'))
async def ai_ds(event): await process_ai_cmd(event, 'تصميم', 'صف تصميماً جرافيكياً احترافياً لـ')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.خطط (.*)'))
async def ai_pl(event): await process_ai_cmd(event, 'خطط', 'ارسم خطة عمل استراتيجية لـ')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.اختبر (.*)'))
async def ai_test(event): await process_ai_cmd(event, 'اختبر', 'اطرح علي سؤالاً صعباً لاختبار معرفتي في')

@client.on(events.NewMessage(outgoing=True, pattern=r'\.حكمة'))
async def ai_w(event): await process_ai_cmd(event, 'حكمة', '')
