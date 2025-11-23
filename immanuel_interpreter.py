import json
import os
import random
from datetime import datetime
from immanuel import charts
from immanuel.classes.serialize import ToJSON
from immanuel.setup import settings
import swisseph as swe

IMMANUEL_EPHE = os.path.join(os.path.dirname(__file__), "immanuel-python/immanuel/resources/ephemeris")
EPHE_PATH = IMMANUEL_EPHE if os.path.exists(IMMANUEL_EPHE) else "/swisseph-master/ephe"

try:
    swe.set_ephe_path(EPHE_PATH)
    settings.ephemeris_path = EPHE_PATH
except:
    pass


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
    
    def get_interpretation(self, planet, sign, house):
        if not TrainingDataLoader._data:
            return None
        
        for entry in TrainingDataLoader._data:
            instruction = entry.get("instruction", "")
            output = entry.get("output", "")
            
            if planet in instruction and sign in instruction and f"(House {house})" in instruction:
                return output
        
        for entry in TrainingDataLoader._data:
            instruction = entry.get("instruction", "")
            output = entry.get("output", "")
            
            if planet in instruction and sign in instruction:
                return output
        
        for entry in TrainingDataLoader._data:
            instruction = entry.get("instruction", "")
            output = entry.get("output", "")
            
            if planet in instruction and f"House {house}" in instruction:
                return output
        
        return None
    
    def get_random_general(self):
        general_entries = [e.get("output", "") for e in TrainingDataLoader._data if "general" in e.get("instruction", "").lower()]
        return random.choice(general_entries) if general_entries else "Your chart reflects a unique cosmic signature."


