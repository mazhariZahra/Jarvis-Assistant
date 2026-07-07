import datetime
import speech_recognition as sr
import wikipedia
import wolframalpha
import webbrowser
import pygame
import os
import tempfile
import time
import edge_tts
import random
import threading
import struct
import math
import requests
from PIL import ImageGrab
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import threading
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from dotenv import load_dotenv
load_dotenv()

print("در حال راه‌اندازی جارویس...")
pygame.mixer.init()

# ==================== تنظیمات صدا با edge-tts ====================
VOICE = "fa-IR-DilaraNeural"  # صدای زنانه فارسی (fa-IR-FaridNeural = مردانه)

def speak(text):
    print(f"J.A.R.V.I.S: {text}")
    try:
        asyncio.run(_speak_async(text))
    except Exception as e:
        print(f"خطای صدا: {e}")

async def _speak_async(text):
    communicate = edge_tts.Communicate(text, VOICE)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    await communicate.save(filename)
    
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    pygame.mixer.music.unload()
    os.remove(filename)

# ==================== شنیدن صدا ====================
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 در حال گوش دادن... (چیزی بگو)")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            print("⏳ در حال تشخیص...")
            query = r.recognize_google(audio, language="fa-IR")
            print(f"🗣️ شما: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("❌ متوجه نشدم.")
            return ""
        except sr.RequestError:
            print("❌ اینترنت قطع شده.")
            return ""
        except Exception as e:
            print(f"❌ خطا: {e}")
            return ""

# ==================== تنظیمات موسیقی ====================
MUSIC_PATH = r"D:\music"
song_list = []
current_index = -1

def play_music():
    """پخش یه آهنگ تصادفی از پوشه موسیقی"""
    global song_list, current_index
    try:
        song_list = [f for f in os.listdir(MUSIC_PATH) if f.endswith(('.mp3', '.wav', '.flac'))]
        if song_list:
            current_index = random.randint(0, len(song_list) - 1)
            song = song_list[current_index]
            song_path = os.path.join(MUSIC_PATH, song)
            speak(f"در حال پخش {song}")
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
        else:
            speak("هیچ آهنگی توی پوشه پیدا نکردم.")
    except Exception as e:
        speak("نتونستم آهنگ رو پخش کنم.")

def next_song():
    """پخش آهنگ بعدی"""
    global song_list, current_index
    if not song_list:
        speak("لیست آهنگ خالیه. اول یه آهنگ پخش کن.")
        return
    current_index = (current_index + 1) % len(song_list)
    song = song_list[current_index]
    song_path = os.path.join(MUSIC_PATH, song)
    speak(f"آهنگ بعدی: {song}")
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def prev_song():
    """پخش آهنگ قبلی"""
    global song_list, current_index
    if not song_list:
        speak("لیست آهنگ خالیه. اول یه آهنگ پخش کن.")
        return
    current_index = (current_index - 1) % len(song_list)
    song = song_list[current_index]
    song_path = os.path.join(MUSIC_PATH, song)
    speak(f"آهنگ قبلی: {song}")
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def list_songs():
    """گفتن لیست آهنگ های موجود"""
    global song_list
    try:
        song_list = [f for f in os.listdir(MUSIC_PATH) if f.endswith(('.mp3', '.wav', '.flac'))]
        if not song_list:
            speak("هیچ آهنگی توی پوشه پیدا نکردم")
            return
        speak(f"توی پوشه موسیقی {len(song_list)} تا آهنگ داریم:")
        for i, song in enumerate(song_list, 1):
            #حذف پسوند فایل برای خواندن راحت تر
            name = os.path.splitext(song)[0]
            speak(f"شماره {i}:{name}")
            time.sleep(0.3)  #یه مکث کوچیک بین اسم ها
    except Exception as e:
        speak("نتونستم لیست آهنگ ها رو بخونم.")

def play_specific_song(query):
    """پخش آهنگ با اسم یا شماره"""
    global song_list, current_index
    try:
        song_list = [f for f in os.listdir(MUSIC_PATH) if f.endswith(('.mp3', '.wav', '.flac'))]
        if not song_list:
            speak("هیچ آهنگی توی پوشه پیدا نکردم")
            return
        
        #خذف کلمات اضافه از query
        query = query.replace("پخش کن", "").replace("آهنگ", "").replace("موزیک", "").replace("موسیقی", "").strip()

        #اول چک میکنیم ببینیم شماره گفته یا نه
        #مثلا "شماره 3 رو پخش کن"
        for word in query.split():
            if word.isdigit():
                index = int(word) - 1
                if 0 <= index < len(song_list):
                    current_index = index
                    song = song_list[current_index]
                    song_path = os.path.join(MUSIC_PATH, song)
                    speak(f"در حال پخش شماره {word}: {os.path.splitext(song)[0]}")
                    pygame.mixer.music.load(song_path)
                    pygame.mixer.music.play()
                    return
                else:
                    speak(f"شماره {word} وجود نداره فقط 1 تا {len(song_list)} آهنگ داریم.")
                    return
                
        #اگه شماره نبود دنبال اسم میگردیم
        for i, song in enumerate(song_list):
            name = os.path.splitext(song)[0].lower()
            if query.lower() in name:
                current_index = i
                song_path = os.path.join(MUSIC_PATH, song)
                speak(f"در حال پخش {os.path.splitext(song)[0]}")
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                return
            
        speak(f"آهنگی با اسم {query} پیدا نکردم.")

    except Exception as e:
        speak("نتونستم آهنگ رو پخش کنم")

#-------------------یادداشت ------------

NOTES_FILE = r"D:\AI project\note\notes.txt"

def take_note():
    """گرفتن یادداشت از کاربر و ذخیره فایل"""
    speak("چی رو یادداشت کنم؟")
    note = take_command()
    if note:
        try:
            with open(NOTES_FILE, "a", encoding="utf-8") as f:
                now = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
                f.write(f"[{now}] {note}\n")
            speak("یادداشت ذخیره شد.")
        except:
            speak("نتونستم یادداشت ذخیره کنم.")
    else:
        speak("چیزی نشنیدم. دوباره امتحان کن.")

def read_notes():
    """خوندن یادداشت‌های ذخیره شده"""
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = f.read()
        if notes.strip():
            speak("یادداشت‌های شما:")
            speak(notes)
        else:
            speak("هنوز هیچ یادداشتی ننوشتی.")
    except FileNotFoundError:
        speak("هنوز هیچ یادداشتی ننوشتی.")
    except:
        speak("نتونستم یادداشت‌ها رو بخونم.")

#----------- آلارم -------------

alarm_active = False

def set_alarm():
    """تنظیم آلارم"""
    global alarm_active
    speak("برای چه ساعتی آلارم بزارم؟ مثلاً بگو ۷ و ۳۰ دقیقه")
    
    time_query = take_command()
    if not time_query:
        speak("زمان رو متوجه نشدم.")
        return
    
    try:
        # تبدیل اعداد فارسی به انگلیسی
        persian_nums = "۰۱۲۳۴۵۶۷۸۹"
        english_nums = "0123456789"
        for p, e in zip(persian_nums, english_nums):
            time_query = time_query.replace(p, e)
        
        # حذف کلمات اضافه
        time_query = time_query.replace("ساعت", "").replace("دقیقه", "").strip()
        # جایگزینی "و" با فاصله
        time_query = time_query.replace("و", " ")
        
        parts = time_query.split()
        
        if len(parts) >= 2:
            hour = int(parts[0])
            minute = int(parts[1])
        elif len(parts) == 1:
            hour = int(parts[0])
            minute = 0
        else:
            speak("فرمت زمان رو متوجه نشدم.")
            return
        
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            speak("زمان نامعتبره.")
            return
        
        speak(f"آلارم برای ساعت {hour} و {minute} دقیقه تنظیم شد.")
        
        alarm_thread = threading.Thread(target=_wait_for_alarm, args=(hour, minute))
        alarm_thread.daemon = True
        alarm_thread.start()
    
    except:
        speak("نتونستم زمان رو تشخیص بدم. دوباره بگو.")

def _wait_for_alarm(hour, minute):
    """منتظر موندن تا زمان آلارم برسه"""
    global alarm_active
    alarm_active = True
    
    while alarm_active:
        now = datetime.datetime.now()
        if now.hour == hour and now.minute == minute:
            speak("آلارم! وقتشه! بگو قطع کن تا خاموش بشه.")
            
            try:
                sample_rate = 44100
                duration = 0.3
                frequency = 880
                
                num_samples = int(sample_rate * duration)
                samples = []
                for i in range(num_samples):
                    value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * i / sample_rate))
                    samples.append(struct.pack('<h', value))
                
                beep_data = b''.join(samples)
                
                # تبدیل به stereo
                stereo_data = b''
                for i in range(0, len(beep_data), 2):
                    sample = beep_data[i:i+2]
                    stereo_data += sample + sample
                
                beep_sound = pygame.mixer.Sound(buffer=stereo_data)
                beep_sound.play(-1)
                
                while alarm_active:
                    q = take_command()
                    if q and ("قطع" in q or "بسه" in q or "توقف" in q):
                        beep_sound.stop()
                        speak("آلارم قطع شد.")
                        alarm_active = False
                        break
                    time.sleep(1)
            except:
                alarm_active = False
            break
        time.sleep(10)

