from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from config import db_config
import random
import re
import hashlib
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
import os
import string

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def validate_phone(phone):
    """Валидация номера телефона"""
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    patterns = [
        r'^\+7\d{10}$',
        r'^8\d{10}$',
        r'^7\d{10}$',
        r'^9\d{9}$'
    ]
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False

def validate_email(email):
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Проверка сложности пароля (по условию: 9 символов, буквы, цифры, спецсимволы)"""
    if len(password) < 9:
        return False, "Пароль должен содержать минимум 9 символов"
    if not re.search(r'[A-Za-z]', password):
        return False, "Пароль должен содержать буквы"
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифры"
    if not re.search(r'[!@#$%^&*(),.?":{}|_\-+=]', password):
        return False, "Пароль должен содержать спецсимволы (!@#$%^&* и т.д.)"
    if re.search(r'(password|123456|qwerty|admin)', password.lower()):
        return False, "Пароль слишком простой"
    return True, "OK"

# Хранилище для отслеживания попыток входа (Brute Force защита)
failed_attempts = {}
# Хранилище для отслеживания попыток входа (Brute Force защита)
failed_attempts = {}

def check_bruteforce(ip):
    """
    Проверка на Brute Force атаку.
    Возвращает (можно_продолжить, время_ожидания)
    """
    current_time = time.time()
    
    if ip not in failed_attempts:
        return True, 0
    
    attempts_data = failed_attempts[ip]
    blocked_until = attempts_data.get('blocked_until', 0)
    
    # Если время блокировки еще не прошло
    if blocked_until > current_time:
        remaining = int(blocked_until - current_time)
        return False, remaining
    
    # Блокировка прошла - ничего не делаем, просто разрешаем
    return True, 0

def register_failed_attempt(ip):
    """
    Регистрирует НЕУДАЧНУЮ ПОПЫТКУ ВХОДА (только при нажатии кнопки "Войти")
    """
    current_time = time.time()
    
    if ip in failed_attempts:
        failed_attempts[ip]['count'] += 1
        attempts = failed_attempts[ip]['count']
    else:
        failed_attempts[ip] = {'count': 1}
        attempts = 1
    
    # Определяем задержку в зависимости от количества попыток
    if attempts >= 10:
        delay = 15
    elif attempts >= 5:
        delay = 10
    elif attempts >= 3:
        delay = 5
    else:
        delay = 0
    
    # Применяем блокировку
    if delay > 0:
        failed_attempts[ip]['blocked_until'] = current_time + delay
    else:
        failed_attempts[ip]['blocked_until'] = 0
    
    # Сохраняем время последней попытки
    failed_attempts[ip]['last_attempt'] = current_time
    
    print(f"DEBUG: IP {ip} - неудачная попытка #{attempts}, задержка {delay} сек")
    
    return delay

def reset_bruteforce(ip):
    """Сбрасывает счетчик после УСПЕШНОГО входа"""
    if ip in failed_attempts:
        print(f"DEBUG: IP {ip} - успешный вход, сброс счетчика")
        del failed_attempts[ip]

def get_attempts_info(ip):
    """Возвращает информацию о попытках"""
    if ip not in failed_attempts:
        return {'count': 0, 'blocked_until': 0, 'is_blocked': False, 'remaining': 0}
    
    data = failed_attempts[ip]
    current_time = time.time()
    blocked_until = data.get('blocked_until', 0)
    is_blocked = blocked_until > current_time
    
    return {
        'count': data['count'],
        'blocked_until': blocked_until,
        'is_blocked': is_blocked,
        'remaining': max(0, int(blocked_until - current_time)) if is_blocked else 0
    }

def cleanup_old_attempts():
    """Очищает старые записи (раз в час)"""
    current_time = time.time()
    to_delete = []
    for ip, data in failed_attempts.items():
        last_attempt = data.get('last_attempt', 0)
        # Удаляем записи старше 1 часа
        if current_time - last_attempt > 3600:
            to_delete.append(ip)
    
    for ip in to_delete:
        del failed_attempts[ip]

# Остальные функции (капча, хеширование и т.д.) остаются без изменений
def generate_random_captcha_text(length=5):
    """Генерирует случайный текст для капчи"""
    letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    digits = '23456789'
    all_chars = letters + digits
    captcha_text = ''.join(random.choice(all_chars) for _ in range(length))
    return captcha_text

def add_noise_to_image(image, intensity=1000):
    """Добавляет шум на изображение"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for _ in range(intensity):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point((x, y), fill=color)
    return image

def add_random_lines(image, num_lines=10):
    """Добавляет случайные линии на изображение"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for _ in range(num_lines):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 3))
    return image

def distort_text_position(chars, base_x, base_y, step):
    """Искажает позиции символов"""
    positions = []
    for i, char in enumerate(chars):
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-8, 8)
        x = base_x + (i * step) + x_offset
        y = base_y + y_offset
        positions.append((x, y, char))
    return positions

def generate_captcha_image():
    """Генерирует капчу в виде изображения с полностью случайным текстом."""
    captcha_length = random.randint(5, 7)
    captcha_text = generate_random_captcha_text(captcha_length)
    session['captcha_text'] = captcha_text
    
    width = 50 + (7 * 25)
    height = 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        fonts = []
        try:
            fonts.append(ImageFont.truetype("arial.ttf", random.randint(32, 40)))
            fonts.append(ImageFont.truetype("arialbd.ttf", random.randint(32, 40)))
        except:
            pass
        if not fonts:
            try:
                fonts.append(ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", random.randint(32, 40)))
                fonts.append(ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", random.randint(32, 40)))
            except:
                fonts.append(ImageFont.load_default())
    except:
        fonts = [ImageFont.load_default()]
    
    bg_color = (random.randint(230, 255), random.randint(230, 255), random.randint(230, 255))
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    for _ in range(random.randint(8, 15)):
        shape_type = random.choice(['rectangle', 'ellipse'])
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(x1, width)
        y2 = random.randint(y1, height)
        color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        if shape_type == 'rectangle':
            draw.rectangle([(x1, y1), (x2, y2)], fill=color)
        else:
            draw.ellipse([(x1, y1), (x2, y2)], fill=color)
    
    image = add_noise_to_image(image, random.randint(1000, 1500))
    image = add_random_lines(image, random.randint(8, 15))
    
    base_x = 15
    base_y = 20
    step = width // (captcha_length + 1)
    positions = distort_text_position(captcha_text, base_x, base_y, step)
    
    for i, (x, y, char) in enumerate(positions):
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        font = random.choice(fonts)
        draw.text((x, y), char, fill=color, font=font)
    
    image = add_random_lines(image, random.randint(5, 8))
    
    if random.choice([True, False]):
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 0.9)))
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str, captcha_text

def get_captcha_image():
    """Возвращает капчу как base64 изображение"""
    img_str, text = generate_captcha_image()
    return img_str

def verify_captcha(user_input):
    """Проверяет правильность введенной капчи"""
    expected = session.get('captcha_text', '')
    if 'captcha_text' in session:
        del session['captcha_text']
    if not user_input or not expected:
        return False
    return user_input.upper().strip() == expected.upper().strip()

def hash_password(password):
    """Хеширование пароля"""
    salt = "product_store_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_order_number():
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"