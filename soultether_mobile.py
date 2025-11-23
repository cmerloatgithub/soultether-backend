# soultether_mobile.py - FULL Placidus + FOL + Phantom Houses
# Copy-paste → run → mobile-ready

import os
import json
import random
import threading
from datetime import datetime
import swisseph as swe
from immanuel_interpreter import ImmanuelInterpreter
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import mainthread

try:
    import requests
except ImportError:
    requests = None

try:
    from llm_interpreter import AstrologyLLMInterpreter, LLMInterpretationMode
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    AstrologyLLMInterpreter = None
    LLMInterpretationMode = None

# ================== CONFIG ==================
USE_LLM = False

import os
IMMANUEL_EPHE = os.path.join(os.path.dirname(__file__), "immanuel-python/immanuel/resources/ephemeris")
EPHE_PATH = IMMANUEL_EPHE if os.path.exists(IMMANUEL_EPHE) else "/swisseph-master/ephe"
swe.set_ephe_path(EPHE_PATH)
print(f"Ephemeris path: {EPHE_PATH}")

try:
    from immanuel_interpreter import ImmanuelInterpreter
    IMMANUEL_AVAILABLE = True
except ImportError:
    IMMANUEL_AVAILABLE = False
    ImmanuelInterpreter = None

# Sign names
SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Tiny interpretation databank
INTERP_DB = {
    "phantom_pisces_7th": [
        "Soul operates through deep empathy and boundary dissolution in partnerships.",
        "Relationships are the primary classroom — you absorb, heal, and eventually master unity.",
    ],
    "phantom_gemini_7th": [
        "Communication portal activated — duality bridges ideas; words carry sacred code.",
        "T-square apex: Innovation vs. tension — speak truth amid chaos.",
    ],
    "general": [
        "The Flower of Life was fully activated at your birth. You are a living node.",
        "Trust the phantom layers — they reveal the soul beyond the stars.",
    ],
}


# ================== FULL HOUSE & CHART CALCULATION ==================
def get_full_chart(dt, lat, lon):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

    # Full Placidus houses: returns (house_cusps[12], asc_mc[10])
    houses, ascmc = swe.houses(jd, lat, lon, b"P")  # 'P' = Placidus
    cusps = houses  # 12 house cusps
    asc = ascmc[0]
    mc = ascmc[1]

    # Planets
    planets = {
        swe.SUN: "Sun",
        swe.MOON: "Moon",
        swe.MERCURY: "Mercury",
        swe.VENUS: "Venus",
        swe.MARS: "Mars",
        swe.JUPITER: "Jupiter",
        swe.SATURN: "Saturn",
        swe.URANUS: "Uranus",
        swe.NEPTUNE: "Neptune",
        swe.PLUTO: "Pluto",
        swe.MEAN_NODE: "North Node",
    }

    planet_data = {}
    for body, name in planets.items():
        lon = swe.calc_ut(jd, body)[0][0]
        sign_idx = int(lon // 30)
        deg_in_sign = lon % 30
        house_num = get_house_number(lon, cusps)
        planet_data[name] = {
            "lon": lon,
            "sign": SIGNS[sign_idx],
            "deg": deg_in_sign,
            "house": house_num,
        }

    aspects = calculate_aspects(planet_data)
    
    return {
        "birth": dt.strftime("%Y-%m-%d %H:%M"),
        "lat": lat,
        "lon": lon,
        "asc": f"{SIGNS[int(asc // 30)]} {asc % 30:.2f}°",
        "mc": f"{SIGNS[int(mc // 30)]} {mc % 30:.2f}°",
        "planets": planet_data,
        "cusps": cusps,
        "aspects": aspects,
    }


def calculate_aspects(planet_data, orb=8.0):
    """Calculate major aspects between planets"""
    aspect_angles = {
        0: ("Conjunction", 8.0),
        60: ("Sextile", 6.0),
        90: ("Square", 8.0),
        120: ("Trine", 8.0),
        180: ("Opposition", 8.0),
        150: ("Quincunx", 3.0),
    }
    
    aspects = []
    planets_list = list(planet_data.items())
    
    for i, (name1, data1) in enumerate(planets_list):
        for name2, data2 in planets_list[i+1:]:
            lon1 = data1["lon"]
            lon2 = data2["lon"]
            
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            for angle, (aspect_name, max_orb) in aspect_angles.items():
                orb_diff = abs(diff - angle)
                if orb_diff <= max_orb:
                    aspects.append({
                        "object1": name1,
                        "object2": name2,
                        "type": aspect_name,
                        "orb": orb_diff if diff < 180 else -orb_diff,
                        "angle": angle,
                    })
                    break
    
    return aspects


def get_house_number(planet_lon, cusps):
    """Return house number (1-12) for a longitude"""
    planet_lon = planet_lon % 360
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:  # Wraps over 0°
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
    return 1  # Fallback


# ================== GEOCODING ==================
def geocode_location(location_str):
    if not requests:
        raise ImportError("requests library required for geocoding. Install: pip install requests")
    
    geoapify_key = os.environ.get("GEOAPIFY_API_KEY")
    
    if geoapify_key:
        try:
            response = requests.get(
                "https://api.geoapify.com/v1/geocode/search",
                params={"text": location_str, "apiKey": geoapify_key},
                timeout=10
            )
            if response.status_code == 200 and response.json().get("features"):
                result = response.json()["features"][0]["properties"]
                return float(result["lat"]), float(result["lon"])
        except Exception:
            pass
    
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": location_str, "format": "json"},
            timeout=10,
            headers={"User-Agent": "SoulTether"}
        )
        if response.status_code == 200 and response.json():
            result = response.json()[0]
            return float(result["lat"]), float(result["lon"])
        else:
            raise ValueError(f"Location not found: {location_str}")
    except requests.Timeout:
        raise ValueError(f"Geocoding timeout: Could not reach location service")
    except Exception as e:
        raise ValueError(f"Geocoding error: {str(e)}")