#----------------- آب و هوا -------------------------
def get_weather(query=""):
    """گرفتن وضعیت آب و هوا"""
    try:
        city = "Damghan"
        
        if "دامغان" in query:
            city = "Damghan"
        elif "تهران" in query:
            city = "Tehran"
        elif "اصفهان" in query:
            city = "Isfahan"
        elif "شیراز" in query:
            city = "Shiraz"
        elif "مشهد" in query:
            city = "Mashhad"
        elif "تبریز" in query:
            city = "Tabriz"
        elif "کرج" in query:
            city = "Karaj"
        elif "اهواز" in query:
            city = "Ahvaz"
        elif "قم" in query:
            city = "Qom"
        elif "رشت" in query:
            city = "Rasht"
        elif "یزد" in query:
            city = "Yazd"
        
        WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
        res = requests.get(url)
        data = res.json()
        
        if res.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            
            speak(f"وضعیت هوای {city}: {desc}")
            speak(f"دما {temp} درجه سانتی‌گراد")
            speak(f"رطوبت {humidity} درصد")
            speak(f"سرعت باد {wind} متر بر ثانیه")
        else:
            speak("نتونستم وضعیت هوا رو بگیرم.")
    except:
        speak("خطا در دریافت اطلاعات آب و هوا.")

#----------------------- اسکرین شات ------------------

