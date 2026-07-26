from flask import Flask, render_template, request, jsonify
import jdatetime
from hijri_converter import Gregorian
from datetime import datetime, timedelta
import requests
import pytz
import random

app = Flask(__name__)

# ============================================================
# دیکشنری‌های فارسی
# ============================================================
PERSIAN_MONTHS = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

PERSIAN_WEEKDAYS = {
    0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه‌شنبه",
    4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
}

# ============================================================
# دیکشنری مناسبت‌ها
# ============================================================
shamsi_events = {
    "1-1": ["جشن نوروز", "سال نو"],
    "1-13": ["جشن سیزده به در"],
    "1-12": ["روز جمهوری اسلامی"],
    "2-10": ["روز ملی خلیج فارس"],
    "2-25": ["روز بزرگداشت فردوسی"],
    "3-3": ["فتح خرمشهر", "روز مقاومت"],
    "3-14": ["رحلت امام خمینی"],
    "3-15": ["قیام 15 خرداد"],
    "4-7": ["انفجار دفتر حزب جمهوری اسلامی", "شهادت دکتر بهشتی"],
    "4-13": ["تیر روز", "جشن تیرگان"],
    "5-7": ["مرداد روز", "جشن مردادگان"],
    "5-14": ["صدور فرمان مشروطیت"],
    "5-17": ["روز خبرنگار"],
    "5-28": ["سالروز وقایع 28 مرداد"],
    "6-1": ["روز بزرگداشت ابوعلی سینا", "روز پزشک"],
    "6-4": ["شهریور روز", "جشن شهریورگان"],
    "6-17": ["قیام 17 شهریور"],
    "6-21": ["روز سینما"],
    "6-27": ["روز شعر و ادب پارسی"],
    "7-10": ["مهر روز", "جشن مهرگان"],
    "7-13": ["روز جهانی معلم"],
    "7-20": ["روز بزرگداشت حافظ"],
    "8-10": ["آبان روز", "جشن آبانگان"],
    "8-13": ["روز دانش آموز"],
    "8-24": ["روز کتاب و کتابخوانی"],
    "9-5": ["روز بسیج مستضعفان"],
    "9-9": ["جشن آذرگان", "آذر روز"],
    "9-16": ["روز دانشجو"],
    "9-30": ["جشن شب یلدا"],
    "10-13": ["شهادت سردار سلیمانی"],
    "10-20": ["سالروز قتل امیرکبیر"],
    "11-1": ["زادروز فردوسی"],
    "11-2": ["بهمن روز", "جشن بهمنگان"],
    "11-10": ["جشن سده"],
    "11-12": ["بازگشت امام خمینی"],
    "11-22": ["پیروزی انقلاب اسلامی"],
    "11-29": ["جشن سپندارمذگان"],
    "12-5": ["روز بزرگداشت خواجه نصیرالدین طوسی"],
    "12-15": ["روز درختکاری"],
    "12-29": ["روز ملی شدن صنعت نفت"],
}

hijri_events = {
    "1-1": ["آغاز سال هجرى قمرى", "يورش ابرهه به مكه", "آغاز ایام حسینی"],
    "1-10": ["شهادت امام حسین (ع)"],
    "7-27": ["عید مبعث"],
    "8-15": ["ولادت حضرت بقیه الله الاعظم"],
    "9-1": ["نزول صحف ابراهیم"],
    "10-1": ["عید فطر"],
    "11-1": ["ولادت حضرت معصومه"],
    "12-10": ["عید قربان"],
    "12-18": ["عید غدیر"],
}

