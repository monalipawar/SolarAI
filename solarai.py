from pathlib import Path
import re

path = Path("/mnt/data/solarai_imperial_updated.py")
text = path.read_text(encoding="utf-8")

# Move/fix helper functions by inserting near top after page config.
insert = """
# ── Unit System ────────────────────────────────────────────
if "unit_system" not in st.session_state:
    st.session_state.unit_system = "Imperial"

with st.sidebar:
    st.markdown("### ⚙️ Units")
    st.session_state.unit_system = st.radio(
        "Unit System",
        ["Imperial", "Metric"],
        index=0
    )

IS_IMPERIAL = st.session_state.unit_system == "Imperial"

def km_to_miles(km): return km * 0.621371
def miles_to_km(mi): return mi / 0.621371
def c_to_f(c): return (c * 9/5) + 32
def kg_to_lb(kg): return kg * 2.20462
def m_to_ft(m): return m * 3.28084

def format_distance(km):
    return f"{km_to_miles(km):,.0f} mi" if IS_IMPERIAL else f"{km:,.0f} km"

def format_temperature(c):
    return f"{c_to_f(c):.0f}°F" if IS_IMPERIAL else f"{c:.0f}°C"

def format_altitude_km(km):
    return f"{m_to_ft(km*1000):,.0f} ft" if IS_IMPERIAL else f"{km:,.0f} km"
"""

text = text.replace(')\n\n# ── Global CSS', ')\n' + insert + '\n# ── Global CSS', 1)

# Remove duplicate block at end
text = re.sub(r'\n# ── Unit System ─[\s\S]*$', '\n', text)

# Replace planet displays
text = text.replace("{p['diameter_km']:,} km", "{format_distance(p['diameter_km'])}")
text = text.replace("{p['temp_c']}°C", "{format_temperature(p['temp_c'])}")

# ISS facts
text = text.replace('("⚖️", "Mass", "420,000 kg"),', '("⚖️", "Mass", "925,000 lb" if IS_IMPERIAL else "420,000 kg"),')
text = text.replace('("🏃", "Speed", "27,600 km/h (7.66 km/s)"),', '("🏃", "Speed", "17,150 mph" if IS_IMPERIAL else "27,600 km/h (7.66 km/s)"),')
text = text.replace('("📡", "Altitude", "~400 km above Earth\'s surface"),', '("📡", "Altitude", ("~1,312,000 ft above Earth\'s surface" if IS_IMPERIAL else "~400 km above Earth\'s surface")),')

# Asteroids
text = text.replace("{neo['miss_km']:,} km", "{format_distance(neo['miss_km'])}")
text = text.replace("~{neo['diameter_m']} m", "~{round(neo['diameter_m']*3.28084)} ft' if IS_IMPERIAL else f'~{neo['diameter_m']} m")
text = text.replace("{neo['velocity_kmh']:,} km/h", "{(neo['velocity_kmh']*0.621371):,.0f} mph' if IS_IMPERIAL else f'{neo['velocity_kmh']:,} km/h")

# Distance calculator
text = text.replace('dist_km = st.number_input("Distance in km", min_value=0, value=384400, step=1000, key="dist_inp")',
                    'dist_input = st.number_input(f"Distance in {\'miles\' if IS_IMPERIAL else \'km\'}", min_value=0, value=238855 if IS_IMPERIAL else 384400, step=1000, key="dist_inp")\ndist_km = miles_to_km(dist_input) if IS_IMPERIAL else dist_input')
text = text.replace('{dist_km:,} km is equal to...', '{(f\"{dist_input:,} miles\" if IS_IMPERIAL else f\"{dist_input:,} km\")} is equal to...')

out = "/mnt/data/solarai_full_imperial_metric.py"
Path(out).write_text(text, encoding="utf-8")
print(out)
