"""
AI Assistant — symptom analysis, vitals insights, recommendations.
Pure local logic — no external API calls required.
"""

import re

# ── Symptom database ──────────────────────────────────────────────────────────
SYMPTOM_MAP = [
    {
        'keywords': {'chest pain', 'chest tightness', 'left arm pain', 'shortness of breath', 'sweating', 'jaw pain'},
        'match_min': 2,
        'conditions': ['Acute Myocardial Infarction (Heart Attack)', 'Unstable Angina', 'Pulmonary Embolism'],
        'icd': ['I21', 'I20.0', 'I26'],
        'severity': 'critical',
        'severity_label': 'EMERGENCY',
        'action': 'Call emergency services (911) immediately. Do not drive yourself. Chew aspirin (325 mg) if not allergic while waiting.',
        'icon': 'fa-heart-crack',
        'color': '#EF4444',
    },
    {
        'keywords': {'fever', 'chills', 'muscle aches', 'fatigue', 'headache', 'cough', 'sore throat', 'body pain'},
        'match_min': 3,
        'conditions': ['Influenza (Flu)', 'COVID-19 Infection', 'Upper Respiratory Infection'],
        'icd': ['J11.1', 'U07.1', 'J06.9'],
        'severity': 'moderate',
        'severity_label': 'See a Doctor',
        'action': 'Rest, hydrate, and monitor temperature. Consult a doctor if fever exceeds 39.5°C (103°F) or symptoms worsen after 3 days.',
        'icon': 'fa-temperature-high',
        'color': '#F59E0B',
    },
    {
        'keywords': {'headache', 'nausea', 'vomiting', 'sensitivity to light', 'neck stiffness', 'throbbing'},
        'match_min': 2,
        'conditions': ['Migraine', 'Tension-Type Headache', 'Meningitis (if neck stiffness + fever)'],
        'icd': ['G43.9', 'G44.2', 'G03.9'],
        'severity': 'moderate',
        'severity_label': 'See a Doctor',
        'action': 'Rest in a dark quiet room. If neck stiffness accompanies fever, seek emergency care immediately — this may indicate meningitis.',
        'icon': 'fa-brain',
        'color': '#F59E0B',
    },
    {
        'keywords': {'frequent urination', 'excessive thirst', 'blurred vision', 'fatigue', 'slow healing', 'weight loss', 'tingling'},
        'match_min': 2,
        'conditions': ['Type 2 Diabetes Mellitus', 'Prediabetes', 'Hyperglycemia'],
        'icd': ['E11.9', 'R73.09', 'E16.0'],
        'severity': 'moderate',
        'severity_label': 'Consult Doctor',
        'action': 'Schedule a fasting blood glucose and HbA1c test. Reduce sugar and refined carbohydrate intake while awaiting results.',
        'icon': 'fa-droplet',
        'color': '#8B5CF6',
    },
    {
        'keywords': {'abdominal pain', 'bloating', 'diarrhea', 'constipation', 'nausea', 'stomach cramps', 'indigestion'},
        'match_min': 2,
        'conditions': ['Irritable Bowel Syndrome (IBS)', 'Gastroenteritis', 'Peptic Ulcer Disease'],
        'icd': ['K58.9', 'A09', 'K27.9'],
        'severity': 'mild',
        'severity_label': 'Monitor',
        'action': 'Stay hydrated and follow a bland diet (BRAT). Seek immediate care if you notice blood in stool or severe pain.',
        'icon': 'fa-circle-exclamation',
        'color': '#10B981',
    },
    {
        'keywords': {'shortness of breath', 'wheezing', 'coughing', 'chest tightness', 'breathlessness', 'mucus'},
        'match_min': 2,
        'conditions': ['Bronchial Asthma', 'COPD Exacerbation', 'Pneumonia'],
        'icd': ['J45.9', 'J44.1', 'J18.9'],
        'severity': 'high',
        'severity_label': 'Urgent Care',
        'action': 'Use a prescribed bronchodilator inhaler if available. Seek urgent care if breathing does not improve within 15 minutes.',
        'icon': 'fa-lungs',
        'color': '#EF4444',
    },
    {
        'keywords': {'joint pain', 'swelling', 'stiffness', 'redness', 'warmth', 'limited movement'},
        'match_min': 2,
        'conditions': ['Rheumatoid Arthritis', 'Osteoarthritis', 'Gout'],
        'icd': ['M06.9', 'M19.9', 'M10.9'],
        'severity': 'mild',
        'severity_label': 'Consult Doctor',
        'action': 'Rest and ice the affected joint for 20 minutes. NSAIDs may help. Schedule a rheumatology consultation for persistent symptoms.',
        'icon': 'fa-person-cane',
        'color': '#06B6D4',
    },
    {
        'keywords': {'dizziness', 'fainting', 'lightheadedness', 'blurred vision', 'weakness', 'imbalance'},
        'match_min': 2,
        'conditions': ['Orthostatic Hypotension', 'Anaemia', 'Benign Positional Vertigo'],
        'icd': ['I95.1', 'D64.9', 'H81.1'],
        'severity': 'moderate',
        'severity_label': 'See a Doctor',
        'action': 'Sit or lie down immediately. Stay well-hydrated. Seek urgent evaluation if fainting occurs frequently or is accompanied by chest pain.',
        'icon': 'fa-head-side-virus',
        'color': '#F59E0B',
    },
    {
        'keywords': {'palpitations', 'irregular heartbeat', 'racing heart', 'skipped beats', 'fluttering'},
        'match_min': 1,
        'conditions': ['Atrial Fibrillation', 'Supraventricular Tachycardia', 'Anxiety-Related Palpitations'],
        'icd': ['I48.9', 'I47.1', 'F41.9'],
        'severity': 'high',
        'severity_label': 'Urgent Care',
        'action': 'Avoid caffeine and stimulants. If palpitations last more than 30 minutes or are accompanied by chest pain, seek emergency care.',
        'icon': 'fa-heart-pulse',
        'color': '#EF4444',
    },
    {
        'keywords': {'anxiety', 'panic', 'trembling', 'sweating', 'rapid breathing', 'fear', 'restlessness'},
        'match_min': 2,
        'conditions': ['Panic Disorder', 'Generalized Anxiety Disorder', 'Hyperthyroidism'],
        'icd': ['F41.0', 'F41.1', 'E05.9'],
        'severity': 'moderate',
        'severity_label': 'Consult Doctor',
        'action': 'Practice slow diaphragmatic breathing. Limit caffeine. A mental health evaluation and possible thyroid function test is recommended.',
        'icon': 'fa-brain',
        'color': '#8B5CF6',
    },
    {
        'keywords': {'back pain', 'lower back', 'radiating pain', 'numbness', 'weakness in legs', 'sciatica'},
        'match_min': 2,
        'conditions': ['Lumbar Disc Herniation', 'Sciatica', 'Muscle Strain'],
        'icd': ['M51.1', 'M54.4', 'M54.5'],
        'severity': 'mild',
        'severity_label': 'Monitor',
        'action': 'Apply heat or ice. Gentle stretching may help. Seek evaluation if pain radiates down the leg or causes bladder/bowel changes.',
        'icon': 'fa-person-walking',
        'color': '#06B6D4',
    },
    {
        'keywords': {'rash', 'itching', 'hives', 'swelling', 'skin redness', 'blistering'},
        'match_min': 1,
        'conditions': ['Allergic Reaction', 'Contact Dermatitis', 'Urticaria'],
        'icd': ['T78.1', 'L23.9', 'L50.9'],
        'severity': 'moderate',
        'severity_label': 'See a Doctor',
        'action': 'Avoid the suspected allergen. Antihistamines may relieve symptoms. Seek emergency care if swelling affects the throat or breathing.',
        'icon': 'fa-circle-radiation',
        'color': '#F59E0B',
    },
]

