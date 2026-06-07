import re


from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

from .data import _load_csv_datasets, SYMPTOM_KEYWORDS


_TRAIN_DATA = [
    ("fever cough runny nose chills fatigue body ache", "Flu"),
    ("high fever sore throat runny nose sneezing headache", "Flu"),
    ("fever body pain chills sweating fatigue", "Flu"),
    ("cold cough sneezing runny nose sore throat", "Common Cold"),
    ("runny nose blocked nose sneezing mild fever cough", "Common Cold"),
    ("sore throat runny nose mild cough sneezing", "Common Cold"),
    ("high fever severe headache joint pain rash eye pain fatigue", "Dengue"),
    ("sudden high fever rash behind eyes joint pain muscle pain", "Dengue"),
    ("fever rash joint pain bleeding gums fatigue vomiting", "Dengue"),
    ("high fever chills sweating headache nausea vomiting", "Malaria"),
    ("cyclic fever chills headache muscle pain fatigue", "Malaria"),
    ("fever shivering sweating body pain fatigue", "Malaria"),
    ("prolonged fever stomach pain constipation headache weakness", "Typhoid"),
    ("high fever abdominal pain diarrhea loss of appetite fatigue", "Typhoid"),
    ("fever headache stomach ache weakness loss of appetite", "Typhoid"),
    ("chest pain fever cough breathlessness chills fatigue", "Pneumonia"),
    ("high fever cough chest pain difficulty breathing sweating", "Pneumonia"),
    ("cough with phlegm fever breathlessness chest pain", "Pneumonia"),
    ("fever cough loss of smell fatigue breathlessness", "COVID-19"),
    ("dry cough fever fatigue loss of taste loss of smell", "COVID-19"),
    ("high fever breathlessness chest pain fatigue body ache", "COVID-19"),
    ("stomach pain nausea vomiting diarrhea fever cramps", "Gastroenteritis"),
    ("vomiting diarrhea abdominal pain dehydration fatigue", "Gastroenteritis"),
    ("loose motions stomach pain nausea vomiting weakness", "Gastroenteritis"),
    ("nausea vomiting diarrhea stomach cramps fever", "Food Poisoning"),
    ("vomiting stomach pain diarrhea sweating nausea", "Food Poisoning"),
    ("sudden vomiting loose stool abdominal cramps weakness", "Food Poisoning"),
    ("severe headache nausea light sensitivity vomiting throbbing", "Migraine"),
    ("one-sided headache nausea vomiting visual disturbance", "Migraine"),
    ("pulsating headache sensitivity to light sound nausea", "Migraine"),
    ("headache dizziness blurred vision chest pain fatigue", "Hypertension"),
    ("severe headache palpitations shortness of breath dizziness", "Hypertension"),
    ("headache neck pain dizziness blurred vision nausea", "Hypertension"),
    ("frequent urination excessive thirst fatigue blurred vision", "Diabetes"),
    ("weight loss frequent urination slow healing wounds fatigue", "Diabetes"),
    ("thirst frequent urination weakness fatigue numbness feet", "Diabetes"),
    ("weakness fatigue dizziness pale skin shortness of breath", "Anemia"),
    ("fatigue headache dizziness cold hands feet pale skin", "Anemia"),
    ("tiredness weakness pale skin rapid heartbeat dizziness", "Anemia"),
    ("wheezing chest tightness breathlessness cough night", "Asthma"),
    ("difficulty breathing chest tightness wheezing cough", "Asthma"),
    ("breathlessness coughing wheezing tightness chest", "Asthma"),
    ("persistent cough blood sputum night sweats weight loss fatigue", "Tuberculosis"),
    ("chronic cough chest pain night sweats weight loss fever", "Tuberculosis"),
    ("coughing blood night sweats weight loss fatigue weakness", "Tuberculosis"),
    ("yellow skin yellow eyes dark urine fatigue itching", "Jaundice"),
    ("yellowish skin eyes abdominal pain nausea fatigue", "Jaundice"),
    ("yellow eyes skin dark urine pale stool loss appetite", "Jaundice"),
    ("burning urination frequent urination pelvic pain fever", "Urinary Tract Infection"),
    ("painful urination frequency urgency cloudy urine fever", "Urinary Tract Infection"),
    ("burning pee frequent urination back pain fever chills", "Urinary Tract Infection"),
    ("heartburn chest burning indigestion bloating acidity", "Acid Reflux"),
    ("sour taste mouth burning chest after eating bloating", "Acid Reflux"),
    ("acid regurgitation heartburn nausea chest discomfort", "Acid Reflux"),
    ("abdominal pain bloating diarrhea constipation gas cramps", "IBS"),
    ("stomach cramps bloating alternating diarrhea constipation", "IBS"),
    ("bloating gas stomach pain loose stool constipation", "IBS"),
    ("crushing chest pain left arm pain sweating breathlessness nausea", "Heart Attack"),
    ("severe chest pain radiating arm jaw sweating dizzy", "Heart Attack"),
    ("chest tightness pain arm neck sweating nausea breathless", "Heart Attack"),
    ("sudden numbness face arm leg confusion speech difficulty", "Stroke"),
    ("sudden weakness one side face drooping speech slurred", "Stroke"),
    ("sudden severe headache vision loss balance problem weakness", "Stroke"),
    ("lower right abdominal pain nausea fever vomiting", "Appendicitis"),
    ("sharp pain lower right abdomen fever nausea loss appetite", "Appendicitis"),
    ("abdominal pain right side fever vomiting rebound tenderness", "Appendicitis"),
    ("severe back pain side pain urination pain blood urine", "Kidney Stone"),
    ("sharp flank pain nausea vomiting frequent urination blood urine", "Kidney Stone"),
    ("severe pain back groin nausea vomiting painful urination", "Kidney Stone"),
    ("joint pain swelling stiffness morning stiffness fatigue", "Arthritis"),
    ("swollen joints pain stiffness reduced movement fatigue", "Arthritis"),
    ("joint inflammation pain stiffness warmth swelling", "Arthritis"),
    ("anxiety panic rapid heartbeat sweating trembling restlessness", "Anxiety Disorder"),
    ("excessive worry panic attack chest tightness breathlessness", "Anxiety Disorder"),
    ("nervousness restlessness palpitations sweating headache", "Anxiety Disorder"),
    ("sadness hopelessness fatigue loss interest sleep problems", "Depression"),
    ("low mood no motivation fatigue sleep change appetite change", "Depression"),
    ("persistent sadness worthlessness fatigue concentration loss", "Depression"),
    ("itchy rash blisters fever headache fatigue loss appetite", "Chickenpox"),
    ("blister rash fever itching headache tiredness", "Chickenpox"),
    ("rash blisters all body fever itching fatigue", "Chickenpox"),
    ("high fever rash cough runny nose red eyes koplik spots", "Measles"),
    ("fever rash starts face spreads body cough red eyes", "Measles"),
    ("high fever rash cough cold sensitivity light", "Measles"),
    ("stiff neck high fever severe headache vomiting sensitivity light", "Meningitis"),
    ("neck stiffness fever headache photophobia nausea rash", "Meningitis"),
    ("severe headache stiff neck fever vomiting confusion rash", "Meningitis"),
    ("weight loss rapid heartbeat sweating nervousness heat intolerance", "Hyperthyroidism"),
    ("anxiety palpitations weight loss tremor sweating", "Hyperthyroidism"),
    ("increased heartbeat weight loss nervousness sweating insomnia", "Hyperthyroidism"),
    ("weight gain fatigue cold intolerance constipation dry skin", "Hypothyroidism"),
    ("weight gain tiredness depression hair loss constipation cold", "Hypothyroidism"),
    ("fatigue weight gain constipation dry skin slow heart rate", "Hypothyroidism"),
    ("facial pain nasal congestion headache thick discharge fever", "Sinusitis"),
    ("sinus pressure headache blocked nose facial pain post nasal", "Sinusitis"),
    ("stuffy nose facial pressure headache loss smell discharge", "Sinusitis"),
    ("hives itching rash swelling sneezing runny nose", "Allergic Reaction"),
    ("skin rash itching redness swelling watery eyes sneezing", "Allergic Reaction"),
    ("allergic rash hives swelling itching runny nose", "Allergic Reaction"),
    ("chronic cough breathlessness wheezing mucus production fatigue", "COPD"),
    ("long term cough difficulty breathing chest tightness mucus", "COPD"),
    ("breathlessness cough phlegm chest tightness fatigue", "COPD"),
    ("burning stomach pain hunger pain nausea vomiting blood stool", "Peptic Ulcer"),
    ("stomach ache worse empty burning nausea dark stool", "Peptic Ulcer"),
    ("upper abdominal burning pain nausea heartburn dark stool", "Peptic Ulcer"),
    ("yellow skin fatigue nausea abdominal pain dark urine fever", "Hepatitis"),
    ("jaundice fatigue loss appetite nausea vomiting abdominal pain", "Hepatitis"),
    ("yellowish eyes skin fatigue nausea dark urine fever", "Hepatitis"),
    ("intense itching rash between fingers wrists worse night", "Scabies"),
    ("itching rash skin burrows worse at night", "Scabies"),
    ("red eyes discharge itching watering light sensitivity", "Conjunctivitis"),
    ("pink eye redness itching discharge tears", "Conjunctivitis"),
    ("lower back pain stiffness muscle spasm radiating leg pain", "Back Pain"),
    ("back ache stiffness difficulty standing walking pain leg", "Back Pain"),
    ("dizziness spinning sensation nausea balance loss", "Vertigo"),
    ("room spinning vertigo nausea vomiting balance problem", "Vertigo"),
    ("excessive thirst dry mouth dark urine dizziness fatigue", "Dehydration"),
    ("thirst dizziness weakness dark urine headache fatigue", "Dehydration"),
]


