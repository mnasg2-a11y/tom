import asyncio
from telethon import events
from __main__ import client  # استيراد العميل الأساسي
# استيراد فئة الذكاء الاصطناعي من ملفك
from الذكاء_الاصطناعي_مال_سورس_كومن import GeminiAI

# إنشاء كائن الذكاء الاصطناعي
ai_engine = GeminiAI()

# --- بيانات القسم للوحة الأوامر ---
SECTION_NAME = "👨‍💻 قـسـم الـمـبـرمـج الـذكـي"
COMMANDS = "• `.برمجة` : لـعـرض لـوحـة أدوات الـتـطويـر والـذكاء"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.برمجة$'))
async def coding_dashboard(event):
    dashboard = (
        "╔════════════════════╗\n"
        "      **👨‍💻 مـبـرمـج كـومـن  P R O**\n"
        "╚════════════════════╝\n\n"
        "🤖 **أدوات الـتـطويـر الـمدمـجـة بـالـذكاء:**\n\n"
        "1️⃣ `.كود` + وصف : لـتوليد أكـواد بـرمـجية احـترافية\n"
        "2️⃣ `.فحص` + كود : لـتـحليل الـأخطاء وإصـلاحـها ذكـيـاً\n"
        "3️⃣ `.شرح_كود` : لـفهم مـنطق أي كـود بـرمـجي (بالرد)\n"
        "4️⃣ `.سكرابت` : لـكتابة سـكـربتات أتمتة لـلـتليجرام\n"
        "5️⃣ `.هيكلة` + فكرة : لـتـخطيط بـناء الـمـشاريع والـقواعد\n"
        "───━━━━─ ● ─━━━━───\n"
        "📡 **الـمـحرك:** Gemini 2.0 Flash Lite\n"
        "💎 **S O U R C E  C O M M O N**"
    )
    await event.edit(dashboard)

# --- تفعيل الأوامر الـ 5 الفرعية المدمجة مع AI ---

@client.on(events.NewMessage(outgoing=True, pattern=r'\.كود (.*)'))
async def gen_code(event):
    prompt = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جـارِ صـياغة الـكود الـبرمجي...**")
    system_prompt = "أنت مبرمج خبير. اكتب كود نظيف، فعال، ومعلق عليه باللغة العربية."
    response = ai_engine.chat(event.sender_id, f"اكتب كود لـ: {prompt}", system_prompt)
    await event.edit(f"💻 **الـكود الـمـقترح:**\n\n{response}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فحص (.*)'))
async def debug_code(event):
    code = event.pattern_match.group(1).strip()
    await event.edit("🔍 **جـارِ تـحـليل الـمنطق وإصـلاح الـعـلل...**")
    system_prompt = "أنت خبير في تنقيح الأخطاء (Debugger). ابحث عن الأخطاء في الكود وقدم الحل الصحيح."
    response = ai_engine.chat(event.sender_id, f"صحح هذا الكود واشرح الخطأ: {code}", system_prompt)
    await event.edit(f"🛠 **تـقـرير الـإصـلاح:**\n\n{response}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.شرح_كود'))
async def explain_logic(event):
    if not event.is_reply: return await event.edit("⚠️ **يـرجى الـرد عـلى كـود لـشرحه.**")
    reply = await event.get_reply_message()
    await event.edit("📖 **جـارِ تـفـكيك الـكود وشـرح مـنطقه...**")
    system_prompt = "اشرح الكود التالي بدقة وببساطة ليفهمه المبتدئين."
    response = ai_engine.chat(event.sender_id, f"اشرح هذا الكود بالتفصيل: {reply.text}", system_prompt)
    await event.edit(f"💡 **شـرح الـمنطق الـبرمجي:**\n\n{response}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.سكرابت (.*)'))
async def telegram_script(event):
    task = event.pattern_match.group(1).strip()
    await event.edit("🤖 **جـارِ تـصميم سـكربت الـأتمتة...**")
    system_prompt = "أنت خبير في مكتبة Telethon و Pyrogram. صمم سكريبت تليجرام يؤدي المهمة المطلوبة."
    response = ai_engine.chat(event.sender_id, f"اكتب سكريبت Telethon لـ: {task}", system_prompt)
    await event.edit(f"📜 **سـكربت الـأتمتة:**\n\n{response}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.هيكلة (.*)'))
async def project_structure(event):
    idea = event.pattern_match.group(1).strip()
    await event.edit("🏗 **جـارِ تـخطيط هـيكلية الـمـشروع...**")
    system_prompt = "أنت مهندس برمجيات (Software Architect). صمم هيكلية الملفات وقواعد البيانات لهذا المشروع."
    response = ai_engine.chat(event.sender_id, f"خطط لهيكلية مشروع: {idea}", system_prompt)
    await event.edit(f"📐 **مـخطط الـبناء الـبرمجي:**\n\n{response}")
