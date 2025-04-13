#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الملف الرئيسي للبوت المحسن
يدعم جميع الميزات الجديدة: خدمات وسائل التواصل الاجتماعي المتعددة، نظام الدفع، واجهة المستخدم المحسنة
تم تعديله ليعمل على منصة Railway
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# استيراد الإعدادات والوحدات
import config
from utils.database import init_database, register_user, create_order, get_user_orders, update_order_status
from utils.services import process_channel_followers, process_post_views, process_post_likes, process_bot_referrals
from utils.social_services import boost_social_service, SOCIAL_BOOST_FUNCTIONS
from utils.payment_system import initialize_payment_system, get_user_credits, can_process_order, process_order_payment
from utils.enhanced_ui import (
    get_main_menu_keyboard, get_services_categories_keyboard, get_category_services_keyboard,
    get_quantity_keyboard, get_order_confirmation_keyboard, get_packages_keyboard,
    get_payment_methods_keyboard, get_my_orders_keyboard, get_my_account_keyboard,
    get_support_keyboard, get_welcome_message, get_about_message, get_balance_message,
    get_packages_message, handle_button_callback, add_button_handlers, ENHANCED_SERVICES
)

# التحقق من وجود متغيرات البيئة وتطبيقها
if os.environ.get('BOT_TOKEN'):
    config.BOT_TOKEN = os.environ.get('BOT_TOKEN')
if os.environ.get('ADMIN_ID'):
    config.ADMIN_ID = int(os.environ.get('ADMIN_ID'))
if os.environ.get('MAX_CONCURRENT_BROWSERS'):
    config.MAX_CONCURRENT_BROWSERS = int(os.environ.get('MAX_CONCURRENT_BROWSERS'))
if os.environ.get('RAILWAY_STATIC_URL'):
    config.ADMIN_DASHBOARD_URL = os.environ.get('RAILWAY_STATIC_URL').rstrip('/') + '/admin'

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
WAITING_FOR_LINK, WAITING_FOR_QUANTITY = range(2)

# معالج أمر البداية
def start_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر البداية /start"""
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    
    # تسجيل المستخدم في قاعدة البيانات
    register_user(user_id, username, first_name, last_name)
    
    # إرسال رسالة الترحيب مع القائمة الرئيسية
    update.message.reply_text(
        get_welcome_message(first_name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )

# معالج أمر المساعدة
def help_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر المساعدة /help"""
    help_text = """
🤖 مساعدة بوت رشق المتابعين والبوتات

الأوامر المتاحة:
/start - بدء استخدام البوت
/help - عرض هذه المساعدة
/menu - عرض القائمة الرئيسية
/balance - عرض رصيدك الحالي
/orders - عرض طلباتك
/packages - عرض باقات الرشق المتاحة
/support - التواصل مع الدعم الفني

للحصول على مساعدة إضافية، يمكنك استخدام قسم "الدعم الفني" من القائمة الرئيسية.
"""
    update.message.reply_text(help_text, parse_mode='HTML')

# معالج أمر القائمة
def menu_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر القائمة /menu"""
    user = update.effective_user
    first_name = user.first_name or ""
    
    update.message.reply_text(
        get_welcome_message(first_name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )

# معالج أمر الرصيد
def balance_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر الرصيد /balance"""
    user_id = update.effective_user.id
    
    update.message.reply_text(
        get_balance_message(user_id),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]]),
        parse_mode='HTML'
    )

# معالج أمر الطلبات
def orders_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر الطلبات /orders"""
    user_id = update.effective_user.id
    
    update.message.reply_text(
        "📊 طلباتي\n\nاختر نوع الطلبات التي تريد عرضها:",
        reply_markup=get_my_orders_keyboard(user_id),
        parse_mode='HTML'
    )

# معالج أمر الباقات
def packages_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر الباقات /packages"""
    update.message.reply_text(
        get_packages_message(),
        reply_markup=get_packages_keyboard(),
        parse_mode='HTML'
    )