SCREENSHOT_PATH = r"D:\AI project\Screenshots"

def take_screenshot():
    """گرفتن اسکرین شات و ذخیره آن"""
    try:
        #ساخت پوشه اگر وجود نداره
        if not os.path.exists(SCREENSHOT_PATH):
            os.makedirs(SCREENSHOT_PATH)
        
        #اسم فایل با تاریخ و ساعت
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{now}.png"
        filepath = os.path.join(SCREENSHOT_PATH, filename)

        #گرفتن اسکرین شات
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)

        speak("اسکرین شات با موفقیت ذخیره شد")
    except:
        speak("نتونستم اسکرین شات بگیرم")

#-------------------- وضعیت سیستم -------------------

def system_status():
    """گفتن وضعیت سیستم"""
    try:
        #باتری
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "در حال شارژ" if battery.power_plugged else "در حال تخلیه"
            speak(f"باتری {percent} درصد - {plugged}")
        else:
            speak("وضعیت باتری در دسترس نیست")
        
        #cpu
        cpu = psutil.cpu_percent(interval=1)
        speak(f"پردازنده {cpu} درصد استفاده شده")

        #RAM
        ram = psutil.virtual_memory()
        speak(f"رم {ram.percent} درصد استفاده شده")

    except:
        speak("نتونستم وضعیت سیستم رو بخونم")

#-------------------- ایمیل ---------------------
# ایمیل
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email():
    """ارسال ایمیل"""
    speak("ایمیل برای چه کسی فرستاده بشه؟")
    to = take_command()
    if not to:
        speak("متوجه نشدم")
        return
    
    #تبدیل اسم به ایمیل(مخاطبین از پیش تعریف شده)
    contacts = {
        "داداشی": "",
        "مامان" : "",
        "زهرا" : "mazharii.zahra82@gmail.com"
    }

    if to in contacts:
        to_email = contacts[to]
    else:
        to_email = to.replace(" ", "") + "@gmail.com"
    
    speak("موضوع ایمیل چی باشه؟")
    subject = take_command()
    if not subject:
        speak("موضوع رو متوجه نشدم")
        return
    
    speak("متن ایمیل رو بگو.")
    body = take_command()
    if not body:
        speak("متن رو متوجه نشدم.")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        speak(f"ایمیل با موفقیت به {to} ارسال شد.")
    except:
        speak("نتونستم ایمیل رو بفرستم. رمز برنامه یا اینترنت رو چک کن")