class ImmanuelInterpreter:
    SIGN_TRAITS = {
        "Aries": {
            "keywords": "pioneering, courageous, direct, competitive, passionate",
            "description": "You charge forward with warrior spirit, fearless and direct. You're the zodiac's initiator—impulsive, courageous, and hungry for new experiences. Your challenge is channeling this fire productively rather than burning out.",
        },
        "Taurus": {
            "keywords": "stable, grounded, sensual, determined, practical",
            "description": "You're the zodiac's anchor—steady, reliable, and deeply grounded. You possess natural patience and build things that last. Your sensory nature makes you appreciate beauty, comfort, and quality. Your challenge is overcoming stubbornness.",
        },
        "Gemini": {
            "keywords": "curious, communicative, versatile, witty, intellectual",
            "description": "Your mind is your superpower. You're naturally curious, articulate, and adaptable. You collect knowledge and connect with people effortlessly. Your challenge is staying focused and avoiding superficiality.",
        },
        "Cancer": {
            "keywords": "nurturing, emotional, protective, intuitive, sensitive",
            "description": "You lead with your heart. Deeply emotional and intuitive, you're naturally protective of loved ones. You remember everything and feel everything intensely. Your challenge is managing emotional overwhelm and releasing the past.",
        },
        "Leo": {
            "keywords": "confident, creative, generous, regal, expressive",
            "description": "You're born to shine. Naturally charismatic and creative, you command attention wherever you go. Your generous heart makes you a natural leader. Your challenge is managing ego and remembering others' needs matter too.",
        },
        "Virgo": {
            "keywords": "analytical, practical, helpful, perfectionist, detail-oriented",
            "description": "You see what others miss. Your analytical mind naturally identifies flaws and solutions. Service-oriented and practical, you improve everything you touch. Your challenge is releasing perfectionism and accepting 'good enough.'",
        },
        "Libra": {
            "keywords": "diplomatic, aesthetic, social, indecisive, justice-seeking",
            "description": "You're the zodiac's diplomat. You naturally see all sides and seek harmony and balance in all things. Your aesthetic sense is refined, and you value relationships deeply. Your challenge is making decisions and avoiding people-pleasing.",
        },
        "Scorpio": {
            "keywords": "intense, magnetic, secretive, transformative, powerful",
            "description": "You possess magnetic intensity that draws people in. You see beneath surfaces, understanding hidden dynamics. Your power lies in transformation and psychological depth. Your challenge is releasing control and trusting others with your depths.",
        },
        "Sagittarius": {
            "keywords": "adventurous, philosophical, optimistic, expansive, truthful",
            "description": "You're the zodiac's explorer and philosopher. Perpetually optimistic and hungry for knowledge, you see the bigger picture. Your infectious enthusiasm inspires others. Your challenge is developing patience and grounding grand visions into reality.",
        },
        "Capricorn": {
            "keywords": "ambitious, responsible, disciplined, strategic, cautious",
            "description": "You're naturally strategic and ambitious. Disciplined and responsible, you take the long view and build enduring success. Your authority comes from earned wisdom. Your challenge is softening your edges and allowing yourself to play.",
        },
        "Aquarius": {
            "keywords": "innovative, humanitarian, detached, revolutionary, intellectual",
            "description": "You think ahead of your time. Idealistic and intellectual, you see possibility in what others dismiss. You're drawn to causes and communities. Your challenge is staying grounded and balancing detachment with genuine human connection.",
        },
        "Pisces": {
            "keywords": "intuitive, compassionate, artistic, dreamy, spiritual",
            "description": "You're a mystic and dreamer. Deeply intuitive and empathic, you feel the world's pain and beauty simultaneously. Your artistic sensitivity and spiritual nature make you profoundly creative. Your challenge is maintaining boundaries and grounding in reality.",
        },
    }
    
    PLANET_MEANINGS = {
        "Sun": "Your core identity and creative life force. How you express your will and seek recognition.",
        "Moon": "Your emotional nature and instinctive needs. How you process feelings and seek security.",
        "Mercury": "Your communication style and intellectual approach. How your mind works and you process information.",
        "Venus": "Your capacity for love, pleasure, and values. What attracts you and brings joy.",
        "Mars": "Your drive, courage, and how you assert yourself. Your passion and competitive nature.",
        "Jupiter": "Your expansion, luck, and higher wisdom. Where you attract abundance and tend toward excess.",
        "Saturn": "Your lessons and where you build lasting strength. Where you face challenges that lead to maturity.",
        "Uranus": "Your individuality and revolutionary impulses. Where you break free from convention.",
        "Neptune": "Your spirituality, creativity, and escapism. Where you access intuition and illusion.",
        "Pluto": "Your transformation and psychological depth. Where you experience death and rebirth.",
        "Chiron": "Your wounded healer archetype and deepest gift. Where pain becomes your greatest wisdom.",
        "Asc": "Your public mask and first impressions. How the world perceives you.",
        "MC": "Your public life, career, and legacy. What you're remembered for.",
        "Part of Fortune": "Your destiny and soul's fulfillment point. Your karmic gift and life's intended blessings. The intersection of opportunity and readiness. Where the universe conspires in your favor through alignment with your purpose. The material and psychological abundance you're meant to receive. Your fortune multiplies when you honor your authentic path.",
        "Vertex": "Your fated encounters and karmic connections. Where destiny meets choice.",
        "True North Node": "Your soul's growth direction and life purpose. Where you're meant to evolve.",
        "True South Node": "Your past life skills and comfort zone. What you're learning to release.",
        "True Lilith": "Your shadow self and primal power. Where you refuse to compromise.",
        "Black Moon Lilith": "Your autonomous power and what you reject. Your deepest rebellion.",
    }
    
    HOUSE_CONTEXTS = {
        1: "identity, appearance, and first impressions",
        2: "values, resources, and self-worth",
        3: "communication, thinking, and learning",
        4: "home, family, and private self",
        5: "creativity, romance, and self-expression",
        6: "work, health, and daily service",
        7: "relationships, marriage, and partnerships",
        8: "shared resources, sexuality, and transformation",
        9: "higher learning, spirituality, and travel",
        10: "career, reputation, and public life",
        11: "friendships, groups, and community",
        12: "spirituality, hidden matters, and karma",
    }
    
    ELEMENT_MEANINGS = {
        "Fire": "Fire signs are passionate, action-oriented, and spiritually driven. They possess natural charisma and courage.",
        "Earth": "Earth signs are practical, grounded, and focused on material manifestation. They possess natural patience and reliability.",
        "Air": "Air signs are intellectual, communicative, and idea-driven. They possess natural curiosity and analytical ability.",
        "Water": "Water signs are intuitive, emotional, and spiritually sensitive. They possess natural empathy and depth.",
    }
    
    MODALITY_MEANINGS = {
        "Cardinal": "Cardinal energy is action-oriented, pioneering, and leadership-focused. These placements make you an initiator.",
        "Fixed": "Fixed energy is stable, persistent, and resistant to change. These placements make you a consolidator.",
        "Mutable": "Mutable energy is adaptable, communicative, and fluid. These placements make you a connector.",
    }
    
    ASPECT_MEANINGS = {
        "Conjunction": "A powerful alignment suggesting fusion and emphasized expression of both planetary energies",
        "Sextile": "A harmonious 60° angle supporting flow, opportunity, and natural expression between planetary energies",
        "Square": "A challenging 90° angle creating dynamic tension and growth through friction and effort",
        "Trine": "The most harmonious 120° angle indicating effortless flow, talent, and natural grace",
        "Opposition": "A confrontational 180° angle revealing polarity, awareness, and the need for balance",
        "Quincunx": "An awkward 150° angle suggesting adjustment, refinement, and learning curves",
    }
    
    ASPECT_INTERACTIONS = {
        ("Sun", "Moon"): {
            "Conjunction": "Your conscious self and emotional nature are perfectly aligned, creating inner harmony and clarity about who you are emotionally.",
            "Sextile": "Your will and emotions work together gracefully. You can express feelings with clarity and act on them with emotional authenticity.",
            "Square": "Your ego and emotions are at odds. You must learn to integrate your need for recognition with your need for emotional security.",
            "Trine": "Your identity and inner emotional world flow effortlessly together. You're comfortable with yourself emotionally and express your feelings naturally.",
            "Opposition": "You oscillate between your conscious identity and emotional needs. Others see your strength while internally you struggle with vulnerability.",
            "Quincunx": "Your will and emotions operate on different wavelengths. You must consciously learn to honor both your ambitions and your emotional truth.",
        },
        ("Sun", "Mercury"): {
            "Conjunction": "Your identity and communication are one. You're the voice in the room, naturally articulate about who you are.",
            "Sextile": "Your ego and mind work well together. You communicate your identity clearly and think through your choices carefully.",
            "Square": "Your will and thinking mind create friction. You must learn to listen as well as speak, and think before commanding.",
            "Trine": "Your identity naturally expresses through clear thinking and communication. You're confident in what you know and how you share it.",
            "Opposition": "Your conscious self and your thoughts sometimes contradict. Others may see you as inconsistent or hear a different version each time.",
            "Quincunx": "Your will and your thinking operate somewhat independently. You must consciously integrate your identity with your intellectual perspective.",
        },
        ("Sun", "Venus"): {
            "Conjunction": "Your identity is inseparable from your values and aesthetic. You are what you love.",
            "Sextile": "Your will and values align naturally. You pursue what's beautiful and align your identity with your authentic desires.",
            "Square": "Your ego and values create tension. You must learn to balance self-assertion with consideration and aesthetic sensitivity.",
            "Trine": "Your identity naturally aligns with your values. You're authentic in your relationships and comfortable with who you are.",
            "Opposition": "Your sense of self and what you value can pull in opposite directions. You oscillate between ambition and connection.",
            "Quincunx": "Your identity and values require conscious integration. You must learn to honor both your individual will and your relational needs.",
        },
        ("Sun", "Mars"): {
            "Conjunction": "Your will and drive are unified. You're direct, passionate, and courageous about pursuing your goals.",
            "Sextile": "Your identity and assertiveness work well together. You pursue your goals with confidence and appropriate aggression.",
            "Square": "Your will and aggression create constant friction. You must channel your passionate intensity into productive action rather than conflict.",
            "Trine": "Your identity flows into effortless action. You're naturally confident in your strength and pursue what you want without doubt.",
            "Opposition": "Your ego and drive can be at odds. You oscillate between assertion and restraint, sometimes explosive.",
            "Quincunx": "Your identity and passions operate on different frequencies. You must consciously align your will with your authentic strength.",
        },
        ("Sun", "Jupiter"): {
            "Conjunction": "Your identity and expansion are fused. You're naturally optimistic, generous, and believe in your potential.",
            "Sextile": "Your will and growth naturally support each other. You're confident and fortunate, able to expand your horizons with ease.",
            "Square": "Your ego and tendency to expand create tension. You must learn humility and develop restraint to avoid overextension.",
            "Trine": "Your identity naturally expands. You're fortunate, optimistic, and confident in your ability to succeed.",
            "Opposition": "Your will and tendency to expand can conflict. You oscillate between confidence and self-doubt, ambition and surrender.",
            "Quincunx": "Your identity and growth impulse require conscious integration. You must learn when to expand and when to consolidate.",
        },
        ("Sun", "Saturn"): {
            "Conjunction": "Your identity and limitations are fused. You're serious, responsible, and mature, building lasting achievement.",
            "Sextile": "Your will and your capacity for discipline work well together. You build sustainably and earn respect through integrity.",
            "Square": "Your ego and restrictions are in constant tension. You must learn that limitations build character and develop patience.",
            "Trine": "Your identity naturally aligns with maturity. You're reliable, responsible, and earn authority through consistent effort.",
            "Opposition": "Your will and your constraints oscillate. You swing between confidence and self-doubt, ambition and fear of failure.",
            "Quincunx": "Your identity and your need for discipline require conscious integration. You must learn to channel your will into structured achievement.",
        },
        ("Moon", "Mercury"): {
            "Conjunction": "Your emotions and thoughts are interwoven. You process feelings through thinking and speak from the heart.",
            "Sextile": "Your feelings and thinking work together gracefully. You're emotionally intelligent and communicate your needs clearly.",
            "Square": "Your emotions and thoughts are often at odds. You must learn to balance feeling with thinking and listening with defending.",
            "Trine": "Your emotions and mind flow together naturally. You're articulate about your feelings and think with emotional wisdom.",
            "Opposition": "Your emotions and thoughts oscillate, sometimes contradicting. You may seem emotionally inconsistent to others.",
            "Quincunx": "Your feelings and thinking operate on different wavelengths. You must consciously integrate emotional truth with rational perspective.",
        },
        ("Moon", "Venus"): {
            "Conjunction": "Your emotions and values are perfectly aligned. You need love to feel secure and nurture through affection.",
            "Sextile": "Your emotional nature and values work together well. You're affectionate and emotionally generous.",
            "Square": "Your needs and values create tension. You must learn to balance emotional needs with relational boundaries.",
            "Trine": "Your emotional nature and values flow together. You're naturally nurturing and comfortable with emotional intimacy.",
            "Opposition": "Your emotions and relational needs oscillate. You swing between neediness and independence, warmth and distance.",
            "Quincunx": "Your emotions and values require conscious integration. You must learn to honor your needs while respecting others' autonomy.",
        },
        ("Moon", "Mars"): {
            "Conjunction": "Your emotions and drive are fused. You're emotionally intense and passionate, acting from gut feelings.",
            "Sextile": "Your feelings and drive work well together. You're emotionally courageous and assertively meet your needs.",
            "Square": "Your emotions and aggression create friction. You must learn to channel emotional intensity into constructive expression.",
            "Trine": "Your emotions flow naturally into action. You're emotionally confident and courageous about your feelings.",
            "Opposition": "Your emotions and drives oscillate. You swing between passive-aggressive and overly direct, needy and defensive.",
            "Quincunx": "Your emotions and passions operate on different frequencies. You must consciously learn to assertively express your needs.",
        },
        ("Mercury", "Venus"): {
            "Conjunction": "Your thinking and values are aligned. You speak beautifully and think about what matters to you deeply.",
            "Sextile": "Your mind and values work well together. You communicate thoughtfully about what matters and make wise choices.",
            "Square": "Your thinking and values create friction. You must learn to balance intellectual logic with heart-centered wisdom.",
            "Trine": "Your mind and values flow together naturally. You're articulate about what you value and think with aesthetic sensibility.",
            "Opposition": "Your thoughts and values oscillate. You can argue convincingly for positions your heart doesn't believe.",
            "Quincunx": "Your thinking and values require conscious integration. You must learn to align what you say with what you truly value.",
        },
        ("Mercury", "Mars"): {
            "Conjunction": "Your thoughts and drive are unified. You're quick-witted, argumentative, and speak with force.",
            "Sextile": "Your mind and assertiveness work well together. You're articulate about what you want and debate skillfully.",
            "Square": "Your thinking and aggression create friction. You must learn to think before speaking and listen rather than interrupt.",
            "Trine": "Your mind flows naturally into action. You're quick, mentally sharp, and act decisively on your ideas.",
            "Opposition": "Your thoughts and drives oscillate. You can overthink or act impulsively, contradicting yourself.",
            "Quincunx": "Your thinking and assertiveness require conscious integration. You must learn to speak with both clarity and compassion.",
        },
        ("Venus", "Mars"): {
            "Conjunction": "Your desire and passion are fused. You're intensely romantic and sexually confident.",
            "Sextile": "Your values and drive work well together. You pursue what you want with charm and directness.",
            "Square": "Your desires and drive create friction. You must learn to balance assertion with consideration and passion with patience.",
            "Trine": "Your values and desire flow together naturally. You're confident, charismatic, and naturally attractive.",
            "Opposition": "Your values and drives oscillate. You swing between aggressive passion and withdrawn hesitation.",
            "Quincunx": "Your desire and assertiveness require conscious integration. You must learn to pursue what you want with authentic grace.",
        },
        ("Jupiter", "Saturn"): {
            "Conjunction": "Your expansion and contraction are fused. You're balanced between growth and restraint, optimistic yet realistic.",
            "Sextile": "Your growth and discipline work well together. You expand wisely and build sustainably.",
            "Square": "Your optimism and caution are in constant tension. You must learn to balance risk-taking with prudence.",
            "Trine": "Your growth and discipline flow together. You're fortunate yet responsible, expanding steadily.",
            "Opposition": "Your expansion and contraction oscillate. You swing between excessive optimism and depression.",
            "Quincunx": "Your growth and limitations require conscious integration. You must learn when to expand and when to consolidate.",
        },
        ("Sun", "Uranus"): {
            "Conjunction": "Your identity and individuality are fused. You're unique, unconventional, and determined to break free from limitations.",
            "Sextile": "Your will and innovation work well together. You're independent and naturally progressive, pioneering new approaches.",
            "Square": "Your ego and need for freedom are in constant friction. You must learn to balance self-expression with responsibility.",
            "Trine": "Your identity naturally expresses through innovation. You're independent, ahead of your time, and inspiring to others.",
            "Opposition": "Your sense of self and your need for freedom oscillate. You swing between conformity and rebellion.",
            "Quincunx": "Your identity and individuality require conscious integration. You must learn to honor your uniqueness without alienating others.",
        },
        ("Sun", "Neptune"): {
            "Conjunction": "Your identity and spirituality are fused. You're visionary, idealistic, and drawn to transcendence.",
            "Sextile": "Your will and creativity work well together. You're inspired and able to manifest your vision with grace.",
            "Square": "Your ego and spiritual ideals are in tension. You must learn to ground your dreams and distinguish fantasy from reality.",
            "Trine": "Your identity naturally flows through artistic and spiritual expression. You're visionary and magnetic.",
            "Opposition": "Your sense of self and your spiritual ideals oscillate. You swing between ego-driven ambition and escapism.",
            "Quincunx": "Your identity and spirituality require conscious integration. You must learn to be spiritual without losing yourself.",
        },
        ("Sun", "Pluto"): {
            "Conjunction": "Your identity and power are fused. You're intensely transformative and magnetic, with compelling presence.",
            "Sextile": "Your will and depth work well together. You're powerful yet grounded, able to transform situations with integrity.",
            "Square": "Your ego and power are in constant friction. You must learn to yield control and embrace transformation gracefully.",
            "Trine": "Your identity naturally embodies power. You're magnetic, psychological deep, and naturally commanding.",
            "Opposition": "Your sense of self and your power oscillate. Others experience you as intense and controlling, internally you struggle with powerlessness.",
            "Quincunx": "Your identity and power require conscious integration. You must learn to wield your influence with wisdom.",
        },
        ("Moon", "Jupiter"): {
            "Conjunction": "Your emotions and expansion are fused. You're optimistic, generous, and emotionally open.",
            "Sextile": "Your feelings and growth work well together. You're emotionally generous and find happiness easily.",
            "Square": "Your emotional needs and tendency to expand are in tension. You must learn restraint and emotional boundaries.",
            "Trine": "Your emotions naturally flow into generosity. You're warm, fortunate, and emotionally generous.",
            "Opposition": "Your emotions and expansion oscillate. You swing between emotional overindulgence and emptiness.",
            "Quincunx": "Your emotions and expansion require conscious integration. You must learn when to give and when to protect yourself.",
        },
        ("Moon", "Saturn"): {
            "Conjunction": "Your emotions and discipline are fused. You're emotionally mature, responsible, and reserved.",
            "Sextile": "Your feelings and structure work well together. You're emotionally steady and responsible.",
            "Square": "Your emotional needs and restrictions are in tension. You must learn that emotional safety comes through structure.",
            "Trine": "Your emotions naturally flow into maturity. You're emotionally stable and trustworthy.",
            "Opposition": "Your emotions and restrictions oscillate. You swing between emotional expression and suppression.",
            "Quincunx": "Your emotions and structure require conscious integration. You must learn to honor your feelings within healthy boundaries.",
        },
        ("Moon", "Uranus"): {
            "Conjunction": "Your emotions and individuality are fused. You're emotionally unconventional and need freedom.",
            "Sextile": "Your feelings and innovation work well together. You're emotionally intuitive and progressive.",
            "Square": "Your emotional needs and need for freedom are in tension. You must learn consistency and emotional reliability.",
            "Trine": "Your emotions naturally express through innovation. You're emotionally intuitive and independent.",
            "Opposition": "Your emotions and freedom oscillate. You swing between emotional dependence and detachment.",
            "Quincunx": "Your emotions and individuality require conscious integration. You must learn emotional authenticity.",
        },
        ("Moon", "Neptune"): {
            "Conjunction": "Your emotions and spirituality are fused. You're profoundly intuitive, dreamy, and empathic.",
            "Sextile": "Your feelings and imagination work well together. You're intuitive, creative, and compassionate.",
            "Square": "Your emotions and spirituality are in tension. You must learn to distinguish intuition from projection.",
            "Trine": "Your emotions naturally flow through spirituality. You're highly intuitive and empathically connected.",
            "Opposition": "Your emotions and spirituality oscillate. You swing between clarity and confusion, empathy and enmeshment.",
            "Quincunx": "Your emotions and spirituality require conscious integration. You must learn psychic protection.",
        },
        ("Moon", "Pluto"): {
            "Conjunction": "Your emotions and power are fused. You're intensely emotional and psychologically deep.",
            "Sextile": "Your feelings and depth work well together. You're emotionally intuitive and transformative.",
            "Square": "Your emotional needs and power are in tension. You must learn to release control and trust others.",
            "Trine": "Your emotions naturally flow into transformation. You're psychologically deep and emotionally powerful.",
            "Opposition": "Your emotions and power oscillate. You swing between emotional manipulation and vulnerability.",
            "Quincunx": "Your emotions and power require conscious integration. You must learn emotional authenticity.",
        },
        ("Mercury", "Jupiter"): {
            "Conjunction": "Your thinking and expansion are fused. You're a natural teacher, optimistic thinker, and philosopher.",
            "Sextile": "Your mind and growth work well together. You're intelligent and able to absorb knowledge easily.",
            "Square": "Your thinking and expansion are in tension. You must learn discernment and avoid overconfidence.",
            "Trine": "Your mind naturally expands. You're gifted at learning, teaching, and philosophical thinking.",
            "Opposition": "Your thoughts and expansion oscillate. You can argue any position and switch perspectives easily.",
            "Quincunx": "Your thinking and expansion require conscious integration. You must learn focused knowledge.",
        },
        ("Mercury", "Saturn"): {
            "Conjunction": "Your thinking and discipline are fused. You're a rigorous thinker, serious, and practical.",
            "Sextile": "Your mind and structure work well together. You think clearly and systematically.",
            "Square": "Your thinking and restrictions are in tension. You must learn flexibility and overcome mental limiting beliefs.",
            "Trine": "Your mind naturally aligns with discipline. You're logical, methodical, and excellent at detailed work.",
            "Opposition": "Your thoughts and structure oscillate. You can overthink or be overly rigid in your thinking.",
            "Quincunx": "Your thinking and discipline require conscious integration. You must learn mental flexibility.",
        },
        ("Mercury", "Uranus"): {
            "Conjunction": "Your thinking and innovation are fused. You're brilliant, unconventional, and visionary.",
            "Sextile": "Your mind and progress work well together. You're innovative and ahead of the curve intellectually.",
            "Square": "Your thinking and innovation are in tension. You must learn to think linearly as well as creatively.",
            "Trine": "Your mind naturally flows through innovation. You're gifted intellectually and naturally think ahead.",
            "Opposition": "Your thoughts and innovation oscillate. You can be brilliant or scatterbrained.",
            "Quincunx": "Your thinking and innovation require conscious integration. You must learn practical application.",
        },
        ("Mercury", "Neptune"): {
            "Conjunction": "Your thinking and spirituality are fused. You're imaginative, poetic, and drawn to higher knowledge.",
            "Sextile": "Your mind and creativity work well together. You're imaginative and able to express abstract ideas.",
            "Square": "Your thinking and spirituality are in tension. You must learn to ground your ideas and distinguish fantasy.",
            "Trine": "Your mind naturally flows through imagination. You're poetic, intuitive, and creative.",
            "Opposition": "Your thoughts and spirituality oscillate. You can be brilliantly insightful or completely confused.",
            "Quincunx": "Your thinking and spirituality require conscious integration. You must learn mental clarity.",
        },
        ("Mercury", "Pluto"): {
            "Conjunction": "Your thinking and power are fused. You're penetrating, intense, and naturally investigative.",
            "Sextile": "Your mind and depth work well together. You're able to penetrate to truth and see psychological patterns.",
            "Square": "Your thinking and power are in tension. You must learn when to speak and when to stay silent.",
            "Trine": "Your mind naturally flows into depth. You're brilliant at investigation and psychology.",
            "Opposition": "Your thoughts and power oscillate. You can be manipulative or transparent.",
            "Quincunx": "Your thinking and power require conscious integration. You must learn ethical use of knowledge.",
        },
        ("Venus", "Jupiter"): {
            "Conjunction": "Your values and expansion are fused. You're generous, loving, and socially popular.",
            "Sextile": "Your desires and growth work well together. You're romantic, gracious, and fortunate in relationships.",
            "Square": "Your values and expansion are in tension. You must learn restraint and avoid overindulgence.",
            "Trine": "Your values naturally expand. You're loving, generous, and magnetically attractive.",
            "Opposition": "Your desires and expansion oscillate. You can be excessively romantic or withdraw from connection.",
            "Quincunx": "Your values and expansion require conscious integration. You must learn balance in giving.",
        },
        ("Venus", "Saturn"): {
            "Conjunction": "Your values and discipline are fused. You're serious about relationships and take commitments deeply.",
            "Sextile": "Your desires and structure work well together. You're loyal and build lasting relationships.",
            "Square": "Your values and restrictions are in tension. You must learn that commitment requires courage.",
            "Trine": "Your values naturally align with depth. You're loyal, faithful, and capable of enduring love.",
            "Opposition": "Your desires and responsibilities oscillate. You swing between commitment and fear of entrapment.",
            "Quincunx": "Your values and discipline require conscious integration. You must learn authentic vulnerability.",
        },
        ("Venus", "Uranus"): {
            "Conjunction": "Your values and individuality are fused. You're unconventional in love and drawn to unique relationships.",
            "Sextile": "Your desires and innovation work well together. You're romantic yet independent.",
            "Square": "Your values and freedom are in tension. You must learn to balance partnership with autonomy.",
            "Trine": "Your values naturally express through uniqueness. You're charismatic and attractive in unusual ways.",
            "Opposition": "Your desires and freedom oscillate. You swing between craving intimacy and needing independence.",
            "Quincunx": "Your values and individuality require conscious integration. You must learn interdependence.",
        },
        ("Venus", "Neptune"): {
            "Conjunction": "Your values and spirituality are fused. You're deeply romantic, idealistic, and compassionate.",
            "Sextile": "Your desires and imagination work well together. You're romantic and able to love selflessly.",
            "Square": "Your values and idealism are in tension. You must learn to see people clearly without rose-colored glasses.",
            "Trine": "Your values naturally flow through compassion. You're romantic, spiritual, and magnetically empathic.",
            "Opposition": "Your desires and ideals oscillate. You can love purely or become lost in fantasy.",
            "Quincunx": "Your values and spirituality require conscious integration. You must learn discernment in relationships.",
        },
        ("Venus", "Pluto"): {
            "Conjunction": "Your values and power are fused. You're intensely romantic, magnetic, and psychologically deep.",
            "Sextile": "Your desires and depth work well together. You're passionate and capable of profound intimacy.",
            "Square": "Your values and power are in tension. You must learn to release control in relationships.",
            "Trine": "Your values naturally embody intensity. You're magnetically attractive and capable of deep love.",
            "Opposition": "Your desires and power oscillate. You can be possessive or withdrawn.",
            "Quincunx": "Your values and power require conscious integration. You must learn trust.",
        },
        ("Mars", "Jupiter"): {
            "Conjunction": "Your drive and expansion are fused. You're ambitious, confident, and courageous.",
            "Sextile": "Your action and growth work well together. You're fortunate in your endeavors and naturally successful.",
            "Square": "Your drive and expansion are in tension. You must learn discipline and avoid recklessness.",
            "Trine": "Your drive naturally expands. You're lucky, courageous, and able to accomplish much.",
            "Opposition": "Your action and expansion oscillate. You swing between aggressive ambition and passivity.",
            "Quincunx": "Your drive and expansion require conscious integration. You must learn strategic action.",
        },
        ("Mars", "Saturn"): {
            "Conjunction": "Your drive and discipline are fused. You're relentlessly determined and capable of sustained effort.",
            "Sextile": "Your action and structure work well together. You're strategic and able to build lasting achievement.",
            "Square": "Your drive and restrictions are in constant friction. You must learn patience and accept limitations.",
            "Trine": "Your drive naturally aligns with discipline. You're capable, responsible, and able to accomplish goals.",
            "Opposition": "Your action and restraint oscillate. You swing between aggressive assertion and defeated resignation.",
            "Quincunx": "Your drive and discipline require conscious integration. You must learn paced ambition.",
        },
        ("Mars", "Uranus"): {
            "Conjunction": "Your drive and innovation are fused. You're revolutionary, unpredictable, and radically independent.",
            "Sextile": "Your action and progress work well together. You're progressive and able to take bold new action.",
            "Square": "Your drive and innovation are in tension. You must learn to think before acting and respect others' freedom.",
            "Trine": "Your drive naturally flows through innovation. You're pioneering, courageous, and inspiring.",
            "Opposition": "Your action and innovation oscillate. You swing between reckless rebellion and cautious conformity.",
            "Quincunx": "Your drive and innovation require conscious integration. You must learn responsible action.",
        },
        ("Mars", "Neptune"): {
            "Conjunction": "Your drive and spirituality are fused. You're passionate about ideals and spiritually motivated.",
            "Sextile": "Your action and imagination work well together. You're passionate and able to pursue spiritual goals.",
            "Square": "Your drive and spirituality are in tension. You must learn to distinguish true calling from escapism.",
            "Trine": "Your drive naturally flows through spirituality. You're passionate about ideals and able to inspire.",
            "Opposition": "Your action and spirituality oscillate. You swing between passionate crusading and apathetic withdrawal.",
            "Quincunx": "Your drive and spirituality require conscious integration. You must learn discerning action.",
        },
        ("Mars", "Pluto"): {
            "Conjunction": "Your drive and power are fused. You're intensely ambitious, powerful, and formidable.",
            "Sextile": "Your action and depth work well together. You're powerful and able to achieve transformative results.",
            "Square": "Your drive and power are in constant tension. You must learn to release control and respect others' agency.",
            "Trine": "Your drive naturally embodies power. You're magnetic, commanding, and able to lead.",
            "Opposition": "Your action and power oscillate. You swing between domination and paralysis.",
            "Quincunx": "Your drive and power require conscious integration. You must learn ethical power.",
        },
    }
    
    def __init__(self):
        self.training_data = TrainingDataLoader.get_instance()
    
    def get_full_chart(self, dt, lat, lon, location_name=""):
        try:
            native = charts.Subject(
                date_time=dt,
                latitude=lat,
                longitude=lon,
            )
            natal = charts.Natal(native)
            
            chart_data = {
                "birth": dt.strftime("%Y-%m-%d %H:%M"),
                "location_name": location_name,
                "lat": lat,
                "lon": lon,
                "natal": natal,
                "objects": {},
                "aspects": [],
                "elements": {},
                "modalities": {},
                "dignities": {},
            }
            
            for obj_index, obj in natal.objects.items():
                retrograde = False
                if hasattr(obj, 'movement'):
                    retrograde = obj.movement.retrograde if hasattr(obj.movement, 'retrograde') else False
                
                dignities = []
                score = 0
                if hasattr(obj, 'dignities') and obj.dignities:
                    dignities = obj.dignities.formatted if obj.dignities.formatted else []
                    score = obj.dignities.score if hasattr(obj.dignities, 'score') else 0
                
                obj_name = str(obj.name)
                chart_data["objects"][obj_name] = {
                    "name": obj_name,
                    "sign": obj.sign.name,
                    "house": obj.house.number,
                    "lon": obj.longitude.raw,
                    "deg": obj.sign_longitude.raw,
                    "retrograde": retrograde,
                    "decan": obj.decan.number if obj.decan else None,
                    "dignities": dignities,
                    "score": score,
                }
            
            for obj_index, aspects_dict in natal.aspects.items():
                for target_index, aspect in aspects_dict.items():
                    obj1 = natal.objects.get(obj_index)
                    obj2 = natal.objects.get(target_index)
                    if obj1 and obj2:
                        chart_data["aspects"].append({
                            "object1": str(obj1.name),
                            "object2": str(obj2.name),
                            "type": aspect.aspect.name if hasattr(aspect.aspect, 'name') else str(aspect.aspect),
                            "orb": aspect.orb.raw if hasattr(aspect.orb, 'raw') else aspect.orb,
                        })
            
            chart_data["elements"] = {
                "fire": sum(1 for o in natal.objects.values() if o.sign.element == "Fire"),
                "earth": sum(1 for o in natal.objects.values() if o.sign.element == "Earth"),
                "air": sum(1 for o in natal.objects.values() if o.sign.element == "Air"),
                "water": sum(1 for o in natal.objects.values() if o.sign.element == "Water"),
            }
            
            chart_data["modalities"] = {
                "cardinal": sum(1 for o in natal.objects.values() if o.sign.modality == "Cardinal"),
                "fixed": sum(1 for o in natal.objects.values() if o.sign.modality == "Fixed"),
                "mutable": sum(1 for o in natal.objects.values() if o.sign.modality == "Mutable"),
            }
            
            return chart_data
        except Exception as e:
            raise Exception(f"Chart calculation error: {str(e)}")
    
    def get_aspect_meaning(self, aspect_type):
        try:
            degree = float(aspect_type)
        except:
            degree = None
        
        if degree is not None:
            if abs(degree - 0.0) < 1:
                return self.ASPECT_MEANINGS.get("Conjunction", "A powerful alignment suggesting fusion and emphasized expression of both planetary energies")
            elif abs(degree - 60.0) < 1:
                return self.ASPECT_MEANINGS.get("Sextile", "A harmonious 60° angle supporting flow, opportunity, and natural expression between planetary energies")
            elif abs(degree - 90.0) < 1:
                return self.ASPECT_MEANINGS.get("Square", "A challenging 90° angle creating dynamic tension and growth through friction and effort")
            elif abs(degree - 120.0) < 1:
                return self.ASPECT_MEANINGS.get("Trine", "The most harmonious 120° angle indicating effortless flow, talent, and natural grace")
            elif abs(degree - 150.0) < 1:
                return self.ASPECT_MEANINGS.get("Quincunx", "An awkward 150° angle suggesting adjustment, refinement, and learning curves")
            elif abs(degree - 180.0) < 1:
                return self.ASPECT_MEANINGS.get("Opposition", "A confrontational 180° angle revealing polarity, awareness, and the need for balance")
        
        for key, meaning in self.ASPECT_MEANINGS.items():
            if key in str(aspect_type):
                return meaning
        return "A complex planetary relationship influencing your psychology and life patterns."
    
    def get_aspect_name(self, aspect_type):
        try:
            degree = float(aspect_type)
        except:
            return aspect_type
        
        if abs(degree - 0.0) < 1:
            return "Conjunction"
        elif abs(degree - 60.0) < 1:
            return "Sextile"
        elif abs(degree - 90.0) < 1:
            return "Square"
        elif abs(degree - 120.0) < 1:
            return "Trine"
        elif abs(degree - 150.0) < 1:
            return "Quincunx"
        elif abs(degree - 180.0) < 1:
            return "Opposition"
        return f"{degree}°"
    
    def get_contextual_aspect_description(self, planet1, planet2, aspect_name):
        pair = (planet1, planet2)
        if pair in self.ASPECT_INTERACTIONS:
            return self.ASPECT_INTERACTIONS[pair].get(aspect_name, self.get_aspect_meaning(aspect_name))
        
        pair = (planet2, planet1)
        if pair in self.ASPECT_INTERACTIONS:
            return self.ASPECT_INTERACTIONS[pair].get(aspect_name, self.get_aspect_meaning(aspect_name))
        
        return self._generate_dynamic_aspect_description(planet1, planet2, aspect_name)
    
    def _generate_dynamic_aspect_description(self, planet1, planet2, aspect_name):
        p1_full = self.PLANET_MEANINGS.get(planet1, f"{planet1} energy")
        p2_full = self.PLANET_MEANINGS.get(planet2, f"{planet2} energy")
        
        p1_parts = p1_full.split(". ")
        p2_parts = p2_full.split(". ")
        
        p1_meaning = p1_parts[0].lower().replace("your ", "")
        p2_meaning = p2_parts[0].lower().replace("your ", "")
        
        p1_context = (p1_parts[1].lower().replace("your ", "") if len(p1_parts) > 1 else p1_meaning).rstrip(".")
        p2_context = (p2_parts[1].lower().replace("your ", "") if len(p2_parts) > 1 else p2_meaning).rstrip(".")
        
        # Use sum of character values for variety while staying deterministic
        seed = (sum(ord(c) for c in planet1 + planet2) * 7) % 1000
        
        if aspect_name == "Conjunction":
            templates = [
                f"{planet1} and {planet2} are fused into one force. {p1_meaning.capitalize()} merges with {p2_meaning}, amplifying both through concentrated power.",
                f"Powerful union between {planet1} and {planet2}. These energies become inseparable, intensifying their combined expression throughout your life and psychology.",
                f"{planet1} and {planet2} merge completely. This total fusion creates potent archetypal presence where {p1_context} and {p2_context} cannot be separated.",
                f"{planet1} and {planet2} operate as a single unified force. The combination of {p1_meaning} and {p2_meaning} creates singular concentrated power.",
                f"Complete alignment: {planet1} and {planet2} are one in your chart. {p1_context.capitalize()} and {p2_context} fuse into a potent archetypal presence.",
                f"{planet1} blends seamlessly with {planet2}. This conjunction creates undivided expression of {p1_meaning} and {p2_meaning}.",
            ]
            return templates[seed % len(templates)]
        
        elif aspect_name == "Sextile":
            templates = [
                f"{planet1} and {planet2} create natural support. {p1_meaning.capitalize()} and {p2_meaning} bring you unexpected opportunities and effortless pathways.",
                f"Easy cooperation between {planet1} and {planet2}. {p1_context.capitalize()} works smoothly with {p2_context}, creating grace where you might otherwise need effort.",
                f"{planet1} and {planet2} dance together naturally. {p1_meaning.capitalize()} flows with {p2_meaning}, opening doors and bringing ease to this life domain.",
                f"{planet1} and {planet2} generate harmonious support. {p1_meaning} and {p2_meaning} create unexpected opportunities and natural openness.",
                f"Flowing partnership between {planet1} and {planet2}. {p1_context.capitalize()} and {p2_context} work as allies, bringing luck and ease.",
                f"{planet1} and {planet2} are natural collaborators in your chart. {p1_meaning} supports {p2_meaning}, creating effortless flow.",
            ]
            return templates[seed % len(templates)]
        
        elif aspect_name == "Square":
            templates = [
                f"Dynamic tension between {planet1} and {planet2}. {p1_meaning.capitalize()} and {p2_meaning} demand conscious integration. This friction becomes strength when you work with it.",
                f"{planet1} and {planet2} push against each other. The creative tension between {p1_context} and {p2_context} drives growth and forces deeper psychological development.",
                f"Challenging dynamic between {planet1} and {planet2}. {p1_meaning.capitalize()} conflicts with {p2_meaning}, compelling you toward maturity and integrated wholeness.",
                f"Productive friction between {planet1} and {planet2}. {p1_meaning} and {p2_meaning} create tension that cultivates psychological strength and wisdom.",
                f"{planet1} and {planet2} require conscious integration. The {p1_context} and {p2_context} dynamic pushes you toward growth through effort.",
                f"Challenge aspect: {planet1} and {planet2} create necessary tension. This dynamic asks you to unify {p1_meaning} and {p2_meaning} through conscious choice.",
            ]
            return templates[seed % len(templates)]
        
        elif aspect_name == "Trine":
            templates = [
                f"{planet1} and {planet2} align perfectly. {p1_context.capitalize()} and {p2_context} create effortless flow, granting you natural talent and grace in this domain.",
                f"Harmonious resonance between {planet1} and {planet2}. {p1_meaning.capitalize()} and {p2_meaning} support each other continuously, creating luck and psychological ease.",
                f"{planet1} and {planet2} are cosmic partners. {p1_context.capitalize()} flows with {p2_context}, making this area of life feel naturally gifted and blessed.",
                f"Perfect harmony between {planet1} and {planet2}. {p1_meaning} and {p2_meaning} work in natural synchronicity, granting you effortless talent.",
                f"{planet1} and {planet2} are divinely matched. {p1_context} and {p2_context} flow together beautifully, creating grace and natural ability.",
                f"Blessed alignment: {planet1} and {planet2} support your highest expression. {p1_meaning} and {p2_meaning} create luck, flow, and natural grace.",
            ]
            return templates[seed % len(templates)]
        
        elif aspect_name == "Opposition":
            templates = [
                f"{planet1} and {planet2} create inner dialogue. You're asked to honor both {p1_context} and {p2_context}, learning that opposites can integrate rather than conflict.",
                f"Polarized energies in your chart: {planet1} versus {planet2}. This dynamic asks you to develop wisdom that honors {p1_meaning} and {p2_meaning} rather than choosing sides.",
                f"Fundamental tension between {planet1} and {planet2}. Transcend the either-or thinking this aspect creates and find the both-and wisdom that integrates {p1_context} with {p2_context}.",
                f"{planet1} and {planet2} are in opposition. You experience {p1_meaning} and {p2_meaning} as oscillating forces. Integration brings mature wisdom.",
                f"Balancing act between {planet1} and {planet2}. {p1_context} and {p2_context} represent different poles you must learn to honor equally.",
                f"{planet1} opposes {planet2} in your chart. {p1_meaning} and {p2_meaning} create psychological tension that demands your conscious synthesis.",
            ]
            return templates[seed % len(templates)]
        
        elif aspect_name == "Quincunx":
            templates = [
                f"{planet1} and {planet2} operate on misaligned frequencies. These energies demand your conscious attention and creative problem-solving to blend together.",
                f"Adjustment between {planet1} and {planet2}. {p1_meaning.capitalize()} and {p2_meaning} learn to work together through trial, refinement, and persistent effort.",
                f"{planet1} and {planet2} create subtle challenges. The friction between {p1_context} and {p2_context} teaches you flexibility and deepens your psychological wisdom.",
                f"{planet1} and {planet2} require refinement. {p1_meaning} and {p2_meaning} operate at different angles, demanding learning and adjustment.",
                f"Awkward synergy between {planet1} and {planet2}. {p1_context} and {p2_context} teach you adaptive wisdom through consistent practice.",
                f"{planet1} and {planet2} are learning to blend. {p1_meaning} and {p2_meaning} require conscious effort to harmonize, bringing growth through trial.",
            ]
            return templates[seed % len(templates)]
        
        else:
            return self.get_aspect_meaning(aspect_name)
    
    def format_planetary_description(self, planet_name, sign_name, house_num, retrograde=False, dignities=None):
        desc = []
        
        retrograde_text = " (Retrograde)" if retrograde else ""
        desc.append(f"**{planet_name} in {sign_name} (House {house_num}){retrograde_text}**\n")
        
        training_interp = self.training_data.get_interpretation(planet_name, sign_name, house_num)
        
        if training_interp:
            desc.append(training_interp)
        else:
            sign_info = self.SIGN_TRAITS.get(sign_name, {})
            planet_info = self.PLANET_MEANINGS.get(planet_name, "")
            house_context = self.HOUSE_CONTEXTS.get(house_num, "an important life area")
            sign_traits = sign_info.get("keywords", "")
            sign_desc = sign_info.get("description", f"Your {sign_name} nature shapes this energy uniquely.")
            
            personality_part = sign_desc.split("Your challenge")[0].strip()
            
            desc.append(f"Your {planet_name} carries the {sign_name} signature. {personality_part.capitalize() if personality_part else sign_desc}")
            desc.append(f"\nIn terms of {house_context}, this means: {planet_info} When filtered through {sign_name}, you express this energy with {sign_traits}. You approach this life area through a lens of {sign_traits.split(',')[0].strip()} and {sign_traits.split(',')[1].strip() if ',' in sign_traits else 'independence'}.")
        
        if retrograde:
            desc.append(f"\n**Retrograde {planet_name}:** This internalizes the energy. Rather than expressing {planet_name}'s themes outwardly, you process them internally, leading to deeper wisdom and unique insight. People with retrograde {planet_name} often develop these qualities later in life, but when awakened, they possess a profound understanding that comes from internal work rather than external experience.")
        
        return "\n".join(desc)
    
    def generate_reading(self, chart_data, fol_hits):
        reading = []
        reading.append("╔═══════════════════════════════════════════╗")
        reading.append("║         YOUR NATAL CHART READING          ║")
        reading.append("║           Soul Tether Analysis            ║")
        reading.append("╚═══════════════════════════════════════════╝\n")
        reading.append(f"Birth Chart: {chart_data['birth']}")
        reading.append(f"Location: {chart_data['location_name']} ({chart_data['lat']:.4f}°N, {chart_data['lon']:.4f}°E)")
        reading.append("=" * 70)
        
        natal = chart_data["natal"]
        asc = next((o for o in natal.objects.values() if str(o.name) == "Asc"), None)
        mc = next((o for o in natal.objects.values() if str(o.name) == "MC"), None)
        
        reading.append("\n## THE ASCENDANT & MIDHEAVEN: YOUR COSMIC DESTINY POINTS\n")
        
        if asc:
            asc_interp = self.training_data.get_interpretation("Ascendant", asc.sign.name, 1)
            reading.append(f"**Ascendant in {asc.sign.name} {asc.sign_longitude.raw:.1f}°**\n")
            reading.append("Your rising sign is the cosmic mask you wear—the lens through which the world views you upon first encounter. It represents your personality surface, your instinctive reactions, and the energy that precedes you into a room. While your Sun sign reveals your core identity and Moon sign your emotional nature, your Ascendant is the vehicle through which these deeper aspects first become visible to others.\n")
            if asc_interp:
                reading.append(f"{asc_interp}\n")
            reading.append("")
        
        if mc:
            mc_interp = self.training_data.get_interpretation("Midheaven", mc.sign.name, 10)
            reading.append(f"**Midheaven in {mc.sign.name} {mc.sign_longitude.raw:.1f}°**\n")
            reading.append("Your Midheaven is your public persona and the trajectory of your life. It represents your career calling, your reputation, what you're remembered for, and the legacy you leave behind. This is the energy that accumulates over time through your public actions and professional choices. It's not necessarily who you are privately, but who you become in the eyes of society.\n")
            if mc_interp:
                reading.append(f"{mc_interp}\n")
            reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR INNER WORLD: THE LUMINARY TRINITY\n")
        
        sun = next((o for o in natal.objects.values() if str(o.name) == "Sun"), None)
        moon = next((o for o in natal.objects.values() if str(o.name) == "Moon"), None)
        mercury = next((o for o in natal.objects.values() if str(o.name) == "Mercury"), None)
        
        if sun:
            sun_desc = self.format_planetary_description("Sun", sun.sign.name, sun.house.number, 
                          sun.movement.retrograde if hasattr(sun, 'movement') and hasattr(sun.movement, 'retrograde') else False)
            reading.append(sun_desc)
            
            sign_traits = self.SIGN_TRAITS.get(sun.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(sun.house.number, "life")
            reading.append(f"\nYour Sun in {sun.sign.name} is fundamentally: {sign_traits.get('keywords', 'distinctive')}. This is your core identity—your essential self, your creative life force, and the archetypal energy you're meant to embody. In the context of {house_context}, this solar energy drives how you approach and express yourself in this area of life. {sign_traits.get('description', '').split('Your challenge')[0].strip()}\n")
            reading.append("")
        
        if moon:
            moon_desc = self.format_planetary_description("Moon", moon.sign.name, moon.house.number,
                          moon.movement.retrograde if hasattr(moon, 'movement') and hasattr(moon.movement, 'retrograde') else False)
            reading.append(moon_desc)
            
            sign_traits = self.SIGN_TRAITS.get(moon.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(moon.house.number, "life")
            reading.append(f"\nYour Moon in {moon.sign.name} characterizes you as: {sign_traits.get('keywords', 'emotionally unique')}. This is your emotional inner world—your instinctive needs, your unconscious patterns, and how you process feelings. In {house_context}, your lunar nature shapes your emotional responses and deepest needs. This is the part of you that seeks security and comfort. {sign_traits.get('description', '').split('Your challenge')[0].strip()}\n")
            reading.append("")
        
        if mercury:
            mercury_desc = self.format_planetary_description("Mercury", mercury.sign.name, mercury.house.number,
                          mercury.movement.retrograde if hasattr(mercury, 'movement') and hasattr(mercury.movement, 'retrograde') else False)
            reading.append(mercury_desc)
            
            sign_traits = self.SIGN_TRAITS.get(mercury.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(mercury.house.number, "life")
            reading.append(f"\nYour Mercury in {mercury.sign.name} gives you: {sign_traits.get('keywords', 'a distinctive mind')}. This is your communication style, intellectual approach, and how your mind works. Mercury governs thinking, learning, speaking, and information processing. In {house_context}, you apply this mental style to navigate and understand this area. {sign_traits.get('description', '').split('Your challenge')[0].strip()}\n")
            reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR RELATIONAL WORLD: VENUS & MARS\n")
        
        venus = next((o for o in natal.objects.values() if str(o.name) == "Venus"), None)
        mars = next((o for o in natal.objects.values() if str(o.name) == "Mars"), None)
        
        if venus:
            venus_desc = self.format_planetary_description("Venus", venus.sign.name, venus.house.number,
                          venus.movement.retrograde if hasattr(venus, 'movement') and hasattr(venus.movement, 'retrograde') else False)
            reading.append(venus_desc)
            
            sign_traits = self.SIGN_TRAITS.get(venus.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(venus.house.number, "life")
            reading.append(f"\nYour Venus in {venus.sign.name} expresses love and values through: {sign_traits.get('keywords', 'a unique aesthetic')}. Venus governs your capacity for love, pleasure, values, and what attracts you. In {house_context}, this placement reveals your aesthetic preferences, how you give and receive affection, and what brings you joy. Venus represents not just romantic love but also friendship, creativity, and the things you cherish most.\n")
            reading.append("")
        
        if mars:
            mars_desc = self.format_planetary_description("Mars", mars.sign.name, mars.house.number,
                          mars.movement.retrograde if hasattr(mars, 'movement') and hasattr(mars.movement, 'retrograde') else False)
            reading.append(mars_desc)
            
            sign_traits = self.SIGN_TRAITS.get(mars.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(mars.house.number, "life")
            reading.append(f"\nYour Mars in {mars.sign.name} channels your warrior energy through: {sign_traits.get('keywords', 'passionate drive')}. Mars is your drive, ambition, sexuality, and how you assert yourself. In {house_context}, this placement reveals your competitive nature, your passion, and how you pursue what you want. Mars governs motivation, courage, and the raw force you bring to any endeavor.\n")
            reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR OUTER PLANETS: THE DEEPER FORCES\n")
        
        jupiter = next((o for o in natal.objects.values() if str(o.name) == "Jupiter"), None)
        saturn = next((o for o in natal.objects.values() if str(o.name) == "Saturn"), None)
        
        if jupiter:
            jupiter_desc = self.format_planetary_description("Jupiter", jupiter.sign.name, jupiter.house.number,
                          jupiter.movement.retrograde if hasattr(jupiter, 'movement') and hasattr(jupiter.movement, 'retrograde') else False)
            reading.append(jupiter_desc)
            
            sign_traits = self.SIGN_TRAITS.get(jupiter.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(jupiter.house.number, "life")
            reading.append(f"\nYour Jupiter in {jupiter.sign.name} brings expansion and luck through: {sign_traits.get('keywords', 'boundless optimism')}. Jupiter expands whatever it touches. It's your luck, your growth potential, and your capacity for wisdom. In {house_context}, this placement shows where you naturally attract abundance and where you tend toward excess or over-confidence. Jupiter represents your higher learning and spiritual expansion.\n")
            reading.append("")
        
        if saturn:
            saturn_desc = self.format_planetary_description("Saturn", saturn.sign.name, saturn.house.number,
                          saturn.movement.retrograde if hasattr(saturn, 'movement') and hasattr(saturn.movement, 'retrograde') else False)
            reading.append(saturn_desc)
            
            sign_traits = self.SIGN_TRAITS.get(saturn.sign.name, {})
            house_context = self.HOUSE_CONTEXTS.get(saturn.house.number, "life")
            reading.append(f"\nYour Saturn in {saturn.sign.name} teaches discipline through: {sign_traits.get('keywords', 'hard-won wisdom')}. Saturn is your teacher through limitation. It shows where you face challenges and restrictions, and ultimately where you build lasting strength. In {house_context}, Saturn placements are initially difficult but become your greatest source of maturity and earned wisdom. This is where you must develop patience and persistence.\n")
            reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR ELEMENTAL NATURE & TEMPERAMENT\n")
        
        elem = chart_data["elements"]
        total_elems = elem['fire'] + elem['earth'] + elem['air'] + elem['water']
        
        reading.append(f"**Elemental Distribution**: Fire ({elem['fire']}), Earth ({elem['earth']}), Air ({elem['air']}), Water ({elem['water']})\n")
        
        reading.append("Your birth chart contains a unique blend of elemental energies:\n")
        
        if elem['fire'] >= 5:
            reading.append(f"**Strong Fire Influence ({elem['fire']} planets):** You possess abundant passion, enthusiasm, and pioneering spirit. Fire dominant individuals are action-oriented, courageous, and possess natural charisma. You likely jump into situations with confidence and aren't afraid of taking risks. The challenge is learning to think before acting and developing patience with slower processes and people.\n")
        elif elem['fire'] >= 2:
            reading.append(f"**Moderate Fire ({elem['fire']} planets):** You have healthy passion and courage tempered by other elemental influences. You can be enthusiastic when inspired but aren't reckless. You balance spontaneity with consideration.\n")
        else:
            reading.append(f"**Low Fire ({elem['fire']} planets):** You likely prefer planning to impulsiveness. You may struggle with assertiveness or taking initiative. Your strength lies in steadiness and consideration rather than bold action. You benefit from deliberately cultivating courage and spontaneity.\n")
        
        reading.append("")
        
        if elem['earth'] >= 5:
            reading.append(f"**Strong Earth Influence ({elem['earth']} planets):** You're grounded, practical, and focused on material manifestation. Earth dominant individuals excel at bringing ideas into concrete reality. You value stability, reliability, and tangible results. Your challenge is avoiding excessive rigidity and remembering to engage with abstract beauty and ideals.\n")
        elif elem['earth'] >= 2:
            reading.append(f"**Moderate Earth ({elem['earth']} planets):** You balance practicality with flexibility. You can execute plans while remaining adaptable to changing circumstances.\n")
        else:
            reading.append(f"**Low Earth ({elem['earth']} planets):** You're more comfortable with ideas and emotions than practical details. You may struggle with organization and follow-through. Developing practical skills and attention to material concerns strengthens your chart's expression.\n")
        
        reading.append("")
        
        if elem['air'] >= 5:
            reading.append(f"**Strong Air Influence ({elem['air']} planets):** You're intellectual, communicative, and idea-driven. Air dominant individuals excel at analysis, logic, and seeing multiple perspectives. You're naturally curious and enjoy intellectual stimulation. Your challenge is avoiding excessive mental chatter and developing deeper emotional wisdom.\n")
        elif elem['air'] >= 2:
            reading.append(f"**Moderate Air ({elem['air']} planets):** You balance analytical thinking with other modes of knowing. You can think clearly while remaining emotionally available.\n")
        else:
            reading.append(f"**Low Air ({elem['air']} planets):** You process the world through feeling and intuition more than pure logic. You may find excessive analysis fatiguing. Your strength lies in direct experience and emotional truth rather than abstract reasoning.\n")
        
        reading.append("")
        
        if elem['water'] >= 5:
            reading.append(f"**Strong Water Influence ({elem['water']} planets):** You're deeply intuitive, emotionally sensitive, and psychically attuned. Water dominant individuals are empathic, creative, and spiritually inclined. You experience the world through feeling and imagination. Your challenge is developing boundaries and objective discernment to avoid being overwhelmed by others' emotions.\n")
        elif elem['water'] >= 2:
            reading.append(f"**Moderate Water ({elem['water']} planets):** You have healthy emotional intelligence and intuitive access. You can feel deeply while maintaining objectivity.\n")
        else:
            reading.append(f"**Low Water ({elem['water']} planets):** You approach life intellectually rather than emotionally. You may seem detached to water-heavy individuals, but you offer valuable objectivity and logical clarity. Consciously developing emotional expression strengthens your relationships.\n")
        
        reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR MODALITY & ACTION STYLE\n")
        
        mod = chart_data["modalities"]
        
        reading.append(f"**Modality Distribution**: Cardinal ({mod['cardinal']}), Fixed ({mod['fixed']}), Mutable ({mod['mutable']})\n")
        
        reading.append("Your modality balance reveals how you approach change and action:\n")
        
        if mod['cardinal'] > mod['fixed'] and mod['cardinal'] > mod['mutable']:
            reading.append(f"**Cardinal Dominance ({mod['cardinal']} planets):** You're a natural initiator and leader. You excel at starting new projects, taking charge, and pioneering new directions. You possess initiative, courage, and decisiveness. Your challenge is following through and being sensitive to the needs of those who operate differently.\n")
        elif mod['fixed'] > mod['cardinal'] and mod['fixed'] > mod['mutable']:
            reading.append(f"**Fixed Dominance ({mod['fixed']} planets):** You're a stabilizer and consolidator. You excel at sustaining momentum, building solid foundations, and maintaining what matters. You possess loyalty, determination, and staying power. Your challenge is adapting to change and being open to new perspectives.\n")
        elif mod['mutable'] > mod['cardinal'] and mod['mutable'] > mod['fixed']:
            reading.append(f"**Mutable Dominance ({mod['mutable']} planets):** You're an adapter and connector. You excel at flexibility, communication, and seeing multiple viewpoints. You're naturally curious and can shift approach as needed. Your challenge is developing follow-through and making final decisions.\n")
        else:
            reading.append(f"**Balanced Distribution:** You have moderate representation of all modalities. You can initiate when needed, persist when required, and adapt when circumstances demand. This balance makes you versatile and adaptable to various situations.\n")
        
        reading.append("")
        
        reading.append("=" * 70)
        reading.append("\n## SACRED GEOMETRY & FLOWER OF LIFE ALIGNMENTS\n")
        
        if fol_hits:
            reading.append(f"**Sacred Geometry Activation: {len(fol_hits)} Flower of Life Node Alignments**\n")
            reading.append("The Flower of Life is the fundamental sacred geometry pattern found throughout nature, representing divine order and cosmic creation. When celestial bodies align with these geometric nodes in your birth chart, they create concentrated points of archetypal power. These alignments suggest that specific planetary energies are amplified and divinely emphasized in your life blueprint.\n\n")
            
            for i, hit in enumerate(fol_hits, 1):
                orb_desc = "exact" if hit['orb'] < 0.5 else "precise" if hit['orb'] < 1.0 else "aligned"
                sign_info = self.SIGN_TRAITS.get(hit['sign'], {})
                planet_info = self.PLANET_MEANINGS.get(hit['name'], "")
                house_context = self.HOUSE_CONTEXTS.get(hit['house'], "life")
                
                reading.append(f"**{i}. {hit['name']} at {hit['lon']:.2f}° (FOL Node {hit['node']:.2f}°, Orb: {hit['orb']:.2f}°)**")
                reading.append(f"   {hit['sign']} | House {hit['house']} | {orb_desc.capitalize()} alignment\n")
                
                reading.append(f"   Sacred significance: Your {hit['name']} in {hit['sign']} is positioned {orb_desc} to a Flower of Life node. {planet_info} In the context of {house_context}, this amplification means you possess concentrated archetypal power in this domain.")
                
                sign_traits = sign_info.get("keywords", "")
                sign_desc = sign_info.get("description", "").split("Your challenge")[0].strip()
                
                reading.append(f"\n   The {hit['sign']} expression ({sign_traits}) of {hit['name']}'s energy becomes a focal point of your soul's work. {sign_desc} This sacred geometry alignment suggests that mastering and consciously wielding this planetary force is central to your life purpose.")
                
                if hit['orb'] < 0.5:
                    reading.append(f"\n   **Exact alignment** (orb < 0.5°): This is a precise cosmic calibration. The universe has marked this placement with exceptional clarity. This is not coincidence—it reflects a deliberate soul choice to work directly with this archetypal energy.")
                elif hit['orb'] < 1.0:
                    reading.append(f"\n   **Precise alignment** (orb < 1.0°): Very tight coordination with the Flower of Life geometry. Your soul has strong intention around this planetary expression.")
                else:
                    reading.append(f"\n   **Active alignment** (orb ≤ 2.0°): Within the Flower of Life's resonance field. This planetary energy participates in the sacred geometry activation of your chart.")
                
                reading.append("\n")
            
            reading.append(f"\nThese {len(fol_hits)} FOL alignments create concentrated points of cosmic activation in your chart. They represent areas where you have heightened potential, heightened challenge, and heightened spiritual significance. These are not random placements—they are your soul's specific curriculum for this incarnation.\n")
        else:
            reading.append("Your chart does not contain celestial bodies aligning with Flower of Life nodes within 2° orb. This does not diminish your chart's power—it simply means your cosmic activation manifests through traditional planetary aspects and sign positions rather than through sacred geometry node resonance. Your spiritual development operates through different archetypal channels, equally valid and profound.\n\n")
        
        reading.append("=" * 70)
        reading.append("\n## MAJOR ASPECTS: PLANETARY CONVERSIONS\n")
        
        if chart_data["aspects"]:
            seen = set()
            unique_aspects = []
            for aspect in chart_data["aspects"]:
                pair = tuple(sorted([aspect['object1'], aspect['object2']]))
                if pair not in seen:
                    seen.add(pair)
                    unique_aspects.append(aspect)
            
            all_aspects = sorted(unique_aspects, key=lambda a: abs(a['orb']))[:25]
            
            harmonious = [a for a in all_aspects if self.get_aspect_name(a['type']) in ["Trine", "Sextile"]]
            challenging = [a for a in all_aspects if self.get_aspect_name(a['type']) in ["Square", "Opposition"]]
            other = [a for a in all_aspects if self.get_aspect_name(a['type']) in ["Conjunction", "Quincunx"]]
            
            reading.append(f"Your chart contains **{len(chart_data['aspects'])} significant aspects**. The planetary conversions shape your psychology, gifts, and challenges:\n\n")
            
            if harmonious:
                reading.append(f"**Harmonious Aspects ({len(harmonious)} total):**\n")
                for aspect in harmonious[:8]:
                    aspect_name = self.get_aspect_name(aspect['type'])
                    meaning = self.get_contextual_aspect_description(aspect['object1'], aspect['object2'], aspect_name)
                    reading.append(f"• **{aspect['object1']} {aspect_name} {aspect['object2']}** (Orb: {abs(aspect['orb']):.1f}°)")
                    reading.append(f"  {meaning}\n")
            
            if challenging:
                reading.append(f"\n**Challenging Aspects ({len(challenging)} total):**\n")
                for aspect in challenging[:8]:
                    aspect_name = self.get_aspect_name(aspect['type'])
                    meaning = self.get_contextual_aspect_description(aspect['object1'], aspect['object2'], aspect_name)
                    reading.append(f"• **{aspect['object1']} {aspect_name} {aspect['object2']}** (Orb: {abs(aspect['orb']):.1f}°)")
                    reading.append(f"  {meaning}\n")
            
            if other:
                reading.append(f"\n**Concentrated Focal Points ({len(other)} total):**\n")
                for aspect in other[:6]:
                    aspect_name = self.get_aspect_name(aspect['type'])
                    meaning = self.get_contextual_aspect_description(aspect['object1'], aspect['object2'], aspect_name)
                    reading.append(f"• **{aspect['object1']} {aspect_name} {aspect['object2']}** (Orb: {abs(aspect['orb']):.1f}°)")
                    reading.append(f"  {meaning}\n")
            
            reading.append("")
        else:
            reading.append("Your chart shows a unique pattern with minimal major aspects. This suggests independence and self-determination. You're less influenced by planetary conflicts and agreements, instead forging your own path based on individual will and purpose.\n\n")
        
        reading.append("=" * 70)
        reading.append("\n## YOUR COSMIC BLUEPRINT: SYNTHESIS & LIFE DIRECTION\n")
        
        synthesis = self.training_data.get_random_general()
        reading.append(f"{synthesis}\n\n")
        
        reading.append("Your natal chart is a multidimensional portrait of your psychological, emotional, and spiritual self. These planetary placements and their interactions form the substrate of your personality, your talents, your challenges, and your potential. They are not fixed destiny, but rather the raw materials from which you sculpt your life.\n\n")
        
        reading.append("The greatest gift of astrology is its power to illuminate your nature—to show you where your natural gifts lie and where your growth edges reside. Use this knowledge to work *with* your cosmic blueprint rather than against it. Consciously cultivate your strengths, compassionately address your challenges, and watch as your life unfolds with increasing synchronicity and meaning.\n\n")
        
        reading.append("Your soul chose this exact moment to be born into this exact body on this exact location. That choice encoded everything you see in this chart. Trust it. Work with it. Become it.\n")
        
        reading.append("\n" + "=" * 70)
        reading.append("\n✨ End of Reading ✨\n")
        
        output = "\n".join(reading)
        output = output.replace("\n\n\n", "\n\n")
        return output