_SEVERITY_ORDER = {'critical': 4, 'high': 3, 'moderate': 2, 'mild': 1}

COMMON_SYMPTOMS = [
    'Fever', 'Headache', 'Fatigue', 'Cough', 'Chest Pain',
    'Shortness of Breath', 'Nausea', 'Vomiting', 'Diarrhea',
    'Dizziness', 'Joint Pain', 'Back Pain', 'Abdominal Pain',
    'Sore Throat', 'Chills', 'Sweating', 'Muscle Aches',
    'Palpitations', 'Blurred Vision', 'Anxiety',
]


def analyze_symptoms(symptoms_input: str) -> dict:
    """
    Analyze free-text symptoms. Returns structured match results.
    Works with comma-separated text or natural language.
    """
    if not symptoms_input or not symptoms_input.strip():
        return {'matched': False, 'message': 'Please enter at least one symptom.'}

    text    = symptoms_input.lower()
    text    = re.sub(r'[,;/]', ' ', text)
    words   = set(re.split(r'\s+', text.strip()))
    phrases = set()

    compound = [
        'chest pain', 'chest tightness', 'left arm pain', 'shortness of breath',
        'sore throat', 'blurred vision', 'slow healing', 'excessive thirst',
        'frequent urination', 'abdominal pain', 'joint pain', 'neck stiffness',
        'sensitivity to light', 'muscle aches', 'body pain', 'stomach cramps',
        'lower back', 'back pain', 'radiating pain', 'racing heart',
        'irregular heartbeat', 'skipped beats', 'rapid breathing',
        'weakness in legs', 'limited movement', 'skin redness', 'jaw pain',
    ]
    for phrase in compound:
        if phrase in text:
            phrases.add(phrase)

    tokens = words | phrases
    matches = []
    for entry in SYMPTOM_MAP:
        hit = tokens & entry['keywords']
        if len(hit) >= entry['match_min']:
            score = len(hit) / len(entry['keywords'])
            matches.append({
                **entry,
                'matched_keywords': list(hit),
                'score': round(score, 2),
                'keywords': list(entry['keywords']),
            })

    if not matches:
        return {
            'matched': False,
            'message': 'No specific pattern detected. Symptoms may be mild or non-specific. If persistent, consult a healthcare provider.',
        }

    matches.sort(key=lambda x: (_SEVERITY_ORDER.get(x['severity'], 0), x['score']), reverse=True)
    return {'matched': True, 'results': matches[:3]}