#--------------------- فقل کردن ویندوز -------------
def lock_windows():
    """قفل کردن ویندوز"""
    speak("باشه، ویندوز رو قفل میکنم")
    time.sleep(0.5)
    subprocess.call("rundll32.exe user32.dll,LockWorkStation")

#------------------- خاموش و ریستارت ---------------
def shutdown_or_restart(action):
    """خاموش یا ریستارت کردن سیستم"""
    if action == "shutdown":
        speak("باشه، سیستم تا 30 ثانیه دیگه خاموش میشه. میخوای لغوش کنم؟")
        time.sleep(0.5)
        subprocess.call("shutdown /s /t 30")

        #فرصت برای لغو
        q = take_command()
        if q and ("لغو" in q or "بیخیال" in q or "cancel" in q):
            subprocess.call("shutdown /a")
            speak("خاموشی لغو شد.")

    elif action == "restart":
        speak("باشه، سیستم تا 30 ثانیه دیگه ریستارت میشه. میخوای لغوش کنم؟")
        time.sleep(0.5)
        subprocess.call("shutdown /r /t 30")

        #فرصت برای لغو
        q = take_command()
        if q and ("لغو" in q or "بیخیال" in q or "cancel" in q):
            subprocess.call("shutdown /a")
            speak("ریستارت لغو شد")

