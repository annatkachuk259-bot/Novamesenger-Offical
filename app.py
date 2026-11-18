import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json, os, hashlib, time, threading, base64, wave, webbrowser
import sounddevice as sd
import numpy as np
import cv2
import mss
import customtkinter as ctk

# --- ИМПОРТ FIREBASE ---
import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    FIREBASE_AVAILABLE = True
except Exception as e:
    FIREBASE_AVAILABLE = False
    print(f"Ошибка инициализации Firebase: {e}")

SETTINGS_FILE = "settings.json"
SESSION_FILE = "session.json"
VOICES_DIR = "voices"
IMAGES_DIR = "images"
VIDEOS_DIR = "videos"

for d in [VOICES_DIR, IMAGES_DIR, VIDEOS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Настройка CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

THEMES = {
    "dark": {
        "bg": "#13131a", "fg": "#e1e1e6", "entry_bg": "#1c1c24", 
        "accent": "#00afff", "sidebar": "#181820", "bubble_mine": "#007acc", 
        "bubble_other": "#22222f", "card_bg": "#1c1c24", "header": "#181820"
    },
    "light": {
        "bg": "#f5f5f7", "fg": "#1d1d1f", "entry_bg": "#ffffff", 
        "accent": "#0066cc", "sidebar": "#e8e8ed", "bubble_mine": "#007aff", 
        "bubble_other": "#e5e5ea", "card_bg": "#ffffff", "header": "#e5e5ea"
    }
}

LANGUAGES = {
    "ru": {
        "chats": "Чаты", "notes": "Заметки", "profile": "Профиль", "updates": "Обновления", "settings": "Настройки",
        "support": "💬 Техподдержка", "support_title": "Центр поддержки Nova Messenger", 
        "support_desc": "К сожалению, сейчас мы не можем сюда его добавить, но вы можете перейти по ссылке и открыть в телеграме",
        "support_btn": "Открыть в Telegram",
        "auth_title": "Nova Messenger Pro - Вход", "username": "Имя пользователя", "password": "Пароль",
        "login": "Войти", "register": "Регистрация", "logout": "Выход", "new_chat": "+ Новый чат",
        "general_chat": "🟢 Общий чат", "send": "Отправить", "theme": "Тема", "dark": "Тёмная",
        "light": "Светлая", "save": "Сохранить", "dialogs": "Диалоги", "admin": "👑 Админка",
        "error": "Ошибка", "warning": "Внимание", "success": "Успех", "fill_fields": "Заполните все поля!",
        "invalid_credentials": "Неверный логин или пароль!", "user_exists": "Такой пользователь уже существует!",
        "connection_error": "Ошибка соединения: ", "about_me": "О себе (Bio):", "avatar_path": "Путь или Base64 аватара:",
        "profile_updated": "Профиль успешно обновлен!", "add": "Добавить", "delete": "Удалить",
        "select_chat_left": "Выберите чат слева", "delete_chat_q": "Удалить чат с пользователем ",
        "delete_chat_title": "Удалить чат", "new_chat_title": "Новый чат", "new_chat_prompt": "Введите имя пользователя или 'general' для общего чата:",
        "self_chat_err": "Нельзя создать чат с самим собой!", "user_not_found": "Пользователь не найден!",
        "leave_chat_q": "Покинуть общий чат? Новые сообщения перестанут вам приходить до повторного входа.",
        "leave_chat_title": "Общий чат", "listen_voice": "▶ Слушать голос", "save_screen_rec": "🎥 Скачать запись экрана: ",
        "edit": "Редактировать", "info": "Информация", "edit_title": "Редактирование", "edit_prompt": "Введите новый текст сообщения:",
        "delete_msg_q": "Удалить это сообщение?", "delete_msg_title": "Удаление", "updates_center": "🚀 Центр обновлений Nova Messenger",
        "current_version": "Текущая версия: v", "check_updates": "Проверить обновления", "checking_server": "Проверка обновлений с сервера...",
        "server_err": "Не удалось связаться с сервером обновлений.", "no_connection": "Не удалось проверить обновления (нет связи с сервером).",
        "new_version_available": "🎉 Доступна новая версия: v", "download_update": "Скачать обновление", "latest_version_installed": "✓ У вас установлена актуальная версия приложения.",
        "latest_version_info": "У вас установлена самая последняя версия!", "admin_panel": "👑 Панель Администратора", "total_users": "Всего пользователей в системе: ",
        "clear_db_msgs": "Очистить все сообщения в базе", "admin_del_user": "Удалить пользователя ", "admin_clear_q": "Очистить все сообщения и чаты в облаке?",
        "db_cleared": "База сообщений очищена.", "notes_count": "📝 Заметок: ", "active_chats_count": "  |  💬 Активных личных чатов: ",
        "typing": " печатает...", "img_load_err": "[Ошибка загрузки фото]", "video_saved": "Запись экрана сохранена в:\n",
        "save_file_err": "Не удалось сохранить файл: "
    },
    "en": {
        "chats": "Chats", "notes": "Notes", "profile": "Profile", "updates": "Updates", "settings": "Settings",
        "support": "💬 Support", "support_title": "Nova Messenger Support Center", 
        "support_desc": "Unfortunately, we cannot add it here right now, but you can follow the link and open it in Telegram",
        "support_btn": "Open in Telegram",
        "auth_title": "Nova Messenger Pro - Auth", "username": "Username", "password": "Password",
        "login": "Login", "register": "Register", "logout": "Logout", "new_chat": "+ New Chat",
        "general_chat": "🟢 General Chat", "send": "Send", "theme": "Theme", "dark": "Dark",
        "light": "Light", "save": "Save", "dialogs": "Dialogs", "admin": "👑 Admin",
        "error": "Error", "warning": "Warning", "success": "Success", "fill_fields": "Please fill in all fields!",
        "invalid_credentials": "Invalid username or password!", "user_exists": "User already exists!",
        "connection_error": "Connection error: ", "about_me": "Bio:", "avatar_path": "Avatar path or Base64:",
        "profile_updated": "Profile successfully updated!", "add": "Add", "delete": "Delete",
        "select_chat_left": "Select a chat on the left", "delete_chat_q": "Delete chat with user ",
        "delete_chat_title": "Delete Chat", "new_chat_title": "New Chat", "new_chat_prompt": "Enter username or 'general' for general chat:",
        "self_chat_err": "You cannot create a chat with yourself!", "user_not_found": "User not found!",
        "leave_chat_q": "Leave general chat? You will stop receiving new messages until you rejoin.",
        "leave_chat_title": "General Chat", "listen_voice": "▶ Play Voice", "save_screen_rec": "🎥 Download Screen Recording: ",
        "edit": "Edit", "info": "Info", "edit_title": "Edit Message", "edit_prompt": "Enter new message text:",
        "delete_msg_q": "Delete this message?", "delete_msg_title": "Delete", "updates_center": "🚀 Nova Messenger Update Center",
        "current_version": "Current Version: v", "check_updates": "Check for Updates", "checking_server": "Checking updates from server...",
        "server_err": "Failed to connect to update server.", "no_connection": "Could not check for updates (no connection).",
        "new_version_available": "🎉 New version available: v", "download_update": "Download Update", "latest_version_installed": "✓ You have the latest version installed.",
        "latest_version_info": "You are using the latest version!", "admin_panel": "👑 Admin Panel", "total_users": "Total users in system: ",
        "clear_db_msgs": "Clear All Messages in DB", "admin_del_user": "Delete user ", "admin_clear_q": "Clear all messages and chats in the cloud?",
        "db_cleared": "Message database cleared.", "notes_count": "📝 Notes: ", "active_chats_count": "  |  💬 Active Private Chats: ",
        "typing": " is typing...", "img_load_err": "[Image loading error]", "video_saved": "Screen recording saved to:\n",
        "save_file_err": "Failed to save file: "
    }
}

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
            except: 
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
            except:
                return None
        return None

    @staticmethod
    def clear_session():
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
            except:
                pass

class FirebaseDB:
    @staticmethod
    def get_user(username):
        if not FIREBASE_AVAILABLE: return None
        doc = db.collection("users").document(username.lower()).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def save_user(username, password_hash):
        if not FIREBASE_AVAILABLE: return
        db.collection("users").document(username.lower()).set({
            "username": username, 
            "password": password_hash,
            "bio": "Привет! Я использую Nova Messenger.",
            "avatar": ""
        }, merge=True)

    @staticmethod
    def update_user_profile(username, bio, avatar):
        if not FIREBASE_AVAILABLE: return
        db.collection("users").document(username.lower()).update({
            "bio": bio,
            "avatar": avatar
        })

    @staticmethod
    def get_all_users():
        if not FIREBASE_AVAILABLE: return {}
        docs = db.collection("users").stream()
        return {doc.id: doc.to_dict() for doc in docs}

    @staticmethod
    def delete_user(username):
        if not FIREBASE_AVAILABLE: return
        db.collection("users").document(username.lower()).delete()

    @staticmethod
    def get_messages(chat_key):
        if not FIREBASE_AVAILABLE: return []
        docs = db.collection("chats").document(chat_key).collection("messages").order_by("timestamp").stream()
        messages = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            messages.append(d)
        return messages

    @staticmethod
    def add_message(chat_key, msg_data):
        if not FIREBASE_AVAILABLE: return
        msg_data["timestamp"] = firestore.SERVER_TIMESTAMP
        db.collection("chats").document(chat_key).collection("messages").add(msg_data)

    @staticmethod
    def update_message(chat_key, msg_id, new_text):
        if not FIREBASE_AVAILABLE: return
        db.collection("chats").document(chat_key).collection("messages").document(msg_id).update({"text": new_text})

    @staticmethod
    def delete_message(chat_key, msg_id):
        if not FIREBASE_AVAILABLE: return
        db.collection("chats").document(chat_key).collection("messages").document(msg_id).delete()

    @staticmethod
    def clear_all_messages_db():
        if not FIREBASE_AVAILABLE: return
        chats = db.collection("chats").stream()
        for chat in chats:
            msgs = db.collection("chats").document(chat.id).collection("messages").stream()
            for m in msgs: m.reference.delete()

    @staticmethod
    def delete_entire_chat(chat_key):
        if not FIREBASE_AVAILABLE: return
        try:
            msgs_ref = db.collection("chats").document(chat_key).collection("messages")
            docs = msgs_ref.stream()
            for doc in docs:
                doc.reference.delete()
            db.collection("chats").document(chat_key).delete()
        except Exception as e:
            print(f"Ошибка при удалении чата из БД: {e}")

    @staticmethod
    def get_notes(username):
        if not FIREBASE_AVAILABLE: return []
        doc = db.collection("notes").document(username.lower()).get()
        return doc.to_dict().get("items", []) if doc.exists else []

    @staticmethod
    def save_notes(username, notes_list):
        if not FIREBASE_AVAILABLE: return
        db.collection("notes").document(username.lower()).set({"items": notes_list})

    @staticmethod
    def get_chats(username):
        if not FIREBASE_AVAILABLE: return []
        doc = db.collection("user_chats").document(username.lower()).get()
        return doc.to_dict().get("chats", []) if doc.exists else []

    @staticmethod
    def add_chat_for(username, target):
        if not FIREBASE_AVAILABLE: return
        chats = FirebaseDB.get_chats(username)
        if target not in chats:
            chats.append(target)
            db.collection("user_chats").document(username.lower()).set({"chats": chats})

    @staticmethod
    def remove_chat(username, target):
        if not FIREBASE_AVAILABLE: return
        chats = FirebaseDB.get_chats(username)
        if target in chats:
            chats.remove(target)
            db.collection("user_chats").document(username.lower()).set({"chats": chats})

    @staticmethod
    def is_in_general_chat(username):
        if not FIREBASE_AVAILABLE: return True
        doc = db.collection("settings_meta").document("general_members").get()
        if not doc.exists:
            return True
        members = doc.to_dict().get("list", [])
        return username.lower() in members

    @staticmethod
    def join_general_chat(username):
        if not FIREBASE_AVAILABLE: return
        ref = db.collection("settings_meta").document("general_members")
        doc = ref.get()
        members = doc.to_dict().get("list", []) if doc.exists else []
        if username.lower() not in members:
            members.append(username.lower())
            ref.set({"list": members})

    @staticmethod
    def leave_general_chat(username):
        if not FIREBASE_AVAILABLE: return
        ref = db.collection("settings_meta").document("general_members")
        doc = ref.get()
        if doc.exists:
            members = doc.to_dict().get("list", [])
            if username.lower() in members:
                members.remove(username.lower())
                ref.set({"list": members})

    @staticmethod
    def set_typing(chat_key, username):
        if not FIREBASE_AVAILABLE: return
        db.collection("typing").document(chat_key).set({"user": username, "time": time.time()})

    @staticmethod
    def get_typing(chat_key):
        if not FIREBASE_AVAILABLE: return {}
        doc = db.collection("typing").document(chat_key).get()
        return doc.to_dict() if doc.exists else {}

    @staticmethod
    def mark_read(chat_key, current_user):
        if not FIREBASE_AVAILABLE: return
        ref = db.collection("chats").document(chat_key).collection("messages")
        try:
            docs = ref.where(filter=firestore.FieldFilter("user", "!=", current_user))\
                      .where(filter=firestore.FieldFilter("read", "==", False))\
                      .stream()
            for doc in docs: 
                doc.reference.update({"read": True})
        except Exception as e:
            print(f"Ошибка в mark_read: {e}")

    @staticmethod
    def get_latest_version_info():
        if not FIREBASE_AVAILABLE: return None
        doc = db.collection("settings_meta").document("version_info").get()
        return doc.to_dict() if doc.exists else None

class NovaApp:
    CURRENT_VERSION = "1.3"

    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x720")
        self.photo_cache = {}
        self.setup_styles()
        
        self.current_chat_target = "general"
        self.after_id = None
        self.contacts_after_id = None
        self.last_msg_count = 0
        self.is_recording_voice = False
        self.is_recording_screen = False
        self.last_click_time = 0
        
        if not FIREBASE_AVAILABLE:
            messagebox.showwarning("Внимание", "Firebase недоступен! Проверьте файл serviceAccountKey.json")
            
        saved_user = SessionManager.load_session()
        if saved_user and FirebaseDB.get_user(saved_user):
            self.show_main_interface(saved_user)
        else:
            SessionManager.clear_session()
            self.show_auth_window()

    def setup_styles(self):
        theme_name = manager.settings.get("theme", "dark")
        self.colors = THEMES.get(theme_name, THEMES["dark"])
        self.font_family = manager.settings.get("font", "Segoe UI")
        self.lang_code = manager.settings.get("lang", "ru")
        self.t = LANGUAGES.get(self.lang_code, LANGUAGES["ru"])
        
        ctk.set_appearance_mode("Dark" if theme_name == "dark" else "Light")
        self.root.configure(fg_color=self.colors["bg"])

    def show_auth_window(self):
        self.cancel_chat_polling()
        self.cancel_contacts_polling()
        SessionManager.clear_session()
        for widget in self.root.winfo_children(): widget.destroy()
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
        for widget in self.root.winfo_children(): widget.destroy()
        self.setup_styles()
        self.current_user = username
        self.root.title(f"Nova Messenger Pro - [{username}]")
        
        self.sidebar = ctk.CTkFrame(self.root, fg_color=self.colors["sidebar"], width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.content = ctk.CTkFrame(self.root, fg_color=self.colors["bg"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)
        
        self.render_navigation()
        self.switch_tab("chats")

    def render_navigation(self):
        for widget in self.sidebar.winfo_children(): widget.destroy()
        
        # Добавлена поддержка "support" в сайдбар
        tabs = ["chats", "notes", "profile", "updates", "settings", "support"]
        names = {
            "chats": self.t["chats"], "notes": self.t["notes"], 
            "profile": self.t["profile"], "updates": self.t["updates"], 
            "settings": self.t["settings"], "support": self.t["support"]
        }
        
        for tab in tabs:
            ctk.CTkButton(self.sidebar, text=names[tab], command=lambda t=tab: self.switch_tab(t),
                          fg_color="transparent", text_color=self.colors["fg"], hover_color=self.colors["entry_bg"],
                          font=(self.font_family, 12), anchor="w", corner_radius=8).pack(fill="x", padx=15, pady=4, ipady=5)
            
        if self.current_user.lower() in ["никита", "nikita"]:
            ctk.CTkButton(self.sidebar, text=self.t["admin"], command=lambda: self.switch_tab("admin"),
                          fg_color="#332244", text_color="#ff99ff", hover_color="#442a55",
                          font=(self.font_family, 12, "bold"), anchor="w", corner_radius=8).pack(fill="x", padx=15, pady=4, ipady=5)

        ctk.CTkButton(self.sidebar, text=self.t["logout"], command=self.show_auth_window,
                      fg_color="#442222", text_color="white", hover_color="#552a2a",
                      font=(self.font_family, 11), anchor="w", corner_radius=8).pack(side="bottom", fill="x", padx=15, pady=15, ipady=5)

    def cancel_chat_polling(self):
        if hasattr(self, 'after_id') and self.after_id:
            try: 
                self.root.after_cancel(self.after_id)
            except: 
                pass
            self.after_id = None

    def cancel_contacts_polling(self):
        if hasattr(self, 'contacts_after_id') and self.contacts_after_id:
            try:
                self.root.after_cancel(self.contacts_after_id)
            except:
                pass
            self.contacts_after_id = None

    def switch_tab(self, tab_name):
        self.cancel_chat_polling()
        self.cancel_contacts_polling()
        for widget in self.content.winfo_children(): widget.destroy()
        
        if tab_name == "notes": self.render_notes_panel()
        elif tab_name == "profile": self.render_profile_panel()
        elif tab_name == "chats": self.render_chats_panel()
        elif tab_name == "settings": self.render_settings_panel()
        elif tab_name == "updates": self.render_updates_panel()
        elif tab_name == "support": self.render_support_panel()
        elif tab_name == "admin" and self.current_user.lower() in ["никита", "nikita"]:
            self.render_admin_panel()

    # --- ВКЛАДКА ТЕХПОДДЕРЖКИ ---
    def render_support_panel(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Заголовок
        ctk.CTkLabel(f, text=self.t["support_title"], text_color=self.colors["accent"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Требуемый текст над кнопкой
        ctk.CTkLabel(f, text=self.t["support_desc"], text_color=self.colors["fg"], font=(self.font_family, 13), wraplength=500, justify="left").pack(anchor="w", pady=(0, 20))
        
        # Функция открытия ссылки в браузере
        def open_telegram():
            # Замените 'https://t.me/your_telegram_username' на нужную вам ссылку
            webbrowser.open("https://t.me/nova_mesenger_support_bot")

        # Кнопка перехода
        ctk.CTkButton(
            f, 
            text=self.t["support_btn"], 
            command=open_telegram, 
            fg_color=self.colors["accent"], 
            text_color="white", 
            corner_radius=8, 
            height=38,
            font=(self.font_family, 13, "bold")
        ).pack(anchor="w")

    def render_updates_panel(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(f, text=self.t["updates_center"], text_color=self.colors["accent"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(f, text=f"{self.t['current_version']}{self.CURRENT_VERSION} Pro", text_color=self.colors["fg"], font=(self.font_family, 12)).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkButton(f, text=self.t["check_updates"], command=lambda: self.check_for_updates_threaded(manual=True), 
                      fg_color=self.colors["accent"], text_color="white", font=(self.font_family, 11), corner_radius=8).pack(anchor="w", pady=10)

        self.update_result_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.update_result_frame.pack(fill="x", pady=10)
        
        self.check_for_updates_threaded(manual=False)

    def check_for_updates_threaded(self, manual=False):
        for widget in self.update_result_frame.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(self.update_result_frame, text=self.t["checking_server"], text_color="#888888", font=(self.font_family, 11)).pack(anchor="w")

        def background_check():
            remote_info = FirebaseDB.get_latest_version_info()
            self.root.after(0, lambda: self.apply_update_result(remote_info, manual))

        threading.Thread(target=background_check, daemon=True).start()

    def apply_update_result(self, remote_info, manual):
        for widget in self.update_result_frame.winfo_children(): widget.destroy()
        
        if not remote_info:
            if manual:
                messagebox.showerror(self.t["error"], self.t["server_err"])
            else:
                ctk.CTkLabel(self.update_result_frame, text=self.t["no_connection"], text_color="#888888", font=(self.font_family, 11)).pack(anchor="w")
            return

        latest_ver = remote_info.get("latest_version", self.CURRENT_VERSION)
        
        def parse_version(v):
            return tuple(map(int, (v.split("."))))

        try:
            is_newer = parse_version(latest_ver) > parse_version(self.CURRENT_VERSION)
        except:
            is_newer = latest_ver != self.CURRENT_VERSION

        if is_newer:
            card = ctk.CTkFrame(self.update_result_frame, fg_color="#2d4433", corner_radius=12)
            card.pack(fill="x", padx=0, pady=10)
            
            ctk.CTkLabel(card, text=f"{self.t['new_version_available']}{latest_ver}!", text_color="#00ffcc", font=(self.font_family, 13, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=remote_info.get("notes", "Без описания изменений."), text_color="white", font=(self.font_family, 11), justify="left").pack(anchor="w", padx=20, pady=(0, 10))
            
            if "url" in remote_info:
                ctk.CTkButton(card, text=self.t["download_update"], command=lambda: os.startfile(remote_info["url"]), fg_color="#00aa55", text_color="white", corner_radius=8).pack(anchor="w", padx=20, pady=(0, 15))
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
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(f, text=self.t["profile"], text_color=self.colors["fg"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        user_data = FirebaseDB.get_user(self.current_user) or {}
        
        card = ctk.CTkFrame(f, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(card, text=f"{self.t['username']}: {self.current_user}", text_color=self.colors["accent"], font=(self.font_family, 14, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        notes_count = len(FirebaseDB.get_notes(self.current_user))
        chats_count = len(FirebaseDB.get_chats(self.current_user))
        stats_text = f"{self.t['notes_count']}{notes_count}{self.t['active_chats_count']}{chats_count}"
        ctk.CTkLabel(card, text=stats_text, text_color=self.colors["fg"], font=(self.font_family, 11)).pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(f, text=self.t["about_me"], text_color=self.colors["fg"], font=(self.font_family, 11, "bold")).pack(anchor="w", pady=(15, 5))
        self.profile_bio_entry = ctk.CTkEntry(f, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.profile_bio_entry.pack(fill="x", ipady=5)
        self.profile_bio_entry.insert(0, user_data.get("bio", ""))

        ctk.CTkLabel(f, text=self.t["avatar_path"], text_color=self.colors["fg"], font=(self.font_family, 11, "bold")).pack(anchor="w", pady=(15, 5))
        self.profile_avatar_entry = ctk.CTkEntry(f, font=(self.font_family, 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.profile_avatar_entry.pack(fill="x", ipady=5)
        self.profile_avatar_entry.insert(0, user_data.get("avatar", ""))

        ctk.CTkButton(f, text=self.t["save"], command=self.save_profile_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="w", pady=20)

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
        ctk.CTkButton(input_box, text=self.t["add"], command=self.add_note_logic, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="e", padx=15, pady=(0, 15))

        self.notes_inner = ctk.CTkScrollableFrame(self.notes_frame, fg_color="transparent")
        self.notes_inner.pack(fill="both", expand=True, pady=10)
        self.load_notes_ui()

    def load_notes_ui(self):
        for widget in self.notes_inner.winfo_children(): widget.destroy()
        notes = FirebaseDB.get_notes(self.current_user)
        for item in notes:
            text = item.get("text", "") if isinstance(item, dict) else item
            lbl = ctk.CTkLabel(self.notes_inner, text=text, fg_color=self.colors["card_bg"], text_color=self.colors["fg"], font=(self.font_family, 11), corner_radius=8, anchor="w", padx=15, pady=10)
            lbl.pack(fill="x", pady=3)

    def add_note_logic(self):
        text = self.note_input.get().strip()
        if text:
            notes = FirebaseDB.get_notes(self.current_user)
            notes.append({"text": text})
            FirebaseDB.save_notes(self.current_user, notes)
            self.note_input.delete(0, 'end')
            self.load_notes_ui()

    def render_chats_panel(self):
        self.cancel_contacts_polling()
        for widget in self.content.winfo_children(): widget.destroy()

        chats_frame = ctk.CTkFrame(self.content, fg_color="transparent", corner_radius=0)
        chats_frame.pack(fill="both", expand=True)

        left_panel = ctk.CTkFrame(chats_frame, fg_color=self.colors["sidebar"], width=220, corner_radius=0)
        left_panel.pack(side="left", fill="y")

        ctk.CTkLabel(left_panel, text=self.t["dialogs"], text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", padx=15, pady=15)
        ctk.CTkButton(left_panel, text=self.t["new_chat"], command=self.add_new_chat_dialog, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], hover_color=self.colors["bg"], font=(self.font_family, 11), corner_radius=8).pack(fill="x", padx=15, pady=(0, 10))

        self.contacts_list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.contacts_list_frame.pack(fill="both", expand=True, padx=5)

        if FirebaseDB.is_in_general_chat(self.current_user):
            ctk.CTkButton(left_panel, text=self.t["general_chat"], command=lambda: self.open_chat_with("general"), 
                          fg_color="transparent", text_color=self.colors["accent"], hover_color=self.colors["entry_bg"], 
                          font=(self.font_family, 11, "bold"), anchor="w", corner_radius=8).pack(fill="x", padx=15, pady=10, side="bottom")

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
                for widget in self.active_chat_panel.winfo_children(): widget.destroy()
                ctk.CTkLabel(self.active_chat_panel, text=self.t["select_chat_left"], text_color=self.colors["fg"], font=(self.font_family, 14)).pack(expand=True)
        else:
            self.open_chat_with(self.current_chat_target)

    def load_contacts_list(self):
        my_chats = FirebaseDB.get_chats(self.current_user)
        current_buttons = {btn.cget("text") for btn in self.contacts_list_frame.winfo_children() if isinstance(btn, ctk.CTkButton)}
        
        if current_buttons == set(my_chats):
            return 
            
        for widget in self.contacts_list_frame.winfo_children(): widget.destroy()
        
        for username in my_chats:
            btn = ctk.CTkButton(self.contacts_list_frame, text=username, command=lambda u=username: self.open_chat_with(u), fg_color="transparent", text_color=self.colors["fg"], hover_color=self.colors["entry_bg"], font=(self.font_family, 11), anchor="w", corner_radius=6)
            btn.pack(fill="x", pady=2)
            btn.bind("<Button-3>", lambda e, u=username: self.show_chat_context_menu(e, u))

    def start_contacts_polling(self):
        self.cancel_contacts_polling()

        def poll_contacts():
            if not hasattr(self, 'current_user') or not self.current_user:
                return
            
            def background_fetch():
                try:
                    my_chats = FirebaseDB.get_chats(self.current_user)
                    self.root.after(0, lambda: self.update_contacts_safely(my_chats))
                except:
                    pass

            threading.Thread(target=background_fetch, daemon=True).start()

            try:
                self.contacts_after_id = self.root.after(4000, poll_contacts)
            except:
                pass

        self.contacts_after_id = self.root.after(4000, poll_contacts)

    def update_contacts_safely(self, my_chats):
        current_buttons = {btn.cget("text") for btn in self.contacts_list_frame.winfo_children() if isinstance(btn, ctk.CTkButton)}
        if current_buttons != set(my_chats):
            self.load_contacts_list()

    def show_chat_context_menu(self, event, target_user):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["entry_bg"], fg=self.colors["fg"])
        menu.add_command(label=self.t["delete"], command=lambda: self.delete_chat_action(target_user))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def delete_chat_action(self, target_user):
        if messagebox.askyesno(self.t["delete_chat_title"], f"{self.t['delete_chat_q']}{target_user}?"):
            chat_key = f"{min(self.current_user, target_user)}_{max(self.current_user, target_user)}"
            FirebaseDB.remove_chat(self.current_user, target_user)
            FirebaseDB.delete_entire_chat(chat_key)
            
            if self.current_chat_target == target_user:
                self.render_chats_panel()
            else:
                self.load_contacts_list()

    def add_new_chat_dialog(self):
        target_user = simpledialog.askstring(self.t["new_chat_title"], self.t["new_chat_prompt"])
        if target_user:
            target_user = target_user.strip().lower()
            if target_user == "general":
                FirebaseDB.join_general_chat(self.current_user)
                self.render_chats_panel()
                self.open_chat_with("general")
                return

            if target_user == self.current_user:
                messagebox.showerror(self.t["error"], self.t["self_chat_err"])
                return
                
            if FirebaseDB.get_user(target_user):
                FirebaseDB.add_chat_for(self.current_user, target_user)
                FirebaseDB.add_chat_for(target_user, self.current_user)
                
                self.render_chats_panel()
                self.open_chat_with(target_user)
            else:
                messagebox.showerror(self.t["error"], self.t["user_not_found"])

    def leave_general_chat_action(self):
        if messagebox.askyesno(self.t["leave_chat_title"], self.t["leave_chat_q"]):
            FirebaseDB.leave_general_chat(self.current_user)
            my_chats = FirebaseDB.get_chats(self.current_user)
            if my_chats:
                self.current_chat_target = my_chats[0]
            else:
                self.current_chat_target = ""
            self.render_chats_panel()

    def open_chat_with(self, target):
        self.cancel_chat_polling()
        self.current_chat_target = target
        for widget in self.active_chat_panel.winfo_children(): widget.destroy()

        header_frame = ctk.CTkFrame(self.active_chat_panel, fg_color=self.colors["sidebar"], height=60, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        
        title_text = self.t["general_chat"] if target == "general" else f"Чат с: {target}" if self.lang_code == "ru" else f"Chat with: {target}"
        ctk.CTkLabel(header_frame, text=title_text, text_color=self.colors["fg"], font=(self.font_family, 13, "bold")).pack(side="left", padx=20, pady=15)

        if target == "general":
            ctk.CTkButton(header_frame, text="🚪 " + ("Покинуть чат" if self.lang_code == "ru" else "Leave chat"), command=self.leave_general_chat_action, fg_color="#aa3333", text_color="white", width=120, corner_radius=6).pack(side="right", padx=20)

        self.typing_status_lbl = ctk.CTkLabel(header_frame, text="", text_color="#888888", font=(self.font_family, 10, "italic"))
        self.typing_status_lbl.pack(side="left", padx=10)

        self.chat_messages_inner = ctk.CTkScrollableFrame(self.active_chat_panel, fg_color="transparent")
        self.chat_messages_inner.pack(fill="both", expand=True, padx=10, pady=5)

        input_panel = ctk.CTkFrame(self.active_chat_panel, fg_color=self.colors["sidebar"], height=70, corner_radius=0)
        input_panel.pack(fill="x", side="bottom")

        ctk.CTkButton(input_panel, text="🖼️", command=self.send_image_message, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8).pack(side="left", padx=10, pady=15)
        self.voice_btn_widget = ctk.CTkButton(input_panel, text="🎤", command=self.toggle_voice_record, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8)
        self.voice_btn_widget.pack(side="left", padx=2, pady=15)
        
        self.screen_btn_widget = ctk.CTkButton(input_panel, text="📹", command=self.toggle_screen_record, fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], width=40, corner_radius=8)
        self.screen_btn_widget.pack(side="left", padx=2, pady=15)

        self.chat_msg_input = ctk.CTkEntry(input_panel, font=("Segoe UI Emoji", 12), fg_color=self.colors["entry_bg"], text_color=self.colors["fg"], corner_radius=8)
        self.chat_msg_input.pack(side="left", fill="x", expand=True, padx=10, ipady=5)
        self.chat_msg_input.bind("<Return>", lambda e: self.send_text_message())
        self.chat_msg_input.bind("<KeyRelease>", self.on_user_typing)

        ctk.CTkButton(input_panel, text=self.t["send"], command=self.send_text_message, fg_color=self.colors["accent"], text_color="white", width=90, corner_radius=8).pack(side="right", padx=15, pady=15)

        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        FirebaseDB.mark_read(chat_key, self.current_user)

        self.load_active_chat_messages()
        self.start_chat_polling()

    def on_user_typing(self, event):
        target = self.current_chat_target
        if target == "general" and not FirebaseDB.is_in_general_chat(self.current_user): return
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        FirebaseDB.set_typing(chat_key, self.current_user)

    def start_chat_polling(self):
        self.cancel_chat_polling()

        def poll():
            if not hasattr(self, 'current_chat_target') or not self.current_chat_target:
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
                    except:
                        pass

                def process_poll_data(t_info, msgs):
                    if getattr(self, 'current_chat_target', None) != target:
                        return

                    if t_info and t_info.get("user") != self.current_user:
                        if time.time() - t_info.get("time", 0) < 3:
                            self.typing_status_lbl.configure(text=f"{t_info.get('user')}{self.t['typing']}")
                        else:
                            self.typing_status_lbl.configure(text="")
                    else:
                        self.typing_status_lbl.configure(text="")

                    if len(msgs) > self.last_msg_count:
                        self.last_msg_count = len(msgs)
                        FirebaseDB.mark_read(chat_key, self.current_user)
                        self.load_active_chat_messages(is_polling=True)

                threading.Thread(target=background_fetch, daemon=True).start()

            except: 
                pass
            
            try:
                self.after_id = self.root.after(3000, poll)
            except:
                pass

        self.after_id = self.root.after(3000, poll)

    def load_active_chat_messages(self, is_polling=False):
        target = getattr(self, 'current_chat_target', 'general')
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        messages = FirebaseDB.get_messages(chat_key)
        self.last_msg_count = len(messages)

        for widget in self.chat_messages_inner.winfo_children(): widget.destroy()

        for msg in messages:
            if not isinstance(msg, dict): continue
            is_mine = msg.get("user") == self.current_user
            bubble_bg = self.colors["bubble_mine"] if is_mine else self.colors["bubble_other"]
            msg_id = msg.get("id")

            card = ctk.CTkFrame(self.chat_messages_inner, fg_color=bubble_bg, corner_radius=12)
            card.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(card, text=msg.get("user", "Unknown"), text_color="#aaaaaa", font=(self.font_family, 9, "bold")).pack(anchor="w", padx=12, pady=(6, 0))

            msg_type = msg.get("type", "text")
            
            if msg_type == "text":
                text = msg.get("text", "")
                if text:
                    lbl = ctk.CTkLabel(card, text=text, text_color="white" if is_mine else self.colors["fg"], font=("Segoe UI Emoji", 11), justify="left", wraplength=500)
                    lbl.pack(anchor="w", padx=12, pady=4)
            
            elif msg_type == "image":
                try:
                    img_data = base64.b64decode(msg.get("data", ""))
                    tmp_path = os.path.join(IMAGES_DIR, f"temp_{time.time()}.png")
                    with open(tmp_path, "wb") as f: f.write(img_data)
                    
                    pil_img = Image.open(tmp_path)
                    pil_img.thumbnail((200, 200))
                    tk_img = ImageTk.PhotoImage(pil_img)
                    self.photo_cache[tmp_path] = tk_img
                    
                    lbl = tk.Label(card, image=tk_img, bg=bubble_bg)
                    lbl.pack(anchor="w", padx=12, pady=4)
                except:
                    ctk.CTkLabel(card, text=self.t["img_load_err"], text_color="red").pack(anchor="w", padx=12, pady=4)

            elif msg_type == "voice":
                voice_data = base64.b64decode(msg.get("data", ""))
                v_path = os.path.join(VOICES_DIR, f"voice_{time.time()}.wav")
                with open(v_path, "wb") as f: f.write(voice_data)
                
                ctk.CTkButton(card, text=self.t["listen_voice"], command=lambda p=v_path: threading.Thread(target=self.play_voice, args=(p,)).start(), fg_color="#444", text_color="white", corner_radius=6, height=28).pack(anchor="w", padx=12, pady=6)

            elif msg_type == "video":
                v_name = msg.get("name", "screen_record.mp4")
                ctk.CTkButton(card, text=f"{self.t['save_screen_rec']}{v_name}", command=lambda m=msg: self.save_and_play_video(m), fg_color="#444", text_color="white", corner_radius=6, height=28).pack(anchor="w", padx=12, pady=6)

            if is_mine:
                read_status = "✓✓" if msg.get("read", False) else "✓"
                ctk.CTkLabel(card, text=read_status, text_color="#00ffcc" if msg.get("read") else "#aaaaaa", font=(self.font_family, 9)).pack(anchor="e", padx=12, pady=(0, 6))

            for widget_to_bind in card.winfo_children():
                widget_to_bind.bind("<Button-3>", lambda e, m_id=msg_id, m_user=msg.get("user"): self.show_context_menu(e, m_id, m_user))
            card.bind("<Button-3>", lambda e, m_id=msg_id, m_user=msg.get("user"): self.show_context_menu(e, m_id, m_user))

        self.chat_messages_inner._parent_canvas.yview_moveto(1.0)

    def show_context_menu(self, event, msg_id, msg_user):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors["entry_bg"], fg=self.colors["fg"])
        if msg_user == self.current_user:
            menu.add_command(label=self.t["edit"], command=lambda: self.edit_message_action(msg_id))
            menu.add_command(label=self.t["delete"], command=lambda: self.delete_message_action(msg_id))
        else:
            menu.add_command(label=self.t["info"], command=lambda: messagebox.showinfo(self.t["info"], f"Автор / Author: {msg_user}"))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def edit_message_action(self, msg_id):
        new_text = simpledialog.askstring(self.t["edit_title"], self.t["edit_prompt"])
        if new_text:
            target = getattr(self, 'current_chat_target', 'general')
            chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
            FirebaseDB.update_message(chat_key, msg_id, new_text.strip())
            self.load_active_chat_messages()

    def delete_message_action(self, msg_id):
        if messagebox.askyesno(self.t["delete_msg_title"], self.t["delete_msg_q"]):
            target = getattr(self, 'current_chat_target', 'general')
            chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
            FirebaseDB.delete_message(chat_key, msg_id)
            self.load_active_chat_messages()

    def send_text_message(self):
        text = self.chat_msg_input.get().strip()
        if not text: return

        target = getattr(self, 'current_chat_target', 'general')
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"
        
        FirebaseDB.add_chat_for(self.current_user, target)
        FirebaseDB.add_chat_for(target, self.current_user)

        new_msg = {"user": self.current_user, "target": target, "type": "text", "text": text, "read": False}
        FirebaseDB.add_message(chat_key, new_msg)
        self.chat_msg_input.delete(0, 'end')
        self.load_active_chat_messages()

    def send_image_message(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not file_path: return

        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        target = getattr(self, 'current_chat_target', 'general')
        chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

        FirebaseDB.add_chat_for(self.current_user, target)
        FirebaseDB.add_chat_for(target, self.current_user)

        new_msg = {"user": self.current_user, "target": target, "type": "image", "data": encoded, "read": False}
        FirebaseDB.add_message(chat_key, new_msg)
        self.load_active_chat_messages()

    def toggle_screen_record(self):
        if not self.is_recording_screen:
            self.is_recording_screen = True
            self.screen_btn_widget.configure(fg_color="red")
            self.v_filename = f"screen_{int(time.time())}.mp4"
            self.v_path = os.path.join(VIDEOS_DIR, self.v_filename)
            
            def record_loop():
                fps = 20.0
                with mss.mss() as sct:
                    monitor = sct.monitors[1] 
                    width = monitor["width"]
                    height = monitor["height"]
                    
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(self.v_path, fourcc, fps, (width, height))
                    
                    while self.is_recording_screen:
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
                
                if os.path.exists(self.v_path) and os.path.getsize(self.v_path) > 0:
                    with open(self.v_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                    
                    target = getattr(self, 'current_chat_target', 'general')
                    chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

                    FirebaseDB.add_chat_for(self.current_user, target)
                    FirebaseDB.add_chat_for(target, self.current_user)

                    new_msg = {"user": self.current_user, "target": target, "type": "video", "name": self.v_filename, "data": encoded, "read": False}
                    FirebaseDB.add_message(chat_key, new_msg)
                    self.load_active_chat_messages()

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
                with open(save_path, "wb") as f: f.write(video_data)
                messagebox.showinfo(self.t["success"], f"{self.t['video_saved']}{save_path}")
        except Exception as e:
            messagebox.showerror(self.t["error"], f"{self.t['save_file_err']}{e}")

    def toggle_voice_record(self):
        if not self.is_recording_voice:
            self.is_recording_voice = True
            self.voice_btn_widget.configure(fg_color="red")
            self.sample_rate = 44100
            self.recorded_frames = []
            
            def callback(indata, frames, time_info, status):
                if self.is_recording_voice:
                    self.recorded_frames.append(indata.copy())

            self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback)
            self.stream.start()
        else:
            self.is_recording_voice = False
            self.voice_btn_widget.configure(fg_color=self.colors["entry_bg"])
            try:
                self.stream.stop()
                self.stream.close()
            except: pass

            if self.recorded_frames:
                audio_data = np.concatenate(self.recorded_frames, axis=0)
                v_path = os.path.join(VOICES_DIR, f"rec_{time.time()}.wav")
                
                with wave.open(v_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

                with open(v_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')

                target = getattr(self, 'current_chat_target', 'general')
                chat_key = "general" if target == "general" else f"{min(self.current_user, target)}_{max(self.current_user, target)}"

                FirebaseDB.add_chat_for(self.current_user, target)
                FirebaseDB.add_chat_for(target, self.current_user)

                new_msg = {"user": self.current_user, "target": target, "type": "voice", "data": encoded, "read": False}
                FirebaseDB.add_message(chat_key, new_msg)
                self.load_active_chat_messages()

    def play_voice(self, path):
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME)
        except:
            pass

    def render_settings_panel(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(f, text=self.t["settings"], text_color=self.colors["fg"], font=(self.font_family, 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(f, text=self.t["theme"], text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.theme_var = tk.StringVar(value=manager.settings.get("theme", "dark"))
        ctk.CTkRadioButton(f, text=self.t["dark"], variable=self.theme_var, value="dark", text_color=self.colors["fg"]).pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(f, text=self.t["light"], variable=self.theme_var, value="light", text_color=self.colors["fg"]).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(f, text="Язык / Language", text_color=self.colors["fg"], font=(self.font_family, 12, "bold")).pack(anchor="w", pady=(15, 5))
        self.lang_var = tk.StringVar(value=manager.settings.get("lang", "ru"))
        ctk.CTkRadioButton(f, text="Русский", variable=self.lang_var, value="ru", text_color=self.colors["fg"]).pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(f, text="English", variable=self.lang_var, value="en", text_color=self.colors["fg"]).pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(f, text=self.t["save"], command=self.save_settings_action, fg_color=self.colors["accent"], text_color="white", corner_radius=8).pack(anchor="w", pady=30)

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