# ============================================================
# پیام‌های انگیزشی
# ============================================================
motivation_messages = [
    "🌱 امروز روز جدیدی برای ساختن است. قدر لحظات را بدان!",
    "💪 موفقیت از دل تلاش‌های کوچک روزانه زاده می‌شود.",
    "🌟 هر روز یک فرصت تازه برای بهتر شدن است.",
    "😊 لبخند بزن، دنیا جای قشنگی‌ست!",
    "✨ به خودت ایمان داشته باش، می‌توانی!",
    "🌺 آرامش را در دل خود پیدا کن، نه در بیرون.",
    "🔥 امروز را با انرژی مثبت شروع کن.",
    "🌸 زندگی زیباست، پس لذت ببر.",
    "⭐ هر قدم کوچک، تو را به هدف نزدیک‌تر می‌کند.",
    "🌈 پس از هر شب تاریک، صبحی روشن می‌آید.",
    "🍀 شانس را با تلاش خود بساز.",
    "💎 ارزش تو به دانسته‌هایت نیست، به رفتارت است.",
    "🌿 امروز را با عشق به خود و دیگران بگذران.",
    "🎯 هدف خود را امروز مرور کن و گام بردار.",
    "🕊️ آرامش را در دل خود پرورش بده.",
    "🌞 هر روز طلوعی دوباره است، از آن استفاده کن.",
    "🍃 ساده زیستن، زیباترین راه زندگی است.",
    "💫 رویاهایت را باور کن، آنها به واقعیت می‌پیوندند.",
    "🌼 مهربانی، بهترین هدیه‌ای است که می‌توانی بدهی.",
    "🏆 موفقیت، حاصل تکرار کارهای کوچک است.",
]

# ============================================================
# ⏰ تابع دریافت زمان ایران (پایدار)
# ============================================================
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

def get_now_tehran():
    """دریافت زمان فعلی با تایم‌زون ایران (datetime با timezone)"""
    return datetime.now(TEHRAN_TZ)

def get_today_tehran():
    """دریافت تاریخ امروز شمسی بر اساس زمان ایران"""
    now = get_now_tehran()
    return jdatetime.datetime.fromgregorian(datetime=now).date()

# ============================================================
# توابع اصلی
# ============================================================
def get_prayer_times(city="قم", country="Iran"):
        try:url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=7&school=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        timings = data["data"]["timings"]
        return {
            "Fajr": timings["Fajr"],
            "Sunrise": timings["Sunrise"],
            "Dhuhr": timings["Dhuhr"],
            "Asr": timings["Asr"],
            "Maghrib": timings["Maghrib"],
            "Isha": timings["Isha"],
        }
    except:
        return None

def get_weather(city="قم"):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        data = response.json()
        current = data["current_condition"][0]
        return {
            "temp": f"{current['temp_C']}°C",
            "condition": current["weatherDesc"][0]["value"],
            "humidity": f"{current['humidity']}%",
        }
    except:
        return None

def get_gold_usd_prices():
    try:
        url = "https://brsapi.ir/free-api/gold-currency"
        response = requests.get(url, timeout=10)
        data = response.json()
        gold = data.get('gold', {}).get('18', {}).get('price')
        usd = data.get('currency', {}).get('usd', {}).get('price')
        if gold and usd:
            return {"gold": int(gold), "usd": int(usd)}
    except:
        pass
    return None

def get_shamsi_events(year, month, day):
    key = f"{month}-{day}"
    return shamsi_events.get(key, [])

def get_hijri_events(hijri_month, hijri_day):
    key = f"{hijri_month}-{hijri_day}"
    return hijri_events.get(key, [])

def get_persian_date(today):
    weekday = PERSIAN_WEEKDAYS[today.weekday()]
    month = PERSIAN_MONTHS[today.month]
    day = str(today.day).replace("0", "۰").replace("1", "۱").replace("2", "۲").replace("3", "۳").replace("4", "۴").replace("5", "۵").replace("6", "۶").replace("7", "۷").replace("8", "۸").replace("9", "۹")
    year = str(today.year).replace("0", "۰").replace("1", "۱").replace("2", "۲").replace("3", "۳").replace("4", "۴").replace("5", "۵").replace("6", "۶").replace("7", "۷").replace("8", "۸").replace("9", "۹")
    return f"{weekday} {day} {month} {year}"

