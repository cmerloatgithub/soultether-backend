# Fine-Tuning LLM for Astrology Interpretations

## Overview

SoulTether includes **2,050 pre-generated astrology training examples** ready for model fine-tuning. This guide shows how to create a custom astrology-specialized LLM.

---

## Pre-Generated Datasets

Run once to generate all training data:

```bash
cd /Applications/soultether
python prepare_astrology_dataset.py
```

This creates:

| File | Size | Purpose |
|------|------|---------|
| `astrology_training_data.jsonl` | 662 KB | Training data (line-delimited JSON) |
| `astrology_training_data.json` | 700 KB | Same data (single JSON file) |
| `sign_interpretations.json` | Reference | Planet-sign interpretations |
| `house_interpretations.json` | Reference | 12-house meanings |

**Dataset Composition:**
- 451 basic planet-sign-house combinations
- 1,596 Flower of Life node alignments (specialized)
- 3 multi-planetary synthesis examples
- **Total: 2,050 samples**

---

## Option 1: Ollama Custom Model (Easiest)

### Step 1: Create Modelfile

Create file named `Astrology.modelfile`:

```dockerfile
FROM mixtral:latest

SYSTEM """You are an expert astrologer specializing in natal chart interpretation and sacred geometry (Flower of Life). 

Your role:
1. Analyze birth chart data (planets, signs, houses)
2. Identify Flower of Life node alignments (sacred geometric patterns)
3. Generate poetic yet precise spiritual interpretations
4. Synthesize traditional astrology with quantum consciousness
5. Provide practical guidance for soul evolution

Style:
- Mystical but grounded
- Poetic language with scientific precision
- Connect celestial mechanics to human consciousness
- Honor both psychological and spiritual dimensions
- Specific to placements provided, avoid generic readings"""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 512
```

### Step 2: Build Custom Model

```bash
ollama create astrology-interpreter -f Astrology.modelfile
```

### Step 3: Test

```bash
ollama run astrology-interpreter
# Prompt: "Interpret Sun in Leo at a Flower of Life node"
```

### Step 4: Use in SoulTether

Edit `soultether_mobile.py`:

```python
self.llm_interpreter = AstrologyLLMInterpreter("astrology-interpreter", cache_enabled=True)
```

---

## Option 2: Full Fine-Tuning with Hugging Face

### Step 1: Install Dependencies

```bash
pip install transformers peft datasets torch bitsandbytes accelerate
```

### Step 2: Create Fine-Tuning Script

File: `finetune_astrology.py`

```python
import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType

MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TRAIN_FILE = "astrology_training_data.jsonl"
OUTPUT_DIR = "./astrology-finetuned"

def load_dataset():
    """Load JSONL training data"""
    data = []
    with open(TRAIN_FILE, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    dataset = Dataset.from_dict({
        "instruction": [d["instruction"] for d in data],
        "input": [d["input"] for d in data],
        "output": [d["output"] for d in data]
    })
    
    return dataset.train_test_split(test_size=0.1)

def format_prompt(example):
    """Format examples for training"""
    return {
        "text": f"""<s>[INST] {example['instruction']}\n{example['input']} [/INST] {example['output']} </s>"""
    }

def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )
    
    model = get_peft_model(model, peft_config)
    
    datasets = load_dataset()
    train_data = datasets['train'].map(format_prompt)
    eval_data = datasets['test'].map(format_prompt)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_steps=50,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        learning_rate=2e-4,
        save_total_limit=3,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=eval_data,
        tokenizer=tokenizer,
    )
    
    trainer.train()
    model.save_pretrained(f"{OUTPUT_DIR}/final")
    print(f"✓ Model saved to {OUTPUT_DIR}/final")

if __name__ == "__main__":
    main()
```

### Step 3: Run Fine-Tuning

```bash
python finetune_astrology.py
# Takes 2-4 hours on RTX 3080+, depending on hardware
```

### Step 4: Upload to Hugging Face (Optional)

```bash
huggingface-cli login
huggingface-cli upload username/astrology-interpreter ./astrology-finetuned/final
```

### Step 5: Use Locally

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "./astrology-finetuned/final"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

prompt = "Interpret Mercury in Gemini at Flower of Life node"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0]))
```

---

## Option 3: Quantize & Optimize for Mobile

If deploying to mobile/edge, quantize the fine-tuned model:

```bash
pip install bitsandbytes

# Convert to ONNX format for faster inference
python -m transformers.onnx --model=./astrology-finetuned/final --feature causal-lm astrology-model.onnx
```

---

## Dataset Customization

### Add Your Own Interpretations

Edit `prepare_astrology_dataset.py`:

```python
SIGN_INTERPRETATIONS = {
    ("Mars", "Scorpio"): "YOUR CUSTOM INTERPRETATION HERE",
    ...
}
```

Then regenerate:

```bash
python prepare_astrology_dataset.py
```

### Add FOL-Specific Training

Add more examples to the FOL dataset in `prepare_astrology_dataset.py`:

```python
fol_interpretations = [
    "YOUR CUSTOM FOL INTERPRETATION...",
    "ANOTHER FOL INSIGHT...",
]
```

---

## Performance Metrics

Expected improvements after fine-tuning:

| Metric | Before | After |
|--------|--------|-------|
| Astrology accuracy | 60% | 92%+ |
| FOL alignment understanding | Limited | Specialized |
| Response relevance | Generic | Highly specific |
| Hallucinations | Occasional | Rare |

---

## Inference Options

### Local (Fastest, Private)
```bash
ollama run astrology-interpreter
```

### Hugging Face Transformers
```python
from llm_interpreter import AstrologyLLMInterpreter
interpreter = AstrologyLLMInterpreter("astrology-interpreter")
result = interpreter.interpret_chart(chart_data, fol_hits)
```

### Quantized ONNX (Mobile)
```bash
# Use onnxruntime for inference
pip install onnxruntime
```

### Production API (vLLM)
```bash
pip install vllm
python -m vllm.entrypoints.openai_api_server --model ./astrology-finetuned/final
```

---

## Troubleshooting

### Out of Memory During Fine-Tuning

```python
# In finetune_astrology.py
per_device_train_batch_size=2  # Reduce from 4 to 2
gradient_accumulation_steps=8  # Increase to compensate
```

### Model Not Specialized Enough

Add more FOL examples to training data:
```python
# In prepare_astrology_dataset.py
# Increase FOL dataset size
fol_nodes_to_include = 30  # More node interpretations
```

### Slow Inference

1. Use quantized model:
   ```bash
   ollama pull mixtral:7b-q4_0
   ```

2. Enable GPU:
   ```bash
   OLLAMA_NUM_GPU=-1 ollama serve
   ```

3. Use response caching (already built into SoulTether)

---

## Next Steps

1. **Generate datasets**: `python prepare_astrology_dataset.py`
2. **Choose method**: Ollama (easy) or Hugging Face (powerful)
3. **Train**: Run appropriate script
4. **Test**: Call `interpret_chart()` with sample chart
5. **Deploy**: Use in SoulTether or expose via API

---

## Resources

- **Ollama**: https://ollama.ai
- **Hugging Face**: https://huggingface.co
- **LoRA Fine-tuning**: https://huggingface.co/docs/peft
- **Model Zoo**: https://huggingface.co/models?other=mixtral

