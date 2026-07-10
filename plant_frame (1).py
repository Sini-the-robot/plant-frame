import requests
import json
import random
import time
import os
from datetime import datetime
from urllib.parse import quote

GROQ_API_KEY = "YOUR_GROQ_API_KEY"  # اینجا key خودت رو بذار
UPDATE_HOURS = 6

CITIES = [
    {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "country": "Japan"},
    {"name": "Tehran", "lat": 35.69, "lon": 51.39, "country": "Iran"},
    {"name": "Amsterdam", "lat": 52.37, "lon": 4.90, "country": "Netherlands"},
    {"name": "Nairobi", "lat": -1.29, "lon": 36.82, "country": "Kenya"},
    {"name": "Buenos Aires", "lat": -34.60, "lon": -58.38, "country": "Argentina"},
    {"name": "Mumbai", "lat": 19.08, "lon": 72.88, "country": "India"},
    {"name": "Oslo", "lat": 59.91, "lon": 10.75, "country": "Norway"},
    {"name": "Cape Town", "lat": -33.93, "lon": 18.42, "country": "South Africa"},
    {"name": "Mexico City", "lat": 19.43, "lon": -99.13, "country": "Mexico"},
    {"name": "Bangkok", "lat": 13.75, "lon": 100.52, "country": "Thailand"},
    {"name": "Istanbul", "lat": 41.01, "lon": 28.95, "country": "Turkey"},
    {"name": "Sydney", "lat": -33.87, "lon": 151.21, "country": "Australia"},
    {"name": "Cairo", "lat": 30.04, "lon": 31.24, "country": "Egypt"},
    {"name": "Vancouver", "lat": 49.25, "lon": -123.12, "country": "Canada"},
    {"name": "Lisbon", "lat": 38.72, "lon": -9.14, "country": "Portugal"},
    {"name": "Kyoto", "lat": 35.01, "lon": 135.77, "country": "Japan"},
    {"name": "Bogota", "lat": 4.71, "lon": -74.07, "country": "Colombia"},
    {"name": "Helsinki", "lat": 60.17, "lon": 24.94, "country": "Finland"},
    {"name": "Marrakech", "lat": 31.63, "lon": -7.99, "country": "Morocco"},
    {"name": "Tbilisi", "lat": 41.69, "lon": 44.83, "country": "Georgia"},
    {"name": "Reykjavik", "lat": 64.13, "lon": -21.94, "country": "Iceland"},
    {"name": "Chengdu", "lat": 30.57, "lon": 104.07, "country": "China"},
    {"name": "Accra", "lat": 5.56, "lon": -0.20, "country": "Ghana"},
    {"name": "Lima", "lat": -12.05, "lon": -77.04, "country": "Peru"},
    {"name": "Vienna", "lat": 48.21, "lon": 16.37, "country": "Austria"},
    {"name": "Lahore", "lat": 31.55, "lon": 74.34, "country": "Pakistan"},
    {"name": "Addis Ababa", "lat": 9.03, "lon": 38.74, "country": "Ethiopia"},
    {"name": "Prague", "lat": 50.08, "lon": 14.44, "country": "Czech Republic"},
    {"name": "Hanoi", "lat": 21.03, "lon": 105.85, "country": "Vietnam"},
    {"name": "Auckland", "lat": -36.86, "lon": 174.76, "country": "New Zealand"},
]

def get_season(month, lat):
    if lat >= 0:
        if 3 <= month <= 5: return "Spring"
        if 6 <= month <= 8: return "Summer"
        if 9 <= month <= 11: return "Autumn"
        return "Winter"
    else:
        if 3 <= month <= 5: return "Autumn"
        if 6 <= month <= 8: return "Winter"
        if 9 <= month <= 11: return "Spring"
        return "Summer"

def weather_code_to_text(code):
    if code == 0: return "Clear sky"
    if code <= 3: return "Partly cloudy"
    if code <= 48: return "Foggy"
    if code <= 67: return "Rainy"
    if code <= 77: return "Snowy"
    if code <= 82: return "Showers"
    if code >= 95: return "Stormy"
    return "Cloudy"

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto"
    r = requests.get(url, timeout=10)
    d = r.json()
    return {
        "temp": round(d["current"]["temperature_2m"]),
        "humidity": d["current"]["relative_humidity_2m"],
        "condition": weather_code_to_text(d["current"]["weather_code"])
    }

