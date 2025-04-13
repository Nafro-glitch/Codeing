#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة قاعدة البيانات لبوت التيليجرام
تحتوي على الدوال المساعدة للتعامل مع قاعدة البيانات
تم تعديلها لتعمل على منصة Railway
"""

import sqlite3
import logging
import os
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # إنشاء جدول المستخدمين
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            credits INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # إنشاء جدول الطلبات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT,
            target_link TEXT,
            quantity INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # إنشاء جدول المعاملات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            transaction_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
        return False

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return sqlite3.connect(DATABASE_PATH)

def register_user(user_id, username, first_name, last_name):
    """تسجيل مستخدم جديد في قاعدة البيانات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, last_name)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في تسجيل المستخدم: {e}")
        return False

def create_order(user_id, service_type, target_link, quantity):
    """إنشاء طلب جديد في قاعدة البيانات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, service_type, target_link, quantity, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, service_type, target_link, quantity, "pending")
        )
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return order_id
    except Exception as e:
        logger.error(f"خطأ في إنشاء الطلب: {e}")
        return None

def get_user_orders(user_id):
    """الحصول على طلبات المستخدم"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        orders = cursor.fetchall()
        conn.close()
        return orders
    except Exception as e:
        logger.error(f"خطأ في استرجاع طلبات المستخدم: {e}")
        return []

def update_order_status(order_id, new_status):
    """تحديث حالة الطلب"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?",
            (new_status, order_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في تحديث حالة الطلب: {e}")
        return False

def get_all_users():
    """الحصول على جميع المستخدمين"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"خطأ في استرجاع المستخدمين: {e}")
        return []

def get_all_pending_orders():
    """الحصول على جميع الطلبات قيد الانتظار"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at ASC"
        )
        orders = cursor.fetchall()
        conn.close()
        return orders
    except Exception as e:
        logger.error(f"خطأ في استرجاع الطلبات قيد الانتظار: {e}")
        return []
