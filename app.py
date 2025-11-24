from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
import logging
import requests

try:
    import swisseph as swe
    swe.set_ephe_path("/app/ephe")
except:
    swe = None
    import ephem
    from datetime import datetime as dt

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

try:
    from immanuel_interpreter import ImmanuelInterpreter
    IMMANUEL_AVAILABLE = True
except ImportError:
    IMMANUEL_AVAILABLE = False
    ImmanuelInterpreter = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('soultether.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

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


def geocode_location(location_str):
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


def get_full_chart(dt, lat, lon):
    if swe is not None:
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
        houses, ascmc = swe.houses(jd, lat, lon, b"P")
        cusps = houses
        asc = ascmc[0]
        mc = ascmc[1]

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
            lon_deg = swe.calc_ut(jd, body)[0][0]
            sign_idx = int(lon_deg // 30)
            deg_in_sign = lon_deg % 30
            house_num = get_house_number(lon_deg, cusps)
            planet_data[name] = {
                "lon": lon_deg,
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
    else:
        return get_full_chart_ephem(dt, lat, lon)


def get_full_chart_ephem(dt, lat, lon):
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = dt
    
    planet_objects = {
        'Sun': ephem.Sun(),
        'Moon': ephem.Moon(),
        'Mercury': ephem.Mercury(),
        'Venus': ephem.Venus(),
        'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn': ephem.Saturn(),
        'Uranus': ephem.Uranus(),
        'Neptune': ephem.Neptune(),
        'Pluto': ephem.Pluto(),
    }
    
    planet_data = {}
    for name, body in planet_objects.items():
        body.compute(observer)
        lon_deg = float(body.hlon) * 180 / 3.14159265359
        lon_deg = lon_deg % 360
        sign_idx = int(lon_deg // 30)
        deg_in_sign = lon_deg % 30
        planet_data[name] = {
            "lon": lon_deg,
            "sign": SIGNS[sign_idx % 12],
            "deg": deg_in_sign,
            "house": 1,
        }
    
    planet_data['North Node'] = {
        "lon": 0,
        "sign": "Aries",
        "deg": 0,
        "house": 1,
    }
    
    sun = ephem.Sun()
    sun.compute(observer)
    sun_lon = float(sun.hlon) * 180 / 3.14159265359 % 360
    
    asc = sun_lon
    mc = sun_lon + 90
    
    aspects = calculate_aspects(planet_data)
    
    return {
        "birth": dt.strftime("%Y-%m-%d %H:%M"),
        "lat": lat,
        "lon": lon,
        "asc": f"{SIGNS[int(asc // 30)]} {asc % 30:.2f}°",
        "mc": f"{SIGNS[int(mc // 30) % 12]} {mc % 30:.2f}°",
        "planets": planet_data,
        "cusps": [0] * 12,
        "aspects": aspects,
    }


def calculate_aspects(planet_data, orb=8.0):
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
    planet_lon = planet_lon % 360
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
    return 1


def calculate_fol_nodes():
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
    
    for name, data in planets_data.items():
        lon = data["lon"] % 360
        
        for node_angle, node_multiple in fol_nodes:
            diff = abs(lon - node_angle)
            if diff > 180:
                diff = 360 - diff
            
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


def generate_reading(hits, chart):
    import random
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


def log_reading_for_training(interpretation_text, chart_date, fol_hits_count):
    training_data = {
        "timestamp": datetime.now().isoformat(),
        "chart_date": chart_date,
        "fol_hits_count": fol_hits_count,
        "interpretation": interpretation_text,
    }
    
    with open("training_data.jsonl", "a") as f:
        f.write(json.dumps(training_data) + "\n")
    
    logger.info(f"Logged training data: {fol_hits_count} FOL hits")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "SoulTether API"}), 200


@app.route('/calculate_reading', methods=['POST'])
def calculate_reading():
    try:
        data = request.get_json()
        
        date_str = data.get('birth_date')
        hour = int(data.get('hour', 12))
        minute = int(data.get('minute', 0))
        is_am = data.get('is_am', True)
        location = data.get('location')
        
        if hour <= 12:
            if not is_am and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
        
        dt = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
        
        lat, lon = geocode_location(location)
        
        chart = get_full_chart(dt, lat, lon)
        chart["location_name"] = location
        
        hits = calculate_fol(chart, orb_threshold=2.0)
        reading = generate_reading(hits, chart)
        
        log_reading_for_training(reading, date_str, len(hits))
        
        return jsonify({
            "success": True,
            "reading": reading,
            "chart_data": {
                "birth": chart['birth'],
                "location": location,
                "coordinates": {"lat": lat, "lon": lon},
                "ascendant": chart['asc'],
                "midheaven": chart['mc'],
                "planets": chart['planets'],
                "fol_hits": len(hits),
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating reading: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