def calculate_fol_nodes():
    """
    Calculate the 37 nodes of the Flower of Life.
    24 nodes at 15° intervals + 13 at 7.5° intervals.
    Each snapped to nearest multiple of 360/432 (0.833° increments).
    """
    increment = 360.0 / 432.0
    
    nodes = [
        0, 7.5, 15, 22.5, 30, 37.5, 45, 52.5, 60, 67.5, 75, 82.5, 90, 97.5, 105, 112.5, 120, 127.5, 135, 142.5,
        150, 157.5, 165, 172.5, 180, 187.5, 195, 202.5, 210, 217.5, 225, 232.5, 240, 247.5, 255, 262.5, 270,
        277.5, 285, 292.5, 300, 307.5, 315, 322.5, 330, 337.5, 345, 352.5
    ]
    
    nodes = nodes[:37]
    
    nodes_snapped = []
    for angle in nodes:
        multiple = round(angle / increment)
        snapped = (multiple % 432) * increment
        nodes_snapped.append((snapped, multiple % 432))
    
    nodes_snapped = sorted(list(set(nodes_snapped)))
    
    return nodes_snapped


def calculate_fol(chart, orb_threshold=2.0):
    fol_nodes = calculate_fol_nodes()
    
    hits = []
    planets_data = {}
    
    if "natal" in chart:
        for name, obj in chart["natal"].objects.items():
            planets_data[str(obj.name)] = {
                "lon": obj.longitude.raw,
                "sign": obj.sign.name,
                "house": obj.house.number,
            }
    else:
        planets_data = chart.get("planets", {})
    

    
    match_attempts = 0
    
    for name, data in planets_data.items():
        lon = data["lon"] % 360
        
        for node_angle, node_multiple in fol_nodes:
            diff = abs(lon - node_angle)
            if diff > 180:
                diff = 360 - diff
            
            match_attempts += 1
            
            if diff <= orb_threshold:
                sign = data["sign"]
                house = data["house"]
                interpreter = ImmanuelInterpreter()
                interpretation = interpreter.format_planetary_description(name, sign, house)
                hits.append(
                    {
                        "name": name,
                        "lon": lon,
                        "node": node_angle,
                        "node_multiple": node_multiple,
                        "orb": diff,
                        "sign": sign,
                        "house": house,
                        "interpretation": interpretation,
                    }
                )
    
    hits.sort(key=lambda h: h["orb"])
    
    return hits


