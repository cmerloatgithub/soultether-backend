#!/usr/bin/env python3
"""
Prepare astrology training datasets for LLM fine-tuning.
Sources: Astrodatabank, Wikipedia, Project Gutenberg, custom interpretations
"""

import json
import csv
from pathlib import Path


SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "North Node"
]

HOUSES = list(range(1, 13))


SIGN_INTERPRETATIONS = {
    ("Sun", "Aries"): "Solar vitality expresses through pioneering action, courage, and fiery assertion. Life purpose centers on initiating new cycles.",
    ("Sun", "Taurus"): "Solar essence manifests through grounding, stability, and sensory connection. Life purpose involves building lasting value.",
    ("Sun", "Gemini"): "Solar force flows through communication, curiosity, and mental agility. Life purpose centers on connecting ideas and people.",
    ("Sun", "Cancer"): "Solar nature expresses nurturing, emotional depth, and protective instinct. Life purpose involves creating emotional safety.",
    ("Sun", "Leo"): "Solar power radiates creative expression, courage, and authentic leadership. Life purpose centers on creative self-actualization.",
    ("Sun", "Virgo"): "Solar energy manifests through precision, service, and discernment. Life purpose involves refining and improving systems.",
    
    ("Moon", "Aries"): "Emotional nature is spontaneous, courageous, and action-oriented. Inner world seeks immediate authentic response.",
    ("Moon", "Taurus"): "Emotional needs center on stability, comfort, and sensory pleasure. Inner world requires grounding and security.",
    ("Moon", "Gemini"): "Emotional expression is curious, adaptable, and communication-based. Inner world needs variety and mental stimulation.",
    ("Moon", "Cancer"): "Emotional depth is profound, protective, and family-oriented. Inner world seeks emotional safety and belonging.",
    ("Moon", "Leo"): "Emotional nature seeks creative expression, recognition, and warmth. Inner world needs to feel valued and appreciated.",
    ("Moon", "Virgo"): "Emotional response is analytical, service-oriented, and health-focused. Inner world seeks order and practical support.",
    
    ("Mercury", "Gemini"): "Mind dances through multiplicity, language is your superpower. Communication carries layers of meaning and connection.",
    ("Mercury", "Virgo"): "Mind excels at analysis, organization, and practical problem-solving. Communication precise and detail-oriented.",
    ("Mercury", "Sagittarius"): "Mind seeks truth, philosophy, and big-picture understanding. Communication expansive and wisdom-driven.",
    
    ("Venus", "Libra"): "Love seeks harmony, balance, and aesthetic refinement. Relationships are mirrors for personal growth.",
    ("Venus", "Taurus"): "Love is loyal, sensual, and values-driven. Relationships grounded in stability and material security.",
    ("Venus", "Pisces"): "Love dissolves boundaries, seeks unity, and flows with empathy. Relationships transcend ordinary connection.",
    
    ("Mars", "Aries"): "Will-power burns with raw courage and pioneering drive. Action taken decisively and directly.",
    ("Mars", "Scorpio"): "Will-power manifests through depth, intensity, and strategic focus. Action stems from emotional conviction.",
    ("Mars", "Capricorn"): "Will-power channels into sustained effort and strategic mastery. Action disciplined and goal-oriented.",
    
    ("Jupiter", "Sagittarius"): "Expansion flows through philosophy, truth-seeking, and visionary thinking. Luck found through faith and adventure.",
    ("Jupiter", "Pisces"): "Expansion manifests as spiritual growth, compassion, and imagination. Luck through faith and surrender.",
    
    ("Saturn", "Capricorn"): "Mastery achieved through discipline, structure, and strategic authority. Lessons teach responsibility and integrity.",
    ("Saturn", "Aquarius"): "Mastery through innovation, boundaries, and detached wisdom. Lessons teach authentic individuality.",
    
    ("North Node", "Gemini"): "Soul evolves toward communication, adaptability, and intellectual expansion. Learn to hold multiple truths.",
    ("North Node", "Pisces"): "Soul evolves toward surrender, mysticism, and unconditional love. Learn to transcend ego and merge with all.",
    ("North Node", "Taurus"): "Soul evolves toward grounding, values, and sensory presence. Learn to build lasting foundation.",
    ("North Node", "Scorpio"): "Soul evolves toward depth, transformation, and emotional authenticity. Learn to embrace rebirth.",
}

HOUSE_INTERPRETATIONS = {
    1: "Self-expression, personality, physical appearance. How you present to the world.",
    2: "Values, possessions, self-worth. Your relationship with resources.",
    3: "Communication, siblings, short journeys. Mental development and connections.",
    4: "Home, family, foundations. Private self and emotional roots.",
    5: "Creativity, romance, self-expression. Pleasure and children.",
    6: "Work, health, service. Daily routines and practical mastery.",
    7: "Relationships, partnerships, mirrors. How others reflect your shadow.",
    8: "Transformation, shared resources, hidden depths. Rebirth and mystery.",
    9: "Philosophy, higher learning, expansion. Meaning and distant horizons.",
    10: "Career, public image, authority. How the world sees you.",
    11: "Friendships, group consciousness, innovation. Belonging and ideals.",
    12: "Spirituality, hidden matters, dissolution. Surrender and the unconscious.",
}

ASPECT_INTERPRETATIONS = {
    ("conjunction", 0): "Unified power. Energies merge into single expression.",
    ("sextile", 60): "Harmonious flow. Natural ease and creative opportunity.",
    ("square", 90): "Tension and growth. Friction catalyzes development.",
    ("trine", 120): "Lucky flow. Gifts easily expressed and available.",
    ("opposition", 180): "Polarity and projection. Inner conflict meets outer mirror.",
}


