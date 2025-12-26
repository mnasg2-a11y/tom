import asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, UserAdminInvalidError

# استيراد العميل من main
try:
    from main import client
except:
    pass

# قوائم التخزين
spam_chats = []
zagel_users = []  # قائمة زاجل

# رسائل ثابتة
BROADCAST_MSG = "✅ **جاري الإذاعة لأعضاء المجموعة...**\n\nالرجاء الانتظار..."
ZAGEL_MSG = "🕊 **جاري الإذاعة لقائمة زاجل...**\n\nالرجاء الانتظار..."
ZAGEL_EMPTY = "⚠️ **قائمة زاجل فارغة!**\n\nاستخدم `.اضف زاجل @username` لإضافة مستخدمين"
SUCCESS_MSG = "✅ **تمت الإذاعة بنجاح!**\n\nتم الإرسال إلى {} عضو"
ZAGEL_SUCCESS_MSG = "🕊 **تمت الإذاعة لقائمة زاجل بنجاح!**\n\nتم الإرسال إلى {} شخص"
STOP_MSG = "⏹ **تم إيقاف الإذاعة بنجاح**"
ADDED_MSG = "✅ **تم إضافة {} إلى قائمة زاجل**"
REMOVED_MSG = "✅ **تم إزالة {} من قائمة زاجل**"
LIST_MSG = "📋 **قائمة زاجل:**\n\n{}"

# أمر الإذاعة للمجموعة
@client.on(events.NewMessage(outgoing=True, pattern=r"\.للكل"))
async def broadcast_handler(event):
    if not event.is_group:
        await event.edit("❌ **هذا الأمر يعمل فقط في المجموعات!**")
        return
    
    if not event.is_reply:
        await event.edit("❌ **يجب الرد على الرسالة التي تريد إذاعتها!**")
        return
    
    message = await event.get_reply_message()
    chat_id = event.chat_id
    
    await event.edit(BROADCAST_MSG)
    
    spam_chats.append(chat_id)
    success = 0
    total = 0
    
    try:
        async for user in client.iter_participants(chat_id):
            total += 1
            if chat_id not in spam_chats:
                break
            
            if user.bot or user.deleted:
                continue
            
            try:
                if message.text:
                    await client.send_message(user.id, message.text, link_preview=False)
                else:
                    await client.send_file(
                        user.id,
                        message.media,
                        caption=message.text or "",
                        link_preview=False
                    )
                success += 1
                
                # تأخير صغير لتجنب الحظر
                if success % 10 == 0:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"خطأ في إرسال لـ {user.id}: {e}")
                continue
                
    except Exception as e:
        await event.edit(f"❌ **حدث خطأ:** `{str(e)}`")
        return
    
    if chat_id in spam_chats:
        spam_chats.remove(chat_id)
    
    await event.edit(SUCCESS_MSG.format(success))

# أمر إيقاف الإذاعة
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ايقاف للكل"))
async def stop_broadcast_handler(event):
    chat_id = event.chat_id
    
    if chat_id not in spam_chats:
        await event.edit("❌ **لا توجد عملية إذاعة نشطة في هذه المجموعة!**")
        return
    
    spam_chats.remove(chat_id)
    await event.edit(STOP_MSG)

# أمر الإذاعة لقائمة زاجل
@client.on(events.NewMessage(outgoing=True, pattern=r"\.زاجل"))
async def zagel_broadcast_handler(event):
    if not event.is_reply:
        await event.edit("❌ **يجب الرد على الرسالة التي تريد إذاعتها!**")
        return
    
    if not zagel_users:
        await event.edit(ZAGEL_EMPTY)
        return
    
    message = await event.get_reply_message()
    await event.edit(ZAGEL_MSG)
    
    success = 0
    failed = 0
    
    for user_id in zagel_users:
        try:
            if message.text:
                await client.send_message(user_id, message.text, link_preview=False)
            else:
                await client.send_file(
                    user_id,
                    message.media,
                    caption=message.text or "",
                    link_preview=False
                )
            success += 1
            
            # تأخير صغير
            if success % 5 == 0:
                await asyncio.sleep(1)
                
        except Exception as e:
            failed += 1
            print(f"خطأ في إرسال لـ {user_id}: {e}")
            continue
    
    await event.edit(ZAGEL_SUCCESS_MSG.format(success))

# أمر إضافة مستخدم لقائمة زاجل
@client.on(events.NewMessage(outgoing=True, pattern=r"\.اضف زاجل (.*)"))
async def add_zagel_handler(event):
    input_text = event.pattern_match.group(1)
    
    if not input_text:
        await event.edit("❌ **يجب كتابة المعرف أو الأيدي بعد الأمر!**\nمثال: `.اضف زاجل @username`")
        return
    
    # استخراج المعرفات من النص
    words = input_text.split()
    added = 0
    
    for word in words:
        user_id = None
        
        try:
            # إذا كان @username
            if word.startswith("@"):
                entity = await client.get_entity(word)
                user_id = entity.id
            
            # إذا كان أيدي رقمي
            elif word.isdigit():
                user_id = int(word)
                
            if user_id and user_id not in zagel_users:
                zagel_users.append(user_id)
                added += 1
                
        except Exception as e:
            print(f"خطأ في إضافة {word}: {e}")
            continue
    
    await event.edit(ADDED_MSG.format(added))

# أمر إزالة مستخدم من قائمة زاجل
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ازالة زاجل (.*)"))
async def remove_zagel_handler(event):
    input_text = event.pattern_match.group(1)
    
    if not input_text:
        await event.edit("❌ **يجب كتابة المعرف أو الأيدي بعد الأمر!**")
        return
    
    words = input_text.split()
    removed = 0
    
    for word in words:
        user_id = None
        
        try:
            if word.startswith("@"):
                entity = await client.get_entity(word)
                user_id = entity.id
            elif word.isdigit():
                user_id = int(word)
                
            if user_id and user_id in zagel_users:
                zagel_users.remove(user_id)
                removed += 1
                
        except Exception:
            continue
    
    await event.edit(REMOVED_MSG.format(removed))

# أمر عرض قائمة زاجل
@client.on(events.NewMessage(outgoing=True, pattern=r"\.قائمة زاجل"))
async def list_zagel_handler(event):
    if not zagel_users:
        await event.edit("📭 **قائمة زاجل فارغة**")
        return
    
    user_list = []
    for i, user_id in enumerate(zagel_users[:50], 1):  # عرض أول 50 فقط
        try:
            user = await client.get_entity(user_id)
            username = f"@{user.username}" if user.username else "بدون معرف"
            user_list.append(f"{i}. {user.first_name} - {username} ({user_id})")
        except:
            user_list.append(f"{i}. Unknown ({user_id})")
    
    text = LIST_MSG.format("\n".join(user_list))
    if len(zagel_users) > 50:
        text += f"\n\n...و {len(zagel_users) - 50} آخرين"
    
    await event.edit(text)

# أمر مسح قائمة زاجل
@client.on(events.NewMessage(outgoing=True, pattern=r"\.مسح زاجل"))
async def clear_zagel_handler(event):
    zagel_users.clear()
    await event.edit("✅ **تم مسح قائمة زاجل بالكامل**")