# ================== PHANTOM ZONE & READING ENGINE ==================
def generate_reading(hits, chart):
    reading = [
        f"╔ SOUL TETHER ╗",
        f"Birth: {chart['birth']}",
        f"Location: {chart['location_name']} ({chart['lat']:.4f}°, {chart['lon']:.4f}°)",
        "=" * 70,
    ]
    
    if hits:
        reading.append("\n🌸 FLOWER OF LIFE NODE ALIGNMENTS (within 2°):\n")
        
        for hit in hits:
            reading.append(f"  ★ {hit['name']} @ {hit['sign']} {hit['lon']:.2f}°")
            reading.append(f"     FOL Node: {hit['node']:.2f}° | Orb: {hit['orb']:.2f}°")
            reading.append(f"     House: {hit['house']} | {hit['interpretation']}")
            reading.append("")
    else:
        reading.append("\nNo celestial bodies align with Flower of Life nodes (within 2°).")
    
    reading.append("\n" + "=" * 70)
    reading.append("NATAL CHART ANCHORS:")
    reading.append(f"  Ascendant: {chart['asc']}")
    reading.append(f"  Midheaven: {chart['mc']}")
    reading.append("")
    
    for name in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
        if name in chart["planets"]:
            data = chart["planets"][name]
            reading.append(f"  {name}: {data['sign']} {data['deg']:.1f}° (House {data['house']})")
    
    reading.append("\n" + random.choice(INTERP_DB["general"]))
    reading.append("=" * 70)
    
    return "\n".join(reading)


# ================== SCREEN CLASSES ==================
class OpeningScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        root = BoxLayout(orientation="vertical")
        root.canvas.before.clear()
        with root.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(size=root.size, pos=root.pos)
        
        top_bar = BoxLayout(size_hint_y=0.08, padding=10)
        hamburger = Button(text="☰", size_hint_x=0.1, font_size=20)
        hamburger.bind(on_press=self.show_menu)
        top_bar.add_widget(hamburger)
        top_bar.add_widget(Label(text="", size_hint_x=0.8))
        root.add_widget(top_bar)
        
        spacing = Label(size_hint_y=0.1)
        root.add_widget(spacing)
        
        logo = Image(source="Assets/STPNGs/SoulTetherOpen.png", size_hint_y=0.5)
        root.add_widget(logo)
        
        spacing2 = Label(size_hint_y=0.15)
        root.add_widget(spacing2)
        
        fingerprint_btn = Button(size_hint_y=0.1)
        fingerprint_btn.canvas.before.clear()
        with fingerprint_btn.canvas.before:
            Color(0.3, 0.8, 1, 1)
            RoundedRectangle(size=fingerprint_btn.size, pos=fingerprint_btn.pos, radius=[25])
        fingerprint_btn.bind(on_press=self.go_to_birth_data)
        root.add_widget(fingerprint_btn)
        
        text_btn = Label(text="Press When Ready", size_hint_y=0.08, color=(1, 0.2, 0.2, 1), font_size=16)
        root.add_widget(text_btn)
        
        self.add_widget(root)
    
    def show_menu(self, btn):
        pass
    
    def go_to_birth_data(self, btn):
        self.manager.current = "birthdata"


class BirthDataScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        root = BoxLayout(orientation="vertical")
        root.canvas.before.clear()
        with root.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(size=root.size, pos=root.pos)
        
        top_bar = BoxLayout(size_hint_y=0.08, padding=10)
        hamburger = Button(text="☰", size_hint_x=0.15, font_size=20, background_color=(0.95, 0.95, 0.95, 1))
        hamburger.bind(on_press=self.show_menu)
        top_bar.add_widget(hamburger)
        
        logo = Image(source="Assets/STPNGs/SoulTetherIcon.png", size_hint_x=0.2)
        top_bar.add_widget(logo)
        
        top_bar.add_widget(Label(size_hint_x=0.65))
        root.add_widget(top_bar)
        
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10, padding=20)
        content.bind(minimum_height=content.setter('height'))
        
        content.add_widget(Label(text="enter birth date", size_hint_y=None, height=30, color=(0, 0, 0, 1), font_size=16))
        
        self.date_input = TextInput(hint_text="YYYY-MM-DD", size_hint_y=None, height=50, multiline=False)
        self.date_input.background_color = (0.9, 0.2, 0.2, 1)
        content.add_widget(self.date_input)
        
        content.add_widget(Label(text="enter birth time (if known)", size_hint_y=None, height=30, color=(0, 0, 0, 1), font_size=16))
        
        time_grid = GridLayout(cols=3, size_hint_y=None, height=60, spacing=10)
        self.hour_input = TextInput(hint_text="hour", size_hint_x=0.3, multiline=False)
        self.hour_input.background_color = (0.9, 0.2, 0.2, 1)
        time_grid.add_widget(self.hour_input)
        
        time_grid.add_widget(Label(text=":", color=(0, 0, 0, 1), font_size=20))
        
        self.minute_input = TextInput(hint_text="minute", size_hint_x=0.3, multiline=False)
        self.minute_input.background_color = (0.9, 0.2, 0.2, 1)
        time_grid.add_widget(self.minute_input)
        
        ampm_grid = GridLayout(cols=2, size_hint_x=0.4, size_hint_y=None, height=50, spacing=5)
        am_btn = Button(text="AM", background_color=(0.9, 0.2, 0.2, 1))
        ampm_grid.add_widget(am_btn)
        pm_btn = Button(text="PM", background_color=(0.3, 0.7, 1, 1))
        ampm_grid.add_widget(pm_btn)
        self.am_selected = True
        am_btn.bind(on_press=lambda x: self._select_am(am_btn, pm_btn))
        pm_btn.bind(on_press=lambda x: self._select_pm(am_btn, pm_btn))
        
        time_grid.add_widget(ampm_grid)
        content.add_widget(time_grid)
        
        content.add_widget(Label(text="enter birth location", size_hint_y=None, height=30, color=(0, 0, 0, 1), font_size=16))
        
        self.location_input = TextInput(hint_text="City, Country", size_hint_y=None, height=50, multiline=False)
        self.location_input.background_color = (0.9, 0.2, 0.2, 1)
        content.add_widget(self.location_input)
        
        content.add_widget(Label(size_hint_y=None, height=30))
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        
        fingerprint_btn = Button(size_hint_y=0.1, background_color=(1, 0.7, 0.2, 1))
        fingerprint_btn.bind(on_press=self.calculate)
        root.add_widget(fingerprint_btn)
        
        root.add_widget(Label(text="Press When Ready", size_hint_y=0.05, color=(0.3, 0.7, 1, 1), font_size=14))
        
        self.add_widget(root)
    
    def _select_am(self, am_btn, pm_btn):
        self.am_selected = True
        am_btn.background_color = (0.9, 0.2, 0.2, 1)
        pm_btn.background_color = (0.3, 0.7, 1, 1)
    
    def _select_pm(self, am_btn, pm_btn):
        self.am_selected = False
        am_btn.background_color = (0.3, 0.7, 1, 1)
        pm_btn.background_color = (0.9, 0.2, 0.2, 1)
    
    def show_menu(self, btn):
        pass
    
    def calculate(self, btn):
        try:
            hour = int(self.hour_input.text) if self.hour_input.text else 12
            if not self.am_selected and hour != 12:
                hour += 12
            elif self.am_selected and hour == 12:
                hour = 0
            
            minute = int(self.minute_input.text) if self.minute_input.text else 0
            time_str = f"{hour:02d}:{minute:02d}"
            
            dt = datetime.strptime(
                f"{self.date_input.text} {time_str}", "%Y-%m-%d %H:%M"
            )
            
            lat, lon = geocode_location(self.location_input.text)
            
            if self.app.interpreter:
                chart = self.app.interpreter.get_full_chart(dt, lat, lon, self.location_input.text)
                hits = calculate_fol(chart, orb_threshold=2.0)
                reading = self.app.interpreter.generate_reading(chart, hits)
            else:
                chart = get_full_chart(dt, lat, lon)
                chart["location_name"] = self.location_input.text
                hits = calculate_fol(chart, orb_threshold=2.0)
                reading = generate_reading(hits, chart)
            
            self.show_reading(reading)
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
    
    def show_reading(self, reading):
        reader_screen = self.manager.get_screen("reader")
        reader_screen.set_reading(reading)
        self.manager.current = "reader"
    
    def show_error(self, msg):
        Popup(title="Error", content=Label(text=msg), size_hint=(0.8, 0.3)).open()


class ReaderScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_reading = ""
        
        root = BoxLayout(orientation="vertical")
        root.canvas.before.clear()
        with root.canvas.before:
            Color(0.2, 0.5, 0.6, 1)
            RoundedRectangle(size=root.size, pos=root.pos)
        
        top_bar = BoxLayout(size_hint_y=0.08, padding=10)
        hamburger = Button(text="☰", size_hint_x=0.15, font_size=20, background_color=(0.2, 0.5, 0.6, 1), color=(1, 1, 1, 1))
        hamburger.bind(on_press=self.show_menu)
        top_bar.add_widget(hamburger)
        
        logo = Image(source="Assets/STPNGs/SoulTetherWhiteIcon.png", size_hint_x=0.2)
        top_bar.add_widget(logo)
        
        top_bar.add_widget(Label(size_hint_x=0.65))
        root.add_widget(top_bar)
        
        scroll = ScrollView()
        self.result_label = Label(
            text="",
            size_hint_y=None,
            text_size=(340, None),
            color=(0, 0, 0, 1),
            font_size=12,
            halign="left",
            valign="top",
            padding=(10, 10)
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll.add_widget(self.result_label)
        root.add_widget(scroll)
        
        bottom_bar = BoxLayout(size_hint_y=0.08, padding=10, spacing=10)
        bottom_bar.canvas.before.clear()
        with bottom_bar.canvas.before:
            Color(0.2, 0.5, 0.6, 1)
            RoundedRectangle(size=bottom_bar.size, pos=bottom_bar.pos)
        
        back_btn = Button(text="<", size_hint_x=0.15, font_size=18, color=(1, 1, 1, 1))
        back_btn.bind(on_press=self.go_back)
        bottom_bar.add_widget(back_btn)
        
        text_size = Label(text="A — • — A", size_hint_x=0.7, color=(1, 1, 1, 1))
        bottom_bar.add_widget(text_size)
        
        download_btn = Button(text="↓", size_hint_x=0.15, font_size=18, color=(1, 1, 1, 1))
        download_btn.bind(on_press=self.save_reading)
        bottom_bar.add_widget(download_btn)
        
        root.add_widget(bottom_bar)
        
        self.add_widget(root)
    
    def set_reading(self, reading):
        self.current_reading = reading
        self.result_label.text = reading
    
    def show_menu(self, btn):
        pass
    
    def go_back(self, btn):
        self.manager.current = "birthdata"
    
    def save_reading(self, btn):
        with open("soultether_reading.txt", "w") as f:
            f.write(self.current_reading)
        Popup(title="Saved", content=Label(text="Reading saved"), size_hint=(0.8, 0.2)).open()


# ================== KIVY MOBILE APP ==================
class SoulTetherApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interpreter = None
        if IMMANUEL_AVAILABLE:
            try:
                self.interpreter = ImmanuelInterpreter()
                print("✓ Immanuel interpreter initialized")
            except Exception as e:
                print(f"⚠ Immanuel initialization failed: {e}")
                self.interpreter = None
        
        self.llm_interpreter = None
        if USE_LLM and LLM_AVAILABLE:
            try:
                self.llm_interpreter = AstrologyLLMInterpreter("mixtral", cache_enabled=True)
                if self.llm_interpreter.is_available():
                    print("✓ LLM interpreter initialized (Mixtral)")
                else:
                    print("⚠ LLM service not available (Ollama not running)")
                    self.llm_interpreter = None
            except Exception as e:
                print(f"⚠ LLM initialization failed: {e}")
                self.llm_interpreter = None
    
    def build(self):
        Window.size = (360, 720)
        sm = ScreenManager()
        
        sm.add_widget(OpeningScreen(self, name="opening"))
        sm.add_widget(BirthDataScreen(self, name="birthdata"))
        sm.add_widget(ReaderScreen(self, name="reader"))
        
        return sm


if __name__ == "__main__":
    SoulTetherApp().run()