#-------------------- ربات تلگرام --------------------
# توکن تلگرام
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_CHAT_ID = int(os.getenv("YOUR_CHAT_ID"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به پیام‌های تلگرام با قابلیت‌های کامل"""
    user_id = update.effective_chat.id

    # فقط به شما جواب بده
    if user_id != YOUR_CHAT_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید.")
        return
    
    text = update.message.text.strip()
    text_lower = text.lower()
    response = ""

    # 1. سلام و احوالپرسی
    if "سلام" in text_lower:
        response = "سلام زهرا جان! 🌟 جارویس در خدمت شماست.\nبرای دیدن راهنما، help رو بفرست."
    
    # 2. ساعت و تاریخ
    elif "ساعت" in text_lower:
        now = datetime.datetime.now().strftime("%H:%M")
        response = f"🕒 ساعت الان {now} است."
    elif "تاریخ" in text_lower:
        today = datetime.datetime.now().strftime("%Y/%m/%d")
        response = f"📅 امروز {today} است."

    # 3. وضعیت سیستم
    elif "باتری" in text_lower or "وضعیت سیستم" in text_lower:
        try:
            battery = psutil.sensors_battery()
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            response = f"🔋 باتری: {battery.percent}%\n🧠 CPU: {cpu}%\n💾 RAM: {ram.percent}%"
        except:
            response = "❌ نتونستم وضعیت رو بخونم."

    # 4. آب و هوا (هوشمند)
    elif "هوا" in text_lower:
        city = "Tehran"
        if "دامغان" in text_lower: city = "Damghan"
        elif "تهران" in text_lower: city = "Tehran"
        elif "اصفهان" in text_lower: city = "Isfahan"
        elif "شیراز" in text_lower: city = "Shiraz"
        elif "مشهد" in text_lower: city = "Mashhad"
        
        try:
            WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
            res = requests.get(url)
            data = res.json()
            if res.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                response = f"🌤️ هوای {city}:\n{desc}\n🌡️ دما: {temp}°C"
            else:
                response = "❌ نتونستم هوا رو بگیرم."
        except:
            response = "❌ خطا در دریافت هوا."

    # 5. مدیریت موسیقی
    elif "پخش موزیک" in text_lower or "پخش آهنگ" in text_lower:
        play_music()
        response = "🎵 در حال پخش آهنگ تصادفی..."
    elif text_lower == "آهنگ بعدی":
        next_song()
        response = "⏭️ آهنگ بعدی پخش شد."
    elif text_lower == "آهنگ قبلی":
        prev_song()
        response = "⏮️ آهنگ قبلی پخش شد."
    elif text_lower == "توقف آهنگ":
        pygame.mixer.music.stop()
        response = "⏹️ پخش آهنگ متوقف شد."
    elif "لیست آهنگ" in text_lower:
        try:
            songs = [f for f in os.listdir(MUSIC_PATH) if f.endswith(('.mp3', '.wav', '.flac'))]
            if songs:
                response = "🎶 لیست آهنگ‌ها:\n" + "\n".join([f"{i+1}. {os.path.splitext(s)[0]}" for i, s in enumerate(songs[:15])])
            else:
                response = "❌ هیچ آهنگی پیدا نشد."
        except:
            response = "❌ خطا در خوندن لیست."

    # 6. اسکرین‌شات
    elif "اسکرین" in text_lower:
        try:
            if not os.path.exists(SCREENSHOT_PATH):
                os.makedirs(SCREENSHOT_PATH)
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filepath = os.path.join(SCREENSHOT_PATH, f"screenshot_{now}.png")
            ImageGrab.grab().save(filepath)
            await update.message.reply_photo(photo=open(filepath, 'rb'), caption="📸 اسکرین‌شات گرفته شد.")
            return
        except:
            response = "❌ نتونستم اسکرین شات بگیرم."

    # 7. مدیریت فایل‌ها و درایوها
    elif "this pc" in text_lower or "کامپیوتر من" in text_lower:
        open_this_pc()
        response = "💻 This PC باز شد."
    elif "درایو" in text_lower:
        drive_letter = text_lower.split("درایو")[-1].strip().upper()
        if drive_letter in ["C", "D", "E", "F"]:
            open_drive(drive_letter)
            response = f"📁 درایو {drive_letter} باز شد."
        else:
            response = "❌ درایو نامعتبر است."
    elif "باز کردن پوشه" in text_lower:
        folder = text_lower.replace("باز کردن پوشه", "").strip()
        if open_folder(folder):
            response = f"📂 پوشه {folder} باز شد."
        else:
            response = f"❌ پوشه {folder} پیدا نشد."

    # 8. مدیریت برنامه‌ها
    elif "باز کردن" in text_lower:
        app = text_lower.replace("باز کردن", "").strip()
        if open_application(app):
            response = f"🚀 برنامه {app} باز شد."
        else:
            response = f"❌ برنامه {app} پیدا نشد."
    elif "بستن" in text_lower:
        app = text_lower.replace("بستن", "").strip()
        if close_application(app):
            response = f"✅ برنامه {app} بسته شد."
        else:
            response = f"❌ نتونستم {app} رو ببندم."

    # 9. یادداشت‌برداری
    elif text_lower.startswith("یادداشت "):
        note = text_lower.replace("یادداشت ", "").strip()
        try:
            with open(NOTES_FILE, "a", encoding="utf-8") as f:
                now = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
                f.write(f"[{now}] {note}\n")
            response = f"📝 یادداشت ذخیره شد: {note}"
        except:
            response = "❌ نتونستم یادداشت رو ذخیره کنم."
    elif text_lower == "خواندن یادداشت‌ها":
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                notes = f.read()
            response = f"📋 یادداشت‌ها:\n{notes}" if notes.strip() else "📋 هنوز یادداشتی نداری."
        except:
            response = "❌ خطا در خوندن یادداشت‌ها."

    # 10. مدیریت سیستم
    elif "خاموش" in text_lower:
        subprocess.call("shutdown /s /t 30")
        response = "⏳ سیستم تا ۳۰ ثانیه دیگه خاموش میشه. برای لغو، 'لغو' رو بفرست."
    elif "ریستارت" in text_lower:
        subprocess.call("shutdown /r /t 30")
        response = "🔄 سیستم تا ۳۰ ثانیه دیگه ریستارت میشه. برای لغو، 'لغو' رو بفرست."
    elif "قفل" in text_lower:
        subprocess.call("rundll32.exe user32.dll,LockWorkStation")
        response = "🔒 ویندوز قفل شد."
    elif "لغو" in text_lower:
        subprocess.call("shutdown /a")
        response = "✅ خاموشی/ریستارت لغو شد."

    # 11. ایمیل
    elif text_lower.startswith("ایمیل به "):
        try:
            rest = text_lower.replace("ایمیل به ", "")
            if " موضوع " in rest and " متن " in rest:
                to_part = rest.split(" موضوع ")[0].strip()
                subject_part = rest.split(" موضوع ")[1].split(" متن ")[0].strip()
                body_part = rest.split(" متن ")[1].strip()
                response = send_email_telegram(to_part, subject_part, body_part)
            else:
                response = "❌ فرمت اشتباهه. اینطوری بگو:\nایمیل به زهرا موضوع سلام متن چطوری؟"
        except:
            response = "❌ نتونستم ایمیل رو بفرستم."

    # 12. راهنما (بدون /)
    elif text_lower == "help" or text_lower == "راهنما":
        response = """
📋 **راهنمای جارویس تلگرامی:**

🚀 **باز کردن برنامه:** `باز کردن کروم`
❌ **بستن برنامه:** `بستن نوت‌پد`
📁 **باز کردن درایو:** `درایو D`
📂 **باز کردن پوشه:** `باز کردن پوشه دانلود`
🎵 **پخش آهنگ:** `پخش موزیک`
⏭️ **آهنگ بعدی:** `آهنگ بعدی`
⏮️ **آهنگ قبلی:** `آهنگ قبلی`
⏹️ **توقف آهنگ:** `توقف آهنگ`
📋 **لیست آهنگ:** `لیست آهنگ`
📸 **اسکرین‌شات:** `اسکرین`
📝 **یادداشت:** `یادداشت فردا جلسه دارم`
📖 **خواندن یادداشت‌ها:** `خواندن یادداشت‌ها`
✉️ **ایمیل:** `ایمیل به زهرا موضوع سلام متن چطوری؟`
🌤️ **آب و هوا:** `هوای دامغان`
💻 **وضعیت سیستم:** `باتری`
⏳ **خاموش/ریستارت:** `خاموش` / `ریستارت`
🔒 **قفل:** `قفل`
🕒 **ساعت:** `ساعت`
📅 **تاریخ:** `تاریخ`
        """

    # پاسخ پیش‌فرض
    else:
        response = "🤔 متوجه نشدم. برای دیدن راهنما، کلمه 'help' یا 'راهنما' رو بفرست."

    await update.message.reply_text(response)

#----------------------- تابع اجرای ربات ------------
def run_telegram_bot():
    """اجرای ربات تلگرام"""
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # اضافه کردن هندلرها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ربات تلگرام راه اندازی شد")
    app.run_polling(drop_pending_updates=True)


#---------------this pc-------------

def open_this_pc():
    """بازکردن this pc"""
    speak("this pc رو باز میکنم")
    subprocess.call("explorer shell:MyComputerFolder")

#------------drive-----------------

def open_drive(drive_letter):
    """بازکردن یک درایو خاص"""
    speak(f"درایو {drive_letter} رو باز میکنم.")
    subprocess.call(f"explorer {drive_letter}:\\")

#------------folder--------------

def open_folder(folder_name):
    """بازکردن پوشه های خاص"""
    folders = {
        "دانلود": os.path.expanduser("~/Downloads"),
        "downloads" : os.path.expanduser("~/Downloads"),
        "دسکتاپ" : os.path.expanduser("~/Desktop"),
        "desktop": os.path.expanduser("~/Desktop"),
        "سند": os.path.expanduser("~/Documents"),
        "documents": os.path.expanduser("~/Documents"),
        "عکس": os.path.expanduser("~/Pictures"),
        "pictures": os.path.expanduser("~/Pictures"),
        "موزیک": os.path.expanduser("~/Music"),
        "music": os.path.expanduser("~/Music"),
        "ویدیو": os.path.expanduser("~/Videos"),
        "videos": os.path.expanduser("~/Videos"),
    }

    path = folders.get(folder_name.lower())
    if path:
        speak(f"پوشه {folder_name} رو باز میکنم")
        subprocess.call(f'explorer {path}')
        return True
    return False

#--------------apps----------------------

def open_application(app_name):
    """بازکردن برنامه با اسم"""
    import shutil
    
    apps = {
        "فایرفاکس": "firefox",
        "firefox": "firefox",
        "کروم": "chrome",
        "chrome": "chrome",
        "نوت پد": "notepad",
        "notepad": "notepad",
        "ماشین حساب": "calc",
        "calculator": "calc",
        "کلک": "calc",
        "cmd": "cmd",
        "کامند": "cmd",
        "پاورشل": "powershell",
        "powershell": "powershell",
        "اکسپلورر": "explorer",
        "explorer": "explorer",
        "ورد": "winword",
        "word": "winword",
        "اکسل": "excel",
        "excel": "excel",
        "پاورپوینت": "powerpnt",
        "powerpoint": "powerpnt",
        "پینت": "mspaint",
        "paint": "mspaint",
        "edge": "msedge",
        "اج": "msedge",
    }
    
    cmd = apps.get(app_name.lower())
    if cmd:
        # اول چک کن ببینیم توی PATH هست یا نه
        if shutil.which(cmd):
            speak(f"{app_name} رو باز میکنم")
            subprocess.Popen(cmd)
            return True
        else:
            # اگه توی PATH نیست، مسیرهای معروف رو چک کن
            common_paths = {
                "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "msedge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "winword": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                "powerpnt": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            }
            
            path = common_paths.get(cmd)
            if path and os.path.exists(path):
                speak(f"{app_name} رو باز میکنم")
                subprocess.Popen(path)
                return True
    
    return False

#--------------close apps ---------------

def close_application(app_name):
    """بستن برنامه با اسم"""

    process_name = {
         "فایرفاکس": "firefox.exe",
        "firefox": "firefox.exe",
        "کروم": "chrome.exe",
        "chrome": "chrome.exe",
        "نوت‌ پد": "notepad.exe",
        "notepad": "notepad.exe",
        "ماشین حساب": "calculator.exe",
        "calculator": "calculator.exe",
        "کلک": "calculator.exe",
        "اکسپلورر": "explorer.exe",
        "explorer": "explorer.exe",
        "وُرد": "winword.exe",
        "word": "winword.exe",
        "اکسل": "excel.exe",
        "excel": "excel.exe",
        "edge": "msedge.exe",
        "اج": "msedge.exe",
    }

    process = process_name.get(app_name.lower())
    if process:
        speak(f"{app_name} رو میبندم")
        os.system(f"taskkill /f /im {process}")
        return True
    return False    

def send_email_telegram(to_email, subject, body):
    """ارسال ایمیل از طریق ربات تلگرام"""
    try:
        contacts = {
            "زهرا": "mazharii.zahra82@gmail.com",
            "داداشی": "",
            "مامان": "",
        }
        
        if to_email in contacts:
            to_email = contacts[to_email]
        elif "@" not in to_email:
            to_email = to_email + "@gmail.com"
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return f"✅ ایمیل با موفقیت به {to_email} ارسال شد."
    except Exception as e:
        return f"❌ خطا در ارسال ایمیل: {str(e)}"


# ==================== توابع کمکی ====================
def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 11:
        speak("صبح بخیر !")
    elif hour < 14:
        speak("ظهر بخیر !")
    elif hour < 20:
        speak("عصر بخیر!")
    else:
        speak("شب بخیر !")
    speak("من جارویس هستم. چطور میتونم کمکت کنم؟")

def solve_math(query):
    try:
        WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID")
        client = wolframalpha.Client(WOLFRAM_APP_ID)
        res = client.query(query)
        for pod in res.pods:
            if "Result" in pod.title or "Indefinite integral" in pod.title or "Solution" in pod.title:
                return pod.text
        return next(res.results).text
    except:
        return "نتونستم حلش کنم."

def search_wiki(query):
    try:
        wikipedia.set_lang("fa")
        return wikipedia.summary(query, sentences=2)
    except:
        return "چیزی پیدا نکردم."
    

# ==================== حلقه اصلی ====================
def run_jarvis():

    print("شروع برنامه...")
    #شروع ربات تلگرام
    telegram_thread = threading.Thread(target=run_telegram_bot)
    telegram_thread.daemon = True
    telegram_thread.start()

    wish_me()
    
    while True:
        query = take_command()
        
        if query == "":
            continue
        
        # --- خروج ---
        if "خداحافظ" in query or "خاموش شو" in query or "برو بخواب" in query:
            speak("خداحافظ! هر وقت نیاز داشتی من اینجام.")
            break
        
        # --- معرفی ---
        elif "اسمت" in query or "کی هستی" in query:
            speak("من جارویس هستم، دستیار شخصی شما.")
        
        # --- ساعت ---
        elif "ساعت" in query:
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"ساعت الان {now} است.")
        
        # --- تاریخ ---
        elif "تاریخ" in query:
            today = datetime.datetime.now().strftime("%Y/%m/%d")
            speak(f"امروز {today} است.")
        
        # --- جستجوی اینترنتی ---
        elif "جستجو کن" in query or "سرچ کن" in query:
            speak("چی رو جستجو کنم؟")
            sq = take_command()
            if sq:
                speak(f"در حال جستجوی {sq}")
                webbrowser.open(f"https://www.google.com/search?q={sq}")
        
        # --- باز کردن یوتیوب ---
        elif "یوتیوب" in query:
            speak("در حال باز کردن یوتیوب")
            webbrowser.open("youtube.com")
        
        # --- حل مسائل ریاضی ---
        elif "حساب کن" in query or "محاسبه" in query or "حل کن" in query or "چقدر میشه" in query:
            speak("در حال محاسبه...")
            math_q = query.replace("حساب کن", "").replace("محاسبه", "").replace("حل کن", "").replace("چقدر میشه", "").strip()
            if math_q:
                answer = solve_math(math_q)
                speak(answer)
            else:
                speak("چی رو حساب کنم؟")
        
        # --- جستجو در ویکیپدیا ---
        elif "ویکیپدیا" in query or "ویکی پدیا" in query:
            speak("در حال جستجو در ویکیپدیا...")
            topic = query.replace("ویکیپدیا", "").replace("ویکی پدیا", "").replace("درباره", "").strip()
            if topic:
                result = search_wiki(topic)
                speak(result)
            else:
                speak("درباره چی سرچ کنم؟")
        
        # --- حال و احوال ---
        elif "حالت" in query or "چطوری" in query:
            speak("من همیشه خوبم! تو چطوری؟")

        #------ پخش آهنگ خاص -----
        elif ("پخش کن" in query and ("آهنگ" in query or "موزیک" in query or "موسیقی" in query or "شماره" in query)):
            play_specific_song(query)
        
        # --- پخش موسیقی ---
        elif "آهنگ" in query or "موزیک" in query or "موسیقی" in query:
            play_music()
        
        # --- آهنگ بعدی ---
        elif "بعدی" in query or "next" in query:
            next_song()
        
        # --- قطع آهنگ ---
        elif "قطع کن" in query or "بسه" in query or "توقف" in query:
            pygame.mixer.music.stop()
            speak("آهنگ قطع شد.")

        elif "قبلی" in query or "previous" in query:
            prev_song()

        elif "لیست" in query or "چه آهنگ" in query or "چند تا آهنگ" in query:
            list_songs()

        elif "یادداشت" in query or "note" in query:
            take_note()
        
        elif "یادداشت‌ها" in query or "یادداشت ها" in query or "بخون" in query:
            read_notes()

        elif "آلارم" in query or "alarm" in query:
            set_alarm()

        elif "هوا" in query or "آب و هوا" in query or "weather" in query:
            get_weather(query)

        elif "اسکرین شات" in query or "اسکرین" in query or "screenshot" in query:
            take_screenshot()
        
        elif "باتری" in query or "سیستم" in query or "وضعیت" in query:
            system_status()

        elif "ایمیل" in query or "email" in query or "mail" in query:
            send_email()

        elif "قفل" in query or "lock" in query:
            lock_windows()
        
        elif "خاموش" in query or "shutdown" in query:
            shutdown_or_restart("shutdown")

        elif "ریستارت" in query or "restart" in query:
            shutdown_or_restart("restart")

        # --- This PC ---
        elif "this pc" in query or "مای کامپیوتر" in query or "کامپیوتر من" in query:
            open_this_pc()
        
        # --- باز کردن درایو ---
        elif "درایو" in query or "drive" in query:
            found = False
            for char in ["c", "d", "e", "f", "g", "سی", "دی", "ای", "اف", "جی"]:
                persian_to_eng = {"سی": "C", "دی": "D", "ای": "E", "اف": "F", "جی": "G"}
                if char in query:
                    drive = persian_to_eng.get(char, char.upper())
                    open_drive(drive)
                    found = True
                    break
            if not found:
                speak("نتونستم حرف درایو رو تشخیص بدم. بگو مثلاً درایو C.")
        
        # --- بستن برنامه ---
        elif "ببند" in query or "ببندش" in query or "close" in query:
            app = query.replace("ببند", "").replace("ببندش", "").replace("close", "").replace("رو", "").replace("را", "").strip()
            if not close_application(app):
                speak(f"نتونستم {app} رو ببندم. اسم برنامه رو واضح بگو.")
        
        # --- باز کردن پوشه ---
        elif "پوشه" in query or "فولدر" in query or "folder" in query:
            folder = query.replace("پوشه", "").replace("فولدر", "").replace("folder", "").replace("رو باز کن", "").replace("را باز کن", "").replace("را", "").strip()
            if not open_folder(folder):
                speak(f"پوشه {folder} رو نمی‌شناسم.")
        
        # --- باز کردن برنامه ---
        elif "باز کن" in query or "open" in query:
            app = query.replace("باز کن", "").replace("open", "").replace("رو", "").replace("را", "").strip()
            if not open_folder(app):
                if not open_application(app):
                    speak(f"نتونستم {app} رو باز کنم. اسمش رو واضح‌تر بگو.")
        
        # --- نفهمید ---
        else:
            speak("متوجه نشدم، میشه دوباره بگی؟")

if __name__ == "__main__":
    run_jarvis()