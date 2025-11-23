# SoulTether LLM Quick Start

## TL;DR - Get Running in 5 Minutes

### 1. Install Ollama
- **macOS**: Download from https://ollama.ai
- **Linux**: `curl https://ollama.ai/install.sh | sh`

### 2. Pull a Model (Pick One)
```bash
# Best for local (medium-sized, ~49GB VRAM needed)
ollama pull mixtral:latest

# Or lighter alternative (13B, ~23GB VRAM)
ollama pull llama2:13b

# Or quantized version (7GB, CPU-friendly)
ollama pull mixtral:7b-q4_0
```

### 3. Start Ollama Server
```bash
ollama serve
# Runs on localhost:11434 by default
```

### 4. Run SoulTether (in new terminal)
```bash
cd /Applications/soultether
export GEOAPIFY_API_KEY=88242886b01442bc9caa4e61eeeecdd9
python soultether_mobile.py
```

The app will auto-detect Ollama and add AI-generated interpretations!

---

## How It Works

1. **User enters** birth date, time, location
2. **App calculates** natal chart + FOL alignments  
3. **LLM interpreter** (isolated, background process) receives:
   - Chart data (planets, houses, ascendant)
   - FOL node hits (sacred geometry alignments)
4. **LLM generates** poetic, astrologically-informed interpretation
5. **Reading displayed** with both traditional + AI interpretations

---

## Troubleshooting

### "⚠ LLM service not available"
- Make sure `ollama serve` is running in another terminal
- Check: `curl http://localhost:11434/api/tags`

### Slow response
- Use a quantized model: `ollama pull mixtral:7b-q4_0`
- Or smaller: `ollama pull neural-chat:latest`

### Out of memory
```bash
# Use CPU instead of GPU (slower but works)
OLLAMA_NUM_GPU=0 ollama serve

# Or use most lightweight
ollama pull phi:latest  # 2.7B, ultra-fast
```

### Disable LLM if you want
Edit `soultether_mobile.py`:
```python
USE_LLM = False  # Set to False to skip LLM
```

---

## Model Recommendations by Hardware

| Hardware | Recommended Model | VRAM | Speed |
|----------|------------------|------|-------|
| Apple M1/M2/M3 | `mixtral:7b-q4_0` | 8GB | Fast |
| RTX 4090 | `mixtral:latest` | 40GB+ | Excellent |
| RTX 3080 | `llama2:13b` | 24GB | Good |
| RTX 3070 | `llama2:7b` | 16GB | Good |
| CPU Only | `phi:latest` | N/A | Slow |

---

## Customizing Interpretations

### Modify System Prompt
Edit `llm_interpreter.py`, function `_build_prompt()`:
```python
prompt = f"""You are... [customize instruction here]"""
```

### Use Different Model
In `soultether_mobile.py`:
```python
self.llm_interpreter = AstrologyLLMInterpreter("llama2:13b", cache_enabled=True)
```

### Fine-tune on Custom Astrology Data
See `LLM_SETUP.md` for dataset creation and fine-tuning guide.

---

## Performance Tips

- **Caching**: Already built-in! Same chart = instant cached response
- **Max tokens**: Adjust in `interpret_chart()` if responses too long/short
- **Temperature**: Change 0.7 for more/less creative responses
  - Lower (0.3) = more factual
  - Higher (0.9) = more creative

---

## Training Data Sources

Pre-built datasets ready to use:

1. **Astrodatabank** - 15,000+ verified charts
2. **Wikipedia Astrology** - Free for ML use
3. **Project Gutenberg** - Classic astrology books (public domain)
4. **Sacred Geometry databases** - Flower of Life interpretations

See `LLM_SETUP.md` section "Astrology Training Data Sources" for links and scripts.

---

## What Gets Sent to LLM?

**Only this data** (isolated, never to cloud):
- Birth date/time
- Geocoded location name
- Planet positions (degrees & signs)
- Ascendant/Midheaven
- FOL node alignments & orbs
- House placements

**NOT sent:**
- User identity
- Anything sensitive
- Any other personal data

The LLM runs 100% locally on your machine.
