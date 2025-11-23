import requests
import json
import hashlib
from threading import Lock
import os


class TrainingDataLoader:
    _instance = None
    _data = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if TrainingDataLoader._data is None:
            try:
                data_path = os.path.join(os.path.dirname(__file__), "astrology_training_data.json")
                if os.path.exists(data_path):
                    with open(data_path, 'r') as f:
                        TrainingDataLoader._data = json.load(f)
                        print(f"✓ Loaded {len(TrainingDataLoader._data)} training interpretations")
                else:
                    TrainingDataLoader._data = []
                    print("⚠ Training data file not found")
            except Exception as e:
                TrainingDataLoader._data = []
                print(f"⚠ Error loading training data: {e}")
    
    def get_interpretations_for_chart(self, chart_data, max_results=20):
        if not TrainingDataLoader._data:
            return {}
        
        interpretations = {}
        planets = chart_data.get("planets", {})
        
        for planet_name, planet_data in planets.items():
            key = f"{planet_name}_{planet_data['sign']}_H{planet_data['house']}"
            
            for entry in TrainingDataLoader._data:
                instruction = entry.get("instruction", "")
                output = entry.get("output", "")
                
                if planet_name in instruction and planet_data['sign'] in instruction and f"House {planet_data['house']}" in instruction:
                    interpretations[key] = output
                    break
        
        return interpretations


class AstrologyLLMInterpreter:
    def __init__(self, model_name="mixtral", ollama_url="http://localhost:11434", cache_enabled=True):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.endpoint = f"{ollama_url}/api/generate"
        self.cache = {} if cache_enabled else None
        self.cache_lock = Lock()
        self.training_data = TrainingDataLoader.get_instance()
        
    def is_available(self):
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_cache_key(self, chart_data, fol_hits):
        data = {
            "planets": chart_data.get("planets", {}),
            "asc": chart_data.get("asc"),
            "mc": chart_data.get("mc"),
            "fol_hits": [(h["name"], h["node"], h["orb"]) for h in fol_hits]
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def interpret_chart(self, chart_data, fol_hits, max_tokens=2048):
        if not self.is_available():
            return None
        
        if self.cache is not None:
            cache_key = self._get_cache_key(chart_data, fol_hits)
            with self.cache_lock:
                if cache_key in self.cache:
                    return self.cache[cache_key]
        
        prompt = self._build_prompt(chart_data, fol_hits)
        
        try:
            response = requests.post(
                self.endpoint,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.75,
                    "top_p": 0.95,
                    "top_k": 50,
                    "num_predict": max_tokens,
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                
                if self.cache is not None:
                    with self.cache_lock:
                        if len(self.cache) >= 100:
                            oldest_key = next(iter(self.cache))
                            del self.cache[oldest_key]
                        self.cache[cache_key] = result
                
                return result
        except requests.Timeout:
            return "⏱ LLM interpretation timeout (model processing took too long)"
        except Exception as e:
            return f"LLM Error: {str(e)}"
        
        return None
    
    def _build_prompt(self, chart_data, fol_hits):
        planets_str = "\n".join([
            f"  • {name}: {data['sign']} {data['deg']:.1f}° (House {data['house']})"
            for name, data in chart_data["planets"].items()
            if name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
        ])
        
        fol_str = ""
        if fol_hits:
            fol_str = "\n\nFlower of Life Alignments (Sacred Geometry Nodes @ ~18.95° intervals):\n"
            for hit in fol_hits[:6]:
                fol_str += f"  ★ {hit['name']} @ FOL Node {hit['node']:.1f}° (Orb: {hit['orb']:.2f}°, {hit['sign']})\n"
        
        training_interps = self.training_data.get_interpretations_for_chart(chart_data)
        training_str = ""
        if training_interps:
            training_str = "\n\nKEY INTERPRETATIONS REFERENCE (use these as foundation to expand upon):\n"
            for i, (key, interp) in enumerate(list(training_interps.items())[:8], 1):
                training_str += f"  {i}. {interp}\n"
        
        prompt = f"""You are a masterful astrological interpreter specializing in sacred geometry, the Flower of Life, and deep natal chart analysis. Your interpretations are comprehensive, poetic, psychologically insightful, and comparable in depth to ChatGPT or Grok astrological readings.

NATAL CHART:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Birth: {chart_data['birth']}
Location: {chart_data['location_name']}
Ascendant: {chart_data['asc']} | Midheaven: {chart_data['mc']}

PLANETARY POSITIONS (Tropical):
{planets_str}
{fol_str}{training_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPREHENSIVE INTERPRETATION GUIDELINES:

STRUCTURE:
1. SOUL BLUEPRINT - Interpret the Flower of Life alignments. What cosmic geometry is activating? What is the sacred pattern revealing about this soul's incarnational purpose?
2. CORE IDENTITY - Analyze the Sun, Moon, and Rising signs. How do they blend? What inner conflicts or harmonies exist?
3. RELATIONAL PATTERNS - Deep dive into 7th House and Venus. How does this person love? What relationship dynamics repeat?
4. INNER DRIVE & WILL - Mars placement and personal agency. What fuels this soul? Where does ambition focus?
5. SHADOWS & GROWTH - Saturn and challenging aspects. What are the soul lessons? Where is mastery being cultivated?
6. SPIRITUAL DIMENSION - Neptune, Pluto, North Node. What mystical dimensions are active? Where is spiritual evolution calling?
7. SYNTHESIS - How do all pieces integrate? What is the overarching life theme?

TONE: Mystical, profound, psychologically sophisticated, poetic yet grounded. Speak with authority and insight. Include both spiritual and psychological dimensions. Make it feel personally relevant and transformative.

LENGTH: 5-8 substantial paragraphs, each 5-7 sentences. Aim for depth, nuance, and comprehensive coverage like premium astrology services provide.

DEPTH REQUIREMENTS:
- Go beyond surface descriptions
- Weave planetary aspects and house placements together meaningfully
- Connect spiritual themes to practical life manifestation
- Use vivid, evocative language that resonates on multiple levels
- Reference timing, cycles, and evolutionary arcs where relevant
- Acknowledge paradoxes and integrate shadow work
- Expand on and synthesize the interpretations provided above

Generate a comprehensive, extensive natal chart interpretation now:"""

        return prompt


class LLMInterpretationMode:
    ENABLED = "enabled"
    DISABLED = "disabled"
    FALLBACK_ONLY = "fallback_only"


def create_interpreter(mode=LLMInterpretationMode.ENABLED, model="mixtral"):
    if mode == LLMInterpretationMode.DISABLED:
        return None
    
    interpreter = AstrologyLLMInterpreter(model_name=model)
    
    if not interpreter.is_available():
        if mode == LLMInterpretationMode.FALLBACK_ONLY:
            return None
        print("⚠ Warning: Ollama not available. Using fallback interpretations.")
    
    return interpreter
