import streamlit as st
import requests
import math
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="SolarAI",
    page_icon="🪐",
    layout="centered"
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
* { font-family: 'Outfit', sans-serif !important; }
.stApp { background: linear-gradient(160deg, #020617, #0a0f2e, #0f172a) !important; color: white; }
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stMain"] { background: transparent !important; }

.glass-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 18px;
  padding: 18px 20px;
  color: white;
  margin-bottom: 14px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
}
.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.12);
}
.hero-card {
  background: rgba(0,0,0,0.35);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 24px;
  padding: 32px 28px 24px;
  color: white;
  margin-bottom: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.box-title {
  font-size: 10px;
  letter-spacing: 1.4px;
  color: rgba(255,255,255,0.55);
  font-weight: 700;
  margin-bottom: 8px;
  text-transform: uppercase;
}
.chip-row { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 14px; }
.chip {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 20px;
  padding: 4px 13px;
  font-size: 12px;
  color: white;
}
.warn-box {
  background: rgba(180,20,20,0.3);
  border: 1px solid rgba(255,100,100,0.4);
  border-radius: 16px;
  padding: 14px 18px;
  color: white;
  margin-bottom: 12px;
  font-size: 14px;
}
.info-box {
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 14px 18px;
  color: white;
  margin-bottom: 12px;
  font-size: 14px;
  backdrop-filter: blur(8px);
}
.planet-card {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 14px 12px;
  text-align: center;
  color: white;
  backdrop-filter: blur(8px);
  transition: transform 0.2s;
}
.planet-card:hover { transform: translateY(-3px); }
.footer { font-size: 11px; color: rgba(255,255,255,0.35); text-align: center; margin-top: 10px; }
.stTextInput > div > div > input {
  background: rgba(255,255,255,0.1) !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
  border-radius: 12px !important;
  color: white !important;
  font-size: 14px !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.45) !important; }
.stTextInput label { color: white !important; }
.stButton > button {
  background: rgba(255,255,255,0.12) !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
  border-radius: 12px !important;
  color: white !important;
  font-weight: 600 !important;
  transition: all 0.2s;
}
.stButton > button:hover {
  background: rgba(255,255,255,0.22) !important;
  transform: translateY(-1px);
}
.stRadio label, .stRadio div { color: white !important; }
.stSelectbox label { color: white !important; }
.stSlider label { color: white !important; }
.stExpander { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 12px !important; }
.stExpander summary { color: white !important; }
.stSpinner p { color: white !important; }
.stToggle label { color: white !important; }
.main .block-container { position: relative; z-index: 10; }
[data-testid="stVerticalBlock"] { position: relative; z-index: 10; }