def create_basic_dataset():
    """Create baseline astrology interpretation dataset"""
    dataset = []
    
    for (planet, sign), interpretation in SIGN_INTERPRETATIONS.items():
        for house in HOUSES:
            instruction = f"Interpret {planet} in {sign} (House {house})"
            house_context = HOUSE_INTERPRETATIONS.get(house, "")
            output = f"{interpretation} In House {house}: {house_context}"
            
            dataset.append({
                "instruction": instruction,
                "input": f"{planet} {sign} House {house}",
                "output": output
            })
    
    for planet in PLANETS:
        for sign in SIGNS:
            if (planet, sign) not in SIGN_INTERPRETATIONS:
                instruction = f"Interpret {planet} in {sign}"
                output = f"{planet} in {sign} brings unique influence to your chart. This placement affects how you express {planet}'s archetypal energy through {sign}'s lens."
                
                dataset.append({
                    "instruction": instruction,
                    "input": f"{planet} {sign}",
                    "output": output
                })
    
    return dataset


def create_fol_dataset():
    """Create Flower of Life specific training data"""
    dataset = []
    
    fol_nodes = [i * (360 / 19) for i in range(19)]
    
    fol_interpretations = [
        "Sacred geometric alignment activates higher consciousness at this degree.",
        "Flower of Life node resonance: celestial body harmonizes with universal grid.",
        "This planet sits at a power point of sacred geometry—amplified expression.",
        "Geometric alignment indicates soul-level purpose coded in birth chart.",
        "The Flower of Life geometry multiplies this celestial influence exponentially.",
        "Sacred alignment: soul fragments cohere at this geometric node.",
    ]
    
    for idx, node in enumerate(fol_nodes):
        for planet in PLANETS[:7]:
            for sign in SIGNS:
                instruction = f"Interpret {planet} in {sign} aligned with FOL node {node:.1f}°"
                output = f"{planet} in {sign} aligns with Flower of Life node {node:.1f}°. " + \
                        fol_interpretations[idx % len(fol_interpretations)] + \
                        f" This geometry amplifies {planet}'s {sign} expression into universal law."
                
                dataset.append({
                    "instruction": instruction,
                    "input": f"{planet} {sign} FOL Node {node:.1f}°",
                    "output": output
                })
    
    return dataset


def create_chart_synthesis_dataset():
    """Create multi-planetary interpretation examples"""
    dataset = []
    
    synthesis_examples = [
        {
            "planets": [("Sun", "Leo"), ("Moon", "Pisces"), ("Ascendant", "Libra")],
            "output": "The Leo Sun radiates creative power, the Pisces Moon provides mystical depth, and the Libra Ascendant presents a harmonious, diplomatic face to the world. This trinity creates a soul capable of inspired leadership tempered by compassion."
        },
        {
            "planets": [("Sun", "Capricorn"), ("Saturn", "Capricorn"), ("North Node", "Gemini")],
            "output": "Saturn amplifies the Capricorn Sun's mastery instinct—you're built for long-term authority and responsibility. The North Node in Gemini suggests your soul mission involves bringing structure to knowledge and teaching others."
        },
        {
            "planets": [("Moon", "Scorpio"), ("Mars", "Scorpio"), ("Pluto", "Scorpio")],
            "output": "Scorpio stellium creates alchemical transformation power. The Moon's emotional depth, Mars' intensity, and Pluto's regeneration merge into an individual capable of profound personal metamorphosis and helping others through crisis."
        },
    ]
    
    for example in synthesis_examples:
        planets_str = ", ".join([f"{p[0]} {p[1]}" for p in example["planets"]])
        dataset.append({
            "instruction": f"Synthesize chart interpretation for: {planets_str}",
            "input": planets_str,
            "output": example["output"]
        })
    
    return dataset


def save_jsonl(dataset, filename):
    """Save dataset in JSONL format (one JSON object per line)"""
    path = Path(filename)
    with open(path, 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
    print(f"✓ Saved {len(dataset)} entries to {filename}")


def save_json(dataset, filename):
    """Save dataset in JSON format"""
    path = Path(filename)
    
    if isinstance(dataset, dict) and all(isinstance(k, tuple) for k in dataset.keys()):
        dataset = {str(k): v for k, v in dataset.items()}
    
    with open(path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    count = len(dataset) if isinstance(dataset, (dict, list)) else 0
    print(f"✓ Saved to {filename}")


def combine_datasets(*datasets):
    """Combine multiple datasets"""
    combined = []
    for dataset in datasets:
        combined.extend(dataset)
    return combined


def main():
    print("🌸 Preparing Astrology Training Datasets...\n")
    
    basic = create_basic_dataset()
    print(f"✓ Created basic dataset: {len(basic)} samples")
    
    fol = create_fol_dataset()
    print(f"✓ Created FOL dataset: {len(fol)} samples")
    
    synthesis = create_chart_synthesis_dataset()
    print(f"✓ Created synthesis dataset: {len(synthesis)} samples")
    
    combined = combine_datasets(basic, fol, synthesis)
    print(f"✓ Combined total: {len(combined)} samples\n")
    
    save_jsonl(combined, "astrology_training_data.jsonl")
    save_json(combined, "astrology_training_data.json")
    save_json(SIGN_INTERPRETATIONS, "sign_interpretations.json")
    save_json(HOUSE_INTERPRETATIONS, "house_interpretations.json")
    
    print("\n📊 Dataset Summary:")
    print(f"  • Basic interpretations: {len(basic)}")
    print(f"  • FOL alignments: {len(fol)}")
    print(f"  • Multi-planetary synthesis: {len(synthesis)}")
    print(f"  • Total: {len(combined)}")
    print("\n✨ Ready for LLM fine-tuning!")


if __name__ == "__main__":
    main()