# ── Vitals analysis ───────────────────────────────────────────────────────────

_VITALS_META = {
    'age':               {'label': 'Age',             'unit': 'yrs',   'normal': (18, 75),   'warn_hi': 80,  'warn_lo': None, 'vmin': 18,  'vmax': 95 },
    'systolic_bp':       {'label': 'Systolic BP',     'unit': 'mmHg',  'normal': (90, 120),  'warn_hi': 140, 'warn_lo': 85,   'vmin': 80,  'vmax': 200},
    'diastolic_bp':      {'label': 'Diastolic BP',    'unit': 'mmHg',  'normal': (60, 80),   'warn_hi': 90,  'warn_lo': 55,   'vmin': 50,  'vmax': 130},
    'heart_rate':        {'label': 'Heart Rate',      'unit': 'bpm',   'normal': (60, 100),  'warn_hi': 110, 'warn_lo': 50,   'vmin': 45,  'vmax': 150},
    'glucose_level':     {'label': 'Blood Glucose',   'unit': 'mg/dL', 'normal': (70, 100),  'warn_hi': 126, 'warn_lo': 65,   'vmin': 60,  'vmax': 300},
    'bmi':               {'label': 'BMI',             'unit': 'kg/m²', 'normal': (18.5, 25), 'warn_hi': 30,  'warn_lo': 17,   'vmin': 15,  'vmax': 50 },
    'cholesterol':       {'label': 'Cholesterol',     'unit': 'mg/dL', 'normal': (100, 200), 'warn_hi': 240, 'warn_lo': None, 'vmin': 100, 'vmax': 350},
    'oxygen_saturation': {'label': 'O₂ Saturation',  'unit': '%',     'normal': (95, 100),  'warn_hi': None,'warn_lo': 90,   'vmin': 85,  'vmax': 100},
}


def analyze_vitals(vitals: dict) -> list:
    """Return per-vital status with color coding and normal-range context."""
    out = []
    for key, meta in _VITALS_META.items():
        raw = vitals.get(key)
        if raw is None:
            continue
        try:
            v = float(raw)
        except (TypeError, ValueError):
            continue

        lo, hi   = meta['normal']
        w_lo     = meta.get('warn_lo')
        w_hi     = meta.get('warn_hi')
        vmin, vmax = meta['vmin'], meta['vmax']
        pct      = min(100, max(0, int((v - vmin) / max(vmax - vmin, 1) * 100)))

        if v < lo:
            if w_lo is not None and v <= w_lo:
                status, color, badge = 'critical', '#EF4444', 'Critical Low'
            else:
                status, color, badge = 'warning', '#F59E0B', 'Below Normal'
        elif v > hi:
            if w_hi is not None and v >= w_hi:
                status, color, badge = 'critical', '#EF4444', 'Critical High'
            else:
                status, color, badge = 'warning', '#F59E0B', 'Above Normal'
        else:
            status, color, badge = 'normal', '#10B981', 'Normal'

        out.append({
            'key':    key,
            'label':  meta['label'],
            'value':  v,
            'unit':   meta['unit'],
            'status': status,
            'color':  color,
            'badge':  badge,
            'pct':    pct,
            'normal_range': f"{lo}–{hi} {meta['unit']}",
        })
    return out


