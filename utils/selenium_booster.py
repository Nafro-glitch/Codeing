#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة الرشق الفعلي باستخدام Selenium
تستخدم للتشغيل الآلي للمتصفح لتنفيذ عمليات الرشق الفعلية
تم تعديلها لتعمل على منصة Railway
"""

import logging
import time
import random
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# عدد المتصفحات المتزامنة - تقليل العدد في بيئة Railway لتوفير الموارد
MAX_CONCURRENT_BROWSERS = int(os.environ.get("MAX_CONCURRENT_BROWSERS", "2"))

# قائمة وكلاء المستخدم المتنوعة
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0",
]

# إنشاء خيارات المتصفح
def create_browser_options():
    """إنشاء خيارات المتصفح للتشغيل الآلي"""
    options = Options()
    
    # تشغيل بدون واجهة رسومية دائماً في بيئة Railway
    options.add_argument("--headless=new")
    
    # إعدادات ضرورية لبيئة Docker
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # إعدادات إضافية لتحسين الأداء
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    
    # إعدادات لتجنب اكتشاف التشغيل الآلي
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    return options

# إنشاء متصفح جديد
def create_browser():
    """إنشاء متصفح جديد للتشغيل الآلي مع تعديلات لبيئة Railway"""
    try:
        options = create_browser_options()
        
        # محاولة استخدام المتصفح المثبت في Docker
        browser = webdriver.Chrome(options=options)
        
        # تعديل متغيرات JavaScript لتجنب اكتشاف التشغيل الآلي
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("تم إنشاء المتصفح بنجاح باستخدام الطريقة الأولى")
        return browser
    except Exception as e:
        logger.warning(f"فشلت الطريقة الأولى لإنشاء المتصفح: {e}")
        
        # محاولة بديلة باستخدام ChromeDriverManager
        try:
            options = create_browser_options()
            service = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=options)
            browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("تم إنشاء المتصفح بنجاح باستخدام ChromeDriverManager")
            return browser
        except Exception as e2:
            logger.error(f"فشلت المحاولة البديلة لإنشاء المتصفح: {e2}")
            
            # محاولة ثالثة باستخدام مسار محدد للمتصفح في Docker
            try:
                options = create_browser_options()
                browser = webdriver.Chrome(options=options)
                logger.info("تم إنشاء المتصفح بنجاح باستخدام المحاولة الثالثة")
                return browser
            except Exception as e3:
                logger.error(f"فشلت جميع محاولات إنشاء المتصفح: {e3}")
                return None

# تنفيذ رشق متابعين قنوات تيليجرام
def boost_telegram_channel_followers(target_link):
    """
    تنفيذ رشق متابعين لقناة تيليجرام
    
    Args:
        target_link: رابط القناة
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    browser = create_browser()
    if not browser:
        return False
    
    try:
        # فتح رابط القناة
        browser.get(target_link)
        
        # انتظار ظهور زر الاشتراك
        join_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Join') or contains(text(), 'Subscribe') or contains(text(), 'اشترك')]"))
        )
        
        # النقر على زر الاشتراك
        join_button.click()
        
        # انتظار عشوائي لتجنب الاكتشاف
        time.sleep(random.uniform(2, 5))
        
        # التحقق من نجاح الاشتراك
        try:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Unsubscribe') or contains(text(), 'Leave') or contains(text(), 'إلغاء الاشتراك')]"))
            )
            logger.info(f"تم الاشتراك بنجاح في القناة: {target_link}")
            return True
        except TimeoutException:
            logger.warning(f"لم يتم التأكد من نجاح الاشتراك في القناة: {target_link}")
            return False
    
    except Exception as e:
        logger.error(f"خطأ في رشق متابعين القناة: {e}")
        return False
    
    finally:
        browser.quit()

# تنفيذ رشق مشاهدات منشورات تيليجرام
def boost_telegram_post_views(target_link):
    """
    تنفيذ رشق مشاهدات لمنشور تيليجرام
    
    Args:
        target_link: رابط المنشور
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    browser = create_browser()
    if not browser:
        return False
    
    try:
        # فتح رابط المنشور
        browser.get(target_link)
        
        # انتظار تحميل المنشور
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tgme_widget_message_text"))
        )
        
        # التمرير لأسفل لضمان تحميل المنشور بالكامل
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # انتظار عشوائي لزيادة وقت المشاهدة
        time.sleep(random.uniform(5, 15))
        
        logger.info(f"تمت مشاهدة المنشور بنجاح: {target_link}")
        return True
    
    except Exception as e:
        logger.error(f"خطأ في رشق مشاهدات المنشور: {e}")
        return False
    
    finally:
        browser.quit()

# تنفيذ رشق إعجابات منشورات تيليجرام
def boost_telegram_post_likes(target_link):
    """
    تنفيذ رشق إعجابات لمنشور تيليجرام
    
    Args:
        target_link: رابط المنشور
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    browser = create_browser()
    if not browser:
        return False
    
    try:
        # فتح رابط المنشور
        browser.get(target_link)
        
        # انتظار ظهور زر الإعجاب
        like_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tgme_widget_message_like_button"))
        )
        
        # النقر على زر الإعجاب
        like_button.click()
        
        # انتظار عشوائي
        time.sleep(random.uniform(1, 3))
        
        # التحقق من نجاح الإعجاب
        try:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tgme_widget_message_like_button.active"))
            )
            logger.info(f"تم الإعجاب بالمنشور بنجاح: {target_link}")
            return True
        except TimeoutException:
            logger.warning(f"لم يتم التأكد من نجاح الإعجاب بالمنشور: {target_link}")
            return False
    
    except Exception as e:
        logger.error(f"خطأ في رشق إعجابات المنشور: {e}")
        return False
    
    finally:
        browser.quit()