def get_hijri_date(gregorian_date):
    try:
        hijri = Gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day).to_hijri()
        hijri_months = {
            1: "محرم", 2: "صفر", 3: "ربیع‌الاول", 4: "ربیع‌الثانی",
            5: "جمادی‌الاول", 6: "جمادی‌الثانی", 7: "رجب", 8: "شعبان",
            9: "رمضان", 10: "شوال", 11: "ذی‌قعده", 12: "ذی‌الحجه"
        }
        return f"{hijri.day} {hijri_months[hijri.month]} {hijri.year}"
    except:
        return "نامشخص"

def get_next_prayer(prayer_times):
    """محاسبه زمان باقی‌مانده تا اذان بعدی بر اساس زمان ایران"""
    if not prayer_times:
        return None, None
    
    now = get_now_tehran()
    now_time = now.time()
    
    prayers = [
        ("اذان صبح", prayer_times["Fajr"]),
        ("طلوع", prayer_times["Sunrise"]),
        ("اذان ظهر", prayer_times["Dhuhr"]),
        ("اذان عصر", prayer_times["Asr"]),
        ("اذان مغرب", prayer_times["Maghrib"]),
        ("اذان عشاء", prayer_times["Isha"]),
    ]
    
    # پیدا کردن اولین اذان بعد از زمان فعلی
    for name, time_str in prayers:
        try:
            pray_time = datetime.strptime(time_str, "%H:%M").time()
            # ترکیب با تاریخ امروز برای محاسبه دقیق
            pray_datetime = datetime.combine(now.date(), pray_time)
            pray_datetime = TEHRAN_TZ.localize(pray_datetime)
            
            if pray_datetime > now:
                delta = pray_datetime - now
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                if hours > 0:
                    return name, f"{hours} ساعت و {minutes} دقیقه"
                else:
                    return name, f"{minutes} دقیقه"
        except:
            pass
    
    # اگر هیچ اذانی باقی نمانده بود (همه گذشته)، اولین اذان فردا
    return prayers[0][0], "فردا"

# ============================================================
# مسیرهای وب‌سایت
# ============================================================

@app.route('/')
def home():
    today = get_today_tehran()
    city = request.args.get('city', 'قم')
    
    # تاریخ‌ها
    persian_date = get_persian_date(today)
    gregorian = today.togregorian()
    miladi_date = gregorian.strftime("%B %d, %A")
    hijri_date = get_hijri_date(gregorian)
    
    # اطلاعات
    prayer = get_prayer_times(city)
    weather = get_weather(city)
    prices = get_gold_usd_prices()
    shamsi_events_list = get_shamsi_events(today.year, today.month, today.day)
    hijri_obj = Gregorian(gregorian.year, gregorian.month, gregorian.day).to_hijri()
    hijri_events_list = get_hijri_events(hijri_obj.month, hijri_obj.day)
    next_prayer_name, next_prayer_time = get_next_prayer(prayer)
    motivation = random.choice(motivation_messages)
    
    return render_template('index.html',
        persian_date=persian_date,
        miladi_date=miladi_date,
        hijri_date=hijri_date,
        prayer=prayer,
        weather=weather,
        prices=prices,
        shamsi_events=shamsi_events_list,
        hijri_events=hijri_events_list,
        next_prayer_name=next_prayer_name,
        next_prayer_time=next_prayer_time,
        motivation=motivation,
        city=city,
        selected_city=city
    )

@app.route('/api/info')
def api_info():
    today = get_today_tehran()
    city = request.args.get('city', 'قم')
    gregorian = today.togregorian()
    hijri = Gregorian(gregorian.year, gregorian.month, gregorian.day).to_hijri()
    
    prayer = get_prayer_times(city)
    next_name, next_time = get_next_prayer(prayer)
    
    return jsonify({
        "timezone": "Asia/Tehran",
        "server_time": get_now_tehran().isoformat(),
        "shamsi": today.strftime("%Y-%m-%d"),
        "miladi": gregorian.strftime("%Y-%m-%d"),
        "hijri": f"{hijri.year}-{hijri.month}-{hijri.day}",
        "prayer": prayer,
        "next_prayer": {"name": next_name, "remaining": next_time} if next_name else None,
        "weather": get_weather(city),
        "prices": get_gold_usd_prices()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
