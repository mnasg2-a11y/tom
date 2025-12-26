import os
import glob
import importlib
import logging
from telethon import TelegramClient, events

# --- الإعدادات التلقائية المدمجة ---
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'

# قاموس لتخزين معلومات الأقسام تلقائياً
PLUGINS_HELP = {}

client = TelegramClient('CommonSession', API_ID, API_HASH)

def load_plugins():
    """تحميل الأقسام وتسجيل معلوماتها تلقائياً"""
    if not os.path.exists("plugins"):
        os.makedirs("plugins")
    
    path = "plugins/*.py"
    files = glob.glob(path)
    for name in files:
        plugin_name = name.replace(".py", "").replace("/", ".").replace("\\", ".")
        # استيراد الملف كـ module
        module = importlib.import_module(plugin_name)
        
        # التأكد من وجود متغيرات التعريف داخل ملف القسم
        if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
            PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
            print(f"✅ تم تسجيل قسم: {module.SECTION_NAME}")

@client.on(events.NewMessage(pattern=r'\.الاوامر'))
async def dynamic_menu(event):
    """توليد لوحة الأوامر تلقائياً بناءً على الأقسام المحملة"""
    header = "╔════════════════════╗\n      **🚀 سـورس كـومـن الـمـطـور**\n╚════════════════════╝\n"
    
    menu_content = ""
    # الدوران حول جميع الأقسام التي تم تحميلها تلقائياً
    for section, commands in PLUGINS_HELP.items():
        menu_content += f"\n**{section}:**\n{commands}\n"
    
    footer = f"\n---\n📢 **القناة:** @iomk3 | 🛠 **المطور:** @iomk0"
    
    final_menu = header + menu_content + footer
    await event.edit(final_menu)

if __name__ == "__main__":
    print("⚡ سورس كومن يبدأ بالتحميل التلقائي...")
    load_plugins()
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()
