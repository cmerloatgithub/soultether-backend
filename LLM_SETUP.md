# SoulTether LLM Integration Guide

## Overview
This guide explains how to integrate a **medium-sized LLM** (30B+ parameters) for isolated astrology interpretation generation, completely decoupled from user interaction.

## Local LLM Options (30B+ Medium)

### Recommended: Ollama + Mixtral 8x7B or Llama2 13B

**Ollama** is the simplest - single command installation and model serving.

1. **Install Ollama**
   - macOS: https://ollama.ai (download and run)
   - Linux: `curl https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai

2. **Pull a Medium Model**
   ```bash
   # Option 1: Mixtral 8x7B (most capable, ~49GB)
   ollama pull mixtral:latest
   
   # Option 2: Llama2 13B (balanced, ~23GB)
   ollama pull llama2:13b
   
   # Option 3: Neural Chat 7B (lightweight, ~15GB)
   ollama pull neural-chat
   ```

3. **Start Ollama Server** (runs on `localhost:11434`)
   ```bash
   ollama serve
   ```

## Integration with SoulTether

### Installation
```bash
pip install requests  # Already installed for geocoding
```

### Python Integration Code

Create `llm_interpreter.py`:

```python
import requests
import json

class AstrologyLLMInterpreter:
    def __init__(self, model_name="mixtral", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.endpoint = f"{ollama_url}/api/generate"
        
    def is_available(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def interpret_chart(self, chart_data, fol_hits):
        """
        Generate astrology interpretation from chart and FOL alignments
        
        Args:
            chart_data: Dict with 'birth', 'location_name', 'asc', 'mc', 'planets'
            fol_hits: List of celestial body FOL node alignments
        
        Returns:
            str: LLM-generated interpretation
        """
        if not self.is_available():
            return None
        
        prompt = self._build_prompt(chart_data, fol_hits)
        
        try:
            response = requests.post(
                self.endpoint,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
        except Exception as e:
            print(f"LLM Error: {e}")
        
        return None
    
    def _build_prompt(self, chart_data, fol_hits):
        """Build system prompt with chart context for LLM"""
        
        planets_str = "\n".join([
            f"- {name}: {data['sign']} {data['deg']:.1f}° (House {data['house']})"
            for name, data in chart_data["planets"].items()
        ])
        
        fol_str = ""
        if fol_hits:
            fol_str = "\n\nFlower of Life Alignments (Sacred Geometry Nodes):\n"
            fol_str += "\n".join([
                f"- {hit['name']} @ {hit['sign']} {hit['lon']:.2f}° (Node: {hit['node']:.2f}°, Orb: {hit['orb']:.2f}°)"
                for hit in fol_hits[:8]
            ])
        
        prompt = f"""You are an expert astrologer specializing in natal chart interpretation and sacred geometry (Flower of Life).

BIRTH CHART DATA:
Birth: {chart_data['birth']}
Location: {chart_data['location_name']}
Ascendant: {chart_data['asc']}
Midheaven: {chart_data['mc']}

PLANETARY POSITIONS (Tropical):
{planets_str}
{fol_str}

INTERPRETATION TASK:
Generate a poetic yet precise spiritual interpretation of this natal chart. Focus on:
1. The life purpose indicated by FOL node alignments
2. Soul lessons revealed by the Ascendant and 7th/10th house placements
3. Conscious integration of Flower of Life geometry with traditional astrology
4. Practical guidance for spiritual development

Write in a mystical but grounded tone. Be specific to the chart placements provided. Keep to 3-4 paragraphs."""

        return prompt


# Example usage in soultether_mobile.py
if __name__ == "__main__":
    interpreter = AstrologyLLMInterpreter("mixtral")
    
    if interpreter.is_available():
        print("✓ LLM service running")
    else:
        print("✗ Ollama server not found. Start with: ollama serve")
```

### Integration into `soultether_mobile.py`

Add to imports:
```python
from llm_interpreter import AstrologyLLMInterpreter
```

Modify the `calculate` method:
```python
def calculate(self, _):
    try:
        dt = datetime.strptime(
            f"{self.date.text} {self.time.text}", "%Y-%m-%d %H:%M"
        )
        
        lat, lon = geocode_location(self.location.text)
        
        chart = get_full_chart(dt, lat, lon)
        chart["location_name"] = self.location.text
        
        hits = calculate_fol(chart, orb_threshold=2.0)
        
        interpreter = AstrologyLLMInterpreter("mixtral")
        llm_interpretation = interpreter.interpret_chart(chart, hits)
        
        reading = generate_reading(hits, chart)
        
        if llm_interpretation:
            reading += "\n\n" + "="*70
            reading += "\n🔮 SOUL INTERPRETATION (LLM-Generated):\n"
            reading += llm_interpretation
            reading += "\n" + "="*70
        
        self.result.text = reading
        self.result.height = self.result.texture_size[1] + 20
        self.save_btn.disabled = False
        self.save_btn.reading = reading
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        Popup(title="Error", content=Label(text=error_msg), size_hint=(0.85, 0.4)).open()
```

## Astrology Training Data Sources

### Free Astrology Datasets

1. **Astrodatabank** (Largest public astrology database)
   - https://www.astro.com/astro-databank
   - 15,000+ verified birth charts with interpretations
   - **Download**: Some charts available as CSV/JSON exports

2. **Project Gutenberg** (Public domain astrology books)
   - https://www.gutenberg.org/ebooks/search/?query=astrology
   - "Simplified Horoscope" by Evangeline Adams
   - "The Art of Synthesis" by Alice Bailey
   - "Practical Astrology" by various authors

3. **Wikipedia Astrology Articles**
   - https://en.wikipedia.org/wiki/Astrology
   - House systems, planet meanings, aspects, signs
   - Freely available for ML training

4. **Sacred Geometry & Flower of Life**
   - Academic papers on geometric symbolism
   - Drunvalo Melchizedek's "The Ancient Secret of the Flower of Life"
   - Online sacred geometry databases

5. **Cafeastrology.com & AstrologyZone**
   - Sign interpretations (sign-off for ML use)
   - Daily horoscope templates
   - Planet meanings and aspects

### Creating Fine-Tuning Dataset

Structure for model fine-tuning:

```json
{
  "instruction": "Interpret this birth chart data",
  "input": {
    "sun_sign": "Gemini",
    "moon_sign": "Pisces",
    "ascendant": "Libra",
    "fol_alignments": [
      {"planet": "Mercury", "node": 18.947, "orb": 0.5}
    ]
  },
  "output": "Mercury's alignment with the FOL node in Gemini indicates..."
}
```

### Python Script to Scrape & Prepare Training Data

```python
import requests
import json
from bs4 import BeautifulSoup

def scrape_astrodatabank():
    """Fetch and parse astrology interpretations"""
    url = "https://www.astro.com/astro-databank"
    # Note: Respect robots.txt and rate limits
    # Consider requesting bulk export directly from astro.com

def prepare_finetuning_dataset():
    """Create dataset for model fine-tuning"""
    training_data = []
    
    # Load various sources
    for sign in SIGNS:
        for house in range(1, 13):
            for planet in PLANETS:
                training_data.append({
                    "instruction": "Create an astrology interpretation",
                    "input": f"{planet} in {sign} House {house}",
                    "output": lookup_astrodatabank(planet, sign, house)
                })
    
    return training_data

# Save for fine-tuning
dataset = prepare_finetuning_dataset()
with open("astrology_training_data.jsonl", "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")
```

## Fine-Tuning a Model (Optional)

### Using Ollama with Custom Model

1. **Create Modelfile** (`Astrology.modelfile`):
```dockerfile
FROM mixtral:latest

SYSTEM """You are an expert astrologer specializing in natal chart interpretation and Flower of Life sacred geometry. Provide poetic yet precise spiritual guidance based on planetary positions, house placements, and geometric alignments. Be mystical but grounded."""
```

2. **Build Custom Model**:
```bash
ollama create astrology-interpreter -f Astrology.modelfile
ollama run astrology-interpreter
```

3. **Use in SoulTether**:
```python
interpreter = AstrologyLLMInterpreter("astrology-interpreter")
```

### Advanced Fine-Tuning with HuggingFace

```bash
# Install fine-tuning tools
pip install transformers peft datasets torch bitsandbytes

# Use LoRA for efficient fine-tuning
python finetune_astrology.py --model mixtral --dataset astrology_training_data.jsonl
```

## Performance Optimization

### Local Model Specifications
- **Memory**: Mixtral 8x7B = ~49GB | Llama2 13B = ~23GB
- **GPU Required**: RTX 3070+ recommended (or use quantized versions)
- **CPU Fallback**: Possible but slow

### Quantization (Reduce Size & Speed Up)

```bash
# Download quantized models (smaller, faster)
ollama pull mixtral:7b-instruct-q4_0  # 10GB, ~2-3x faster
ollama pull llama2:13b-chat-q4_0       # 7GB
```

### Caching Interpretations

```python
import hashlib

class CachedInterpreter(AstrologyLLMInterpreter):
    def __init__(self, *args, cache_size=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
        self.cache_size = cache_size
    
    def interpret_chart(self, chart_data, fol_hits):
        cache_key = hashlib.md5(
            json.dumps([chart_data, fol_hits], sort_keys=True).encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = super().interpret_chart(chart_data, fol_hits)
        
        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[cache_key] = result
        
        return result
```

## Next Steps

1. **Install Ollama** and pull a model (Mixtral or Llama2)
2. **Test locally**: Run `ollama serve` and verify connectivity
3. **Integrate** `llm_interpreter.py` into SoulTether
4. **Gather** astrology datasets from sources above
5. **(Optional) Fine-tune** custom model on astrology-specific data
6. **Deploy** as background service (systemd, Docker, or LaunchAgent)

## Troubleshooting

**"Connection refused" error**
```bash
# Make sure Ollama is running
ollama serve  # Start in separate terminal
```

**Out of memory**
```bash
# Use quantized model (smaller)
ollama pull mixtral:7b-q4_0
```

**Slow responses**
```bash
# Check GPU availability
# Reduce model size or use quantized version
# Implement response caching
```