# معالج أمر الدعم
def support_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر الدعم /support"""
    update.message.reply_text(
        "📞 الدعم الفني\n\nاختر نوع المساعدة المطلوبة:",
        reply_markup=get_support_keyboard(),
        parse_mode='HTML'
    )

# معالج أمر المسؤول
def admin_command(update: Update, context: CallbackContext) -> None:
    """معالج أمر المسؤول /admin"""
    user_id = update.effective_user.id
    
    # التحقق من صلاحيات المسؤول
    if user_id == config.ADMIN_ID:
        admin_dashboard_url = "http://localhost:5000"
        
        # إذا كان هناك عنوان URL مخصص للوحة التحكم
        if hasattr(config, 'ADMIN_DASHBOARD_URL') and config.ADMIN_DASHBOARD_URL:
            admin_dashboard_url = config.ADMIN_DASHBOARD_URL
        
        update.message.reply_text(
            f"👑 مرحباً بك في لوحة تحكم المسؤول\n\nيمكنك الوصول إلى لوحة التحكم من خلال الرابط التالي:\n{admin_dashboard_url}\n\nاسم المستخدم الافتراضي: admin\nكلمة المرور الافتراضية: admin123",
            parse_mode='HTML'
        )
    else:
        update.message.reply_text("⛔ عذراً، هذا الأمر متاح للمسؤولين فقط.")

# معالج الرسائل
def message_handler(update: Update, context: CallbackContext) -> int:
    """معالج الرسائل العادية"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # إذا كان المستخدم في حالة انتظار الرابط
    if context.user_data.get("waiting_for_link"):
        service_id = context.user_data.get("current_service")
        quantity = context.user_data.get("current_quantity")
        
        # البحث عن اسم الخدمة
        service_name = None
        for category_info in ENHANCED_SERVICES.values():
            if service_id in category_info["services"]:
                service_name = category_info["services"][service_id]
                break
        
        # حساب التكلفة
        from utils.payment_system import get_service_cost
        cost = get_service_cost(service_id, quantity)
        
        # التحقق من الرصيد
        if not can_process_order(user_id, service_id, quantity):
            update.message.reply_text(
                f"❌ عذراً، رصيدك غير كافٍ لتنفيذ هذا الطلب.\n\nالتكلفة: {cost} نقطة\nرصيدك الحالي: {get_user_credits(user_id)} نقطة\n\nيرجى شراء رصيد إضافي من قسم 'باقات الرشق'.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]]),
                parse_mode='HTML'
            )
            context.user_data["waiting_for_link"] = False
            return ConversationHandler.END
        
        # تخزين الرابط
        target_link = text.strip()
        context.user_data["target_link"] = target_link
        
        # عرض تأكيد الطلب
        update.message.reply_text(
            f"""
🚀 تأكيد الطلب:

🔹 الخدمة: {service_name}
🔹 الكمية: {quantity}
🔹 الرابط: {target_link}
🔹 التكلفة: {cost} نقطة

هل تريد تأكيد الطلب؟
""",
            reply_markup=get_order_confirmation_keyboard(service_id, quantity, target_link),
            parse_mode='HTML'
        )
        
        context.user_data["waiting_for_link"] = False
        return ConversationHandler.END
    
    # إذا لم يكن في حالة خاصة، عرض القائمة الرئيسية
    menu_command(update, context)
    return ConversationHandler.END

# معالج تأكيد الطلب
def confirm_order_callback(update: Update, context: CallbackContext) -> None:
    """معالج تأكيد الطلب"""
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    if callback_data.startswith("confirm_"):
        parts = callback_data.split("_")
        service_id = parts[1]
        quantity = int(parts[2])
        target_link = parts[3]
        
        # البحث عن اسم الخدمة
        service_name = None
        for category_info in ENHANCED_SERVICES.values():
            if service_id in category_info["services"]:
                service_name = category_info["services"][service_id]
                break
        
        # معالجة الدفع
        if process_order_payment(user_id, service_id, quantity):
            # إنشاء الطلب
            order_id = create_order(user_id, service_id, target_link, quantity)
            
            # بدء تنفيذ الطلب
            if service_id in SOCIAL_BOOST_FUNCTIONS:
                # تنفيذ الطلب في الخلفية
                asyncio.create_task(boost_social_service(service_id, target_link, quantity))
            
            query.edit_message_text(
                f"""
✅ تم إنشاء الطلب بنجاح!

🔹 رقم الطلب: {order_id}
🔹 الخدمة: {service_name}
🔹 الكمية: {quantity}
🔹 الرابط: {target_link}
🔹 الحالة: قيد التنفيذ

سيتم تنفيذ الطلب في أقرب وقت ممكن. يمكنك متابعة حالة الطلب من قسم "طلباتي".
""",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]]),
                parse_mode='HTML'
            )
        else:
            query.edit_message_text(
                "❌ عذراً، حدث خطأ أثناء معالجة الطلب. يرجى التحقق من رصيدك والمحاولة مرة أخرى.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]]),
                parse_mode='HTML'
            )
    
    elif callback_data == "cancel_order":
        query.edit_message_text(
            "❌ تم إلغاء الطلب.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]]),
            parse_mode='HTML'
        )

# الدالة الرئيسية
def main() -> None:
    """الدالة الرئيسية لتشغيل البوت"""
    # تهيئة قواعد البيانات
    init_database()
    initialize_payment_system()
    
    # إنشاء المحدث
    updater = Updater(config.BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # إضافة معالجات الأوامر
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("menu", menu_command))
    dispatcher.add_handler(CommandHandler("balance", balance_command))
    dispatcher.add_handler(CommandHandler("orders", orders_command))
    dispatcher.add_handler(CommandHandler("packages", packages_command))
    dispatcher.add_handler(CommandHandler("support", support_command))
    dispatcher.add_handler(CommandHandler("admin", admin_command))
    
    # إضافة معالج الرسائل
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    
    # إضافة معالج الأزرار
    add_button_handlers(dispatcher)
    
    # بدء البوت
    PORT = int(os.environ.get('PORT', '8080'))
    if os.environ.get('RAILWAY_STATIC_URL'):
        # استخدام webhook في Railway
        webhook_url = os.environ.get('RAILWAY_STATIC_URL').rstrip('/') + '/' + config.BOT_TOKEN
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=config.BOT_TOKEN,
                            webhook_url=webhook_url)
        logger.info(f"تم بدء تشغيل البوت على المنفذ {PORT} باستخدام webhook!")
        logger.info(f"Webhook URL: {webhook_url}")
    else:
        # استخدام long polling في بيئة التطوير
        updater.start_polling()
        logger.info("تم بدء تشغيل البوت!")
    
    # الانتظار حتى يتم إيقاف البوت
    updater.idle()

if __name__ == '__main__':
    main()