# تنفيذ رشق روابط إحالة بوتات تيليجرام
def boost_telegram_bot_referrals(target_link):
    """
    تنفيذ رشق روابط إحالة لبوت تيليجرام
    
    Args:
        target_link: رابط البوت مع معرف الإحالة
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    browser = create_browser()
    if not browser:
        return False
    
    try:
        # فتح رابط البوت
        browser.get(target_link)
        
        # انتظار ظهور زر البدء
        start_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Send Message') or contains(text(), 'Start') or contains(text(), 'إرسال رسالة') or contains(text(), 'ابدأ')]"))
        )
        
        # النقر على زر البدء
        start_button.click()
        
        # انتظار عشوائي
        time.sleep(random.uniform(2, 5))
        
        logger.info(f"تم النقر على رابط الإحالة بنجاح: {target_link}")
        return True
    
    except Exception as e:
        logger.error(f"خطأ في رشق رابط الإحالة: {e}")
        return False
    
    finally:
        browser.quit()

# تنفيذ رشق مشاهدات تيك توك
def boost_tiktok_views(target_link):
    """
    تنفيذ رشق مشاهدات لفيديو تيك توك
    
    Args:
        target_link: رابط فيديو تيك توك
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    browser = create_browser()
    if not browser:
        return False
    
    try:
        # فتح رابط الفيديو
        browser.get(target_link)
        
        # انتظار تحميل الفيديو
        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        
        # التمرير لأسفل لضمان تشغيل الفيديو
        browser.execute_script("window.scrollTo(0, 100);")
        
        # انتظار لمدة كافية لاحتساب المشاهدة (15-30 ثانية)
        view_time = random.uniform(15, 30)
        time.sleep(view_time)
        
        logger.info(f"تمت مشاهدة فيديو تيك توك بنجاح لمدة {view_time:.1f} ثانية: {target_link}")
        return True
    
    except Exception as e:
        logger.error(f"خطأ في رشق مشاهدات تيك توك: {e}")
        return False
    
    finally:
        browser.quit()

# تنفيذ رشق متعدد باستخدام مجموعة من المتصفحات
async def execute_multiple_boosts(boost_function, target_link, quantity):
    """
    تنفيذ رشق متعدد باستخدام مجموعة من المتصفحات
    
    Args:
        boost_function: دالة الرشق المطلوب تنفيذها
        target_link: الرابط المستهدف
        quantity: عدد عمليات الرشق المطلوبة
    
    Returns:
        int: عدد عمليات الرشق الناجحة
    """
    successful_boosts = 0
    
    # تقليل عدد العمليات المتزامنة في بيئة Railway لتوفير الموارد
    max_workers = min(MAX_CONCURRENT_BROWSERS, 2)
    logger.info(f"تنفيذ عمليات الرشق باستخدام {max_workers} متصفح متزامن")
    
    # تقسيم العمليات إلى مجموعات للتنفيذ المتوازي
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # إنشاء قائمة المهام
        tasks = [executor.submit(boost_function, target_link) for _ in range(quantity)]
        
        # معالجة النتائج
        for i, future in enumerate(tasks):
            try:
                result = future.result()
                if result:
                    successful_boosts += 1
                
                # تحديث التقدم كل 5 عمليات
                if (i + 1) % 5 == 0 or i == len(tasks) - 1:
                    logger.info(f"تم تنفيذ {i + 1}/{quantity} من عمليات الرشق، نجح منها: {successful_boosts}")
                
                # إضافة تأخير عشوائي بين العمليات لتجنب الاكتشاف
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                logger.error(f"خطأ في تنفيذ عملية الرشق رقم {i + 1}: {e}")
    
    return successful_boosts

# قاموس لتحديد دالة الرشق المناسبة لكل نوع خدمة
BOOST_FUNCTIONS = {
    "channel_followers": boost_telegram_channel_followers,
    "post_views": boost_telegram_post_views,
    "post_likes": boost_telegram_post_likes,
    "bot_referrals": boost_telegram_bot_referrals,
    "tiktok_views": boost_tiktok_views,
}

# الدالة الرئيسية للرشق
async def boost_service(service_type, target_link, quantity):
    """
    تنفيذ رشق لخدمة معينة
    
    Args:
        service_type: نوع الخدمة
        target_link: الرابط المستهدف
        quantity: عدد عمليات الرشق المطلوبة
    
    Returns:
        int: عدد عمليات الرشق الناجحة
    """
    if service_type not in BOOST_FUNCTIONS:
        logger.error(f"نوع الخدمة غير مدعوم: {service_type}")
        return 0
    
    boost_function = BOOST_FUNCTIONS[service_type]
    logger.info(f"بدء تنفيذ {quantity} عملية رشق لـ {service_type}: {target_link}")
    
    successful_boosts = await execute_multiple_boosts(boost_function, target_link, quantity)
    
    logger.info(f"اكتمل تنفيذ عمليات الرشق لـ {service_type}: {target_link}")
    logger.info(f"إجمالي العمليات: {quantity}, الناجحة: {successful_boosts}")
    
    return successful_boosts