@keyframes pulse-star { 0%,100%{opacity:0.4;transform:scale(1)} 50%{opacity:1;transform:scale(1.3)} }
@keyframes float-planet { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
@keyframes orbit { from{transform:rotate(0deg) translateX(60px) rotate(0deg)} to{transform:rotate(360deg) translateX(60px) rotate(-360deg)} }
@keyframes fade-in { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.main-content { animation: fade-in 0.5s ease; }
</style>
""", unsafe_allow_html=True)

# ── Star field canvas ──────────────────────────────────────────────────────────
st.markdown("""
<canvas id="starCanvas" style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;"></canvas>
<script>
(function(){
  var C = document.getElementById('starCanvas');
  if (!C) return;
  var ctx = C.getContext('2d');
  var W, H, stars = [], shooters = [];
  function resize(){ W = C.width = window.innerWidth; H = C.height = window.innerHeight; init(); }
  function rnd(a,b){ return a + Math.random()*(b-a); }
  function mkStar(){ return { x:rnd(0,W), y:rnd(0,H), r:rnd(0.3,1.8), a:rnd(0.2,0.9), ts:rnd(0.01,0.04), tp:rnd(0,6.28) }; }
  function mkShooter(){ return { x:rnd(0,W*0.7), y:rnd(0,H*0.3), vx:rnd(4,9), vy:rnd(2,5), len:rnd(80,160), a:1, life:1 }; }
  function init(){ stars=[]; for(var i=0;i<220;i++) stars.push(mkStar()); }
  var t=0, nextShoot=rnd(3000,8000), lastShoot=0;
  function animate(now){
    t++;
    ctx.clearRect(0,0,W,H);
    // deep space gradient
    var g = ctx.createRadialGradient(W*0.5,H*0.3,0,W*0.5,H*0.5,W*0.8);
    g.addColorStop(0,'rgba(10,15,46,0.98)');
    g.addColorStop(0.5,'rgba(2,6,23,0.98)');
    g.addColorStop(1,'rgba(0,2,10,1)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
    // nebula blobs
    [[W*0.2,H*0.2,'rgba(60,0,120,0.06)'],[W*0.8,H*0.6,'rgba(0,60,120,0.07)'],[W*0.5,H*0.8,'rgba(80,20,0,0.05)']].forEach(function(n){
      var ng=ctx.createRadialGradient(n[0],n[1],0,n[0],n[1],W*0.35);
      ng.addColorStop(0,n[2]); ng.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=ng; ctx.fillRect(0,0,W,H);
    });
    // stars
    stars.forEach(function(s){
      s.tp+=s.ts;
      ctx.save(); ctx.globalAlpha=s.a*(0.4+0.6*Math.sin(s.tp));
      ctx.fillStyle='white'; ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,6.28); ctx.fill();
      ctx.restore();
    });
    // shooting stars
    if(now-lastShoot > nextShoot){ shooters.push(mkShooter()); lastShoot=now; nextShoot=rnd(3000,9000); }
    shooters=shooters.filter(function(sh){
      var grad=ctx.createLinearGradient(sh.x,sh.y,sh.x-sh.vx*sh.len/sh.vx,sh.y-sh.vy*sh.len/sh.vx);
      grad.addColorStop(0,'rgba(255,255,255,'+sh.a+')');
      grad.addColorStop(1,'rgba(255,255,255,0)');
      ctx.beginPath(); ctx.moveTo(sh.x,sh.y); ctx.lineTo(sh.x-sh.len*0.7,sh.y-sh.len*0.4);
      ctx.strokeStyle=grad; ctx.lineWidth=1.5; ctx.stroke();
      sh.x+=sh.vx; sh.y+=sh.vy; sh.a*=0.96; sh.life-=0.025;
      return sh.life>0;
    });
    requestAnimationFrame(animate);
  }
  window.addEventListener('resize',resize);
  resize();
  requestAnimationFrame(animate);
})();
</script>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
PLANETS = {
    "Mercury": {"emoji":"🟤","color":"#b5b5b5","desc":"Closest to the Sun","diameter_km":4879,"moons":0,"day_hours":1407.6,"year_days":88,"temp_c":167,"fact":"A year on Mercury is shorter than a day on Mercury!"},
    "Venus":   {"emoji":"🟡","color":"#e8c97a","desc":"Hottest planet","diameter_km":12104,"moons":0,"day_hours":5832.5,"year_days":225,"temp_c":464,"fact":"Venus rotates backwards compared to most planets."},
    "Earth":   {"emoji":"🔵","color":"#4fa3e0","desc":"Our home","diameter_km":12756,"moons":1,"day_hours":24,"year_days":365,"temp_c":15,"fact":"Earth is the only planet not named after a god."},
    "Mars":    {"emoji":"🔴","color":"#c1440e","desc":"The Red Planet","diameter_km":6792,"moons":2,"day_hours":24.6,"year_days":687,"temp_c":-65,"fact":"Mars has the tallest volcano in the solar system — Olympus Mons."},
    "Jupiter": {"emoji":"🟠","color":"#c88b3a","desc":"Largest planet","diameter_km":142984,"moons":95,"day_hours":9.9,"year_days":4333,"temp_c":-110,"fact":"Jupiter's Great Red Spot is a storm that has lasted 350+ years."},
    "Saturn":  {"emoji":"🪐","color":"#e4d191","desc":"The Ringed Planet","diameter_km":120536,"moons":146,"day_hours":10.7,"year_days":10759,"temp_c":-140,"fact":"Saturn's rings are made of ice and rock, and are only ~10m thick."},
    "Uranus":  {"emoji":"🩵","color":"#7de8e8","desc":"The Ice Giant","diameter_km":51118,"moons":27,"day_hours":17.2,"year_days":30687,"temp_c":-195,"fact":"Uranus rotates on its side — its axial tilt is 98 degrees!"},
    "Neptune": {"emoji":"💙","color":"#5b7fde","desc":"Windiest planet","diameter_km":49528,"moons":16,"day_hours":16.1,"year_days":60190,"temp_c":-200,"fact":"Winds on Neptune can reach 2,100 km/h — the fastest in the solar system."},
}

MOON_PHASES = [
    (0.0,  "🌑", "New Moon"),
    (0.125,"🌒", "Waxing Crescent"),
    (0.25, "🌓", "First Quarter"),
    (0.375,"🌔", "Waxing Gibbous"),
    (0.5,  "🌕", "Full Moon"),
    (0.625,"🌖", "Waning Gibbous"),
    (0.75, "🌗", "Last Quarter"),
    (0.875,"🌘", "Waning Crescent"),
]

CONSTELLATIONS = [
    ("Orion","The Hunter","Winter","⭐ Betelgeuse, Rigel, Bellatrix"),
    ("Ursa Major","The Great Bear","Year-round","⭐ Dubhe, Merak (Big Dipper)"),
    ("Scorpius","The Scorpion","Summer","⭐ Antares, Shaula"),
    ("Leo","The Lion","Spring","⭐ Regulus, Denebola"),
    ("Cassiopeia","The Queen","Year-round","⭐ Schedar, Caph"),
    ("Cygnus","The Swan","Summer","⭐ Deneb, Albireo"),
    ("Virgo","The Maiden","Spring","⭐ Spica"),
    ("Gemini","The Twins","Winter","⭐ Castor, Pollux"),
]

SPACE_EVENTS_2025 = [
    ("🌑","New Moon","Jan 29, 2025"),
    ("🌕","Full Moon (Snow Moon)","Feb 12, 2025"),
    ("☄️","Perseid Meteor Shower Peak","Aug 11-13, 2025"),
    ("🌙","Total Lunar Eclipse","Mar 14, 2025"),
    ("🌞","Solar Eclipse (partial)","Mar 29, 2025"),
    ("🪐","Saturn at Opposition","Sep 21, 2025"),
    ("♃","Jupiter at Opposition","Dec 7, 2025"),
    ("☄️","Geminid Meteor Shower Peak","Dec 13-14, 2025"),
    ("🌑","Annular Solar Eclipse","Feb 17, 2026"),
    ("🔭","James Webb Deep Field Update","Ongoing 2025"),
]

SPACE_FACTS = [
    "🌌 There are more stars in the universe than grains of sand on all of Earth's beaches.",
    "⚫ A black hole's gravity is so strong that not even light can escape.",
    "🌙 The Moon is slowly drifting away from Earth at ~3.8 cm per year.",
    "☀️ The Sun accounts for 99.86% of all mass in the solar system.",
    "🪐 If you could put Saturn in water, it would float — it's less dense than water.",
    "🔭 The light you see from distant stars may be thousands of years old.",
    "🌍 Earth's magnetic field flips roughly every 200,000–300,000 years.",
    "🚀 In space, astronauts grow up to 2 inches taller due to spinal expansion.",
    "💫 Neutron stars are so dense that a teaspoon would weigh ~1 billion tons.",
    "🌠 Shooting stars are actually tiny meteoroids burning up in the atmosphere.",
    "☄️ Halley's Comet visits Earth roughly every 75–76 years.",
    "🌌 The Milky Way galaxy is about 100,000 light-years across.",
    "🌑 There is a mountain on the Moon called Mons Huygens, taller than any on Earth.",
    "🔴 Mars has the longest canyon in the solar system — Valles Marineris, 4,000 km long.",
    "💨 Uranus radiates almost no internal heat — scientists still don't fully understand why.",
]

# ── Helper functions ───────────────────────────────────────────────────────────
def get_moon_phase(date):
    y, m, d = date.year, date.month, date.day
    if m < 3: y -= 1; m += 12
    a = y // 100; b = a // 4; c = 2 - a + b
    e = int(365.25 * (y + 4716)); f = int(30.6001 * (m + 1))
    jd = c + d + e + f - 1524.5
    phase = ((jd - 2451549.5) % 29.53058867) / 29.53058867
    for threshold, icon, name in reversed(MOON_PHASES):
        if phase >= threshold:
            return icon, name, round(phase * 29.53, 1)
    return "🌑", "New Moon", 0.0

def fetch_iss_position():
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        d = r.json()
        lat = float(d["iss_position"]["latitude"])
        lon = float(d["iss_position"]["longitude"])
        return lat, lon, d["timestamp"]
    except:
        return None, None, None

def fetch_astronauts():
    try:
        r = requests.get("http://api.open-notify.org/astros.json", timeout=5)
        return r.json().get("people", [])
    except:
        return []

def fetch_apod():
    """NASA APOD via a free proxy / demo endpoint."""
    try:
        r = requests.get(
            "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY",
            timeout=8
        )
        return r.json()
    except:
        return None

def fetch_near_earth_objects():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        r = requests.get(
            f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key=DEMO_KEY",
            timeout=8
        )
        data = r.json()
        neos = []
        for date_key, objects in data.get("near_earth_objects", {}).items():
            for obj in objects[:6]:
                neos.append({
                    "name": obj["name"].replace("(","").replace(")",""),
                    "diameter_m": round(obj["estimated_diameter"]["meters"]["estimated_diameter_max"]),
                    "velocity_kmh": round(float(obj["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"])),
                    "miss_km": round(float(obj["close_approach_data"][0]["miss_distance"]["kilometers"])),
                    "hazardous": obj["is_potentially_hazardous_asteroid"],
                })
        return neos
    except:
        return []

def light_year_converter(km):
    ly = km / 9.461e12
    if ly < 0.001: return f"{km:,.0f} km"
    if ly < 1: return f"{ly:.4f} light-years"
    return f"{ly:,.2f} light-years"

def planet_orbit_svg(planet_name):
    planet = PLANETS[planet_name]
    size_map = {"Mercury":8,"Venus":12,"Earth":13,"Mars":10,"Jupiter":28,"Saturn":26,"Uranus":20,"Neptune":19}
    r = size_map.get(planet_name, 12)
    col = planet["color"]
    rings = ""
    if planet_name == "Saturn":
        rings = f'<ellipse cx="50" cy="50" rx="{r+14}" ry="5" fill="none" stroke="{col}" stroke-width="3" opacity="0.5"/>'
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="width:70px;height:70px;animation:float-planet 4s ease-in-out infinite;">
      <defs>
        <radialGradient id="pg_{planet_name}" cx="35%" cy="35%">
          <stop offset="0%" stop-color="white" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="{col}"/>
        </radialGradient>
      </defs>
      {rings}
      <circle cx="50" cy="50" r="{r}" fill="url(#pg_{planet_name})"/>
    </svg>"""

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("tab", "🌌 Dashboard"), ("diary", []), ("wishlist", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:16px 0 8px;">
  <div style="font-size:44px;font-weight:900;color:white;letter-spacing:-2px;text-shadow:0 0 40px rgba(100,150,255,0.5);">
    🪐 SolarAI
  </div>
  <div style="font-size:14px;color:rgba(255,255,255,0.55);margin-top:4px;">
    Your personal space & astronomy companion
  </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation tabs ────────────────────────────────────────────────────────────
tabs = ["🌌 Dashboard", "🪐 Planets", "🛸 ISS Tracker", "☄️ Asteroids", "🔭 Sky Tonight", "🚀 Events", "📔 Space Diary"]
selected_tab = st.radio("", tabs, horizontal=True, label_visibility="collapsed")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════
if selected_tab == "🌌 Dashboard":

    now = datetime.now()
    moon_icon, moon_name, moon_days = get_moon_phase(now)

    # Hero card
    st.markdown(f"""
    <div class="hero-card main-content">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:4px;">{now.strftime("%A, %B %d %Y · %I:%M %p UTC")}</div>
          <div style="font-size:32px;font-weight:900;color:white;letter-spacing:-1px;">What's in the Sky Tonight?</div>
          <div style="font-size:15px;color:rgba(255,255,255,0.7);margin-top:6px;">
            {moon_icon} Moon is <strong>{moon_days} days</strong> into its cycle — <strong>{moon_name}</strong>
          </div>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,0.06);border-radius:16px;padding:16px 24px;border:1px solid rgba(255,255,255,0.1);">
          <div style="font-size:52px;">{moon_icon}</div>
          <div style="font-size:13px;font-weight:700;color:white;margin-top:4px;">{moon_name}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);">Day {moon_days} of 29.5</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Daily space fact
    fact = SPACE_FACTS[now.day % len(SPACE_FACTS)]
    st.markdown(f'<div class="info-box"><div class="box-title">✨ Space Fact of the Day</div>{fact}</div>', unsafe_allow_html=True)

    # Quick stats row
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:12px 0 8px;">🌟 Solar System At a Glance</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    stats = [
        ("☀️", "Distance to Sun", "149.6M km", "1 AU"),
        ("🌙", "Moon Distance", "384,400 km", "Light: 1.28 sec"),
        ("⭐", "Nearest Star", "4.24 ly", "Proxima Centauri"),
        ("🌌", "Milky Way Width", "100,000 ly", "~250B stars"),
    ]
    for col, (ico, lbl, val, sub) in zip(cols, stats):
        with col:
            st.markdown(f"""<div class="glass-card" style="text-align:center;padding:14px 10px;">
              <div style="font-size:26px;">{ico}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.5);margin:4px 0;">{lbl}</div>
              <div style="font-size:15px;font-weight:700;color:white;">{val}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # APOD section
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:16px 0 8px;">📸 NASA Astronomy Picture of the Day</p>', unsafe_allow_html=True)
    with st.spinner("Loading APOD..."):
        apod = fetch_apod()
    if apod and "url" in apod:
        media = apod.get("media_type", "image")
        title = apod.get("title", "")
        expl = apod.get("explanation", "")[:300] + "..."
        if media == "image":
            st.markdown(f"""<div class="glass-card">
              <div class="box-title">📷 {apod.get('date','')}</div>
              <img src="{apod['url']}" style="width:100%;border-radius:12px;margin-bottom:10px;object-fit:cover;max-height:340px;" alt="{title}"/>
              <div style="font-size:16px;font-weight:700;color:white;margin-bottom:6px;">{title}</div>
              <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.7;">{expl}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="glass-card">
              <div class="box-title">📹 NASA APOD Video</div>
              <div style="font-size:16px;font-weight:700;color:white;margin-bottom:6px;">{title}</div>
              <div style="font-size:13px;color:rgba(255,255,255,0.7);">{expl}</div>
              <a href="{apod['url']}" target="_blank" style="color:#60a5fa;">▶ Watch Video</a>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">📷 APOD temporarily unavailable — try again shortly.</div>', unsafe_allow_html=True)

    # Tonight's constellations
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:16px 0 8px;">✨ Notable Constellations</p>', unsafe_allow_html=True)
    cols2 = st.columns(2)
    for i, (name, meaning, season, stars) in enumerate(CONSTELLATIONS[:4]):
        with cols2[i % 2]:
            st.markdown(f"""<div class="glass-card">
              <div style="font-size:13px;font-weight:700;color:white;">{name}</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">"{meaning}" · Best in {season}</div>
              <div style="font-size:11px;color:rgba(255,200,100,0.8);margin-top:4px;">{stars}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 2 — PLANETS
# ═══════════════════════════════════════════════════════════
elif selected_tab == "🪐 Planets":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">🪐 Solar System Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:16px;">Click a planet to explore its details</p>', unsafe_allow_html=True)

    selected_planet = st.selectbox("Select a planet", list(PLANETS.keys()), label_visibility="collapsed")

    # Planet grid
    planet_cols = st.columns(4)
    for i, (pname, pdata) in enumerate(PLANETS.items()):
        with planet_cols[i % 4]:
            border = "rgba(255,255,255,0.5)" if pname == selected_planet else "rgba(255,255,255,0.12)"
            st.markdown(f"""<div class="planet-card" style="border:1px solid {border};margin-bottom:10px;">
              {planet_orbit_svg(pname)}
              <div style="font-size:12px;font-weight:700;color:white;margin-top:4px;">{pname}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.5);">{pdata['desc']}</div>
            </div>""", unsafe_allow_html=True)

    # Selected planet detail
    p = PLANETS[selected_planet]
    st.markdown(f"""
    <div class="hero-card" style="margin-top:16px;">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div>{planet_orbit_svg(selected_planet)}</div>
        <div style="flex:1;">
          <div style="font-size:28px;font-weight:900;color:white;">{selected_planet}</div>
          <div style="font-size:14px;color:rgba(255,255,255,0.6);margin-top:2px;">{p['desc']}</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-top:16px;">
        <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">DIAMETER</div>
          <div style="font-size:16px;font-weight:700;color:white;">{p['diameter_km']:,} km</div>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">MOONS</div>
          <div style="font-size:16px;font-weight:700;color:white;">{p['moons']}</div>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">DAY LENGTH</div>
          <div style="font-size:16px;font-weight:700;color:white;">{p['day_hours']}h</div>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">YEAR LENGTH</div>
          <div style="font-size:16px;font-weight:700;color:white;">{p['year_days']} days</div>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">AVG TEMP</div>
          <div style="font-size:16px;font-weight:700;color:{'#f87171' if p['temp_c']>0 else '#60a5fa'};">{p['temp_c']}°C</div>
        </div>
      </div>
      <div style="margin-top:14px;padding:12px 16px;background:rgba(255,255,255,0.05);border-radius:12px;border-left:3px solid {p['color']};">
        <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-bottom:4px;">💡 DID YOU KNOW?</div>
        <div style="font-size:14px;color:rgba(255,255,255,0.9);">{p['fact']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Age & weight on other planets
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">⚖️ How Much Would You Weigh?</p>', unsafe_allow_html=True)
    weight_input = st.number_input("Your weight on Earth (kg)", min_value=1, max_value=500, value=70, key="weight_inp")
    gravity_ratios = {"Mercury":0.38,"Venus":0.91,"Earth":1.0,"Mars":0.38,"Jupiter":2.34,"Saturn":1.06,"Uranus":0.92,"Neptune":1.19}
    wt_cols = st.columns(4)
    for i, (pname, ratio) in enumerate(gravity_ratios.items()):
        with wt_cols[i % 4]:
            wt = round(weight_input * ratio, 1)
            col = "#4ade80" if wt < weight_input else "#fb923c" if wt > weight_input else "#60a5fa"
            st.markdown(f"""<div class="glass-card" style="text-align:center;padding:12px 8px;">
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">{pname}</div>
              <div style="font-size:22px;font-weight:700;color:{col};">{wt} kg</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);">{ratio}× gravity</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 3 — ISS TRACKER
# ═══════════════════════════════════════════════════════════
elif selected_tab == "🛸 ISS Tracker":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">🛸 ISS Live Tracker</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:12px;">The International Space Station orbits Earth every 90 minutes at 27,600 km/h</p>', unsafe_allow_html=True)

    col_r, _ = st.columns([1, 4])
    with col_r:
        refresh = st.button("🔄 Refresh Position")

    with st.spinner("Fetching live ISS position..."):
        lat, lon, ts = fetch_iss_position()

    if lat is not None:
        dt_utc = datetime.utcfromtimestamp(ts).strftime("%H:%M:%S UTC")
        st.markdown(f"""
        <div class="hero-card">
          <div class="box-title">🛸 International Space Station — Live Position</div>
          <div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:8px;">
            <div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">LATITUDE</div>
              <div style="font-size:28px;font-weight:700;color:white;">{lat:.4f}°</div>
            </div>
            <div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">LONGITUDE</div>
              <div style="font-size:28px;font-weight:700;color:white;">{lon:.4f}°</div>
            </div>
            <div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">TIME</div>
              <div style="font-size:28px;font-weight:700;color:#4ade80;">{dt_utc}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        import streamlit.components.v1 as comp
        comp.html(f"""
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <div id="iss-map" style="height:320px;width:100%;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.15);"></div>
        <script>
        var map = L.map('iss-map', {{zoomControl:true,scrollWheelZoom:false}}).setView([{lat},{lon}], 2);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          attribution:'© CartoDB',maxZoom:18,subdomains:'abcd'
        }}).addTo(map);
        var icon = L.divIcon({{html:'<div style="font-size:28px;filter:drop-shadow(0 0 8px cyan);">🛸</div>',iconSize:[36,36],className:''}});
        L.marker([{lat},{lon}],{{icon:icon}}).addTo(map).bindPopup('<b>ISS</b><br>{lat:.2f}°, {lon:.2f}°').openPopup();
        L.circle([{lat},{lon}],{{radius:2200000,color:'rgba(100,220,255,0.3)',fillColor:'rgba(100,220,255,0.05)',fillOpacity:0.5}}).addTo(map);
        </script>
        """, height=340)
    else:
        st.markdown('<div class="warn-box">⚠️ Could not fetch ISS position. Check your connection.</div>', unsafe_allow_html=True)

    # Astronauts currently in space
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:16px 0 8px;">👨‍🚀 Humans Currently in Space</p>', unsafe_allow_html=True)
    with st.spinner("Fetching crew..."):
        people = fetch_astronauts()

    if people:
        spacecraft_groups = {}
        for p in people:
            sc = p.get("craft", "Unknown")
            spacecraft_groups.setdefault(sc, []).append(p["name"])

        for craft, names in spacecraft_groups.items():
            names_html = "".join(f'<div class="chip">👨‍🚀 {n}</div>' for n in names)
            st.markdown(f"""<div class="glass-card">
              <div class="box-title">🛸 {craft}</div>
              <div class="chip-row">{names_html}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.5);">{len(names)} crew member{"s" if len(names)>1 else ""}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🌍 Total humans in space right now: <strong>{len(people)}</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">👨‍🚀 Could not load crew data.</div>', unsafe_allow_html=True)

    # ISS Facts
    st.markdown("---")
    facts = [
        ("📏", "Length", "109 meters (longer than a football field)"),
        ("⚖️", "Mass", "420,000 kg"),
        ("🏃", "Speed", "27,600 km/h (7.66 km/s)"),
        ("🌍", "Orbits/day", "~15.5 orbits around Earth"),
        ("📡", "Altitude", "~400 km above Earth's surface"),
        ("📅", "In service", "Since November 2, 2000"),
    ]
    cols3 = st.columns(3)
    for i, (ico, lbl, val) in enumerate(facts):
        with cols3[i % 3]:
            st.markdown(f"""<div class="glass-card" style="padding:12px;">
              <div style="font-size:20px;">{ico}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.5);margin-top:4px;">{lbl}</div>
              <div style="font-size:13px;font-weight:600;color:white;">{val}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 4 — ASTEROIDS
# ═══════════════════════════════════════════════════════════
elif selected_tab == "☄️ Asteroids":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">☄️ Near-Earth Objects</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:12px;">Asteroids and comets making a close approach to Earth today — via NASA NeoWs API</p>', unsafe_allow_html=True)

    with st.spinner("Scanning for near-Earth objects..."):
        neos = fetch_near_earth_objects()

    if neos:
        hazardous = [n for n in neos if n["hazardous"]]
        safe = [n for n in neos if not n["hazardous"]]

        if hazardous:
            st.markdown(f'<div class="warn-box">⚠️ <strong>{len(hazardous)} potentially hazardous asteroid{"s" if len(hazardous)>1 else ""}</strong> in today\'s close approach list.</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="info-box">🔭 Found <strong>{len(neos)} near-Earth objects</strong> passing by today — {len(safe)} safe, {len(hazardous)} flagged hazardous.</div>', unsafe_allow_html=True)

        for neo in neos:
            danger_col = "#f87171" if neo["hazardous"] else "#4ade80"
            danger_tag = "⚠️ Potentially Hazardous" if neo["hazardous"] else "✅ Safe Pass"
            miss_m = neo["miss_km"] / 384400  # moon distances
            st.markdown(f"""<div class="glass-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:white;">☄️ {neo['name']}</div>
                  <div style="font-size:12px;color:{danger_col};margin-top:2px;">{danger_tag}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:11px;color:rgba(255,255,255,0.5);">Miss Distance</div>
                  <div style="font-size:16px;font-weight:700;color:white;">{neo['miss_km']:,} km</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);">{miss_m:.1f}× moon distance</div>
                </div>
              </div>
              <div style="display:flex;gap:16px;margin-top:10px;flex-wrap:wrap;">
                <div><div style="font-size:10px;color:rgba(255,255,255,0.5);">DIAMETER</div><div style="font-size:14px;color:white;font-weight:600;">~{neo['diameter_m']} m</div></div>
                <div><div style="font-size:10px;color:rgba(255,255,255,0.5);">VELOCITY</div><div style="font-size:14px;color:white;font-weight:600;">{neo['velocity_kmh']:,} km/h</div></div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">☄️ No close approaches loaded — NASA API may be rate-limited. Try again in a moment.</div>', unsafe_allow_html=True)

    # Asteroid size comparison
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">📏 Asteroid Size Reference</p>', unsafe_allow_html=True)
    size_refs = [
        ("🪨 Pebble","< 1 m","Harmless — burns in atmosphere"),
        ("🏠 House-sized","10–50 m","Local damage if it hits"),
        ("🏙️ City-killer","100–500 m","Regional devastation"),
        ("🌍 Planet-threat","1–10 km","Mass extinction event"),
        ("☄️ Chicxulub scale","10+ km","Dinosaur-level extinction"),
    ]
    for ico, size, effect in size_refs:
        st.markdown(f"""<div class="glass-card" style="padding:10px 16px;margin-bottom:6px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
            <div style="font-size:14px;font-weight:600;color:white;">{ico} {size}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.6);">{effect}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 5 — SKY TONIGHT
# ═══════════════════════════════════════════════════════════
elif selected_tab == "🔭 Sky Tonight":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">🔭 Sky Tonight</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:16px;">What can you see with the naked eye or a telescope tonight?</p>', unsafe_allow_html=True)

    now = datetime.now()
    moon_icon, moon_name, moon_days = get_moon_phase(now)
    moonlight = round(math.sin(moon_days / 29.53 * math.pi) * 100)
    seeing = "Excellent" if moonlight < 20 else "Good" if moonlight < 50 else "Fair" if moonlight < 75 else "Poor"
    seeing_col = "#4ade80" if seeing == "Excellent" else "#a3e635" if seeing == "Good" else "#facc15" if seeing == "Fair" else "#f87171"

    st.markdown(f"""<div class="hero-card">
      <div class="box-title">🌙 Tonight's Observing Conditions</div>
      <div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:8px;">
        <div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);">MOON PHASE</div>
          <div style="font-size:32px;">{moon_icon}</div>
          <div style="font-size:14px;font-weight:600;color:white;">{moon_name}</div>
        </div>
        <div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);">MOONLIGHT</div>
          <div style="font-size:28px;font-weight:700;color:white;">{moonlight}%</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.5);">illumination</div>
        </div>
        <div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);">DARK SKY QUALITY</div>
          <div style="font-size:28px;font-weight:700;color:{seeing_col};">{seeing}</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.5);">for stargazing</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Visible planets tonight (rough guide)
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:14px 0 8px;">🪐 Planets Visible Tonight</p>', unsafe_allow_html=True)
    month = now.month
    visible_map = {
        "Venus":  [1,2,3,9,10,11,12],
        "Mars":   [1,2,3,4,10,11,12],
        "Jupiter":[3,4,5,6,7,8,9],
        "Saturn": [5,6,7,8,9,10],
    }
    visible = [(p, PLANETS[p]) for p, months in visible_map.items() if month in months]
    if not visible:
        visible = [("Jupiter", PLANETS["Jupiter"]), ("Saturn", PLANETS["Saturn"])]

    pcols = st.columns(len(visible))
    for col, (pname, pdata) in zip(pcols, visible):
        with col:
            st.markdown(f"""<div class="planet-card" style="padding:16px 10px;">
              {planet_orbit_svg(pname)}
              <div style="font-size:13px;font-weight:700;color:white;margin-top:6px;">{pname}</div>
              <div style="font-size:10px;color:#4ade80;">Visible tonight</div>
            </div>""", unsafe_allow_html=True)

    # Constellation guide
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:16px 0 8px;">✨ All Constellations Guide</p>', unsafe_allow_html=True)
    for name, meaning, season, stars in CONSTELLATIONS:
        in_season = (season == "Year-round") or (season.lower() in ["winter","spring","summer","fall","autumn"] and True)
        st.markdown(f"""<div class="glass-card" style="padding:12px 16px;margin-bottom:6px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div>
              <div style="font-size:14px;font-weight:700;color:white;">⭐ {name} — {meaning}</div>
              <div style="font-size:11px;color:rgba(255,200,100,0.8);margin-top:2px;">{stars}</div>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.5);">Best: {season}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Light pollution guide
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">💡 Light Pollution Scale (Bortle)</p>', unsafe_allow_html=True)
    bortle = [
        (1,"⬛","Excellent dark sky","Zodiacal light, airglow visible"),
        (2,"🟫","True dark sky","M33 direct vision, faint zodiacal band"),
        (3,"🟩","Rural sky","Some LP on horizon, M15 and M4 visible"),
        (4,"🟨","Rural/suburban","LP clearly visible, >500 stars"),
        (5,"🟧","Suburban sky","M33 only with averted vision"),
        (6,"🟥","Bright suburban","Zodiacal light invisible, M33 invisible"),
        (7,"🔴","Suburban/urban","Sky glow greyish-white"),
        (8,"🟣","City sky","Only 20-30 stars in 6th mag"),
        (9,"⬜","Inner city","Only ~10 stars visible"),
    ]
    for num, dot, label, desc in bortle:
        st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
          <div style="font-size:16px;">{dot}</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);min-width:16px;">{num}</div>
          <div style="flex:1;">
            <div style="font-size:12px;font-weight:600;color:white;">{label}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.45);">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 6 — EVENTS
# ═══════════════════════════════════════════════════════════
elif selected_tab == "🚀 Events":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">🚀 Upcoming Space Events</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:16px;">Eclipses, meteor showers, oppositions and more</p>', unsafe_allow_html=True)

    for ico, name, date in SPACE_EVENTS_2025:
        st.markdown(f"""<div class="glass-card" style="padding:14px 18px;margin-bottom:8px;">
          <div style="display:flex;align-items:center;gap:14px;">
            <div style="font-size:32px;">{ico}</div>
            <div style="flex:1;">
              <div style="font-size:15px;font-weight:700;color:white;">{name}</div>
              <div style="font-size:12px;color:rgba(255,200,100,0.8);margin-top:2px;">📅 {date}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Meteor shower calendar
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">🌠 Annual Meteor Shower Calendar</p>', unsafe_allow_html=True)
    showers = [
        ("🌠","Quadrantids","Jan 3–4","~120/hr","Boötes"),
        ("🌠","Lyrids","Apr 22–23","~18/hr","Lyra"),
        ("🌠","Eta Aquariids","May 5–6","~50/hr","Aquarius"),
        ("🌠","Perseids","Aug 11–13","~100/hr","Perseus"),
        ("🌠","Draconids","Oct 8","Variable","Draco"),
        ("🌠","Orionids","Oct 21–22","~20/hr","Orion"),
        ("🌠","Leonids","Nov 17–18","~15/hr","Leo"),
        ("🌠","Geminids","Dec 13–14","~120/hr","Gemini"),
        ("🌠","Ursids","Dec 22–23","~10/hr","Ursa Minor"),
    ]
    for ico, name, peak, rate, radiant in showers:
        st.markdown(f"""<div class="glass-card" style="padding:10px 16px;margin-bottom:6px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
            <div>
              <div style="font-size:14px;font-weight:600;color:white;">{ico} {name}</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">Radiant: {radiant}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:13px;font-weight:700;color:#facc15;">{peak}</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.5);">{rate} at peak</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Space missions
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">🛸 Active & Notable Space Missions</p>', unsafe_allow_html=True)
    missions = [
        ("🔭","James Webb Space Telescope","NASA/ESA/CSA","Observing 13B+ light-years away"),
        ("🚀","Artemis Program","NASA","Return humans to the Moon"),
        ("🤖","Perseverance Rover","NASA","Exploring Jezero Crater on Mars"),
        ("🌌","Voyager 1","NASA","Interstellar space — 24B km from Earth"),
        ("🪐","Juno","NASA","Orbiting Jupiter since 2016"),
        ("☀️","Parker Solar Probe","NASA","Closest spacecraft to the Sun ever"),
        ("🌍","Sentinel-6","ESA/NASA","Monitoring sea-level rise"),
        ("🚀","Starship","SpaceX","Next-gen heavy-lift launch vehicle"),
    ]
    for ico, name, agency, desc in missions:
        st.markdown(f"""<div class="glass-card" style="padding:12px 16px;margin-bottom:6px;">
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            <div style="font-size:26px;">{ico}</div>
            <div style="flex:1;">
              <div style="font-size:14px;font-weight:700;color:white;">{name}</div>
              <div style="font-size:11px;color:rgba(100,200,255,0.8);">{agency}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:2px;">{desc}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 7 — SPACE DIARY
# ═══════════════════════════════════════════════════════════
elif selected_tab == "📔 Space Diary":

    st.markdown('<p style="color:white;font-weight:900;font-size:22px;margin-bottom:4px;">📔 Space Diary</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.6);font-size:13px;margin-bottom:16px;">Log your stargazing sessions, observations, and cosmic wishes</p>', unsafe_allow_html=True)

    # Log a session
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">🔭 Log a Stargazing Session</p>', unsafe_allow_html=True)
    with st.expander("📝 Add new observation"):
        c1, c2 = st.columns(2)
        with c1:
            obs_location = st.text_input("Location", placeholder="e.g. Backyard, local park", key="obs_loc")
            obs_sky = st.selectbox("Sky conditions", ["Clear ⭐", "Partly cloudy ⛅", "Hazy 🌫️", "Light pollution 🌆"], key="obs_sky")
        with c2:
            obs_equipment = st.selectbox("Equipment used", ["Naked eye", "Binoculars", "Small telescope", "Large telescope", "Camera"], key="obs_eq")
            obs_rating = st.slider("Session rating", 1, 10, 7, key="obs_rate")
        obs_what = st.multiselect("What did you observe?",
            ["Moon", "Jupiter", "Saturn", "Mars", "Venus", "Meteor shower", "Shooting star", "Satellite", "ISS", "Constellation", "Nebula", "Galaxy", "Star cluster", "Aurora"],
            key="obs_what")
        obs_notes = st.text_area("Notes", placeholder="What was special about tonight?", height=80, key="obs_notes")

        if st.button("💾 Save Session", key="save_session"):
            if obs_location.strip():
                entry = {
                    "date": datetime.now().strftime("%B %d, %Y · %I:%M %p"),
                    "location": obs_location,
                    "sky": obs_sky, "equipment": obs_equipment,
                    "rating": obs_rating, "observed": obs_what,
                    "notes": obs_notes
                }
                st.session_state.diary.insert(0, entry)
                st.session_state.diary = st.session_state.diary[:20]
                st.success("✅ Session logged!")
            else:
                st.warning("Please enter a location.")

    # Show diary entries
    if st.session_state.diary:
        st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin:16px 0 8px;">📖 Your Observations</p>', unsafe_allow_html=True)
        for entry in st.session_state.diary:
            obs_tags = "".join(f'<span class="chip">✨ {o}</span>' for o in entry.get("observed", []))
            stars = "⭐" * min(entry["rating"] // 2, 5)
            st.markdown(f"""<div class="glass-card">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,0.45);margin-bottom:6px;">
                <span>📅 {entry['date']}</span><span>{stars} {entry['rating']}/10</span>
              </div>
              <div style="font-size:14px;font-weight:600;color:white;">📍 {entry['location']}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:2px;">{entry['sky']} · {entry['equipment']}</div>
              {f'<div class="chip-row" style="margin-top:8px;">{obs_tags}</div>' if obs_tags else ''}
              {f'<div style="font-size:13px;color:rgba(255,255,255,0.75);margin-top:6px;font-style:italic;">"{entry["notes"]}"</div>' if entry["notes"] else ''}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">📔 No sessions logged yet — add your first stargazing observation above!</div>', unsafe_allow_html=True)

    # Space wishlist
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">🌠 Cosmic Wishlist</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.5);font-size:12px;margin-bottom:10px;">Things you want to see before you die 🌌</p>', unsafe_allow_html=True)

    wish_input = st.text_input("", placeholder="e.g. See a total solar eclipse, observe the Andromeda Galaxy...", key="wish_inp", label_visibility="collapsed")
    if st.button("⭐ Add to Wishlist", key="add_wish") and wish_input.strip():
        if wish_input.strip() not in st.session_state.wishlist:
            st.session_state.wishlist.append(wish_input.strip())
            st.rerun()

    if st.session_state.wishlist:
        for i, wish in enumerate(st.session_state.wishlist):
            wc1, wc2 = st.columns([5, 1])
            with wc1:
                st.markdown(f'<div class="chip" style="padding:8px 14px;font-size:13px;">🌠 {wish}</div>', unsafe_allow_html=True)
            with wc2:
                if st.button("✕", key=f"del_wish_{i}"):
                    st.session_state.wishlist.pop(i)
                    st.rerun()

    # Light-year distance calculator
    st.markdown("---")
    st.markdown('<p style="color:white;font-weight:700;font-size:15px;margin-bottom:8px;">🔢 Space Distance Calculator</p>', unsafe_allow_html=True)
    dist_km = st.number_input("Distance in km", min_value=0, value=384400, step=1000, key="dist_inp")
    dist_ly = dist_km / 9.461e12
    dist_au = dist_km / 149_597_870.7
    light_sec = dist_km / 299_792.458
    st.markdown(f"""<div class="glass-card">
      <div class="box-title">📏 {dist_km:,} km is equal to...</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:8px;">
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:10px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">LIGHT-YEARS</div>
          <div style="font-size:16px;font-weight:700;color:#60a5fa;">{dist_ly:.4e}</div>
        </div>
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:10px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">ASTRONOMICAL UNITS</div>
          <div style="font-size:16px;font-weight:700;color:#fbbf24;">{dist_au:.4f} AU</div>
        </div>
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:10px;text-align:center;">
          <div style="font-size:10px;color:rgba(255,255,255,0.5);">LIGHT TRAVEL TIME</div>
          <div style="font-size:16px;font-weight:700;color:#4ade80;">{light_sec:.2f} sec</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p class="footer">
  🪐 SolarAI · Data from NASA API, Open Notify & Open-Meteo · All free, no API keys required<br>
  Built with the same soul as NimbusAI 🌤️
</p>
""", unsafe_allow_html=True)