def _preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_ml_models():
    training_df, testing_df = _load_csv_datasets()
    texts = [t for t, _ in _TRAIN_DATA]
    labels = [l for _, l in _TRAIN_DATA]

    processed_texts = [_preprocess(t) for t in texts]
    tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
    X_train = tfidf.fit_transform(processed_texts)

    label_enc = LabelEncoder()
    y_train = label_enc.fit_transform(labels)

    model = RandomForestClassifier(n_estimators=120, random_state=23)
    model.fit(X_train, y_train)

    metrics = {}
    try:
        y_pred = model.predict(X_train)
        metrics = {
            "accuracy": float((y_pred == y_train).mean()),
        }
    except Exception:
        metrics = {}

    return model, "RandomForest", tfidf, label_enc, metrics, _preprocess


_ml_model, _ml_best_name, _tfidf, _label_enc, _metrics_df, _preprocess = build_ml_models()
_training_df, _testing_df = _load_csv_datasets()


SYMPTOM_MAP = {
    "abdominal_pain": ["stomach_pain", "belly_pain"],
    "diarrhea": ["diarrhoea"],
    "fever": ["high_fever", "mild_fever"],
    "frequent_urination": ["polyuria", "continuous_feel_of_urine"],
    "urination_pain": ["burning_micturition"],
    "blurred_vision": ["blurred_and_distorted_vision"],
    "sneezing": ["continuous_sneezing"],
    "cold": ["congestion"],
    "swelling": ["swelled_lymph_nodes", "swelling_joints", "swelling_of_stomach", "swollen_legs", "swollen_extremeties"],
    "redness": ["redness_of_eyes", "red_spots_over_body"],
    "eye_pain": ["pain_behind_the_eyes"],
    "sore_throat": ["throat_irritation", "patches_in_throat"],
    "unconscious": ["coma", "altered_sensorium"]
}