def get_plant(city, country, lat, temp, humidity, condition, season):
    prompt = f"""You are a botanist. Choose ONE native or naturalized plant species currently active in this location.

Location: {city}, {country} (lat: {lat:.1f})
Season: {season}
Temperature: {temp}°C
Humidity: {humidity}%
Weather: {condition}

Respond ONLY with valid JSON, no markdown:
{{
  "latin": "Genus species",
  "common": "Common name",
  "note": "One elegant sentence max 18 words describing what this plant is doing right now, poetic-scientific tone",
  "phenology": "Current stage (Flowering / Dormant / Fruiting / Budding / Seeding)",
  "image_prompt": "Detailed botanical illustration of [plant name], japanese woodblock ukiyo-e style, fine ink lines, muted earth tones, cream background, scientific illustration, no text, no labels"
}}"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.7
        },
        timeout=20
    )
    raw = r.json()["choices"][0]["message"]["content"]
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def get_image_url(image_prompt):
    encoded = quote(image_prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=900&seed={seed}&nologo=true"

def build_html(city, country, weather, season, plant, image_url, updated_at):
    refresh_seconds = UPDATE_HOURS * 3600
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="{refresh_seconds}">
<title>Flora · {city}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Space+Mono:wght@400&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #111110;
    min-height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-columns: 1fr 420px;
    grid-template-rows: 100vh;
    overflow: hidden;
    font-family: 'Cormorant Garamond', Georgia, serif;
  }}

  /* تصویر — سمت چپ، تمام ارتفاع */
  .image-zone {{
    position: relative;
    overflow: hidden;
    background: #1a1a15;
  }}

  .image-zone img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  .image-loading {{
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 1rem;
    background: #1a1a15;
  }}

  .spinner {{
    width: 32px; height: 32px;
    border: 1.5px solid #333;
    border-top-color: #5a7a5a;
    border-radius: 50%;
    animation: spin 1.2s linear infinite;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  .spinner-text {{
    font-size: 0.6rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.15em;
    color: #555;
    text-transform: uppercase;
  }}

  /* پنل اطلاعات — سمت راست */
  .info-panel {{
    background: #f0ebe0;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #c8c0b0;
    position: relative;
  }}

  /* corner marks */
  .info-panel::before {{
    content: '';
    position: absolute;
    top: 20px; right: 20px;
    width: 20px; height: 20px;
    border-top: 1.5px solid #1a1a18;
    border-right: 1.5px solid #1a1a18;
  }}
  .info-panel::after {{
    content: '';
    position: absolute;
    bottom: 20px; left: 20px;
    width: 20px; height: 20px;
    border-bottom: 1.5px solid #1a1a18;
    border-left: 1.5px solid #1a1a18;
  }}

  .panel-header {{
    padding: 2.5rem 2.5rem 2rem;
    border-bottom: 1px solid #c8c0b0;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}

  .panel-title {{
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
    color: #8a8478;
  }}

  .panel-date {{
    font-size: 0.6rem;
    font-family: 'Space Mono', monospace;
    color: #8a8478;
  }}

  .weather-grid {{
    padding: 1.5rem 2.5rem;
    border-bottom: 1px solid #c8c0b0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
    background: rgba(255,255,255,0.5);
  }}

  .weather-item {{ display: flex; flex-direction: column; gap: 0.2rem; }}

  .weather-label {{
    font-size: 0.5rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8a8478;
  }}

  .weather-value {{
    font-size: 1.1rem;
    font-weight: 300;
    color: #1a1a18;
  }}

  .plant-section {{
    padding: 2.5rem 2.5rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  .plant-latin {{
    font-size: 2.6rem;
    font-style: italic;
    font-weight: 300;
    line-height: 1.1;
    color: #1a1a18;
    margin-bottom: 0.4rem;
  }}

  .plant-common {{
    font-size: 0.6rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #2d5a3d;
    margin-bottom: 2rem;
  }}

  .divider {{
    width: 36px;
    height: 1px;
    background: #c8c0b0;
    margin-bottom: 2rem;
  }}

  .plant-note {{
    font-size: 1.15rem;
    font-weight: 300;
    line-height: 1.7;
    color: #3a3830;
    font-style: italic;
    margin-bottom: 2rem;
  }}

  .phenology-tag {{
    display: inline-block;
    font-size: 0.55rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #2d5a3d;
    border: 1px solid #2d5a3d;
    padding: 0.3rem 0.8rem;
    width: fit-content;
  }}

  .panel-footer {{
    padding: 1.5rem 2.5rem;
    border-top: 1px solid #c8c0b0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .location-text {{
    font-size: 0.58rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.1em;
    color: #8a8478;
  }}

  .updated-text {{
    font-size: 0.52rem;
    font-family: 'Space Mono', monospace;
    color: #c8c0b0;
  }}
</style>
</head>
<body>

<div class="image-zone">
  <div class="image-loading" id="loader">
    <div class="spinner"></div>
    <span class="spinner-text">Painting the plant</span>
  </div>
  <img
    src="{image_url}"
    alt="{plant['common']}"
    onload="document.getElementById('loader').style.display='none'"
    onerror="document.getElementById('loader').style.display='none'"
  />
</div>

<div class="info-panel">

  <div class="panel-header">
    <span class="panel-title">Flora · Today</span>
    <span class="panel-date">{datetime.now().strftime('%d %B %Y')}</span>
  </div>

  <div class="weather-grid">
    <div class="weather-item">
      <span class="weather-label">Temperature</span>
      <span class="weather-value">{weather['temp']}°C</span>
    </div>
    <div class="weather-item">
      <span class="weather-label">Humidity</span>
      <span class="weather-value">{weather['humidity']}%</span>
    </div>
    <div class="weather-item">
      <span class="weather-label">Condition</span>
      <span class="weather-value">{weather['condition']}</span>
    </div>
    <div class="weather-item">
      <span class="weather-label">Season</span>
      <span class="weather-value">{season}</span>
    </div>
  </div>

  <div class="plant-section">
    <div class="plant-latin">{plant['latin']}</div>
    <div class="plant-common">{plant['common'].upper()}</div>
    <div class="divider"></div>
    <div class="plant-note">{plant['note']}</div>
    <div class="phenology-tag">{plant['phenology']}</div>
  </div>

  <div class="panel-footer">
    <span class="location-text">{city}, {country}</span>
    <span class="updated-text">updated {updated_at}</span>
  </div>

</div>
</body>
</html>"""

