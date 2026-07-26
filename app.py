from flask import Flask, render_template, request, jsonify
import jdatetime
from hijri_converter import Gregorian
from datetime import datetime
import requests
import pytz

app = Flask(__name__)

# ============================================================
# توابع کمکی (همان کدهای ربات)
# ============================================================
def get_today_tehran():
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    return jdatetime.datetime.fromgregorian(datetime=now).date()

def get_prayer_times(city="قم", country="Iran"):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=8"
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

# ============================================================
# مسیرهای (Routes) وب‌سایت
# ============================================================

@app.route('/')
def home():
    """صفحه اصلی وب‌سایت"""
    today = get_today_tehran()
    
    # تاریخ شمسی
    persian_date = today.strftime("%A %d %B %Y")
    persian_date = persian_date.replace("0", "۰").replace("1", "۱").replace("2", "۲").replace("3", "۳").replace("4", "۴").replace("5", "۵").replace("6", "۶").replace("7", "۷").replace("8", "۸").replace("9", "۹")
    
    # تاریخ میلادی
    gregorian = today.togregorian()
    miladi_date = gregorian.strftime("%B %d, %A")
    
    # تاریخ قمری
    hijri = Gregorian(gregorian.year, gregorian.month, gregorian.day).to_hijri()
    hijri_months = {
        1: "محرم", 2: "صفر", 3: "ربیع‌الاول", 4: "ربیع‌الثانی",
        5: "جمادی‌الاول", 6: "جمادی‌الثانی", 7: "رجب", 8: "شعبان",
        9: "رمضان", 10: "شوال", 11: "ذی‌قعده", 12: "ذی‌الحجه"
    }
    hijri_date = f"{hijri.day} {hijri_months[hijri.month]} {hijri.year}"
    
    # دریافت اطلاعات
    prayer = get_prayer_times()
    weather = get_weather()
    
    return render_template('index.html',
        persian_date=persian_date,
        miladi_date=miladi_date,
        hijri_date=hijri_date,
        prayer=prayer,
        weather=weather
    )

@app.route('/api/info')
def api_info():
    """API برای دریافت اطلاعات به صورت JSON"""
    today = get_today_tehran()
    gregorian = today.togregorian()
    hijri = Gregorian(gregorian.year, gregorian.month, gregorian.day).to_hijri()
    
    return jsonify({
        "shamsi": today.strftime("%Y-%m-%d"),
        "miladi": gregorian.strftime("%Y-%m-%d"),
        "hijri": f"{hijri.year}-{hijri.month}-{hijri.day}",
        "prayer": get_prayer_times(),
        "weather": get_weather()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