def match_disease(symptoms):
    if not symptoms or len(symptoms) <= 1:
        return None, 0

    ref_df = _testing_df if _testing_df is not None else _training_df
    if ref_df is not None:
        sym_cols = [c for c in ref_df.columns if c != 'prognosis']
        
        # Expand symptoms to match dataset column naming conventions
        expanded_symptoms = []
        for s in symptoms:
            expanded_symptoms.append(s)
            if s in SYMPTOM_MAP:
                expanded_symptoms.extend(SYMPTOM_MAP[s])
                
        scores = {}
        for _, row in ref_df.iterrows():
            disease = str(row['prognosis']).strip()
            score = sum(1 for s in expanded_symptoms if s in sym_cols and row.get(s, 0) == 1)
            if score > 0:
                scores[disease] = scores.get(disease, 0) + score
        if scores:
            best = max(scores, key=scores.get)
            conf = min(97, int((scores[best] / max(len(symptoms), 1)) * 100))
            if scores[best] >= 3:
                conf = min(97, conf + 10)
            return best, conf

    sentence = _preprocess(" ".join(s.replace("_", " ") for s in symptoms))
    X_input = _tfidf.transform([sentence])
    if hasattr(_ml_model, 'predict_proba'):
        probs = _ml_model.predict_proba(X_input)[0]
        best_idx = int(probs.argmax())
        confidence = int(probs[best_idx] * 100)
        disease = _label_enc.inverse_transform([best_idx])[0]
    else:
        pred = _ml_model.predict(X_input)[0]
        disease = _label_enc.inverse_transform([pred])[0]
        confidence = 65

    if len(symptoms) >= 4:
        confidence = min(97, confidence + 10)
    elif len(symptoms) <= 1:
        confidence = max(0, confidence - 20)

    return (disease, confidence) if confidence >= 20 else (None, 0)


def fuzzy_contains(text, keyword, threshold=1):
    text = text.lower()
    keyword = keyword.lower()
    if keyword in text:
        return True
    words = text.split()
    if keyword in words:
        return True
    def _edit_distance(a, b):
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a) + 1):
            dp[i][0] = i
        for j in range(len(b) + 1):
            dp[0][j] = j
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        return dp[len(a)][len(b)]
    if " " in keyword:
        kwords = keyword.split()
        for i in range(len(words) - len(kwords) + 1):
            chunk = " ".join(words[i:i+len(kwords)])
            if _edit_distance(chunk, keyword) <= threshold + 1:
                return True
    return False


def extract_symptoms(text):
    text_lower = text.lower().strip()
    replacements = {
        "r ": "are ", "hv ": "have ", "frm ": "from ", "bcz ": "because ",
        "im ": "i am ", "i m ": "i am ", "n ": "and ", "wid ": "with ",
        "felling": "feeling", "feleing": "feeling", "feelling": "feeling",
        "haveing": "having", "havng": "having", "hving": "having",
        "headche": "headache", "stomache": "stomach", "fver": "fever",
        "cuf": "cough", "kof": "cough", "temperture": "temperature",
    }
    for bad, good in replacements.items():
        text_lower = text_lower.replace(bad, good)

    found = []
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for kw in keywords:
            if fuzzy_contains(text_lower, kw):
                found.append(symptom)
                break
    return list(set(found))
