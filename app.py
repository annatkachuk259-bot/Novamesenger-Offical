import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json, os, hashlib, time, threading, base64, wave, webbrowser, glob, io, re
import sounddevice as sd
import numpy as np
import cv2
import mss
import customtkinter as ctk

import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False

SETTINGS_FILE = "settings.json"
SESSION_FILE = "session.json"
VOICES_DIR = "voices"
IMAGES_DIR = "images"
VIDEOS_DIR = "videos"

MAX_VOICE_SECONDS = 60
MAX_SCREEN_SECONDS = 45
MAX_IMAGE_SIDE = 1280
USERNAME_RE = re.compile(r"^[A-Za-z0-9_а-яА-ЯёЁ.-]{3,24}$")

for d in [VOICES_DIR, IMAGES_DIR, VIDEOS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

THEMES = {
    "dark": {
        "bg": "#13131a", "fg": "#e1e1e6", "entry_bg": "#1c1c24",
        "accent": "#00afff", "sidebar": "#181820", "bubble_mine": "#007acc",
        "bubble_other": "#22222f", "card_bg": "#1c1c24", "header": "#181820",
        "active_tab": "#1f293a", "active_text": "#ffffff", "muted": "#8e8ea0"
    },
    "light": {
        "bg": "#f5f5f7", "fg": "#1d1d1f", "entry_bg": "#ffffff",
        "accent": "#0066cc", "sidebar": "#e8e8ed", "bubble_mine": "#007aff",
        "bubble_other": "#e5e5ea", "card_bg": "#ffffff", "header": "#e5e5ea",
        "active_tab": "#d0e4ff", "active_text": "#004499", "muted": "#666670"
    }
}

LANGUAGE_REGISTRY = {
    "ru": "Русский",
    "en": "English",
    "bg": "Български",
    "de": "Deutsch",
    "es": "Español",
}

LANGUAGES = {
    "ru": {
        "chats": "Чаты", "notes": "Заметки", "profile": "Профиль", "updates": "Обновления",
        "settings": "Настройки", "about_app": "О приложении", "about_desc": "Nova Messenger — десктопный клиент на Python и CustomTkinter с облачной синхронизацией через Firebase.", "signpath_info": "Проект распространяется с открытым исходным кодом.",
        "support": "💬 Техподдержка", "support_title": "Центр поддержки Nova Messenger", "support_desc": "К сожалению, сейчас мы не можем сюда его добавить, но вы можете перейти по ссылке и открыть в телеграме", "support_btn": "Открыть в Telegram",
        "auth_title": "Nova Messenger Pro - Вход", "username": "Имя пользователя", "password": "Пароль", "login": "Войти",
        "register": "Регистрация", "logout": "Выход", "new_chat": "+ Новый чат", "general_chat": "🟢 Общий чат",
        "send": "Отправить", "theme": "Тема", "dark": "Тёмная", "light": "Светлая",
        "save": "Сохранить", "dialogs": "Диалоги", "admin": "👑 Админка", "error": "Ошибка",
        "warning": "Внимание", "success": "Успех", "fill_fields": "Заполните все поля!", "invalid_credentials": "Неверный логин или пароль!",
        "user_exists": "Такой пользователь уже существует!", "connection_error": "Ошибка соединения: ", "about_me": "О себе (Bio):", "avatar_path": "Путь или Base64 аватара:",
        "profile_updated": "Профиль успешно обновлен!", "add": "Добавить", "delete": "Удалить", "select_chat_left": "Выберите чат слева",
        "delete_chat_q": "Удалить чат с пользователем ", "delete_chat_title": "Удалить чат", "new_chat_title": "Новый чат", "new_chat_prompt": "Введите имя пользователя или 'general' для общего чата:",
        "self_chat_err": "Нельзя создать чат с самим собой!", "user_not_found": "Пользователь не найден!", "leave_chat_q": "Покинуть общий чат? Новые сообщения перестанут вам приходить до повторного входа.", "leave_chat_title": "Общий чат",
        "listen_voice": "▶ Слушать голос", "save_screen_rec": "🎥 Скачать запись экрана: ", "edit": "Редактировать", "info": "Информация",
        "edit_title": "Редактирование", "edit_prompt": "Введите новый текст сообщения:", "delete_msg_q": "Удалить это сообщение?", "delete_msg_title": "Удаление",
        "updates_center": "🚀 Центр обновлений Nova Messenger", "current_version": "Текущая версия: v", "check_updates": "Проверить обновления", "checking_server": "Проверка обновлений с сервера...",
        "server_err": "Не удалось связаться с сервером обновлений.", "no_connection": "Не удалось проверить обновления (нет связи с сервером).", "new_version_available": "🎉 Доступна новая версия: v", "download_update": "Скачать обновление",
        "latest_version_installed": "✓ У вас установлена актуальная версия приложения.", "latest_version_info": "У вас установлена самая последняя версия!", "admin_panel": "👑 Панель Администратора", "total_users": "Всего пользователей в системе: ",
        "clear_db_msgs": "Очистить все сообщения в базе", "admin_del_user": "Удалить пользователя ", "admin_clear_q": "Очистить все сообщения и чаты в облаке?", "db_cleared": "База сообщений очищена.",
        "notes_count": "📝 Заметок: ", "active_chats_count": "  |  💬 Активных личных чатов: ", "typing": " печатает...", "img_load_err": "[Ошибка загрузки фото]",
        "video_saved": "Запись экрана сохранена в:\n", "save_file_err": "Не удалось сохранить файл: ", "search_placeholder": "Поиск по чатам и сообщениям...", "scroll_down": "↓ Вниз",
        "hotkey_hint": "Enter — отправить, Ctrl+Enter — новая строка", "voice_limit": "Достигнут лимит записи голоса (60 сек). Запись сохранена.", "screen_limit": "Достигнут лимит записи экрана (45 сек). Запись сохранена.", "change_username_title": "Сменить имя пользователя",
        "new_username_label": "Новое имя пользователя (3–24 символа):", "change_username_btn": "Сменить имя", "invalid_username": "Имя должно быть от 3 до 24 символов (буквы, цифры, '.', '_', '-').", "same_username_err": "Это уже ваше текущее имя пользователя.",
        "username_changed": "Имя пользователя успешно изменено на ", "chat_with_prefix": "Чат с: ", "leave_general_btn": "🚪 Покинуть чат"
    },
    "en": {
        "chats": "Chats", "notes": "Notes", "profile": "Profile", "updates": "Updates",
        "settings": "Settings", "about_app": "About", "about_desc": "Nova Messenger — a desktop client built with Python and CustomTkinter with Firebase cloud sync.", "signpath_info": "Released as open-source software.",
        "support": "💬 Support", "support_title": "Nova Messenger Support Center", "support_desc": "Unfortunately, we cannot add it here right now, but you can follow the link and open it in Telegram", "support_btn": "Open in Telegram",
        "auth_title": "Nova Messenger Pro - Auth", "username": "Username", "password": "Password", "login": "Login",
        "register": "Register", "logout": "Logout", "new_chat": "+ New Chat", "general_chat": "🟢 General Chat",
        "send": "Send", "theme": "Theme", "dark": "Dark", "light": "Light",
        "save": "Save", "dialogs": "Dialogs", "admin": "👑 Admin", "error": "Error",
        "warning": "Warning", "success": "Success", "fill_fields": "Please fill in all fields!", "invalid_credentials": "Invalid username or password!",
        "user_exists": "User already exists!", "connection_error": "Connection error: ", "about_me": "Bio:", "avatar_path": "Avatar path or Base64:",
        "profile_updated": "Profile successfully updated!", "add": "Add", "delete": "Delete", "select_chat_left": "Select a chat on the left",
        "delete_chat_q": "Delete chat with user ", "delete_chat_title": "Delete Chat", "new_chat_title": "New Chat", "new_chat_prompt": "Enter username or 'general' for general chat:",
        "self_chat_err": "You cannot create a chat with yourself!", "user_not_found": "User not found!", "leave_chat_q": "Leave general chat? You will stop receiving new messages until you rejoin.", "leave_chat_title": "General Chat",
        "listen_voice": "▶ Play Voice", "save_screen_rec": "🎥 Download Screen Recording: ", "edit": "Edit", "info": "Info",
        "edit_title": "Edit Message", "edit_prompt": "Enter new message text:", "delete_msg_q": "Delete this message?", "delete_msg_title": "Delete",
        "updates_center": "🚀 Nova Messenger Update Center", "current_version": "Current Version: v", "check_updates": "Check for Updates", "checking_server": "Checking updates from server...",
        "server_err": "Failed to connect to update server.", "no_connection": "Could not check for updates (no connection).", "new_version_available": "🎉 New version available: v", "download_update": "Download Update",
        "latest_version_installed": "✓ You have the latest version installed.", "latest_version_info": "You are using the latest version!", "admin_panel": "👑 Admin Panel", "total_users": "Total users in system: ",
        "clear_db_msgs": "Clear All Messages in DB", "admin_del_user": "Delete user ", "admin_clear_q": "Clear all messages and chats in the cloud?", "db_cleared": "Message database cleared.",
        "notes_count": "📝 Notes: ", "active_chats_count": "  |  💬 Active Private Chats: ", "typing": " is typing...", "img_load_err": "[Image loading error]",
        "video_saved": "Screen recording saved to:\n", "save_file_err": "Failed to save file: ", "search_placeholder": "Search chats and messages...", "scroll_down": "↓ Down",
        "hotkey_hint": "Enter — send, Ctrl+Enter — new line", "voice_limit": "Voice recording limit reached (60s). Saved.", "screen_limit": "Screen recording limit reached (45s). Saved.", "change_username_title": "Change Username",
        "new_username_label": "New username (3–24 chars):", "change_username_btn": "Change Username", "invalid_username": "Username must be 3–24 chars (letters, digits, '.', '_', '-').", "same_username_err": "This is already your current username.",
        "username_changed": "Username successfully changed to ", "chat_with_prefix": "Chat with: ", "leave_general_btn": "🚪 Leave chat"
    },
    "bg": {
        "chats": "Чатове", "notes": "Бележки", "profile": "Профил", "updates": "Актуализации",
        "settings": "Настройки", "about_app": "За приложението", "about_desc": "Nova Messenger — десктоп клиент с Python и CustomTkinter с облачна синхронизация чрез Firebase.", "signpath_info": "Проектът се разпространява с отворен код.",
        "support": "💬 Поддръжка", "support_title": "Център за поддръжка на Nova Messenger", "support_desc": "За съжаление в момента не можем да го добавим тук, но можете да отворите връзката в Telegram", "support_btn": "Отвори в Telegram",
        "auth_title": "Nova Messenger Pro - Вход", "username": "Потребителско име", "password": "Парола", "login": "Вход",
        "register": "Регистрация", "logout": "Изход", "new_chat": "+ Нов чат", "general_chat": "🟢 Общ чат",
        "chat_with_prefix": "Чат с: ", "leave_general_btn": "🚪 Напусни чата", "send": "Изпрати", "theme": "Тема",
        "dark": "Тъмна", "light": "Светла", "save": "Запази", "dialogs": "Диалози",
        "admin": "👑 Админ", "error": "Грешка", "warning": "Внимание", "success": "Успех",
        "fill_fields": "Моля, попълнете всички полета!", "invalid_credentials": "Невалидно потребителско име или парола!", "user_exists": "Такъв потребител вече съществува!", "connection_error": "Грешка при свързване: ",
        "about_me": "За мен (Bio):", "avatar_path": "Път или Base64 на аватара:", "profile_updated": "Профилът е обновен успешно!", "add": "Добави",
        "delete": "Изтрий", "select_chat_left": "Изберете чат отляво", "delete_chat_q": "Да се изтрие ли чатът с потребител ", "delete_chat_title": "Изтриване на чат",
        "new_chat_title": "Нов чат", "new_chat_prompt": "Въведете потребителско име или 'general' за общия чат:", "self_chat_err": "Не можете да създадете чат със себе си!", "user_not_found": "Потребителят не е намерен!",
        "leave_chat_q": "Да се напусне ли общият чат? Няма да получавате нови съобщения, докато не се върнете.", "leave_chat_title": "Общ чат", "listen_voice": "▶ Слушай гласово", "save_screen_rec": "🎥 Запази запис на екрана: ",
        "edit": "Редактирай", "info": "Информация", "edit_title": "Редактиране", "edit_prompt": "Въведете нов текст на съобщението:",
        "delete_msg_q": "Да се изтрие ли това съобщение?", "delete_msg_title": "Изтриване", "updates_center": "🚀 Център за актуализации на Nova Messenger", "current_version": "Текуща версия: v",
        "check_updates": "Провери за актуализации", "checking_server": "Проверка за актуализации от сървъра...", "server_err": "Неуспешна връзка със сървъра за актуализации.", "no_connection": "Неуспешна проверка за актуализации (няма връзка).",
        "new_version_available": "🎉 Налична е нова версия: v", "download_update": "Изтегли актуализация", "latest_version_installed": "✓ Използвате актуалната версия на приложението.", "latest_version_info": "Използвате най-новата версия!",
        "admin_panel": "👑 Админ панел", "total_users": "Общо потребители в системата: ", "clear_db_msgs": "Изчисти всички съобщения в базата", "admin_del_user": "Изтриване на потребител ",
        "admin_clear_q": "Да се изчистят ли всички съобщения и чатове в облака?", "db_cleared": "Базата със съобщения е изчистена.", "notes_count": "📝 Бележки: ", "active_chats_count": "  |  💬 Активни лични чатове: ",
        "typing": " пише...", "img_load_err": "[Грешка при зареждане на снимка]", "video_saved": "Записът на екрана е запазен в:\n", "save_file_err": "Неуспешно запазване на файл: ",
        "search_placeholder": "Търсене в чатове и съобщения...", "scroll_down": "↓ Надолу", "hotkey_hint": "Enter — изпрати, Ctrl+Enter — нов ред", "voice_limit": "Достигнат е лимитът за гласов запис (60 сек). Записът е запазен.",
        "screen_limit": "Достигнат е лимитът за запис на екрана (45 сек). Записът е запазен.", "change_username_title": "Смяна на потребителско име", "new_username_label": "Ново потребителско име (3–24 символа):", "change_username_btn": "Смени името",
        "invalid_username": "Името трябва да е от 3 до 24 символа (букви, цифри, '.', '_', '-').", "same_username_err": "Това вече е текущото ви потребителско име.", "username_changed": "Потребителското име е променено на "
    },
    "de": {
        "chats": "Chats", "notes": "Notizen", "profile": "Profil", "updates": "Updates",
        "settings": "Einstellungen", "about_app": "Über die App", "about_desc": "Nova Messenger — ein Desktop-Client mit Python und CustomTkinter sowie Cloud-Sync über Firebase.", "signpath_info": "Open-Source-Projekt.",
        "support": "💬 Support", "support_title": "Nova Messenger Support-Center", "support_desc": "Leider können wir den Support hier gerade nicht direkt einbinden, aber du kannst den Link öffnen und in Telegram starten", "support_btn": "In Telegram öffnen",
        "auth_title": "Nova Messenger Pro - Login", "username": "Benutzername", "password": "Passwort", "login": "Anmelden",
        "register": "Registrieren", "logout": "Abmelden", "new_chat": "+ Neuer Chat", "general_chat": "🟢 Allgemeiner Chat",
        "chat_with_prefix": "Chat mit: ", "leave_general_btn": "🚪 Chat verlassen", "send": "Senden", "theme": "Design",
        "dark": "Dunkel", "light": "Hell", "save": "Speichern", "dialogs": "Dialoge",
        "admin": "👑 Admin", "error": "Fehler", "warning": "Warnung", "success": "Erfolg",
        "fill_fields": "Bitte alle Felder ausfüllen!", "invalid_credentials": "Ungültiger Benutzername oder Passwort!", "user_exists": "Benutzer existiert bereits!", "connection_error": "Verbindungsfehler: ",
        "about_me": "Über mich (Bio):", "avatar_path": "Avatar-Pfad oder Base64:", "profile_updated": "Profil erfolgreich aktualisiert!", "add": "Hinzufügen",
        "delete": "Löschen", "select_chat_left": "Wähle links einen Chat aus", "delete_chat_q": "Chat mit Benutzer löschen: ", "delete_chat_title": "Chat löschen",
        "new_chat_title": "Neuer Chat", "new_chat_prompt": "Benutzername oder 'general' für den allgemeinen Chat eingeben:", "self_chat_err": "Du kannst keinen Chat mit dir selbst erstellen!", "user_not_found": "Benutzer nicht gefunden!",
        "leave_chat_q": "Allgemeinen Chat verlassen? Neue Nachrichten kommen erst nach erneutem Beitritt an.", "leave_chat_title": "Allgemeiner Chat", "listen_voice": "▶ Sprachnachricht abspielen", "save_screen_rec": "🎥 Bildschirmaufnahme speichern: ",
        "edit": "Bearbeiten", "info": "Info", "edit_title": "Nachricht bearbeiten", "edit_prompt": "Neuen Nachrichtentext eingeben:",
        "delete_msg_q": "Diese Nachricht löschen?", "delete_msg_title": "Löschen", "updates_center": "🚀 Nova Messenger Update-Center", "current_version": "Aktuelle Version: v",
        "check_updates": "Nach Updates suchen", "checking_server": "Suche nach Updates auf dem Server...", "server_err": "Verbindung zum Update-Server fehlgeschlagen.", "no_connection": "Updates konnten nicht geprüft werden (keine Verbindung).",
        "new_version_available": "🎉 Neue Version verfügbar: v", "download_update": "Update herunterladen", "latest_version_installed": "✓ Du verwendest die aktuelle Version der App.", "latest_version_info": "Du verwendest bereits die neueste Version!",
        "admin_panel": "👑 Admin-Bereich", "total_users": "Nutzer insgesamt im System: ", "clear_db_msgs": "Alle Nachrichten in der DB löschen", "admin_del_user": "Benutzer löschen: ",
        "admin_clear_q": "Alle Nachrichten und Chats in der Cloud löschen?", "db_cleared": "Nachrichtendatenbank geleert.", "notes_count": "📝 Notizen: ", "active_chats_count": "  |  💬 Aktive private Chats: ",
        "typing": " schreibt...", "img_load_err": "[Fehler beim Laden des Bildes]", "video_saved": "Bildschirmaufnahme gespeichert unter:\n", "save_file_err": "Datei konnte nicht gespeichert werden: ",
        "search_placeholder": "Chats und Nachrichten durchsuchen...", "scroll_down": "↓ Nach unten", "hotkey_hint": "Enter — senden, Strg+Enter — neue Zeile", "voice_limit": "Sprachlimit erreicht (60 Sek.). Gespeichert.",
        "screen_limit": "Bildschirmlimit erreicht (45 Sek.). Gespeichert.", "change_username_title": "Benutzernamen ändern", "new_username_label": "Neuer Benutzername (3–24 Zeichen):", "change_username_btn": "Namen ändern",
        "invalid_username": "Name muss 3–24 Zeichen haben (Buchstaben, Ziffern, '.', '_', '-').", "same_username_err": "Das ist bereits dein aktueller Benutzername.", "username_changed": "Benutzername erfolgreich geändert in "
    },
    "es": {
        "chats": "Chats", "notes": "Notas", "profile": "Perfil", "updates": "Actualizaciones",
        "settings": "Ajustes", "about_app": "Acerca de", "about_desc": "Nova Messenger — un cliente de escritorio en Python y CustomTkinter con sincronización en la nube mediante Firebase.", "signpath_info": "Proyecto de código abierto.",
        "support": "💬 Soporte", "support_title": "Centro de soporte de Nova Messenger", "support_desc": "Por desgracia, ahora no podemos añadirlo aquí, pero puedes ir al enlace y abrirlo en Telegram", "support_btn": "Abrir en Telegram",
        "auth_title": "Nova Messenger Pro - Iniciar sesión", "username": "Usuario", "password": "Contraseña", "login": "Entrar",
        "register": "Registrarse", "logout": "Cerrar sesión", "new_chat": "+ Nuevo chat", "general_chat": "🟢 Chat general",
        "chat_with_prefix": "Chat con: ", "leave_general_btn": "🚪 Salir del chat", "send": "Enviar", "theme": "Tema",
        "dark": "Oscuro", "light": "Claro", "save": "Guardar", "dialogs": "Diálogos",
        "admin": "👑 Admin", "error": "Error", "warning": "Aviso", "success": "Éxito",
        "fill_fields": "¡Rellena todos los campos!", "invalid_credentials": "¡Usuario o contraseña incorrectos!", "user_exists": "¡Ese usuario ya existe!", "connection_error": "Error de conexión: ",
        "about_me": "Sobre mí (Bio):", "avatar_path": "Ruta o Base64 del avatar:", "profile_updated": "¡Perfil actualizado con éxito!", "add": "Añadir",
        "delete": "Eliminar", "select_chat_left": "Selecciona un chat a la izquierda", "delete_chat_q": "¿Eliminar el chat con el usuario ", "delete_chat_title": "Eliminar chat",
        "new_chat_title": "Nuevo chat", "new_chat_prompt": "Introduce el nombre de usuario o 'general' para el chat general:", "self_chat_err": "¡No puedes crear un chat contigo mismo!", "user_not_found": "¡Usuario no encontrado!",
        "leave_chat_q": "¿Salir del chat general? Dejarás de recibir mensajes nuevos hasta que vuelvas a entrar.", "leave_chat_title": "Chat general", "listen_voice": "▶ Escuchar audio", "save_screen_rec": "🎥 Descargar grabación de pantalla: ",
        "edit": "Editar", "info": "Información", "edit_title": "Editar", "edit_prompt": "Introduce el nuevo texto del mensaje:",
        "delete_msg_q": "¿Eliminar este mensaje?", "delete_msg_title": "Eliminar", "updates_center": "🚀 Centro de actualizaciones de Nova Messenger", "current_version": "Versión actual: v",
        "check_updates": "Buscar actualizaciones", "checking_server": "Buscando actualizaciones en el servidor...", "server_err": "No se pudo conectar con el servidor de actualizaciones.", "no_connection": "No se pudieron comprobar las actualizaciones (sin conexión).",
        "new_version_available": "🎉 Nueva versión disponible: v", "download_update": "Descargar actualización", "latest_version_installed": "✓ Tienes instalada la versión más reciente de la app.", "latest_version_info": "¡Ya tienes la última versión!",
        "admin_panel": "👑 Panel de administración", "total_users": "Total de usuarios en el sistema: ", "clear_db_msgs": "Borrar todos los mensajes de la BD", "admin_del_user": "Eliminar usuario ",
        "admin_clear_q": "¿Borrar todos los mensajes y chats en la nube?", "db_cleared": "Base de datos de mensajes vaciada.", "notes_count": "📝 Notas: ", "active_chats_count": "  |  💬 Chats privados activos: ",
        "typing": " está escribiendo...", "img_load_err": "[Error al cargar la imagen]", "video_saved": "Grabación de pantalla guardada en:\n", "save_file_err": "No se pudo guardar el archivo: ",
        "search_placeholder": "Buscar en chats y mensajes...", "scroll_down": "↓ Abajo", "hotkey_hint": "Enter — enviar, Ctrl+Enter — nueva línea", "voice_limit": "Límite de grabación de voz alcanzado (60 s). Guardado.",
        "screen_limit": "Límite de grabación de pantalla alcanzado (45 s). Guardado.", "change_username_title": "Cambiar nombre de usuario", "new_username_label": "Nuevo nombre de usuario (3–24 caracteres):", "change_username_btn": "Cambiar nombre",
        "invalid_username": "El nombre debe tener entre 3 y 24 caracteres (letras, números, '.', '_', '-').", "same_username_err": "Ese ya es tu nombre de usuario actual.", "username_changed": "Nombre de usuario cambiado con éxito a "
    }
}

def get_translation(lang_code, key):
    lang_dict = LANGUAGES.get(lang_code) or LANGUAGES["ru"]
    if key in lang_dict:
        return lang_dict[key]
    return LANGUAGES["ru"].get(key, key)

def get_translation(lang_code, key):
    lang_dict = LANGUAGES.get(lang_code) or LANGUAGES["ru"]
    if key in lang_dict:
        return lang_dict[key]
    return LANGUAGES["ru"].get(key, key)

class AppManager:
    def __init__(self):
        self.settings = self.load_settings_local()

    def load_settings_local(self):
        if not os.path.exists(SETTINGS_FILE):
            return {"theme": "dark", "lang": "ru", "font": "Segoe UI"}
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {
                    "theme": data.get("theme", "dark"),
                    "lang": data.get("lang", "ru"),
                    "font": data.get("font", "Segoe UI")
                }
            except Exception:
                return {"theme": "dark", "lang": "ru", "font": "Segoe UI"}

    def save_settings_local(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

manager = AppManager()

class SessionManager:
    @staticmethod
    def save_session(username):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": username}, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_session():
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("username")
            except Exception:
                return None
        return None

    @staticmethod
    def clear_session():
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
            except Exception:
                pass
def render_settings_panel(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(scroll, text=self.t["settings"], text_color=self.colors["fg"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 18))

        pref_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        pref_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(pref_card, text=self.t["theme"], text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(14, 5))
        self.theme_var = tk.StringVar(value=manager.settings.get("theme", "dark"))
        ctk.CTkRadioButton(pref_card, text=self.t["dark"], variable=self.theme_var, value="dark", text_color=self.colors["fg"]).pack(anchor="w", padx=28, pady=2)
        ctk.CTkRadioButton(pref_card, text=self.t["light"], variable=self.theme_var, value="light", text_color=self.colors["fg"]).pack(anchor="w", padx=28, pady=2)

        # --- Выпадающий список языков (вместо кучи кнопок) ---
        ctk.CTkLabel(pref_card, text="Язык / Language", text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(14, 5))
        current_lang = manager.settings.get("lang", "ru")
        if current_lang not in LANGUAGE_REGISTRY:
            current_lang = "ru"

        lang_display_names = list(LANGUAGE_REGISTRY.values())
        self.lang_var = tk.StringVar(value=LANGUAGE_REGISTRY[current_lang])

        ctk.CTkOptionMenu(
            pref_card,
            values=lang_display_names,
            variable=self.lang_var,
            fg_color=self.colors["entry_bg"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent"],
            text_color=self.colors["fg"],
            dropdown_fg_color=self.colors["entry_bg"],
            dropdown_text_color=self.colors["fg"],
            dropdown_hover_color=self.colors["active_tab"],
            corner_radius=8
        ).pack(anchor="w", padx=28, pady=(2, 6))
        # -----------------------------------------------------

        ctk.CTkButton(pref_card, text=self.t["save"], command=self.save_settings_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="w", padx=20, pady=(14, 16))

        updates_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        updates_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(updates_card, text=self.t["updates_center"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(updates_card, text=f"{self.t['current_version']}{self.CURRENT_VERSION} Pro", text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=20, pady=(0, 10))
        ctk.CTkButton(updates_card, text=self.t["check_updates"], command=lambda: self.check_for_updates_threaded(manual=True), fg_color=self.colors["accent"], text_color="white", font=(self.font_family, 11), corner_radius=8).pack(anchor="w", padx=20, pady=(0, 8))

        self.update_result_frame = ctk.CTkFrame(updates_card, fg_color="transparent")
        self.update_result_frame.pack(fill="x", padx=20, pady=(0, 14))
        self.check_for_updates_threaded(manual=False)

        support_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        support_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(support_card, text=self.t["support_title"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 6))
        ctk.CTkLabel(support_card, text=self.t["support_desc"], text_color=self.colors["fg"], font=(self.font_family, 12), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkButton(
            support_card,
            text=self.t["support_btn"],
            command=lambda: webbrowser.open("https://t.me/nova_mesenger_support_bot"),
            fg_color=self.colors["accent"],
            text_color="white",
            corner_radius=8,
            height=36,
            font=(self.font_family, 12, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 16))

        about_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        about_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(about_card, text=self.t["about_app"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 6))
        ctk.CTkLabel(about_card, text=f"Nova Messenger Pro — v{self.CURRENT_VERSION}", text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(0, 4))
        ctk.CTkLabel(about_card, text=self.t["about_desc"], text_color=self.colors["fg"], font=(self.font_family, 11), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 8))
        ctk.CTkLabel(about_card, text=self.t["signpath_info"], text_color="#00ffcc" if manager.settings.get("theme", "dark") == "dark" else "#007755", font=(self.font_family, 11, "bold"), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

def save_settings_action(self):
        manager.settings["theme"] = self.theme_var.get()
        selected_label = self.lang_var.get()
        code_by_display = {v: k for k, v in LANGUAGE_REGISTRY.items()}
        manager.settings["lang"] = code_by_display.get(selected_label, "ru")
        manager.save_settings_local()

        self.setup_styles()
        self.render_navigation()
        self.switch_tab("settings")

class FirebaseDB:
    @staticmethod
    def get_user(username):
        if not FIREBASE_AVAILABLE:
            return None
        doc = db.collection("users").document(username.lower()).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def save_user(username, password_hash):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("users").document(username.lower()).set({
            "username": username,
            "password": password_hash,
            "bio": "Привет! Я использую Nova Messenger.",
            "avatar": ""
        }, merge=True)

    @staticmethod
    def update_user_profile(username, bio, avatar):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("users").document(username.lower()).update({
            "bio": bio,
            "avatar": avatar
        })

    @staticmethod
    def change_username(old_username, new_username):
        old_key = old_username.strip().lower()
        new_key = new_username.strip().lower()
        if not FIREBASE_AVAILABLE:
            return True, None

        if FirebaseDB.get_user(new_key):
            return False, "user_exists"

        old_doc = db.collection("users").document(old_key).get()
        old_data = old_doc.to_dict() if old_doc.exists else {}

        new_payload = {
            "username": new_key,
            "password": old_data.get("password", ""),
            "bio": old_data.get("bio", "Привет! Я использую Nova Messenger."),
            "avatar": old_data.get("avatar", "")
        }
        db.collection("users").document(new_key).set(new_payload, merge=True)

        notes = FirebaseDB.get_notes(old_key)
        if notes:
            FirebaseDB.save_notes(new_key, notes)

        chats = FirebaseDB.get_chats(old_key)
        if chats:
            db.collection("user_chats").document(new_key).set({"chats": chats})

        if FirebaseDB.is_in_general_chat(old_key):
            FirebaseDB.join_general_chat(new_key)

        if old_doc.exists:
            db.collection("users").document(old_key).delete()

        return True, None

    @staticmethod
    def get_all_users():
        if not FIREBASE_AVAILABLE:
            return {}
        docs = db.collection("users").stream()
        return {doc.id: doc.to_dict() for doc in docs}

    @staticmethod
    def delete_user(username):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("users").document(username.lower()).delete()

    @staticmethod
    def get_messages(chat_key):
        if not FIREBASE_AVAILABLE:
            return []
        docs = db.collection("chats").document(chat_key).collection("messages").order_by("timestamp").stream()
        messages = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            messages.append(d)
        return messages

    @staticmethod
    def get_unread_count(chat_key, current_user):
        if not FIREBASE_AVAILABLE:
            return 0
        try:
            ref = db.collection("chats").document(chat_key).collection("messages")
            docs = ref.where(filter=firestore.FieldFilter("user", "!=", current_user))\
                      .where(filter=firestore.FieldFilter("read", "==", False))\
                      .stream()
            return sum(1 for _ in docs)
        except Exception:
            return 0

    @staticmethod
    def add_message(chat_key, msg_data):
        if not FIREBASE_AVAILABLE:
            return
        msg_data["timestamp"] = firestore.SERVER_TIMESTAMP
        db.collection("chats").document(chat_key).collection("messages").add(msg_data)

    @staticmethod
    def update_message(chat_key, msg_id, new_text):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("chats").document(chat_key).collection("messages").document(msg_id).update({"text": new_text})

    @staticmethod
    def delete_message(chat_key, msg_id):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("chats").document(chat_key).collection("messages").document(msg_id).delete()

    @staticmethod
    def clear_all_messages_db():
        if not FIREBASE_AVAILABLE:
            return
        chats = db.collection("chats").stream()
        for chat in chats:
            msgs = db.collection("chats").document(chat.id).collection("messages").stream()
            for m in msgs:
                m.reference.delete()

    @staticmethod
    def delete_entire_chat(chat_key):
        if not FIREBASE_AVAILABLE:
            return
        try:
            msgs_ref = db.collection("chats").document(chat_key).collection("messages")
            for doc in msgs_ref.stream():
                doc.reference.delete()
            db.collection("chats").document(chat_key).delete()
        except Exception:
            pass

    @staticmethod
    def get_notes(username):
        if not FIREBASE_AVAILABLE:
            return []
        doc = db.collection("notes").document(username.lower()).get()
        return doc.to_dict().get("items", []) if doc.exists else []

    @staticmethod
    def save_notes(username, notes_list):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("notes").document(username.lower()).set({"items": notes_list})

    @staticmethod
    def get_chats(username):
        if not FIREBASE_AVAILABLE:
            return []
        doc = db.collection("user_chats").document(username.lower()).get()
        return doc.to_dict().get("chats", []) if doc.exists else []

    @staticmethod
    def add_chat_for(username, target):
        if not FIREBASE_AVAILABLE:
            return
        chats = FirebaseDB.get_chats(username)
        if target not in chats:
            chats.append(target)
            db.collection("user_chats").document(username.lower()).set({"chats": chats})

    @staticmethod
    def remove_chat(username, target):
        if not FIREBASE_AVAILABLE:
            return
        chats = FirebaseDB.get_chats(username)
        if target in chats:
            chats.remove(target)
            db.collection("user_chats").document(username.lower()).set({"chats": chats})

    @staticmethod
    def is_in_general_chat(username):
        if not FIREBASE_AVAILABLE:
            return True
        doc = db.collection("settings_meta").document("general_members").get()
        if not doc.exists:
            return True
        members = doc.to_dict().get("list", [])
        return username.lower() in members

    @staticmethod
    def join_general_chat(username):
        if not FIREBASE_AVAILABLE:
            return
        ref = db.collection("settings_meta").document("general_members")
        doc = ref.get()
        members = doc.to_dict().get("list", []) if doc.exists else []
        if username.lower() not in members:
            members.append(username.lower())
            ref.set({"list": members})

    @staticmethod
    def leave_general_chat(username):
        if not FIREBASE_AVAILABLE:
            return
        ref = db.collection("settings_meta").document("general_members")
        doc = ref.get()
        if doc.exists:
            members = doc.to_dict().get("list", [])
            if username.lower() in members:
                members.remove(username.lower())
                ref.set({"list": members})

    @staticmethod
    def set_typing(chat_key, username):
        if not FIREBASE_AVAILABLE:
            return
        db.collection("typing").document(chat_key).set({"user": username, "time": time.time()})

    @staticmethod
    def get_typing(chat_key):
        if not FIREBASE_AVAILABLE:
            return {}
        doc = db.collection("typing").document(chat_key).get()
        return doc.to_dict() if doc.exists else {}

    @staticmethod
    def mark_read(chat_key, current_user):
        if not FIREBASE_AVAILABLE:
            return
        ref = db.collection("chats").document(chat_key).collection("messages")
        try:
            docs = ref.where(filter=firestore.FieldFilter("user", "!=", current_user))\
                      .where(filter=firestore.FieldFilter("read", "==", False))\
                      .stream()
            for doc in docs:
                doc.reference.update({"read": True})
        except Exception:
            pass

    @staticmethod
    def get_latest_version_info():
        if not FIREBASE_AVAILABLE:
            return None
        doc = db.collection("settings_meta").document("version_info").get()
        return doc.to_dict() if doc.exists else None

class NovaApp:
    CURRENT_VERSION = "1.4"

    def __init__(self, root):
        self.root = root
        self.root.geometry("1040x740")
        self.photo_cache = {}
        self.setup_styles()

        self.active_tab = "chats"
        self.nav_buttons = {}
        self.contact_buttons = {}
        self.unread_counts = {}
        self.general_chat_btn = None
        self.current_chat_target = "general"
        self.current_messages_cache = []
        self.search_query = ""
        self.after_id = None
        self.contacts_after_id = None
        self.last_msg_count = 0
        self.is_recording_voice = False
        self.is_recording_screen = False
        self.voice_start_time = 0
        self.screen_start_time = 0
        self.last_click_time = 0

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        if not FIREBASE_AVAILABLE:
            messagebox.showwarning(self.t["warning"], "Firebase недоступен! Проверьте файл serviceAccountKey.json")

        saved_user = SessionManager.load_session()
        if saved_user and FirebaseDB.get_user(saved_user):
            self.show_main_interface(saved_user)
        else:
            SessionManager.clear_session()
            self.show_auth_window()

    def cleanup_temp_files(self):
        for temp_file in glob.glob(os.path.join(IMAGES_DIR, "temp_*.png")):
            try:
                os.remove(temp_file)
            except Exception:
                pass

    def on_close(self):
        self.is_recording_voice = False
        self.is_recording_screen = False
        self.cancel_chat_polling()
        self.cancel_contacts_polling()
        self.cleanup_temp_files()
        self.root.destroy()

    def setup_styles(self):
        theme_name = manager.settings.get("theme", "dark")
        self.colors = THEMES.get(theme_name, THEMES["dark"])
        self.font_family = manager.settings.get("font", "Segoe UI")
        requested_lang = manager.settings.get("lang", "ru")
        self.lang_code = requested_lang if requested_lang in LANGUAGES else "ru"
        self.t = {key: get_translation(self.lang_code, key) for key in LANGUAGES["ru"]}

        ctk.set_appearance_mode("Dark" if theme_name == "dark" else "Light")
        self.root.configure(fg_color=self.colors["bg"])

    def show_auth_window(self):
        self.cancel_chat_polling()
        self.cancel_contacts_polling()
        SessionManager.clear_session()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_styles()
        self.root.title(self.t["auth_title"])

        bg_frame = ctk.CTkFrame(self.root, fg_color=self.colors["bg"], corner_radius=0)
        bg_frame.pack(fill="both", expand=True)

        card_frame = ctk.CTkFrame(bg_frame, fg_color=self.colors["sidebar"], corner_radius=16, width=380, height=450)
        card_frame.place(relx=0.5, rely=0.5, anchor="center")
        card_frame.pack_propagate(False)

        ctk.CTkLabel(card_frame, text="Nova Messenger", text_color=self.colors["accent"], font=(self.font_family, 20, "bold")).pack(pady=(35, 25))

        ctk.CTkLabel(card_frame, text=self.t["username"], text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=30)
        self.auth_user_entry = ctk.CTkEntry(card_frame, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], border_width=1, corner_radius=8)
        self.auth_user_entry.pack(fill="x", padx=30, pady=(5, 15), ipady=5)

        ctk.CTkLabel(card_frame, text=self.t["password"], text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=30)
        self.auth_pass_entry = ctk.CTkEntry(card_frame, show="*", font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], border_width=1, corner_radius=8)
        self.auth_pass_entry.pack(fill="x", padx=30, pady=(5, 25), ipady=5)

        btn_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.login_btn = ctk.CTkButton(btn_frame, text=self.t["login"], command=self.login_action, fg_color=self.colors["accent"], text_color="white", font=(self.font_family, 11, "bold"), corner_radius=8, height=35)
        self.login_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.reg_btn = ctk.CTkButton(btn_frame, text=self.t["register"], command=self.register_action, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], font=(self.font_family, 11), corner_radius=8, height=35)
        self.reg_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_action(self):
        if time.time() - self.last_click_time < 1.0:
            return
        self.last_click_time = time.time()

        username = self.auth_user_entry.get().strip().lower()
        password_raw = self.auth_pass_entry.get().strip()

        if not username or not password_raw:
            messagebox.showerror(self.t["error"], self.t["fill_fields"])
            return

        password = self.hash_password(password_raw)
        self.login_btn.configure(state="disabled")
        self.reg_btn.configure(state="disabled")

        def background_login():
            try:
                user_data = FirebaseDB.get_user(username)
                if user_data and user_data.get("password") == password:
                    SessionManager.save_session(username)
                    self.root.after(0, lambda: self.show_main_interface(username))
                else:
                    self.root.after(0, lambda: messagebox.showerror(self.t["error"], self.t["invalid_credentials"]))
                    self.root.after(0, lambda: self.login_btn.configure(state="normal"))
                    self.root.after(0, lambda: self.reg_btn.configure(state="normal"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self.t["error"], f"{self.t['connection_error']}{e}"))
                self.root.after(0, lambda: self.login_btn.configure(state="normal"))
                self.root.after(0, lambda: self.reg_btn.configure(state="normal"))

        threading.Thread(target=background_login, daemon=True).start()

    def register_action(self):
        if time.time() - self.last_click_time < 1.0:
            return
        self.last_click_time = time.time()

        username = self.auth_user_entry.get().strip().lower()
        password_raw = self.auth_pass_entry.get().strip()

        if not username or not password_raw:
            messagebox.showerror(self.t["error"], self.t["fill_fields"])
            return

        password = self.hash_password(password_raw)
        self.login_btn.configure(state="disabled")
        self.reg_btn.configure(state="disabled")

        def background_register():
            try:
                if FirebaseDB.get_user(username):
                    self.root.after(0, lambda: messagebox.showerror(self.t["error"], self.t["user_exists"]))
                    self.root.after(0, lambda: self.login_btn.configure(state="normal"))
                    self.root.after(0, lambda: self.reg_btn.configure(state="normal"))
                else:
                    FirebaseDB.save_user(username, password)
                    FirebaseDB.join_general_chat(username)
                    SessionManager.save_session(username)
                    self.root.after(0, lambda: messagebox.showinfo(self.t["success"], self.t["profile_updated"]))
                    self.root.after(0, lambda: self.show_main_interface(username))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self.t["error"], f"{self.t['connection_error']}{e}"))
                self.root.after(0, lambda: self.login_btn.configure(state="normal"))
                self.root.after(0, lambda: self.reg_btn.configure(state="normal"))

        threading.Thread(target=background_register, daemon=True).start()

    def show_main_interface(self, username):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_styles()
        self.current_user = username
        self.root.title(f"Nova Messenger Pro v{self.CURRENT_VERSION} - [{username}]")

        self.sidebar = ctk.CTkFrame(self.root, fg_color=self.colors["sidebar"], width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self.root, fg_color=self.colors["bg"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        self.render_navigation()
        self.switch_tab(self.active_tab or "chats")

    def highlight_active_tab(self):
        for tab_name, btn in self.nav_buttons.items():
            if not btn.winfo_exists():
                continue
            is_selected = tab_name == self.active_tab
            if tab_name == "admin":
                btn.configure(
                    fg_color="#533273" if is_selected else "#332244",
                    text_color="#ffffff" if is_selected else "#ff99ff",
                    font=(self.font_family, 12, "bold")
                )
            else:
                btn.configure(
                    fg_color=self.colors["active_tab"] if is_selected else "transparent",
                    text_color=self.colors["accent"] if is_selected else self.colors["fg"],
                    font=(self.font_family, 12, "bold" if is_selected else "normal")
                )

    def update_chats_nav_label(self):
        btn = self.nav_buttons.get("chats")
        if btn and btn.winfo_exists():
            total_unread = sum(self.unread_counts.values())
            label = f"{self.t['chats']} ({total_unread})" if total_unread > 0 else self.t["chats"]
            btn.configure(text=label)

    def highlight_active_chat(self):
        for uname, btn in self.contact_buttons.items():
            if not btn.winfo_exists():
                continue
            is_selected = uname == self.current_chat_target
            unread = self.unread_counts.get(uname, 0)
            suffix = f" ({unread})" if unread > 0 and not is_selected else ""
            btn.configure(
                text=f"{uname}{suffix}",
                fg_color=self.colors["active_tab"] if is_selected else "transparent",
                text_color=self.colors["accent"] if is_selected else self.colors["fg"],
                font=(self.font_family, 11, "bold" if is_selected or unread > 0 else "normal")
            )

        if self.general_chat_btn and self.general_chat_btn.winfo_exists():
            is_gen_selected = self.current_chat_target == "general"
            unread_gen = self.unread_counts.get("general", 0)
            suffix_gen = f" ({unread_gen})" if unread_gen > 0 and not is_gen_selected else ""
            self.general_chat_btn.configure(
                text=f"{self.t['general_chat']}{suffix_gen}",
                fg_color=self.colors["active_tab"] if is_gen_selected else "transparent",
                text_color=self.colors["active_text"] if is_gen_selected else self.colors["accent"],
                font=(self.font_family, 11, "bold")
            )

    def render_navigation(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.nav_buttons = {}

        tabs = ["chats", "notes", "profile", "settings"]
        names = {
            "chats": self.t["chats"],
            "notes": self.t["notes"],
            "profile": self.t["profile"],
            "settings": self.t["settings"]
        }

        for tab in tabs:
            btn = ctk.CTkButton(
                self.sidebar,
                text=names[tab],
                command=lambda t=tab: self.switch_tab(t),
                fg_color="transparent",
                text_color=self.colors["fg"],
                hover_color=self.colors["entry_bg"],
                font=(self.font_family, 12),
                anchor="w",
                corner_radius=8
            )
            btn.pack(fill="x", padx=15, pady=4, ipady=5)
            self.nav_buttons[tab] = btn

        if self.current_user.lower() in ["никита", "nikita"]:
            admin_btn = ctk.CTkButton(
                self.sidebar,
                text=self.t["admin"],
                command=lambda: self.switch_tab("admin"),
                fg_color="#332244",
                text_color="#ff99ff",
                hover_color="#442a55",
                font=(self.font_family, 12, "bold"),
                anchor="w",
                corner_radius=8
            )
            admin_btn.pack(fill="x", padx=15, pady=4, ipady=5)
            self.nav_buttons["admin"] = admin_btn

        ctk.CTkButton(
            self.sidebar,
            text=self.t["logout"],
            command=self.show_auth_window,
            fg_color="#442222",
            text_color="white",
            hover_color="#552a2a",
            font=(self.font_family, 11),
            anchor="w",
            corner_radius=8
        ).pack(side="bottom", fill="x", padx=15, pady=15, ipady=5)

        self.highlight_active_tab()
        self.update_chats_nav_label()

    def cancel_chat_polling(self):
        if getattr(self, "after_id", None):
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def cancel_contacts_polling(self):
        if getattr(self, "contacts_after_id", None):
            try:
                self.root.after_cancel(self.contacts_after_id)
            except Exception:
                pass
            self.contacts_after_id = None

    def switch_tab(self, tab_name):
        self.cancel_chat_polling()
        self.cancel_contacts_polling()
        for widget in self.content.winfo_children():
            widget.destroy()

        if tab_name == "admin" and self.current_user.lower() not in ["никита", "nikita"]:
            tab_name = "chats"

        self.active_tab = tab_name
        self.highlight_active_tab()

        if tab_name == "notes":
            self.render_notes_panel()
        elif tab_name == "profile":
            self.render_profile_panel()
        elif tab_name == "chats":
            self.render_chats_panel()
        elif tab_name == "settings":
            self.render_settings_panel()
        elif tab_name == "admin":
            self.render_admin_panel()

    def check_for_updates_threaded(self, manual=False):
        for widget in self.update_result_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.update_result_frame, text=self.t["checking_server"], text_color="#888888", font=(self.font_family, 11)).pack(anchor="w")

        def background_check():
            try:
                remote_info = FirebaseDB.get_latest_version_info()
            except Exception:
                remote_info = None
            self.root.after(0, lambda: self.apply_update_result(remote_info, manual))

        threading.Thread(target=background_check, daemon=True).start()

    def apply_update_result(self, remote_info, manual):
        if not hasattr(self, "update_result_frame") or not self.update_result_frame.winfo_exists():
            return
        for widget in self.update_result_frame.winfo_children():
            widget.destroy()

        if not remote_info:
            if manual:
                messagebox.showerror(self.t["error"], self.t["server_err"])
            else:
                ctk.CTkLabel(self.update_result_frame, text=self.t["no_connection"], text_color="#888888", font=(self.font_family, 11)).pack(anchor="w")
            return

        latest_ver = str(remote_info.get("latest_version", self.CURRENT_VERSION))

        def parse_version(v):
            return tuple(map(int, v.split(".")))

        try:
            is_newer = parse_version(latest_ver) > parse_version(self.CURRENT_VERSION)
        except Exception:
            is_newer = latest_ver != self.CURRENT_VERSION

        if is_newer:
            card = ctk.CTkFrame(self.update_result_frame, fg_color="#2d4433", corner_radius=12)
            card.pack(fill="x", padx=0, pady=8)

            ctk.CTkLabel(card, text=f"{self.t['new_version_available']}{latest_ver}!", text_color="#00ffcc", font=(self.font_family, 13, "bold")).pack(anchor="w", padx=18, pady=(12, 4))
            ctk.CTkLabel(card, text=remote_info.get("notes", "Без описания изменений."), text_color="white", font=(self.font_family, 11), justify="left").pack(anchor="w", padx=18, pady=(0, 10))

            if "url" in remote_info and remote_info["url"]:
                ctk.CTkButton(
                    card,
                    text=self.t["download_update"],
                    command=lambda url=remote_info["url"]: webbrowser.open(url),
                    fg_color="#00aa55",
                    text_color="white",
                    corner_radius=8
                ).pack(anchor="w", padx=18, pady=(0, 14))
        else:
            if manual:
                messagebox.showinfo(self.t["updates"], self.t["latest_version_info"])
            else:
                ctk.CTkLabel(self.update_result_frame, text=self.t["latest_version_installed"], text_color="#888888", font=(self.font_family, 11)).pack(anchor="w")

    def render_admin_panel(self):
        admin_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        admin_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(admin_frame, text=self.t["admin_panel"], text_color="#ff77ff", font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 20))

        users = FirebaseDB.get_all_users()
        ctk.CTkLabel(admin_frame, text=f"{self.t['total_users']}{len(users)}", text_color=self.colors["fg"], font=(self.font_family, 12)).pack(anchor="w", pady=5)

        list_frame = ctk.CTkFrame(admin_frame, fg_color=self.colors["entry_bg"], corner_radius=12)
        list_frame.pack(fill="both", expand=True, pady=15)

        for u in users.keys():
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            ctk.CTkLabel(row, text=u, text_color=self.colors["fg"], font=(self.font_family, 12)).pack(side="left")
            if u != self.current_user:
                ctk.CTkButton(row, text=self.t["delete"], command=lambda usr=u: self.admin_delete_user(usr), fg_color="#aa3333", text_color="white", width=80, corner_radius=6).pack(side="right")

        ctk.CTkButton(admin_frame, text=self.t["clear_db_msgs"], command=self.admin_clear_all_msgs, fg_color="#aa5500", text_color="white", corner_radius=8).pack(anchor="w", pady=10)

    def admin_delete_user(self, username):
        if messagebox.askyesno(self.t["admin"], f"{self.t['admin_del_user']}{username}?"):
            FirebaseDB.delete_user(username)
            self.render_admin_panel()

    def admin_clear_all_msgs(self):
        if messagebox.askyesno(self.t["admin"], self.t["admin_clear_q"]):
            FirebaseDB.clear_all_messages_db()
            messagebox.showinfo(self.t["success"], self.t["db_cleared"])

    def render_profile_panel(self):
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(f, text=self.t["profile"], text_color=self.colors["fg"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 16))

        user_data = FirebaseDB.get_user(self.current_user) or {}
        current_bio = user_data.get("bio", "")

        card = ctk.CTkFrame(f, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="x", pady=8)

        ctk.CTkLabel(card, text=f"{self.t['username']}: {self.current_user}", text_color=self.colors["accent"], font=(self.font_family, 14, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        if current_bio:
            ctk.CTkLabel(card, text=current_bio, text_color=self.colors["fg"], font=(self.font_family, 11), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 6))

        notes_count = len(FirebaseDB.get_notes(self.current_user))
        chats_count = len(FirebaseDB.get_chats(self.current_user))
        stats_text = f"{self.t['notes_count']}{notes_count}{self.t['active_chats_count']}{chats_count}"
        ctk.CTkLabel(card, text=stats_text, text_color=self.colors["muted"], font=(self.font_family, 11)).pack(anchor="w", padx=20, pady=(0, 14))

        username_card = ctk.CTkFrame(f, fg_color=self.colors["card_bg"], corner_radius=12)
        username_card.pack(fill="x", pady=10)

        ctk.CTkLabel(username_card, text=self.t["change_username_title"], text_color=self.colors["accent"], font=(self.font_family, 13, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(username_card, text=self.t["new_username_label"], text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=20, pady=(0, 6))

        row = ctk.CTkFrame(username_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 14))

        self.new_username_entry = ctk.CTkEntry(row, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.new_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self.new_username_entry.bind("<Return>", lambda _e: self.change_username_action())

        self.change_username_btn = ctk.CTkButton(row, text=self.t["change_username_btn"], command=self.change_username_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8)
        self.change_username_btn.pack(side="right")

        ctk.CTkLabel(f, text=self.t["about_me"], text_color=self.colors["fg"], font=(self.font_family, 11, "bold")).pack(anchor="w", pady=(12, 5))
        self.profile_bio_entry = ctk.CTkEntry(f, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.profile_bio_entry.pack(fill="x", ipady=5)
        self.profile_bio_entry.insert(0, current_bio)

        ctk.CTkLabel(f, text=self.t["avatar_path"], text_color=self.colors["fg"], font=(self.font_family, 11, "bold")).pack(anchor="w", pady=(12, 5))
        self.profile_avatar_entry = ctk.CTkEntry(f, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.profile_avatar_entry.pack(fill="x", ipady=5)
        self.profile_avatar_entry.insert(0, user_data.get("avatar", ""))

        ctk.CTkButton(f, text=self.t["save"], command=self.save_profile_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="w", pady=18)

    def change_username_action(self):
        new_name = self.new_username_entry.get().strip().lower()
        if not new_name or not USERNAME_RE.match(new_name):
            messagebox.showerror(self.t["error"], self.t["invalid_username"])
            return

        if new_name == self.current_user.lower():
            messagebox.showwarning(self.t["warning"], self.t["same_username_err"])
            return

        self.change_username_btn.configure(state="disabled")
        old_name = self.current_user

        def worker():
            try:
                ok, err_key = FirebaseDB.change_username(old_name, new_name)
                if not ok:
                    msg = self.t.get(err_key or "user_exists", self.t["user_exists"])
                    self.root.after(0, lambda m=msg: messagebox.showerror(self.t["error"], m))
                    self.root.after(0, lambda: self.change_username_btn.configure(state="normal") if hasattr(self, "change_username_btn") and self.change_username_btn.winfo_exists() else None)
                    return

                SessionManager.save_session(new_name)
                self.root.after(0, lambda: self._on_username_changed(new_name))
            except Exception as e:
                self.root.after(0, lambda err=e: messagebox.showerror(self.t["error"], f"{self.t['connection_error']}{err}"))
                self.root.after(0, lambda: self.change_username_btn.configure(state="normal") if hasattr(self, "change_username_btn") and self.change_username_btn.winfo_exists() else None)

        threading.Thread(target=worker, daemon=True).start()

    def _on_username_changed(self, new_name):
        self.current_user = new_name
        self.root.title(f"Nova Messenger Pro v{self.CURRENT_VERSION} - [{new_name}]")
        self.render_navigation()
        messagebox.showinfo(self.t["success"], f"{self.t['username_changed']}{new_name}")
        self.render_profile_panel()

    def save_profile_action(self):
        new_bio = self.profile_bio_entry.get().strip()
        new_avatar = self.profile_avatar_entry.get().strip()
        FirebaseDB.update_user_profile(self.current_user, new_bio, new_avatar)
        messagebox.showinfo(self.t["success"], self.t["profile_updated"])
        self.render_profile_panel()

    def render_notes_panel(self):
        self.notes_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.notes_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(self.notes_frame, text=self.t["notes"], text_color=self.colors["fg"], font=(self.font_family, 16, "bold")).pack(anchor="w", pady=(0, 10))

        input_box = ctk.CTkFrame(self.notes_frame, fg_color=self.colors["sidebar"], corner_radius=12)
        input_box.pack(fill="x", pady=10)
        self.note_input = ctk.CTkEntry(input_box, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.note_input.pack(fill="x", padx=15, pady=(15, 10), ipady=5)
        self.note_input.bind("<Return>", lambda e: self.add_note_logic())
        ctk.CTkButton(input_box, text=self.t["add"], command=self.add_note_logic, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="e", padx=15, pady=(0, 15))

        self.notes_inner = ctk.CTkScrollableFrame(self.notes_frame, fg_color="transparent")
        self.notes_inner.pack(fill="both", expand=True, pady=10)
        self.load_notes_ui()

    def load_notes_ui(self):
        for widget in self.notes_inner.winfo_children():
            widget.destroy()
        notes = FirebaseDB.get_notes(self.current_user)
        for idx, item in enumerate(notes):
            text = item.get("text", "") if isinstance(item, dict) else str(item)
            row = ctk.CTkFrame(self.notes_inner, fg_color=self.colors["card_bg"], corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=text, text_color=self.colors["fg"], font=(self.font_family, 11), anchor="w", justify="left", wraplength=520).pack(side="left", fill="x", expand=True, padx=15, pady=10)
            ctk.CTkButton(row, text="✕", width=32, height=28, fg_color="#aa3333", text_color="white", corner_radius=6, command=lambda i=idx: self.delete_note_logic(i)).pack(side="right", padx=10)

    def add_note_logic(self):
        text = self.note_input.get().strip()
        if text:
            notes = FirebaseDB.get_notes(self.current_user)
            notes.append({"text": text})
            FirebaseDB.save_notes(self.current_user, notes)
            self.note_input.delete(0, "end")
            self.load_notes_ui()

    def delete_note_logic(self, index):
        notes = FirebaseDB.get_notes(self.current_user)
        if 0 <= index < len(notes):
            notes.pop(index)
            FirebaseDB.save_notes(self.current_user, notes)
            self.load_notes_ui()

    def render_chats_panel(self):
        self.cancel_contacts_polling()
        self.contact_buttons = {}
        self.general_chat_btn = None
        for widget in self.content.winfo_children():
            widget.destroy()

        chats_frame = ctk.CTkFrame(self.content, fg_color="transparent", corner_radius=0)
        chats_frame.pack(fill="both", expand=True)

        left_panel = ctk.CTkFrame(chats_frame, fg_color=self.colors["sidebar"], width=230, corner_radius=0)
        left_panel.pack(side="left", fill="y")

        ctk.CTkLabel(left_panel, text=self.t["dialogs"], text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=15, pady=(15, 8))

        self.search_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text=self.t["search_placeholder"],
            font=(self.font_family, 11),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["fg"],
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=15, pady=(0, 8), ipady=3)
        if self.search_query:
            self.search_entry.insert(0, self.search_query)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        ctk.CTkButton(left_panel, text=self.t["new_chat"], command=self.add_new_chat_dialog, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], hover_color=self.colors["bg"], font=(self.font_family, 11), corner_radius=8).pack(fill="x", padx=15, pady=(0, 10))

        self.contacts_list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.contacts_list_frame.pack(fill="both", expand=True, padx=5)

        if FirebaseDB.is_in_general_chat(self.current_user):
            self.general_chat_btn = ctk.CTkButton(
                left_panel,
                text=self.t["general_chat"],
                command=lambda: self.open_chat_with("general"),
                fg_color="transparent",
                text_color=self.colors["accent"],
                hover_color=self.colors["entry_bg"],
                font=(self.font_family, 11, "bold"),
                anchor="w",
                corner_radius=8
            )
            self.general_chat_btn.pack(fill="x", padx=15, pady=10, side="bottom")

        self.active_chat_panel = ctk.CTkFrame(chats_frame, fg_color=self.colors["bg"], corner_radius=0)
        self.active_chat_panel.pack(side="right", fill="both", expand=True)

        self.load_contacts_list()
        self.start_contacts_polling()

        if self.current_chat_target == "general" and not FirebaseDB.is_in_general_chat(self.current_user):
            my_chats = FirebaseDB.get_chats(self.current_user)
            if my_chats:
                self.open_chat_with(my_chats[0])
            else:
                self.current_chat_target = ""
                for widget in self.active_chat_panel.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(self.active_chat_panel, text=self.t["select_chat_left"], text_color=self.colors["fg"], font=(self.font_family, 14)).pack(expand=True)
        else:
            self.open_chat_with(self.current_chat_target)

    def on_search_change(self, event=None):
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_query = self.search_entry.get().strip().lower()
        self.load_contacts_list(force_rebuild=True)
        self.render_messages_list()

    def load_contacts_list(self, force_rebuild=False):
        my_chats = FirebaseDB.get_chats(self.current_user)
        filtered_chats = [u for u in my_chats if not self.search_query or self.search_query in u.lower()]
        current_buttons = set(self.contact_buttons.keys())

        if force_rebuild or current_buttons != set(filtered_chats):
            for widget in self.contacts_list_frame.winfo_children():
                widget.destroy()
            self.contact_buttons = {}

            for username in filtered_chats:
                btn = ctk.CTkButton(
                    self.contacts_list_frame,
                    text=username,
                    command=lambda u=username: self.open_chat_with(u),
                    fg_color="transparent",
                    text_color=self.colors["fg"],
                    hover_color=self.colors["entry_bg"],
                    font=(self.font_family, 11),
                    anchor="w",
                    corner_radius=6
                )
                btn.pack(fill="x", pady=2)
                btn.bind("<Button-3>", lambda e, u=username: self.show_chat_context_menu(e, u))
                self.contact_buttons[username] = btn

        self.highlight_active_chat()
        self.update_chats_nav_label()

    def refresh_unread_counts(self, my_chats):
        new_counts = {}
        targets = list(my_chats)
        if FirebaseDB.is_in_general_chat(self.current_user):
            targets.append("general")
        for tgt in targets:
            if tgt == self.current_chat_target:
                new_counts[tgt] = 0
            else:
                key = "general" if tgt == "general" else f"{min(self.current_user, tgt)}_{max(self.current_user, tgt)}"
                new_counts[tgt] = FirebaseDB.get_unread_count(key, self.current_user)
        self.unread_counts = new_counts

    def start_contacts_polling(self):
        self.cancel_contacts_polling()

        def poll_contacts():
            if not getattr(self, "current_user", None):
                return

            def background_fetch():
                try:
                    my_chats = FirebaseDB.get_chats(self.current_user)
                    self.refresh_unread_counts(my_chats)
                    self.root.after(0, lambda: self.update_contacts_safely(my_chats))
                except Exception:
                    pass

            threading.Thread(target=background_fetch, daemon=True).start()

            try:
                self.contacts_after_id = self.root.after(4000, poll_contacts)
            except Exception:
                pass

        self.contacts_after_id = self.root.after(4000, poll_contacts)

    def update_contacts_safely(self, my_chats):
        if not hasattr(self, "contacts_list_frame") or not self.contacts_list_frame.winfo_exists():
            return
        filtered_chats = [u for u in my_chats if not self.search_query or self.search_query in u.lower()]
        if set(self.contact_buttons.keys()) != set(filtered_chats):
            self.load_contacts_list(force_rebuild=True)
        else:
            self.highlight_active_chat()
            self.update_chats_nav_label()

    def show_chat_context_menu(self, event, target_user):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["entry_bg"], fg=self.colors["fg"])
        menu.add_command(label=self.t["info"], command=lambda: self.show_user_info(target_user))
        menu.add_command(label=self.t["delete"], command=lambda: self.delete_chat_action(target_user))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_user_info(self, username):
        u_data = FirebaseDB.get_user(username) or {}
        bio = u_data.get("bio", "—")
        messagebox.showinfo(self.t["info"], f"{self.t['username']}: {username}\n{self.t['about_me']} {bio}")

    def delete_chat_action(self, target_user):
        if messagebox.askyesno(self.t["delete_chat_title"], f"{self.t['delete_chat_q']}{target_user}?"):
            chat_key = f"{min(self.current_user, target_user)}_{max(self.current_user, target_user)}"
            FirebaseDB.remove_chat(self.current_user, target_user)
            FirebaseDB.delete_entire_chat(chat_key)

            if self.current_chat_target == target_user:
                self.render_chats_panel()
            else:
                self.load_contacts_list(force_rebuild=True)

    def add_new_chat_dialog(self):
        target_user = simpledialog.askstring(self.t["new_chat_title"], self.t["new_chat_prompt"])
        if target_user:
            target_user = target_user.strip().lower()
            if target_user == "general":
                FirebaseDB.join_general_chat(self.current_user)
                self.current_chat_target = "general"
                self.render_chats_panel()
                return

            if target_user == self.current_user:
                messagebox.showerror(self.t["error"], self.t["self_chat_err"])
                return

            if FirebaseDB.get_user(target_user):
                FirebaseDB.add_chat_for(self.current_user, target_user)
                FirebaseDB.add_chat_for(target_user, self.current_user)
                self.current_chat_target = target_user
                self.render_chats_panel()
            else:
                messagebox.showerror(self.t["error"], self.t["user_not_found"])

    def leave_general_chat_action(self):
        if messagebox.askyesno(self.t["leave_chat_title"], self.t["leave_chat_q"]):
            FirebaseDB.leave_general_chat(self.current_user)
            my_chats = FirebaseDB.get_chats(self.current_user)
            self.current_chat_target = my_chats[0] if my_chats else ""
            self.render_chats_panel()

    def open_chat_with(self, target):
        self.cancel_chat_polling()
        self.current_chat_target = target
        self.unread_counts[target] = 0
        self.highlight_active_chat()
        self.update_chats_nav_label()
        for widget in self.active_chat_panel.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.active_chat_panel, fg_color=self.colors["sidebar"], height=60, corner_radius=0)
        header_frame.pack(fill="x", side="top")

        title_text = self.t["general_chat"] if target == "general" else f"{self.t['chat_with_prefix']}{target}"
        ctk.CTkLabel(header_frame, text=title_text, text_color=self.colors["fg"], font=(self.font_family, 13, "bold")).pack(side="left", padx=20, pady=15)

        if target and target != "general":
            u_info = FirebaseDB.get_user(target) or {}
            bio_preview = u_info.get("bio", "")
            if bio_preview:
                ctk.CTkLabel(header_frame, text=f"• {bio_preview[:40]}", text_color=self.colors["muted"], font=(self.font_family, 10)).pack(side="left", padx=(0, 8))

        self.typing_status_lbl = ctk.CTkLabel(header_frame, text="", text_color="#888888", font=(self.font_family, 10, "italic"))
        self.typing_status_lbl.pack(side="left", padx=8)

        if target == "general":
            ctk.CTkButton(header_frame, text=self.t["leave_general_btn"], command=self.leave_general_chat_action, fg_color="#aa3333", text_color="white", width=130, corner_radius=6).pack(side="right", padx=15)

        ctk.CTkButton(header_frame, text=self.t["scroll_down"], command=self.scroll_chat_to_bottom, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=75, corner_radius=6).pack(side="right", padx=(0, 8))

        self.chat_messages_inner = ctk.CTkScrollableFrame(self.active_chat_panel, fg_color="transparent")
        self.chat_messages_inner.pack(fill="both", expand=True, padx=10, pady=5)

        input_panel = ctk.CTkFrame(self.active_chat_panel, fg_color=self.colors["sidebar"], height=82, corner_radius=0)
        input_panel.pack(fill="x", side="bottom")

        ctk.CTkButton(input_panel, text="🖼️", command=self.send_image_message, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8).pack(side="left", padx=(10, 4), pady=15)
        self.voice_btn_widget = ctk.CTkButton(input_panel, text="🎤", command=self.toggle_voice_record, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8)
        self.voice_btn_widget.pack(side="left", padx=2, pady=15)
        self.screen_btn_widget = ctk.CTkButton(input_panel, text="📹", command=self.toggle_screen_record, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8)
        self.screen_btn_widget.pack(side="left", padx=(2, 8), pady=15)

        input_col = ctk.CTkFrame(input_panel, fg_color="transparent")
        input_col.pack(side="left", fill="x", expand=True, pady=(8, 6))

        self.chat_msg_input = ctk.CTkEntry(input_col, font=("Segoe UI Emoji", 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.chat_msg_input.pack(fill="x", ipady=5)
        self.chat_msg_input.bind("<Return>", self.handle_return_key)
        self.chat_msg_input.bind("<Control-Return>", self.handle_ctrl_return_key)
        self.chat_msg_input.bind("<KeyRelease>", self.on_user_typing)

        ctk.CTkLabel(input_col, text=self.t["hotkey_hint"], text_color=self.colors["muted"], font=(self.font_family, 9)).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(input_panel, text=self.t["send"], command=self.send_text_message, fg_color=self.colors["accent"], text_color="white", width=90, corner_radius=8).pack(side="right", padx=15, pady=15)

        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        FirebaseDB.mark_read(chat_key, self.current_user)

        self.load_active_chat_messages()
        self.start_chat_polling()

    def handle_return_key(self, event):
        self.send_text_message()
        return "break"

    def handle_ctrl_return_key(self, event):
        if hasattr(self, "chat_msg_input") and self.chat_msg_input.winfo_exists():
            self.chat_msg_input.insert("insert", "\n")
        return "break"

    def scroll_chat_to_bottom(self):
        if hasattr(self, "chat_messages_inner") and self.chat_messages_inner.winfo_exists():
            try:
                self.chat_messages_inner._parent_canvas.yview_moveto(1.0)
            except Exception:
                pass

    def on_user_typing(self, event):
        target = self.current_chat_target
        if target == "general" and not FirebaseDB.is_in_general_chat(self.current_user):
            return
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        FirebaseDB.set_typing(chat_key, self.current_user)

    def start_chat_polling(self):
        self.cancel_chat_polling()

        def poll():
            if not getattr(self, "current_chat_target", None):
                return

            try:
                target = self.current_chat_target
                if target == "general" and not FirebaseDB.is_in_general_chat(self.current_user):
                    return

                chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

                def background_fetch():
                    try:
                        t_info = FirebaseDB.get_typing(chat_key)
                        msgs = FirebaseDB.get_messages(chat_key)
                        self.root.after(0, lambda: process_poll_data(t_info, msgs))
                    except Exception:
                        pass

                def process_poll_data(t_info, msgs):
                    if getattr(self, "current_chat_target", None) != target:
                        return
                    if not hasattr(self, "typing_status_lbl") or not self.typing_status_lbl.winfo_exists():
                        return

                    if t_info and t_info.get("user") != self.current_user:
                        if time.time() - t_info.get("time", 0) < 3:
                            self.typing_status_lbl.configure(text=f"{t_info.get('user')}{self.t['typing']}")
                        else:
                            self.typing_status_lbl.configure(text="")
                    else:
                        self.typing_status_lbl.configure(text="")

                    if len(msgs) != self.last_msg_count:
                        self.last_msg_count = len(msgs)
                        FirebaseDB.mark_read(chat_key, self.current_user)
                        self.current_messages_cache = msgs
                        self.render_messages_list()

                threading.Thread(target=background_fetch, daemon=True).start()
            except Exception:
                pass

            try:
                self.after_id = self.root.after(3000, poll)
            except Exception:
                pass

        self.after_id = self.root.after(3000, poll)

    def load_active_chat_messages(self, is_polling=False):
        target = getattr(self, "current_chat_target", "general")
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        messages = FirebaseDB.get_messages(chat_key)
        self.current_messages_cache = messages
        self.last_msg_count = len(messages)
        self.render_messages_list()

    def open_image_viewer(self, pil_image):
        viewer = ctk.CTkToplevel(self.root)
        viewer.title(self.t["info"])
        viewer.geometry("760x620")
        w, h = pil_image.size
        scale = min(720 / max(w, 1), 560 / max(h, 1), 1.0)
        resized = pil_image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
        tk_full = ImageTk.PhotoImage(resized)
        lbl = tk.Label(viewer, image=tk_full, bg="#111111")
        lbl.image = tk_full
        lbl.pack(fill="both", expand=True, padx=10, pady=10)

    def render_messages_list(self):
        if not hasattr(self, "chat_messages_inner") or not self.chat_messages_inner.winfo_exists():
            return
        for widget in self.chat_messages_inner.winfo_children():
            widget.destroy()

        for msg in self.current_messages_cache:
            if not isinstance(msg, dict):
                continue
            msg_type = msg.get("type", "text")
            text = msg.get("text", "")
            sender = msg.get("user", "Unknown")

            if self.search_query:
                if msg_type != "text" or (self.search_query not in text.lower() and self.search_query not in sender.lower()):
                    continue

            is_mine = sender == self.current_user
            bubble_bg = self.colors["bubble_mine"] if is_mine else self.colors["bubble_other"]
            msg_id = msg.get("id")

            card = ctk.CTkFrame(self.chat_messages_inner, fg_color=bubble_bg, corner_radius=12)
            card.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(card, text=sender, text_color="#aaaaaa", font=(self.font_family, 9, "bold")).pack(anchor="w", padx=12, pady=(6, 0))

            if msg_type == "text":
                if text:
                    lbl = ctk.CTkLabel(card, text=text, text_color="white" if is_mine else self.colors["fg"], font=("Segoe UI Emoji", 11), justify="left", wraplength=500)
                    lbl.pack(anchor="w", padx=12, pady=4)

            elif msg_type == "image":
                try:
                    img_data = base64.b64decode(msg.get("data", ""))
                    full_pil = Image.open(io.BytesIO(img_data))
                    tmp_path = os.path.join(IMAGES_DIR, f"temp_{time.time()}.png")
                    full_pil.save(tmp_path)

                    thumb_pil = full_pil.copy()
                    thumb_pil.thumbnail((220, 220))
                    tk_img = ImageTk.PhotoImage(thumb_pil)
                    self.photo_cache[tmp_path] = tk_img

                    lbl = tk.Label(card, image=tk_img, bg=bubble_bg, cursor="hand2")
                    lbl.pack(anchor="w", padx=12, pady=4)
                    lbl.bind("<Button-1>", lambda e, im=full_pil: self.open_image_viewer(im))
                except Exception:
                    ctk.CTkLabel(card, text=self.t["img_load_err"], text_color="red").pack(anchor="w", padx=12, pady=4)

            elif msg_type == "voice":
                voice_data = base64.b64decode(msg.get("data", ""))
                v_path = os.path.join(VOICES_DIR, f"voice_{time.time()}.wav")
                with open(v_path, "wb") as f:
                    f.write(voice_data)

                ctk.CTkButton(card, text=self.t["listen_voice"], command=lambda p=v_path: threading.Thread(target=self.play_voice, args=(p,), daemon=True).start(), fg_color="#444", text_color="white", corner_radius=6, height=28).pack(anchor="w", padx=12, pady=6)

            elif msg_type == "video":
                v_name = msg.get("name", "screen_record.mp4")
                ctk.CTkButton(card, text=f"{self.t['save_screen_rec']}{v_name}", command=lambda m=msg: self.save_and_play_video(m), fg_color="#444", text_color="white", corner_radius=6, height=28).pack(anchor="w", padx=12, pady=6)

            if is_mine:
                read_status = "✓✓" if msg.get("read", False) else "✓"
                ctk.CTkLabel(card, text=read_status, text_color="#00ffcc" if msg.get("read") else "#aaaaaa", font=(self.font_family, 9)).pack(anchor="e", padx=12, pady=(0, 6))

            for widget_to_bind in card.winfo_children():
                widget_to_bind.bind("<Button-3>", lambda e, m_id=msg_id, m_user=sender: self.show_context_menu(e, m_id, m_user))
            card.bind("<Button-3>", lambda e, m_id=msg_id, m_user=sender: self.show_context_menu(e, m_id, m_user))

        self.scroll_chat_to_bottom()

    def show_context_menu(self, event, msg_id, msg_user):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["entry_bg"], fg=self.colors["fg"])
        if msg_user == self.current_user:
            menu.add_command(label=self.t["edit"], command=lambda: self.edit_message_action(msg_id))
            menu.add_command(label=self.t["delete"], command=lambda: self.delete_message_action(msg_id))
        else:
            menu.add_command(label=self.t["info"], command=lambda: self.show_user_info(msg_user))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def edit_message_action(self, msg_id):
        new_text = simpledialog.askstring(self.t["edit_title"], self.t["edit_prompt"])
        if new_text:
            target = getattr(self, "current_chat_target", "general")
            chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
            FirebaseDB.update_message(chat_key, msg_id, new_text.strip())
            self.load_active_chat_messages()

    def delete_message_action(self, msg_id):
        if messagebox.askyesno(self.t["delete_msg_title"], self.t["delete_msg_q"]):
            target = getattr(self, "current_chat_target", "general")
            chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
            FirebaseDB.delete_message(chat_key, msg_id)
            self.load_active_chat_messages()

    def send_text_message(self):
        text = self.chat_msg_input.get().strip()
        if not text:
            return

        target = getattr(self, "current_chat_target", "general")
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

        FirebaseDB.add_chat_for(self.current_user, target)
        FirebaseDB.add_chat_for(target, self.current_user)

        new_msg = {"user": self.current_user, "target": target, "type": "text", "text": text, "read": False}
        FirebaseDB.add_message(chat_key, new_msg)
        self.chat_msg_input.delete(0, "end")
        self.load_active_chat_messages()

    def compress_image_bytes(self, file_path):
        img = Image.open(file_path)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > MAX_IMAGE_SIDE:
            scale = MAX_IMAGE_SIDE / float(max(w, h))
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        if img.mode == "RGBA":
            img.save(buf, format="PNG", optimize=True)
        else:
            img.save(buf, format="JPEG", quality=82, optimize=True)
        return buf.getvalue()

    def send_image_message(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return

        try:
            img_bytes = self.compress_image_bytes(file_path)
            encoded = base64.b64encode(img_bytes).decode("utf-8")
        except Exception as e:
            messagebox.showerror(self.t["error"], f"{self.t['img_load_err']} {e}")
            return

        target = getattr(self, "current_chat_target", "general")
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

        FirebaseDB.add_chat_for(self.current_user, target)
        FirebaseDB.add_chat_for(target, self.current_user)

        new_msg = {"user": self.current_user, "target": target, "type": "image", "data": encoded, "read": False}
        FirebaseDB.add_message(chat_key, new_msg)
        self.load_active_chat_messages()

    def toggle_screen_record(self):
        if not self.is_recording_screen:
            self.is_recording_screen = True
            self.screen_start_time = time.time()
            self.screen_btn_widget.configure(fg_color="red")
            self.v_filename = f"screen_{int(time.time())}.mp4"
            self.v_path = os.path.join(VIDEOS_DIR, self.v_filename)

            def record_loop():
                fps = 20.0
                hit_limit = False
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    width = monitor["width"]
                    height = monitor["height"]

                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    out = cv2.VideoWriter(self.v_path, fourcc, fps, (width, height))

                    while self.is_recording_screen:
                        if time.time() - self.screen_start_time >= MAX_SCREEN_SECONDS:
                            hit_limit = True
                            self.is_recording_screen = False
                            break
                        start_time = time.time()
                        img = sct.grab(monitor)
                        frame = np.array(img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        out.write(frame)

                        elapsed = time.time() - start_time
                        sleep_time = (1.0 / fps) - elapsed
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                    out.release()

                self.root.after(0, lambda: self.screen_btn_widget.configure(fg_color=self.colors["entry_bg"]) if self.screen_btn_widget.winfo_exists() else None)
                if hit_limit:
                    self.root.after(0, lambda: messagebox.showinfo(self.t["warning"], self.t["screen_limit"]))

                if os.path.exists(self.v_path) and os.path.getsize(self.v_path) > 0:
                    with open(self.v_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")

                    target = getattr(self, "current_chat_target", "general")
                    chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

                    FirebaseDB.add_chat_for(self.current_user, target)
                    FirebaseDB.add_chat_for(target, self.current_user)

                    new_msg = {"user": self.current_user, "target": target, "type": "video", "name": self.v_filename, "data": encoded, "read": False}
                    FirebaseDB.add_message(chat_key, new_msg)
                    self.root.after(0, self.load_active_chat_messages)

            threading.Thread(target=record_loop, daemon=True).start()
        else:
            self.is_recording_screen = False
            self.screen_btn_widget.configure(fg_color=self.colors["entry_bg"])

    def save_and_play_video(self, msg):
        try:
            video_data = base64.b64decode(msg.get("data", ""))
            v_name = msg.get("name", "screen_record.mp4")
            save_path = filedialog.asksaveasfilename(defaultextension=".mp4", initialfile=v_name, filetypes=[("MP4 files", "*.mp4")])
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(video_data)
                messagebox.showinfo(self.t["success"], f"{self.t['video_saved']}{save_path}")
        except Exception as e:
            messagebox.showerror(self.t["error"], f"{self.t['save_file_err']}{e}")

    def finish_voice_record(self, hit_limit=False):
        self.is_recording_voice = False
        if hasattr(self, "voice_btn_widget") and self.voice_btn_widget.winfo_exists():
            self.voice_btn_widget.configure(fg_color=self.colors["entry_bg"])
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass

        if hit_limit:
            messagebox.showinfo(self.t["warning"], self.t["voice_limit"])

        if getattr(self, "recorded_frames", None):
            audio_data = np.concatenate(self.recorded_frames, axis=0)
            v_path = os.path.join(VOICES_DIR, f"rec_{time.time()}.wav")

            with wave.open(v_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

            with open(v_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")

            target = getattr(self, "current_chat_target", "general")
            chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

            FirebaseDB.add_chat_for(self.current_user, target)
            FirebaseDB.add_chat_for(target, self.current_user)

            new_msg = {"user": self.current_user, "target": target, "type": "voice", "data": encoded, "read": False}
            FirebaseDB.add_message(chat_key, new_msg)
            self.load_active_chat_messages()

    def monitor_voice_limit(self):
        if not self.is_recording_voice:
            return
        if time.time() - self.voice_start_time >= MAX_VOICE_SECONDS:
            self.finish_voice_record(hit_limit=True)
        else:
            self.root.after(500, self.monitor_voice_limit)

    def toggle_voice_record(self):
        if not self.is_recording_voice:
            self.is_recording_voice = True
            self.voice_start_time = time.time()
            self.voice_btn_widget.configure(fg_color="red")
            self.sample_rate = 44100
            self.recorded_frames = []

            def callback(indata, frames, time_info, status):
                if self.is_recording_voice:
                    self.recorded_frames.append(indata.copy())

            self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback)
            self.stream.start()
            self.root.after(500, self.monitor_voice_limit)
        else:
            self.finish_voice_record(hit_limit=False)

    def play_voice(self, path):
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME)
        except Exception:
            pass

    def render_settings_panel(self):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(scroll, text=self.t["settings"], text_color=self.colors["fg"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 18))

        pref_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        pref_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(pref_card, text=self.t["theme"], text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(14, 5))
        self.theme_var = tk.StringVar(value=manager.settings.get("theme", "dark"))
        ctk.CTkRadioButton(pref_card, text=self.t["dark"], variable=self.theme_var, value="dark", text_color=self.colors["fg"]).pack(anchor="w", padx=28, pady=2)
        ctk.CTkRadioButton(pref_card, text=self.t["light"], variable=self.theme_var, value="light", text_color=self.colors["fg"]).pack(anchor="w", padx=28, pady=2)

        ctk.CTkLabel(pref_card, text="Язык / Language / Език", text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(14, 5))
        current_lang = manager.settings.get("lang", "ru")
        if current_lang not in LANGUAGE_REGISTRY:
            current_lang = "ru"
        self.lang_var = tk.StringVar(value=current_lang)
        for lang_code, lang_label in LANGUAGE_REGISTRY.items():
            ctk.CTkRadioButton(
                pref_card,
                text=lang_label,
                variable=self.lang_var,
                value=lang_code,
                text_color=self.colors["fg"]
            ).pack(anchor="w", padx=28, pady=2)

        ctk.CTkButton(pref_card, text=self.t["save"], command=self.save_settings_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="w", padx=20, pady=(14, 16))

        updates_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        updates_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(updates_card, text=self.t["updates_center"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(updates_card, text=f"{self.t['current_version']}{self.CURRENT_VERSION} Pro", text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=20, pady=(0, 10))
        ctk.CTkButton(updates_card, text=self.t["check_updates"], command=lambda: self.check_for_updates_threaded(manual=True), fg_color=self.colors["accent"], text_color="white", font=(self.font_family, 11), corner_radius=8).pack(anchor="w", padx=20, pady=(0, 8))

        self.update_result_frame = ctk.CTkFrame(updates_card, fg_color="transparent")
        self.update_result_frame.pack(fill="x", padx=20, pady=(0, 14))
        self.check_for_updates_threaded(manual=False)

        support_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        support_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(support_card, text=self.t["support_title"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 6))
        ctk.CTkLabel(support_card, text=self.t["support_desc"], text_color=self.colors["fg"], font=(self.font_family, 12), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkButton(
            support_card,
            text=self.t["support_btn"],
            command=lambda: webbrowser.open("https://t.me/nova_mesenger_support_bot"),
            fg_color=self.colors["accent"],
            text_color="white",
            corner_radius=8,
            height=36,
            font=(self.font_family, 12, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 16))

        about_card = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=12)
        about_card.pack(fill="x", pady=(0, 18))

        ctk.CTkLabel(about_card, text=self.t["about_app"], text_color=self.colors["accent"], font=(self.font_family, 15, "bold")).pack(anchor="w", padx=20, pady=(14, 6))
        ctk.CTkLabel(about_card, text=f"Nova Messenger Pro — v{self.CURRENT_VERSION}", text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=20, pady=(0, 4))
        ctk.CTkLabel(about_card, text=self.t["about_desc"], text_color=self.colors["fg"], font=(self.font_family, 11), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 8))
        ctk.CTkLabel(about_card, text=self.t["signpath_info"], text_color="#00ffcc" if manager.settings.get("theme", "dark") == "dark" else "#007755", font=(self.font_family, 11, "bold"), wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

    def save_settings_action(self):
        manager.settings["theme"] = self.theme_var.get()
        manager.settings["lang"] = self.lang_var.get()
        manager.save_settings_local()

        self.setup_styles()
        self.render_navigation()
        self.switch_tab("settings")

if __name__ == "__main__":
    root = ctk.CTk()
    app = NovaApp(root)
    root.mainloop()