def get_recommendations(prediction: int, probability: float, vitals: dict) -> list:
    """Return up to 5 prioritized, actionable health recommendations."""
    recs = []

    sbp  = float(vitals.get('systolic_bp',       0))
    dbp  = float(vitals.get('diastolic_bp',       0))
    gluc = float(vitals.get('glucose_level',      0))
    bmi  = float(vitals.get('bmi',                0))
    chol = float(vitals.get('cholesterol',        0))
    o2   = float(vitals.get('oxygen_saturation', 100))
    hr   = float(vitals.get('heart_rate',        72))

    if sbp >= 140 or dbp >= 90:
        recs.append({'icon': 'fa-heart', 'color': '#EF4444',
            'title': 'Hypertension Detected',
            'text': f'BP {int(sbp)}/{int(dbp)} mmHg is in the hypertensive range. Reduce sodium intake, avoid alcohol, increase aerobic activity. Consider antihypertensive medication if persistent.'})
    elif sbp > 120 or dbp > 80:
        recs.append({'icon': 'fa-heart', 'color': '#F59E0B',
            'title': 'Elevated Blood Pressure',
            'text': f'BP {int(sbp)}/{int(dbp)} mmHg is elevated (pre-hypertension). Lifestyle modifications: reduce sodium, lose weight if overweight, exercise 30 min/day.'})

    if gluc >= 126:
        recs.append({'icon': 'fa-droplet', 'color': '#EF4444',
            'title': 'Diabetic Range Glucose',
            'text': f'Fasting glucose {int(gluc)} mg/dL meets diagnostic criteria for diabetes (≥126). Schedule HbA1c and fasting glucose tests. Refer to endocrinologist.'})
    elif gluc >= 100:
        recs.append({'icon': 'fa-droplet', 'color': '#F59E0B',
            'title': 'Prediabetic Glucose',
            'text': f'Glucose {int(gluc)} mg/dL is in the prediabetic range (100–125). Reduce refined carbohydrates and sugar. 150 minutes of moderate exercise weekly can prevent progression.'})

    if bmi >= 30:
        recs.append({'icon': 'fa-scale-balanced', 'color': '#F59E0B',
            'title': 'Obesity — Elevated Risk Factor',
            'text': f'BMI {bmi:.1f} indicates obesity. A 5–10% reduction in body weight reduces cardiovascular and diabetic risk significantly. Structured diet and exercise plan recommended.'})
    elif bmi >= 25:
        recs.append({'icon': 'fa-scale-balanced', 'color': '#06B6D4',
            'title': 'Overweight BMI',
            'text': f'BMI {bmi:.1f} is in the overweight range. Target BMI 18.5–24.9 through 150 min/week moderate exercise and balanced caloric intake.'})

    if chol >= 240:
        recs.append({'icon': 'fa-flask', 'color': '#EF4444',
            'title': 'High Cholesterol',
            'text': f'Total cholesterol {int(chol)} mg/dL is high (≥240). Reduce saturated fat, increase soluble fiber. Statin therapy assessment is recommended.'})
    elif chol >= 200:
        recs.append({'icon': 'fa-flask', 'color': '#F59E0B',
            'title': 'Borderline Cholesterol',
            'text': f'Cholesterol {int(chol)} mg/dL is borderline (200–239). Dietary changes: oats, nuts, olive oil. Re-test in 3 months.'})

    if o2 < 92:
        recs.append({'icon': 'fa-lungs', 'color': '#EF4444',
            'title': 'Critical O₂ Saturation',
            'text': f'Oxygen saturation {o2}% is critically low. Seek immediate medical attention. May indicate respiratory failure.'})
    elif o2 < 95:
        recs.append({'icon': 'fa-lungs', 'color': '#F59E0B',
            'title': 'Low O₂ Saturation',
            'text': f'SpO₂ {o2}% is below normal (95–100%). Evaluate for asthma, COPD, or other pulmonary conditions.'})

    if hr > 100:
        recs.append({'icon': 'fa-heart-pulse', 'color': '#F59E0B',
            'title': 'Tachycardia',
            'text': f'Heart rate {int(hr)} bpm is elevated (normal 60–100). Avoid caffeine and stimulants. Persistent tachycardia warrants an ECG and cardiac evaluation.'})
    elif hr < 50:
        recs.append({'icon': 'fa-heart-pulse', 'color': '#06B6D4',
            'title': 'Bradycardia',
            'text': f'Heart rate {int(hr)} bpm is low. May be normal for athletes. If accompanied by dizziness or fatigue, seek cardiac evaluation.'})

    if prediction == 1 and probability >= 70:
        recs.insert(0, {'icon': 'fa-stethoscope', 'color': '#EF4444',
            'title': 'High Cardiovascular Risk — Urgent Review',
            'text': f'FL model confidence: {probability:.1f}% risk. Schedule a comprehensive cardiovascular workup within 2 weeks. Includes stress test, lipid panel, ECG, and echocardiogram.'})
    elif prediction == 1:
        recs.insert(0, {'icon': 'fa-stethoscope', 'color': '#F59E0B',
            'title': 'Elevated Disease Risk',
            'text': f'FL model detected elevated risk ({probability:.1f}% probability). Schedule a preventive health check-up within the next 4 weeks.'})
    else:
        recs.append({'icon': 'fa-shield-heart', 'color': '#10B981',
            'title': 'Low Risk — Maintain Healthy Habits',
            'text': 'Your current vitals suggest low cardiovascular risk. Maintain 150 min/week aerobic exercise, balanced nutrition, adequate sleep, and annual check-ups.'})

    return recs[:5]