def run():
    city_data = random.choice(CITIES)
    city = city_data["name"]
    country = city_data["country"]
    lat = city_data["lat"]
    lon = city_data["lon"]

    print(f"[{datetime.now().strftime('%H:%M')}] {city}, {country}")

    try:
        weather = get_weather(lat, lon)
        print(f"  Weather : {weather['temp']}°C, {weather['condition']}")

        month = datetime.now().month
        season = get_season(month, lat)

        plant = get_plant(city, country, lat, weather["temp"], weather["humidity"], weather["condition"], season)
        print(f"  Plant   : {plant['latin']} ({plant['common']})")

        image_url = get_image_url(plant.get("image_prompt", f"botanical illustration of {plant['latin']}, japanese woodblock style"))
        print(f"  Image   : generating...")

        updated_at = datetime.now().strftime("%H:%M")
        html = build_html(city, country, weather, season, plant, image_url, updated_at)

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plant_frame_output.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  Saved   : plant_frame_output.html\n")

    except Exception as e:
        print(f"  Error   : {e}\n")

if __name__ == "__main__":
    print("=" * 40)
    print("  Plant Frame")
    print(f"  Updates every {UPDATE_HOURS} hours")
    print("  Open plant_frame_output.html")
    print("=" * 40 + "\n")

    while True:
        run()
        print(f"  Next update in {UPDATE_HOURS} hours.\n")
        time.sleep(UPDATE_HOURS * 3600)
