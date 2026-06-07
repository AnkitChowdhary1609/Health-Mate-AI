"""HealthMate static data and diet planner."""
from pathlib import Path
import pandas as pd

DISEASE_INFO = {
    "Fungal infection": {
        "severity": "mild",
        "simple_name": "Fungal Skin Infection",
        "description": "A skin infection caused by tiny fungal organisms. Very common and easily treatable.",
        "home_remedies": ["Keep the affected area clean and dry", "Apply antifungal cream (like clotrimazole) twice daily", "Wear loose, breathable clothing", "Avoid sharing towels or clothing", "Use talcum powder to keep skin dry"],
        "diet": ["Reduce sugar intake — fungi love sugar!", "Eat yogurt with live cultures (probiotics)", "Include garlic in your meals (natural antifungal)", "Drink plenty of water (8 glasses/day)", "Avoid processed foods"],
        "when_to_visit": False,
        "recovery_days": "7-14 days with treatment"
    },
    "Allergy": {
        "severity": "mild",
        "simple_name": "Allergic Reaction",
        "description": "Your immune system is overreacting to something harmless like dust, pollen, or food.",
        "home_remedies": ["Identify and avoid the trigger", "Take antihistamine tablets (like cetirizine)", "Use saline nasal spray for nasal symptoms", "Apply cold compress for skin reactions", "Keep windows closed during high pollen season"],
        "diet": ["Avoid the known allergen", "Eat anti-inflammatory foods (turmeric, ginger)", "Stay hydrated", "Local honey may help with pollen allergies", "Omega-3 rich foods like fish help reduce inflammation"],
        "when_to_visit": False,
        "recovery_days": "1-3 days once trigger is avoided"
    },
    "GERD": {
        "severity": "moderate",
        "simple_name": "Acid Reflux (Heartburn Disease)",
        "description": "Stomach acid frequently flows back into your throat, causing burning sensation. Very manageable with lifestyle changes.",
        "home_remedies": ["Don't lie down for 2-3 hours after eating", "Eat smaller meals more frequently", "Elevate head while sleeping", "Avoid spicy, oily, and acidic foods", "Antacids can provide quick relief"],
        "diet": ["Eat small, frequent meals", "Avoid spicy foods, citrus, tomatoes, caffeine, alcohol", "Include oatmeal, bananas, melons, green vegetables", "Drink ginger tea before meals", "Avoid carbonated drinks"],
        "when_to_visit": False,
        "recovery_days": "Manageable long-term with lifestyle changes"
    },
    "Diabetes": {
        "severity": "moderate",
        "simple_name": "Diabetes (High Blood Sugar)",
        "description": "Your body has trouble managing blood sugar levels. This needs regular monitoring and management.",
        "home_remedies": ["Monitor blood sugar regularly", "Exercise for 30 minutes daily (walking is great!)", "Maintain healthy weight", "Take medications as prescribed", "Check feet daily for any sores"],
        "diet": ["Avoid sugary foods, white rice, white bread", "Eat whole grains, legumes, vegetables", "Small portions, 5-6 meals a day", "Include methi (fenugreek), karela (bitter gourd)", "Drink plenty of water, avoid sugary drinks"],
        "when_to_visit": True,
        "recovery_days": "Lifelong management — very manageable!"
    },
    "Hypertension": {
        "severity": "moderate",
        "simple_name": "High Blood Pressure",
        "description": "Your blood is pushing too hard against your artery walls. Very common and controllable.",
        "home_remedies": ["Reduce salt intake significantly", "Exercise regularly — 30 min walks daily", "Practice deep breathing / meditation", "Limit alcohol, quit smoking", "Monitor BP at home regularly"],
        "diet": ["DASH diet: fruits, vegetables, whole grains", "Reduce salt to less than 1 teaspoon/day", "Eat bananas, leafy greens, beets (lower BP naturally)", "Avoid processed foods, pickles, papad", "Limit tea/coffee to 1-2 cups/day"],
        "when_to_visit": True,
        "recovery_days": "Manageable with medication and lifestyle"
    },
    "Common Cold": {
        "severity": "mild",
        "simple_name": "Common Cold",
        "description": "A viral infection of your nose and throat. It will go away on its own in a few days!",
        "home_remedies": ["Rest as much as possible", "Drink warm fluids — kadha, ginger tea, warm water", "Steam inhalation 2-3 times a day", "Gargle with warm salt water", "Eat warm soups like dal shorba"],
        "diet": ["Hot soups and broths", "Ginger-honey-lemon tea", "Garlic in food (natural antiviral)", "Vitamin C foods: amla, oranges, guava", "Avoid cold foods, ice cream, cold drinks"],
        "when_to_visit": False,
        "recovery_days": "5-7 days naturally"
    },
    "Migraine": {
        "severity": "moderate",
        "simple_name": "Migraine (Severe Headache)",
        "description": "Intense throbbing headaches, often with nausea and light sensitivity. Triggers vary by person.",
        "home_remedies": ["Rest in a dark, quiet room", "Apply cold/warm pack to head or neck", "Stay well hydrated", "Note your triggers (food, stress, sleep)", "Over-the-counter pain relievers if needed"],
        "diet": ["Stay well hydrated throughout the day", "Avoid caffeine, alcohol, aged cheese, chocolate", "Eat regular meals — don't skip!", "Magnesium-rich foods: pumpkin seeds, spinach", "Maintain consistent meal timing"],
        "when_to_visit": False,
        "recovery_days": "4-72 hours per episode"
    },
    "Dengue": {
        "severity": "severe",
        "simple_name": "Dengue Fever",
        "description": "A mosquito-spread viral fever. Needs close monitoring — see a doctor!",
        "home_remedies": ["Rest completely", "Drink ORS (oral rehydration solution) constantly", "Eat papaya leaf extract — helps platelets", "Monitor for warning signs: bleeding, severe pain", "Use mosquito nets and repellents"],
        "diet": ["ORS frequently to prevent dehydration", "Papaya leaf juice (helps increase platelets)", "Pomegranate juice", "Coconut water for electrolytes", "Soft, easily digestible foods"],
        "when_to_visit": True,
        "recovery_days": "1-2 weeks with proper care"
    },
    "Malaria": {
        "severity": "severe",
        "simple_name": "Malaria",
        "description": "A serious mosquito-spread illness that needs immediate medical treatment.",
        "home_remedies": ["Seek medical care IMMEDIATELY", "Rest and stay hydrated", "Reduce fever with cold compress", "Eat light, easily digestible food"],
        "diet": ["Light foods: khichdi, dal rice", "Fresh fruits and juices", "Plenty of fluids and coconut water", "Avoid spicy and oily foods"],
        "when_to_visit": True,
        "recovery_days": "1-4 weeks with treatment"
    },
    "Typhoid": {
        "severity": "severe",
        "simple_name": "Typhoid Fever",
        "description": "A bacterial infection that needs antibiotic treatment. Please see a doctor.",
        "home_remedies": ["Seek medical care for antibiotics", "Rest completely", "Eat soft, easily digestible foods", "Stay very well hydrated"],
        "diet": ["Soft foods: khichdi, boiled rice, banana", "ORS to replace fluids", "Avoid raw vegetables and street food", "Boil all drinking water"],
        "when_to_visit": True,
        "recovery_days": "3-4 weeks with antibiotics"
    },
    "Heart attack": {
        "severity": "emergency",
        "simple_name": "Heart Attack",
        "description": "EMERGENCY! Blood flow to the heart is blocked. CALL 108 IMMEDIATELY!",
        "home_remedies": ["CALL 108 RIGHT NOW", "Chew aspirin if available (325mg)", "Sit or lie down comfortably", "Loosen tight clothing", "Stay calm and wait for ambulance"],
        "diet": ["Long-term: low salt, low fat diet after recovery"],
        "when_to_visit": True,
        "recovery_days": "Emergency — immediate hospital needed"
    },
    "Pneumonia": {
        "severity": "severe",
        "simple_name": "Pneumonia (Lung Infection)",
        "description": "A serious lung infection. You need medical treatment — antibiotics prescribed by a doctor.",
        "home_remedies": ["See a doctor for antibiotics ASAP", "Rest completely", "Stay well hydrated", "Steam inhalation for comfort", "Monitor breathing carefully"],
        "diet": ["High protein foods for recovery", "Warm soups and broths", "Fresh fruits for vitamin C", "Stay very well hydrated"],
        "when_to_visit": True,
        "recovery_days": "1-3 weeks with treatment"
    },
    "Chicken pox": {
        "severity": "mild",
        "simple_name": "Chickenpox",
        "description": "A viral infection causing itchy blisters. Contagious but manageable at home for most people.",
        "home_remedies": ["Don't scratch! Trim nails to avoid scratching", "Calamine lotion on blisters for itch relief", "Cool oatmeal baths reduce itching", "Wear loose, soft cotton clothing", "Isolate from others (very contagious!)"],
        "diet": ["Soft, cool foods — avoid spicy/acidic", "Ice pops or cold smoothies to soothe", "Plenty of fluids", "Vitamin C rich foods for immunity", "Light, easily digestible meals"],
        "when_to_visit": False,
        "recovery_days": "7-10 days for most people"
    },
    "Tuberculosis": {
        "severity": "severe",
        "simple_name": "Tuberculosis (TB)",
        "description": "A serious bacterial lung infection. Government provides FREE treatment! Please see a doctor immediately.",
        "home_remedies": ["MUST see doctor — free TB treatment available at govt. hospitals", "Take medicines EVERY day without fail", "Cover mouth when coughing", "Eat nutritious food to boost immunity"],
        "diet": ["High protein: eggs, dal, paneer, chicken", "Iron-rich foods: spinach, dates", "Vitamin D: sunlight, fish", "Avoid alcohol completely"],
        "when_to_visit": True,
        "recovery_days": "6 months of treatment (free govt. program)"
    },
    "Chronic cholestasis": {
        "severity": "moderate",
        "simple_name": "Chronic Cholestasis",
        "description": "A long-term condition where the flow of bile from the liver is reduced or blocked.",
        "home_remedies": ["Avoid alcohol completely", "Manage itching with cool baths", "Wear loose clothing", "Get regular check-ups"],
        "diet": ["Low-fat diet", "High fiber foods", "Vitamin supplements (A, D, E, K) as prescribed", "Avoid fried and greasy foods"],
        "when_to_visit": True,
        "recovery_days": "Chronic condition - needs lifelong management"
    },
    "Drug Reaction": {
        "severity": "moderate",
        "simple_name": "Drug Reaction",
        "description": "An adverse allergic reaction to a medication.",
        "home_remedies": ["Stop taking the suspected medication immediately", "Apply cold compress for rashes", "Take antihistamines if prescribed", "Keep a record of the medicine to avoid in future"],
        "diet": ["Drink plenty of water to flush out the system", "Avoid spicy or irritating foods", "Eat simple, bland foods if nauseous"],
        "when_to_visit": True,
        "recovery_days": "1-2 weeks after stopping medication"
    },
    "Peptic ulcer diseae": {
        "severity": "moderate",
        "simple_name": "Peptic Ulcer Disease",
        "description": "Sores that develop on the lining of the stomach, lower esophagus, or small intestine.",
        "home_remedies": ["Avoid NSAID painkillers like ibuprofen", "Eat smaller, more frequent meals", "Manage stress through relaxation techniques", "Don't lie down right after eating"],
        "diet": ["Avoid spicy and acidic foods", "Limit alcohol and caffeine", "Eat foods rich in probiotics like yogurt", "Consume apples, pears, and oatmeal"],
        "when_to_visit": True,
        "recovery_days": "Few weeks with proper medication"
    },
    "AIDS": {
        "severity": "severe",
        "simple_name": "HIV/AIDS",
        "description": "A chronic, potentially life-threatening condition caused by the human immunodeficiency virus (HIV).",
        "home_remedies": ["Strictly follow prescribed Antiretroviral Therapy (ART)", "Practice safe sex", "Avoid infections by washing hands frequently", "Get plenty of rest"],
        "diet": ["High-protein, high-calorie diet to prevent weight loss", "Safe food handling (cook meat thoroughly)", "Take a daily multivitamin", "Drink plenty of clean, filtered water"],
        "when_to_visit": True,
        "recovery_days": "Lifelong condition manageable with ART"
    },
    "Gastroenteritis": {
        "severity": "moderate",
        "simple_name": "Gastroenteritis (Stomach Flu)",
        "description": "Inflammation of the stomach and intestines, usually caused by a viral or bacterial infection.",
        "home_remedies": ["Get plenty of rest", "Sip fluids slowly to stay hydrated", "Use a heating pad for stomach cramps", "Wash hands frequently to prevent spreading"],
        "diet": ["BRAT diet (Bananas, Rice, Applesauce, Toast)", "Drink Oral Rehydration Solutions (ORS)", "Avoid dairy, caffeine, and alcohol", "Eat small, easily digestible meals"],
        "when_to_visit": False,
        "recovery_days": "1-3 days"
    },
    "Bronchial Asthma": {
        "severity": "moderate",
        "simple_name": "Bronchial Asthma",
        "description": "A condition in which your airways narrow and swell and may produce extra mucus.",
        "home_remedies": ["Identify and avoid asthma triggers (dust, smoke, pet dander)", "Always carry your inhaler", "Practice breathing exercises (like pursed lip breathing)", "Keep indoor air clean"],
        "diet": ["Foods rich in Vitamin C and E", "Omega-3 fatty acids (fish, flaxseeds)", "Avoid foods that cause gas or bloating", "Stay hydrated"],
        "when_to_visit": True,
        "recovery_days": "Chronic - manageable with medication"
    },
    "Cervical spondylosis": {
        "severity": "moderate",
        "simple_name": "Cervical Spondylosis (Neck Arthritis)",
        "description": "Age-related wear and tear affecting the spinal disks in your neck.",
        "home_remedies": ["Use a firm mattress and a supportive neck pillow", "Apply heat or ice packs to the neck", "Do gentle neck stretches", "Maintain good posture while sitting and working"],
        "diet": ["Calcium and Vitamin D rich foods", "Anti-inflammatory foods like turmeric and ginger", "Omega-3 rich foods", "Stay hydrated for joint lubrication"],
        "when_to_visit": True,
        "recovery_days": "Ongoing management required"
    },
    "Paralysis (brain hemorrhage)": {
        "severity": "emergency",
        "simple_name": "Paralysis from Brain Hemorrhage",
        "description": "Loss of muscle function due to bleeding in the brain. A medical emergency.",
        "home_remedies": ["Call for emergency medical help IMMEDIATELY", "Do not move the person unless in danger", "Keep the person calm and still", "Do not give them anything to eat or drink"],
        "diet": ["Post-treatment: specialized diet based on swallowing ability (often pureed or soft foods)", "High nutrition for recovery"],
        "when_to_visit": True,
        "recovery_days": "Months to years with intense physiotherapy"
    },
    "Jaundice": {
        "severity": "moderate",
        "simple_name": "Jaundice",
        "description": "Yellowing of the skin and eyes due to high bilirubin levels, often indicating liver issues.",
        "home_remedies": ["Get plenty of bed rest", "Avoid all alcohol", "Do not take unprescribed medicines", "Maintain good hygiene"],
        "diet": ["Drink lots of water and fresh fruit juices (sugarcane, lemon)", "Eat light, easily digestible foods", "Avoid oily, spicy, and heavy meals", "Eat frequent, small meals"],
        "when_to_visit": True,
        "recovery_days": "2-4 weeks depending on the underlying cause"
    },
    "hepatitis A": {
        "severity": "moderate",
        "simple_name": "Hepatitis A",
        "description": "A highly contagious liver infection caused by the hepatitis A virus.",
        "home_remedies": ["Rest extensively", "Practice strict handwashing", "Avoid alcohol completely", "Avoid preparing food for others"],
        "diet": ["Small, frequent meals", "High-carbohydrate, low-fat diet", "Drink plenty of water and clear fluids", "Avoid fatty foods that are hard to digest"],
        "when_to_visit": True,
        "recovery_days": "Few weeks to a few months"
    },
    "Hepatitis B": {
        "severity": "severe",
        "simple_name": "Hepatitis B",
        "description": "A serious liver infection caused by the hepatitis B virus that can become chronic.",
        "home_remedies": ["Get plenty of rest", "Avoid alcohol completely", "Practice safe sex", "Do not share personal care items like razors or toothbrushes"],
        "diet": ["Healthy, balanced diet", "Avoid raw or undercooked shellfish", "Limit fatty foods", "Stay hydrated"],
        "when_to_visit": True,
        "recovery_days": "Varies; can be chronic and require lifelong management"
    },
    "Hepatitis C": {
        "severity": "severe",
        "simple_name": "Hepatitis C",
        "description": "An infection caused by a virus that attacks the liver and leads to inflammation.",
        "home_remedies": ["Avoid alcohol completely", "Check with doctor before taking any supplements or OTC meds", "Get vaccinated against Hep A and B", "Rest as needed"],
        "diet": ["Nutritious, well-balanced diet", "Maintain a healthy weight", "Drink plenty of water", "Avoid overly processed foods"],
        "when_to_visit": True,
        "recovery_days": "8-12 weeks with modern antiviral treatment"
    },
    "Hepatitis D": {
        "severity": "severe",
        "simple_name": "Hepatitis D",
        "description": "A serious liver disease caused by the hepatitis D virus. Only occurs in people who are also infected with the hepatitis B virus.",
        "home_remedies": ["Strictly follow medical advice", "Avoid alcohol entirely", "Rest well", "Protect others from your blood and bodily fluids"],
        "diet": ["Nutrient-dense diet", "Low-fat meals", "Adequate protein intake", "Avoid foods that stress the liver"],
        "when_to_visit": True,
        "recovery_days": "Chronic condition; requires ongoing medical care"
    },
    "Hepatitis E": {
        "severity": "moderate",
        "simple_name": "Hepatitis E",
        "description": "A liver disease caused by the hepatitis E virus, usually transmitted through contaminated drinking water.",
        "home_remedies": ["Rest extensively", "Drink only purified or boiled water", "Maintain proper sanitation", "Avoid alcohol"],
        "diet": ["Light, easily digestible foods", "Avoid fatty and oily foods", "Stay well-hydrated", "Eat frequent small meals"],
        "when_to_visit": True,
        "recovery_days": "4-6 weeks usually self-limiting"
    },
    "Alcoholic hepatitis": {
        "severity": "severe",
        "simple_name": "Alcoholic Hepatitis",
        "description": "Inflammation of the liver caused by drinking alcohol.",
        "home_remedies": ["STOP drinking alcohol immediately and completely", "Join a support group", "Rest well", "Avoid medications that stress the liver"],
        "diet": ["High-calorie, high-protein diet (as malnutrition is common)", "Vitamin and mineral supplements as prescribed", "Small, frequent meals", "Avoid salty foods if fluid retention occurs"],
        "when_to_visit": True,
        "recovery_days": "Varies; requires lifelong abstinence from alcohol"
    },
    "Dimorphic hemmorhoids(piles)": {
        "severity": "moderate",
        "simple_name": "Hemorrhoids (Piles)",
        "description": "Swollen and inflamed veins in the rectum and anus that cause discomfort and bleeding.",
        "home_remedies": ["Take warm sitz baths for 10-15 minutes daily", "Don't strain during bowel movements", "Use over-the-counter hemorrhoid creams", "Keep the anal area clean"],
        "diet": ["High-fiber diet (beans, whole grains, vegetables)", "Drink plenty of water (8-10 glasses)", "Avoid spicy foods that can irritate", "Avoid excessive caffeine"],
        "when_to_visit": True,
        "recovery_days": "1-2 weeks for mild cases"
    },
    "Varicose veins": {
        "severity": "mild",
        "simple_name": "Varicose Veins",
        "description": "Gnarled, enlarged veins, most commonly appearing in the legs and feet.",
        "home_remedies": ["Elevate your legs when resting", "Wear compression stockings", "Avoid standing or sitting for long periods", "Exercise regularly to improve circulation"],
        "diet": ["Low-salt diet to prevent swelling", "Foods rich in rutin (apples, grapes, cherries) to strengthen veins", "High fiber to prevent constipation", "Stay hydrated"],
        "when_to_visit": False,
        "recovery_days": "Chronic condition; managed with lifestyle changes"
    },
    "Hypothyroidism": {
        "severity": "moderate",
        "simple_name": "Hypothyroidism (Underactive Thyroid)",
        "description": "A condition in which the thyroid gland doesn't produce enough crucial hormones.",
        "home_remedies": ["Take prescribed thyroid medication regularly on an empty stomach", "Manage stress", "Get adequate sleep", "Exercise regularly to boost metabolism"],
        "diet": ["Iodine-rich foods if deficient", "Avoid eating large amounts of raw cruciferous vegetables (cabbage, broccoli)", "Ensure adequate selenium (Brazil nuts)", "Balanced diet to prevent weight gain"],
        "when_to_visit": True,
        "recovery_days": "Lifelong condition managed with medication"
    },
    "Hyperthyroidism": {
        "severity": "moderate",
        "simple_name": "Hyperthyroidism (Overactive Thyroid)",
        "description": "A condition in which the thyroid gland produces too much of the hormone thyroxine.",
        "home_remedies": ["Take prescribed medications exactly as directed", "Practice relaxation techniques to manage anxiety", "Avoid strenuous exercise if heart rate is high", "Keep cool environments as you may feel hot easily"],
        "diet": ["Avoid excess iodine (kelp, seaweed)", "Ensure adequate calcium and vitamin D for bone health", "Eat nutrient-dense foods to prevent weight loss", "Limit caffeine to prevent worsening of palpitations"],
        "when_to_visit": True,
        "recovery_days": "Ongoing management required"
    },
    "Hypoglycemia": {
        "severity": "moderate",
        "simple_name": "Hypoglycemia (Low Blood Sugar)",
        "description": "A condition in which your blood sugar (glucose) level is lower than normal.",
        "home_remedies": ["Always carry a fast-acting carb (candy, juice, glucose tablets)", "Check blood sugar if you feel shaky or dizzy", "Don't skip meals", "Be careful when exercising"],
        "diet": ["Follow the 15-15 rule when low: 15g carbs, wait 15 mins", "Eat regular, balanced meals", "Include complex carbs and proteins to stabilize sugars", "Avoid excessive alcohol, especially on an empty stomach"],
        "when_to_visit": True,
        "recovery_days": "Immediate relief after consuming carbs; ongoing management needed"
    },
    "Osteoarthristis": {
        "severity": "moderate",
        "simple_name": "Osteoarthritis",
        "description": "The most common form of arthritis, caused by the wearing down of the protective cartilage on the ends of your bones.",
        "home_remedies": ["Engage in low-impact exercise (swimming, cycling)", "Use hot and cold therapy on painful joints", "Maintain a healthy weight to reduce joint stress", "Use supportive devices or braces if needed"],
        "diet": ["Anti-inflammatory diet", "Foods rich in Omega-3 (fatty fish)", "Vitamin D and calcium for bone health", "Antioxidant-rich fruits and vegetables"],
        "when_to_visit": True,
        "recovery_days": "Chronic condition; managed with lifestyle and treatment"
    },
    "Arthritis": {
        "severity": "moderate",
        "simple_name": "Arthritis",
        "description": "Inflammation of one or more joints, causing pain and stiffness that can worsen with age.",
        "home_remedies": ["Exercise regularly but gently", "Apply heating pads or ice packs", "Try relaxation techniques or massage", "Rest joints when they are swollen or inflamed"],
        "diet": ["Mediterranean-style diet", "Eat plenty of fish, nuts, and seeds", "Reduce processed foods and red meat", "Use olive oil instead of butter"],
        "when_to_visit": True,
        "recovery_days": "Chronic condition; manageable"
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "severity": "moderate",
        "simple_name": "Vertigo (BPPV)",
        "description": "A sudden sensation that you're spinning or that the inside of your head is spinning, triggered by certain head movements.",
        "home_remedies": ["Sit down immediately when you feel dizzy", "Move your head slowly and carefully", "Sleep with your head slightly elevated", "Avoid bending over to pick things up"],
        "diet": ["Stay well-hydrated", "Avoid excess salt which can cause fluid retention in the inner ear", "Limit caffeine and alcohol", "Adequate Vitamin D"],
        "when_to_visit": True,
        "recovery_days": "Often resolves in a few weeks or months"
    },
    "Acne": {
        "severity": "mild",
        "simple_name": "Acne",
        "description": "A skin condition that occurs when your hair follicles become plugged with oil and dead skin cells.",
        "home_remedies": ["Wash your face twice daily with a gentle cleanser", "Don't pop or squeeze pimples", "Use non-comedogenic makeup and lotions", "Shower after heavy sweating"],
        "diet": ["Limit dairy and high-glycemic foods (sugar, white bread)", "Eat zinc-rich foods (beans, nuts)", "Stay hydrated", "Eat foods rich in antioxidants"],
        "when_to_visit": False,
        "recovery_days": "Continuous management"
    },
    "Urinary tract infection": {
        "severity": "moderate",
        "simple_name": "Urinary Tract Infection (UTI)",
        "description": "An infection in any part of your urinary system — your kidneys, ureters, bladder and urethra.",
        "home_remedies": ["Drink plenty of water to flush bacteria", "Use a heating pad for pelvic pain", "Urinate when you feel the need; don't hold it", "Wipe from front to back"],
        "diet": ["Drink unsweetened cranberry juice", "Avoid bladder irritants like coffee, alcohol, and spicy foods", "Eat probiotic-rich foods like yogurt", "Increase Vitamin C intake"],
        "when_to_visit": True,
        "recovery_days": "3-7 days with antibiotics"
    },
    "Psoriasis": {
        "severity": "moderate",
        "simple_name": "Psoriasis",
        "description": "A skin disease that causes red, itchy scaly patches, most commonly on the knees, elbows, trunk and scalp.",
        "home_remedies": ["Take daily baths with oatmeal or Epsom salts", "Moisturize skin heavily right after bathing", "Expose skin to small amounts of sunlight", "Avoid psoriasis triggers (stress, skin injuries)"],
        "diet": ["Anti-inflammatory diet", "Omega-3 fatty acids", "Maintain a healthy weight", "Limit alcohol, which can trigger flare-ups"],
        "when_to_visit": True,
        "recovery_days": "Chronic condition with flare-ups"
    },
    "Impetigo": {
        "severity": "mild",
        "simple_name": "Impetigo",
        "description": "A highly contagious skin infection that mainly affects infants and children, appearing as red sores on the face.",
        "home_remedies": ["Keep the sores clean and covered", "Wash the affected area gently with mild soap", "Wash the person's clothes and towels daily and don't share them", "Cut nails short to prevent scratching"],
        "diet": ["Nutritious diet to boost the immune system", "Adequate hydration", "Foods rich in Vitamin C and Zinc", "Avoid sugary foods that might impair immunity"],
        "when_to_visit": True,
        "recovery_days": "7-10 days with treatment"
    }
}

SEVERE_DISEASES = [
    'Heart attack', 'Dengue', 'Malaria', 'Typhoid', 'Pneumonia', 'Tuberculosis',
    'Paralysis (brain hemorrhage)', 'hepatitis A', 'Hepatitis B', 'Hepatitis C'
]

_EXTRA_DISEASE_INFO = {
    "Flu": {
        "severity": "mild", "simple_name": "Influenza (Flu)",
        "description": "A viral respiratory illness more intense than a common cold. Comes on suddenly.",
        "home_remedies": ["Rest completely", "Drink warm fluids — kadha, ginger tea", "Paracetamol for fever and body pain", "Steam inhalation twice daily", "Gargle warm salt water"],
        "diet": ["Warm soups and broths", "Ginger-honey-lemon tea", "Vitamin C foods: amla, guava, orange", "Avoid cold foods and drinks"],
        "when_to_visit": False, "recovery_days": "5-7 days"
    },
    "COVID-19": {
        "severity": "moderate", "simple_name": "COVID-19",
        "description": "A respiratory illness caused by the SARS-CoV-2 virus. Ranges from mild to severe.",
        "home_remedies": ["Isolate immediately", "Rest and stay hydrated", "Paracetamol for fever", "Monitor oxygen with pulse oximeter", "Steam inhalation for breathing comfort"],
        "diet": ["High vitamin C foods", "Warm soups and liquids", "Zinc-rich foods: pumpkin seeds, dal", "Avoid cold drinks"],
        "when_to_visit": True, "recovery_days": "10-14 days"
    },
    "Food Poisoning": {
        "severity": "moderate", "simple_name": "Food Poisoning",
        "description": "Illness caused by eating contaminated food. Usually resolves in 1-2 days.",
        "home_remedies": ["Sip ORS constantly to prevent dehydration", "Rest and avoid solid food for a few hours", "Start BRAT diet when ready", "Avoid dairy, spicy, oily foods"],
        "diet": ["Bananas, Rice, Applesauce, Toast (BRAT)", "ORS sachets (Electral)", "Coconut water for electrolytes", "Avoid dairy, caffeine, alcohol"],
        "when_to_visit": False, "recovery_days": "1-3 days"
    },
    "IBS": {
        "severity": "mild", "simple_name": "Irritable Bowel Syndrome (IBS)",
        "description": "A common gut disorder causing cramps, bloating, and altered bowel habits.",
        "home_remedies": ["Identify and avoid trigger foods", "Eat smaller meals", "Manage stress with yoga or meditation", "Keep a food and symptom diary"],
        "diet": ["Low-FODMAP diet recommended", "Avoid beans, cabbage, onion, fizzy drinks", "Eat soluble fiber: oats, bananas", "Probiotics: yogurt, curd"],
        "when_to_visit": False, "recovery_days": "Chronic — manageable with diet"
    },
    "Anemia": {
        "severity": "moderate", "simple_name": "Anemia (Low Blood Count)",
        "description": "Your blood has too few red blood cells or not enough hemoglobin.",
        "home_remedies": ["Take prescribed iron supplements", "Eat iron-rich foods daily", "Get enough Vitamin C (helps iron absorption)", "Rest when fatigued", "Avoid tea/coffee with meals"],
        "diet": ["Iron-rich: spinach, dal, beetroot, dates, meat", "Vitamin C: amla, lemon, orange", "Avoid tea/coffee immediately after iron-rich meals", "Pomegranate juice daily"],
        "when_to_visit": True, "recovery_days": "Weeks to months with treatment"
    },
    "Sinusitis": {
        "severity": "mild", "simple_name": "Sinusitis (Sinus Infection)",
        "description": "Inflammation of the sinuses causing pain, pressure, and nasal congestion.",
        "home_remedies": ["Steam inhalation 3x daily", "Warm compress over face", "Saline nasal rinse (Jal Neti)", "Stay well hydrated", "Avoid cold air and allergens"],
        "diet": ["Warm soups and broths", "Ginger and turmeric tea", "Spicy food can help open sinuses", "Avoid dairy (may thicken mucus)", "Drink 10+ glasses warm water"],
        "when_to_visit": False, "recovery_days": "7-10 days"
    },
    "Anxiety Disorder": {
        "severity": "moderate", "simple_name": "Anxiety Disorder",
        "description": "Persistent, excessive worry that interferes with daily activities.",
        "home_remedies": ["Deep breathing: inhale 4, hold 4, exhale 6", "Exercise — 30 min daily walk significantly helps", "Limit caffeine and alcohol", "Talk to someone you trust", "Practice mindfulness or meditation"],
        "diet": ["Magnesium-rich foods: leafy greens, nuts", "Omega-3: fish, flaxseed", "Avoid caffeine and energy drinks", "Chamomile tea helps calm nerves"],
        "when_to_visit": True, "recovery_days": "Ongoing — therapy is very effective"
    },
    "Depression": {
        "severity": "moderate", "simple_name": "Depression",
        "description": "A mood disorder causing persistent sadness and loss of interest.",
        "home_remedies": ["Talk to a mental health professional", "Exercise daily — proven mood booster", "Maintain a sleep routine", "Stay socially connected", "Limit alcohol and avoid drugs"],
        "diet": ["Omega-3 fatty acids: fish, walnuts, flaxseed", "Folate-rich foods: leafy greens, lentils", "Avoid processed sugar and alcohol", "Dark chocolate in moderation can help mood"],
        "when_to_visit": True, "recovery_days": "Weeks to months with proper support"
    },
    "Dehydration": {
        "severity": "mild", "simple_name": "Dehydration",
        "description": "Your body loses more fluid than you take in. Common in heat, illness, or exercise.",
        "home_remedies": ["Drink ORS immediately", "Sip water frequently — don't gulp", "Coconut water for electrolytes", "Avoid caffeine and alcohol", "Rest in a cool place"],
        "diet": ["ORS (Electral sachets)", "Coconut water", "Nimbu paani with salt and sugar", "Fruits with high water content: watermelon, cucumber"],
        "when_to_visit": False, "recovery_days": "Hours with proper hydration"
    },
    "Back Pain": {
        "severity": "mild", "simple_name": "Back Pain",
        "description": "Pain in the lower, middle, or upper back. Usually muscular in origin.",
        "home_remedies": ["Cold pack first 48 hours, then warm pack", "Ibuprofen gel or tablets (after food)", "Avoid bed rest — gentle movement helps", "Correct sitting posture", "Gentle yoga stretches"],
        "diet": ["Anti-inflammatory foods: turmeric, ginger", "Calcium and Vitamin D for bone health", "Stay hydrated for disc health", "Magnesium-rich foods: spinach, nuts"],
        "when_to_visit": False, "recovery_days": "Days to weeks"
    },
    "Vertigo": {
        "severity": "mild", "simple_name": "Vertigo (Dizziness/Spinning)",
        "description": "A feeling that you or your surroundings are spinning. Usually inner-ear related.",
        "home_remedies": ["Sit or lie down immediately when dizzy", "Move head slowly and carefully", "Epley maneuver (see YouTube) helps BPPV", "Sleep with head slightly elevated", "Avoid sudden head movements"],
        "diet": ["Low-salt diet (reduces inner ear fluid)", "Stay hydrated", "Avoid caffeine and alcohol", "Adequate Vitamin D"],
        "when_to_visit": True, "recovery_days": "Days to weeks — Epley maneuver often cures BPPV"
    },
    "Meningitis": {
        "severity": "emergency", "simple_name": "Meningitis",
        "description": "EMERGENCY: Inflammation of the brain and spinal cord lining. Needs immediate hospital care.",
        "home_remedies": ["CALL 108 IMMEDIATELY", "Do not wait — this is life-threatening", "Keep person calm and still", "Go to nearest hospital NOW"],
        "diet": ["Hospital care required"],
        "when_to_visit": True, "recovery_days": "Emergency — immediate hospitalization needed"
    },
    "COPD": {
        "severity": "severe", "simple_name": "COPD (Chronic Lung Disease)",
        "description": "A chronic lung disease that makes it hard to breathe. Mainly caused by smoking.",
        "home_remedies": ["Quit smoking — the single most important step", "Pulmonary rehabilitation exercises", "Use prescribed inhalers correctly", "Avoid air pollutants and smoke", "Get flu vaccine annually"],
        "diet": ["High-calorie, high-protein diet (many lose weight)", "Small, frequent meals (big meals worsen breathlessness)", "Stay hydrated to thin mucus", "Avoid gassy foods that push on diaphragm"],
        "when_to_visit": True, "recovery_days": "Chronic — managed with medication"
    },
    "Kidney Stone": {
        "severity": "severe", "simple_name": "Kidney Stone",
        "description": "Hard deposits in the kidneys causing severe pain when passing through urinary tract.",
        "home_remedies": ["Drink lots of water (3+ liters daily)", "Pain relief: ibuprofen or diclofenac", "Walk — movement helps stone pass", "Hot water bottle on back/side for pain", "Strain urine to catch the stone"],
        "diet": ["Drink 3+ liters water daily — most important!", "Reduce oxalate foods: spinach, nuts, tea", "Limit salt and animal protein", "Lemon water (citrate prevents stones)", "Avoid dehydration"],
        "when_to_visit": True, "recovery_days": "Days to weeks; large stones need medical procedure"
    },
    "Stroke": {
        "severity": "emergency", "simple_name": "Stroke",
        "description": "EMERGENCY: Blood supply to brain is cut off. Use FAST: Face drooping, Arm weakness, Speech slurred, Time to call 108!",
        "home_remedies": ["CALL 108 IMMEDIATELY", "Note the time symptoms started — critical for treatment", "Lay person on their side if vomiting", "Do NOT give food/water", "Every minute counts — don't wait!"],
        "diet": ["Hospital care required immediately"],
        "when_to_visit": True, "recovery_days": "Emergency — immediate hospitalization needed"
    },
    "Appendicitis": {
        "severity": "emergency", "simple_name": "Appendicitis",
        "description": "EMERGENCY: Inflammation of the appendix. Needs immediate surgery.",
        "home_remedies": ["CALL 108 IMMEDIATELY", "Do NOT eat or drink anything", "Do NOT take painkillers — masks symptoms", "Go to hospital NOW", "Do NOT apply heat to abdomen"],
        "diet": ["Hospital care required — nothing by mouth"],
        "when_to_visit": True, "recovery_days": "Emergency surgery — recovery 2-4 weeks"
    },
    "Measles": {
        "severity": "moderate", "simple_name": "Measles",
        "description": "A highly contagious viral disease causing fever and widespread rash.",
        "home_remedies": ["Isolate completely — very contagious", "Rest and stay hydrated", "Paracetamol for fever", "Vitamin A supplements (reduces complications)", "Cool damp cloth for rash comfort"],
        "diet": ["Soft, easily digestible foods", "Plenty of fluids", "Vitamin A: carrots, sweet potato", "Avoid strong light (eyes are sensitive)"],
        "when_to_visit": True, "recovery_days": "7-10 days"
    },
    "Scabies": {
        "severity": "mild", "simple_name": "Scabies",
        "description": "A skin infestation by tiny mites causing intense itching, especially at night.",
        "home_remedies": ["Use prescribed permethrin cream all over body", "Wash all clothes/bedding in hot water", "All household members should be treated", "Trim nails to avoid skin damage from scratching", "Antihistamine for itch relief"],
        "diet": ["Eat immune-boosting foods", "Stay hydrated", "No specific dietary restriction"],
        "when_to_visit": True, "recovery_days": "2-4 weeks with treatment"
    },
    "Conjunctivitis": {
        "severity": "mild", "simple_name": "Conjunctivitis (Pink Eye)",
        "description": "Inflammation of the eye's outer layer causing redness, discharge, and itching.",
        "home_remedies": ["Clean eye with clean cotton dipped in warm water", "Don't rub eyes", "Don't share towels — very contagious", "Antibiotic eye drops if bacterial (see pharmacist)", "Cold compress for relief"],
        "diet": ["Vitamin A rich foods for eye health", "Stay hydrated", "Avoid eye strain from screens"],
        "when_to_visit": False, "recovery_days": "5-7 days"
    },
    "Hyperthyroidism": {
        "severity": "moderate", "simple_name": "Hyperthyroidism (Overactive Thyroid)",
        "description": "The thyroid gland produces too much hormone, speeding up body functions.",
        "home_remedies": ["Take medications exactly as prescribed", "Avoid strenuous exercise if heart rate is high", "Stay in cool environments", "Manage stress with relaxation techniques", "Wear sunglasses (eye sensitivity common)"],
        "diet": ["Avoid excess iodine: kelp, seaweed", "Calcium and Vitamin D for bone health", "Nutrient-dense foods to prevent weight loss", "Limit caffeine — worsens palpitations"],
        "when_to_visit": True, "recovery_days": "Ongoing management required"
    },
    "Hypothyroidism": {
        "severity": "moderate", "simple_name": "Hypothyroidism (Underactive Thyroid)",
        "description": "The thyroid gland doesn't produce enough hormone, slowing body functions.",
        "home_remedies": ["Take thyroid medication every morning on empty stomach", "Exercise regularly to boost metabolism", "Get adequate sleep", "Manage stress", "Regular TSH blood tests"],
        "diet": ["Iodine-rich foods if deficient: iodized salt, seafood", "Selenium: Brazil nuts", "Limit raw cruciferous vegetables (cabbage, broccoli)", "Balanced diet to manage weight"],
        "when_to_visit": True, "recovery_days": "Lifelong condition managed with medication"
    },
}

for _k, _v in _EXTRA_DISEASE_INFO.items():
    if _k not in DISEASE_INFO:
        DISEASE_INFO[_k] = _v

def normalize_disease_name(name):
    if not name:
        return name
    name_clean = str(name).strip().lower()
    
    # Map synonyms / mismatches
    mapping = {
        "gerd": "GERD",
        "acid reflux": "GERD",
        "acid reflux (heartburn disease)": "GERD",
        "bronchial asthma": "Asthma",
        "asthma": "Asthma",
        "diabetes": "Diabetes",
        "diabetes ": "Diabetes",
        "hypertension": "Hypertension",
        "hypertension ": "Hypertension",
        "chicken pox": "Chickenpox",
        "chickenpox": "Chickenpox",
        "peptic ulcer diseae": "Peptic Ulcer",
        "peptic ulcer": "Peptic Ulcer",
        "peptic ulcer disease": "Peptic Ulcer",
        "(vertigo) paroymsal  positional vertigo": "Vertigo",
        "vertigo (dizziness/spinning)": "Vertigo",
        "vertigo": "Vertigo",
        "urinary tract infection": "Urinary Tract Infection",
        "influenza (flu)": "Flu",
        "flu": "Flu",
        "irritable bowel syndrome (ibs)": "IBS",
        "ibs": "IBS",
        "anemia (low blood count)": "Anemia",
        "anemia": "Anemia",
        "sinusitis (sinus infection)": "Sinusitis",
        "sinusitis": "Sinusitis",
        "anxiety disorder": "Anxiety Disorder",
        "dehydration": "Dehydration"
    }
    
    # Check exact normalized map
    if name_clean in mapping:
        return mapping[name_clean]
        
    # Check if name is simple_name of any key in DISEASE_INFO
    # or case-insensitive key matches
    for k, v in DISEASE_INFO.items():
        if k.lower() == name_clean:
            return k
        simple = v.get("simple_name", "").lower()
        if simple and (name_clean in simple or simple in name_clean):
            return k
            
    return name

def _load_csv_datasets():
    script_dir = Path(__file__).resolve().parent
    for base in [script_dir / "../data", script_dir, script_dir / "..", script_dir / "Data"]:
        train_path = base / "Training.csv"
        test_path = base / "Testing.csv"
        if test_path.exists():
            try:
                df_test = pd.read_csv(test_path)
                df_train = pd.read_csv(train_path) if train_path.exists() else df_test
                return df_train, df_test
            except Exception:
                pass
    return None, None

def get_diet_plan(user_profile, condition=None):
    if condition:
        condition = normalize_disease_name(condition)
    age = user_profile.get("age", 30)
    weight = user_profile.get("weight", 70)
    height = user_profile.get("height", 170)
    gender = user_profile.get("gender", "Male")
    
    bmi = weight / ((height/100)**2) if height > 0 else 22
    
    if bmi < 18.5: bmi_cat = "Underweight"
    elif bmi < 25: bmi_cat = "Normal"
    elif bmi < 30: bmi_cat = "Overweight"
    else: bmi_cat = "Obese"

    # Calculate calories
    if gender == "Male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    calories = int(bmr * 1.4)
    
    plan = {
        "bmi": round(bmi, 1),
        "bmi_category": bmi_cat,
        "daily_calories": calories,
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": [],
        "water": "8-10 glasses daily",
        "avoid": []
    }
    
    if bmi_cat == "Underweight":
        plan["breakfast"] = ["Paratha with ghee + milk + banana", "Poha with peanuts + lassi"]
        plan["lunch"] = ["Rice + dal + sabzi + curd + roti", "Rajma chawal + salad"]
        plan["dinner"] = ["Paneer sabzi + roti + dal soup", "Egg curry + rice + vegetables"]
        plan["snacks"] = ["Banana + peanut butter", "Chikki (peanut brittle)", "Dry fruits + milk"]
        plan["avoid"] = ["Skipping meals", "Too much junk food"]
        plan["goal"] = "Gain 0.5-1 kg per week"
    elif bmi_cat == "Normal":
        plan["breakfast"] = ["Oats with fruits + milk", "Idli sambar + coconut chutney"]
        plan["lunch"] = ["Roti + dal + mixed sabzi + salad", "Brown rice + fish/chicken curry + vegetables"]
        plan["dinner"] = ["Khichdi + curd + salad", "Roti + paneer/chicken sabzi + dal"]
        plan["snacks"] = ["Handful of mixed nuts", "Seasonal fruits", "Sprouts chaat"]
        plan["avoid"] = ["Processed foods", "Excess sugar", "Late night eating"]
        plan["goal"] = "Maintain current weight"
    elif bmi_cat == "Overweight":
        plan["breakfast"] = ["Moong dal chilla + mint chutney", "Vegetable oats upma + green tea"]
        plan["lunch"] = ["Small roti + lots of sabzi + dal + salad", "Brown rice (small) + grilled chicken/paneer + vegetables"]
        plan["dinner"] = ["Soup + salad + small portion roti", "Dal + vegetables (no rice at night)"]
        plan["snacks"] = ["Cucumber slices with hummus", "Roasted chana", "Green tea"]
        plan["avoid"] = ["White rice, maida products", "Fried foods, sweets", "Sugary drinks"]
        plan["goal"] = "Lose 0.5 kg per week"
    else:
        plan["breakfast"] = ["Vegetable clear soup + 1 toast", "Sprouts with lemon + black tea"]
        plan["lunch"] = ["Lots of salad + small dal + 1 roti", "Steamed vegetables + grilled protein"]
        plan["dinner"] = ["Vegetable soup + 1 chapati", "Palak paneer (small) + salad"]
        plan["snacks"] = ["Cucumber, tomato slices", "Green tea", "Buttermilk"]
        plan["avoid"] = ["Rice, fried foods, sweets, alcohol", "White bread, pasta", "Full-fat dairy"]
        plan["goal"] = "Lose 1 kg per week under medical guidance"

    if condition in DISEASE_INFO:
        d = DISEASE_INFO[condition]
        plan["notes"] = d.get("diet", [])
        severity = d.get("severity", "mild")
        
        # Modify the diet heavily for moderate/severe/emergency conditions
        if severity in ["moderate", "severe", "emergency"]:
            diet_items = d.get("diet", [])
            plan["goal"] = f"Prioritize recovery from {d.get('simple_name', condition)}"
            plan["avoid"].extend(["Spicy foods", "Oily/fried foods", "Heavy/large meals", "Alcohol", "Caffeine"])
            
            # Extract foods to eat vs foods to avoid from the condition's diet info
            eat_tips = [tip for tip in diet_items if "avoid" not in tip.lower() and "limit" not in tip.lower()]
            avoid_tips = [tip for tip in diet_items if "avoid" in tip.lower() or "limit" in tip.lower()]
            
            plan["avoid"].extend(avoid_tips)
            
            plan["breakfast"] = [
                eat_tips[0] if len(eat_tips) > 0 else "Easily digestible light food (e.g., oatmeal or porridge)",
                "Warm fluids / Herbal tea"
            ]
            plan["lunch"] = [
                eat_tips[1] if len(eat_tips) > 1 else "Soft boiled vegetables and khichdi/rice",
                eat_tips[2] if len(eat_tips) > 2 else "Clear soup or dal"
            ]
            plan["dinner"] = [
                eat_tips[3] if len(eat_tips) > 3 else "Very light meal (e.g., vegetable soup, boiled moong dal)",
                "Easily digestible food to ensure restful sleep"
            ]
            plan["snacks"] = [
                "ORS / Coconut water (stay hydrated)",
                eat_tips[4] if len(eat_tips) > 4 else "Fresh fruits (if allowed)"
            ]
    
    return plan


_TRAIN_DATA = [
    # Flu / Common Cold
    ("fever cough runny nose chills fatigue body ache", "Flu"),
    ("high fever sore throat runny nose sneezing headache", "Flu"),
    ("fever body pain chills sweating fatigue", "Flu"),
    ("cold cough sneezing runny nose sore throat", "Common Cold"),
    ("runny nose blocked nose sneezing mild fever cough", "Common Cold"),
    ("sore throat runny nose mild cough sneezing", "Common Cold"),
    # Dengue
    ("high fever severe headache joint pain rash eye pain fatigue", "Dengue"),
    ("sudden high fever rash behind eyes joint pain muscle pain", "Dengue"),
    ("fever rash joint pain bleeding gums fatigue vomiting", "Dengue"),
    # Malaria
    ("high fever chills sweating headache nausea vomiting", "Malaria"),
    ("cyclic fever chills headache muscle pain fatigue", "Malaria"),
    ("fever shivering sweating body pain fatigue", "Malaria"),
    # Typhoid
    ("prolonged fever stomach pain constipation headache weakness", "Typhoid"),
    ("high fever abdominal pain diarrhea loss of appetite fatigue", "Typhoid"),
    ("fever headache stomach ache weakness loss of appetite", "Typhoid"),
    # Pneumonia
    ("chest pain fever cough breathlessness chills fatigue", "Pneumonia"),
    ("high fever cough chest pain difficulty breathing sweating", "Pneumonia"),
    ("cough with phlegm fever breathlessness chest pain", "Pneumonia"),
    # COVID-19
    ("fever cough loss of smell fatigue breathlessness", "COVID-19"),
    ("dry cough fever fatigue loss of taste loss of smell", "COVID-19"),
    ("high fever breathlessness chest pain fatigue body ache", "COVID-19"),
    # Gastroenteritis
    ("stomach pain nausea vomiting diarrhea fever cramps", "Gastroenteritis"),
    ("vomiting diarrhea abdominal pain dehydration fatigue", "Gastroenteritis"),
    ("loose motions stomach pain nausea vomiting weakness", "Gastroenteritis"),
    # Food Poisoning
    ("nausea vomiting diarrhea stomach cramps fever", "Food Poisoning"),
    ("vomiting stomach pain diarrhea sweating nausea", "Food Poisoning"),
    ("sudden vomiting loose stool abdominal cramps weakness", "Food Poisoning"),
    # Migraine
    ("severe headache nausea light sensitivity vomiting throbbing", "Migraine"),
    ("one-sided headache nausea vomiting visual disturbance", "Migraine"),
    ("pulsating headache sensitivity to light sound nausea", "Migraine"),
    # Hypertension
    ("headache dizziness blurred vision chest pain fatigue", "Hypertension"),
    ("severe headache palpitations shortness of breath dizziness", "Hypertension"),
    ("headache neck pain dizziness blurred vision nausea", "Hypertension"),
    # Diabetes
    ("frequent urination excessive thirst fatigue blurred vision", "Diabetes"),
    ("weight loss frequent urination slow healing wounds fatigue", "Diabetes"),
    ("thirst frequent urination weakness fatigue numbness feet", "Diabetes"),
    # Anemia
    ("weakness fatigue dizziness pale skin shortness of breath", "Anemia"),
    ("fatigue headache dizziness cold hands feet pale skin", "Anemia"),
    ("tiredness weakness pale skin rapid heartbeat dizziness", "Anemia"),
    # Asthma
    ("wheezing chest tightness breathlessness cough night", "Asthma"),
    ("difficulty breathing chest tightness wheezing cough", "Asthma"),
    ("breathlessness coughing wheezing tightness chest", "Asthma"),
    # Tuberculosis
    ("persistent cough blood sputum night sweats weight loss fatigue", "Tuberculosis"),
    ("chronic cough chest pain night sweats weight loss fever", "Tuberculosis"),
    ("coughing blood night sweats weight loss fatigue weakness", "Tuberculosis"),
    # Jaundice
    ("yellow skin yellow eyes dark urine fatigue itching", "Jaundice"),
    ("yellowish skin eyes abdominal pain nausea fatigue", "Jaundice"),
    ("yellow eyes skin dark urine pale stool loss appetite", "Jaundice"),
    # UTI
    ("burning urination frequent urination pelvic pain fever", "Urinary Tract Infection"),
    ("painful urination frequency urgency cloudy urine fever", "Urinary Tract Infection"),
    ("burning pee frequent urination back pain fever chills", "Urinary Tract Infection"),
    # Acid Reflux / GERD
    ("heartburn chest burning indigestion bloating acidity", "Acid Reflux"),
    ("sour taste mouth burning chest after eating bloating", "Acid Reflux"),
    ("acid regurgitation heartburn nausea chest discomfort", "Acid Reflux"),
    # Irritable Bowel Syndrome
    ("abdominal pain bloating diarrhea constipation gas cramps", "IBS"),
    ("stomach cramps bloating alternating diarrhea constipation", "IBS"),
    ("bloating gas stomach pain loose stool constipation", "IBS"),
    # Heart Attack
    ("crushing chest pain left arm pain sweating breathlessness nausea", "Heart Attack"),
    ("severe chest pain radiating arm jaw sweating dizzy", "Heart Attack"),
    ("chest tightness pain arm neck sweating nausea breathless", "Heart Attack"),
    # Stroke
    ("sudden numbness face arm leg confusion speech difficulty", "Stroke"),
    ("sudden weakness one side face drooping speech slurred", "Stroke"),
    ("sudden severe headache vision loss balance problem weakness", "Stroke"),
    # Appendicitis
    ("lower right abdominal pain nausea fever vomiting", "Appendicitis"),
    ("sharp pain lower right abdomen fever nausea loss appetite", "Appendicitis"),
    ("abdominal pain right side fever vomiting rebound tenderness", "Appendicitis"),
    # Kidney Stone
    ("severe back pain side pain urination pain blood urine", "Kidney Stone"),
    ("sharp flank pain nausea vomiting frequent urination blood urine", "Kidney Stone"),
    ("severe pain back groin nausea vomiting painful urination", "Kidney Stone"),
    # Arthritis
    ("joint pain swelling stiffness morning stiffness fatigue", "Arthritis"),
    ("swollen joints pain stiffness reduced movement fatigue", "Arthritis"),
    ("joint inflammation pain stiffness warmth swelling", "Arthritis"),
    # Anxiety Disorder
    ("anxiety panic rapid heartbeat sweating trembling restlessness", "Anxiety Disorder"),
    ("excessive worry panic attack chest tightness breathlessness", "Anxiety Disorder"),
    ("nervousness restlessness palpitations sweating headache", "Anxiety Disorder"),
    # Depression
    ("sadness hopelessness fatigue loss interest sleep problems", "Depression"),
    ("low mood no motivation fatigue sleep change appetite change", "Depression"),
    ("persistent sadness worthlessness fatigue concentration loss", "Depression"),
    # Chickenpox
    ("itchy rash blisters fever headache fatigue loss appetite", "Chickenpox"),
    ("blister rash fever itching headache tiredness", "Chickenpox"),
    ("rash blisters all body fever itching fatigue", "Chickenpox"),
    # Measles
    ("high fever rash cough runny nose red eyes koplik spots", "Measles"),
    ("fever rash starts face spreads body cough red eyes", "Measles"),
    ("high fever rash cough cold sensitivity light", "Measles"),
    # Meningitis
    ("stiff neck high fever severe headache vomiting sensitivity light", "Meningitis"),
    ("neck stiffness fever headache photophobia nausea rash", "Meningitis"),
    ("severe headache stiff neck fever vomiting confusion rash", "Meningitis"),
    # Hyperthyroidism
    ("weight loss rapid heartbeat sweating nervousness heat intolerance", "Hyperthyroidism"),
    ("anxiety palpitations weight loss tremor sweating", "Hyperthyroidism"),
    ("increased heartbeat weight loss nervousness sweating insomnia", "Hyperthyroidism"),
    # Hypothyroidism
    ("weight gain fatigue cold intolerance constipation dry skin", "Hypothyroidism"),
    ("weight gain tiredness depression hair loss constipation cold", "Hypothyroidism"),
    ("fatigue weight gain constipation dry skin slow heart rate", "Hypothyroidism"),
    # Sinusitis
    ("facial pain nasal congestion headache thick discharge fever", "Sinusitis"),
    ("sinus pressure headache blocked nose facial pain post nasal", "Sinusitis"),
    ("stuffy nose facial pressure headache loss smell discharge", "Sinusitis"),
    # Allergic Reaction
    ("hives itching rash swelling sneezing runny nose", "Allergic Reaction"),
    ("skin rash itching redness swelling watery eyes sneezing", "Allergic Reaction"),
    ("allergic rash hives swelling itching runny nose", "Allergic Reaction"),
    # COPD
    ("chronic cough breathlessness wheezing mucus production fatigue", "COPD"),
    ("long term cough difficulty breathing chest tightness mucus", "COPD"),
    ("breathlessness cough phlegm chest tightness fatigue", "COPD"),
    # Peptic Ulcer
    ("burning stomach pain hunger pain nausea vomiting blood stool", "Peptic Ulcer"),
    ("stomach ache worse empty burning nausea dark stool", "Peptic Ulcer"),
    ("upper abdominal burning pain nausea heartburn dark stool", "Peptic Ulcer"),
    # Hepatitis
    ("yellow skin fatigue nausea abdominal pain dark urine fever", "Hepatitis"),
    ("jaundice fatigue loss appetite nausea vomiting abdominal pain", "Hepatitis"),
    ("yellowish eyes skin fatigue nausea dark urine fever", "Hepatitis"),
    # Scabies
    ("intense itching rash between fingers wrists worse night", "Scabies"),
    ("itching rash skin burrows worse at night", "Scabies"),
    # Conjunctivitis
    ("red eyes discharge itching watering light sensitivity", "Conjunctivitis"),
    ("pink eye redness itching discharge tears", "Conjunctivitis"),
    # Back Pain
    ("lower back pain stiffness muscle spasm radiating leg pain", "Back Pain"),
    ("back ache stiffness difficulty standing walking pain leg", "Back Pain"),
    # Vertigo
    ("dizziness spinning sensation nausea balance loss", "Vertigo"),
    ("room spinning vertigo nausea vomiting balance problem", "Vertigo"),
    # Dehydration
    ("excessive thirst dry mouth dark urine dizziness fatigue", "Dehydration"),
    ("thirst dizziness weakness dark urine headache fatigue", "Dehydration"),
]

SYMPTOM_KEYWORDS = {
    # ── Fever ──────────────────────────────────────────────────────────────────
    "fever": [
        "fever","temperature","bukhar","bukhaar","buhkar","fevar","fiver","fevr","pyrexia",
        "tez bukhar","body hot","feeling hot","hot body","body temperature","temp high",
        "i have fever","got fever","running temperature","having fever","mujhe bukhar hai",
        "bukhar aa gaya","bukhar hai","body burning","burning up","feel warm","body warm",
        "slight fever","mild fever","low grade fever","low fever","subfebril",
    ],
    "high_fever": [
        "high fever","very high fever","tez bukhar","bahut tez bukhar","105","104","103",
        "103 fever","104 fever","105 fever","very high temperature","burning fever",
        "extreme fever","fever 103","fever 104","fever 105","fever above 103",
    ],
    # ── Cold / Cough / Throat ───────────────────────────────────────────────────
    "cough": [
        "cough","khansi","khaansi","khasi","caugh","cof","coughing","dry cough","wet cough",
        "cough all night","cough at night","cant stop coughing","persistent cough",
        "chesty cough","productive cough","phlegm","balgam","mucus cough","khasi ho rahi",
        "khansi ho rahi hai","khansi aa rahi","i am coughing","cough nahi ruk raha",
        "khansi nahi ruk rahi","keep coughing","cough problem",
    ],
    "cold": [
        "cold","sardi","sardi ho gayi","common cold","nasal","sardi lagna","thanda",
        "sardi aa gayi","sardi lag gayi","i have cold","mujhe sardi hai","caught a cold",
        "cold and cough","got cold","runny nose and cough","naak behna","nose behna",
        "nasal infection","catarrh",
    ],
    "runny_nose": [
        "runny nose","naak behna","nasal discharge","stuffy nose","blocked nose",
        "nose running","nasal congestion","naak jam gayi","naak band","blocked nasal",
        "nose blocked","naak se paani","watery nose","dripping nose","naak behta hai",
        "nose dripping","post nasal drip","nose full","naak full",
    ],
    "sore_throat": [
        "sore throat","gale mein dard","throat pain","swallowing pain","throat hurts",
        "gala dard","throat ache","sore throut","gale mein kharash","kharash","gala kharab",
        "throat infection","tonsils","tonsillitis","gale mein jalan","gala sookh raha",
        "dry throat","throat dry","i have throat pain","gala dukh raha hai","gala dard hai",
        "pain while swallowing","hurts to swallow","difficulty swallowing","dysphagia",
    ],
    "sneezing": [
        "sneeze","sneezing","chaank","aachoo","continuous sneezing","cant stop sneezing",
        "keep sneezing","sneezing a lot","frequent sneezing","bari bari chaank","baar baar chaank",
        "allergic sneezing","sneezing and runny nose","hay fever",
    ],
    # ── Head / Neuro ───────────────────────────────────────────────────────────
    "headache": [
        "headache","head pain","sir dard","migraine","head ache","head hurts","hedache",
        "headach","headech","sar dard","sar mein dard","sir mein dard","my head hurts",
        "head is paining","i have headache","mujhe sir dard hai","sir mein dard hai",
        "head throbbing","throbbing head","head is heavy","heavy head","bhara bhara sir",
        "head pressure","pressure in head","head feels heavy","skull pain","head bang",
        "head spinning","cluster headache","tension headache","sir ghoom raha",
    ],
    "dizziness": [
        "dizzy","dizziness","chakkar","lightheaded","vertigo","spinning","diziness",
        "chaker","chakkar aana","head spinning","mujhe chakkar aa rahe","chakkar aa rahe hain",
        "feel dizzy","feeling dizzy","room spinning","balance problem","unsteady",
        "giddy","giddiness","nauseated and dizzy","dizzy and weak","about to faint",
        "chakkar sar mein","sir ghoom raha hai","chakar","chakker",
    ],
    "stiff_neck": [
        "stiff neck","neck stiff","gardan akad","neck pain","gardan dard","neck stiffness",
        "cant move neck","neck is stiff","stiff in neck","gardan akdi hui","neck tight",
        "rigid neck","neck rigidity","painful neck","neck ache","gardan mein dard",
    ],
    "blurred_vision": [
        "blurred vision","cant see clearly","vision problem","dhundhla dikhna",
        "blurry vision","blur","eyes blurry","vision blurry","dhundhla","double vision",
        "seeing double","vision loss","partial vision","black spots in vision",
        "floaters","flashes of light","eye vision","sight problem","weak eyesight",
    ],
    "unconscious": [
        "unconscious","faint","blackout","passed out","behosh","behoshi","fainted",
        "lost consciousness","collapsed","fell unconscious","going unconscious",
        "nearly fainted","almost fainted","blacked out","sudden collapse","syncope",
    ],
    # ── Chest / Heart / Lungs ──────────────────────────────────────────────────
    "chest_pain": [
        "chest pain","seene mein dard","heart pain","chest tightness","chest hurts",
        "chest ache","cheast pain","chest presure","chest pressure","seene dard",
        "seene mein jalan","pain in chest","my chest hurts","chest mein dard",
        "chest dard hai","tightness in chest","heaviness in chest","chest feels tight",
        "chest discomfort","squeezing chest","crushing chest","left chest pain",
        "right chest pain","chest burning","chest like someone sitting on it",
    ],
    "breathlessness": [
        "breathless","difficulty breathing","cant breathe","short of breath","saans",
        "shortness of breath","breathing problem","saans lene mein taklif","breathlesness",
        "cant breath","saans phool rahi","saans phoolna","saans lene mein dikkat",
        "breathing difficulty","hard to breathe","trouble breathing","breath short",
        "out of breath","no breath","saans band","suffocating","choking","dyspnea",
        "respiratory","labored breathing","rapid breathing","fast breathing",
        "meri saans phool rahi hai","saans nahi aa raha",
    ],
    "palpitations": [
        "palpitation","heart racing","dhak dhak","fast heartbeat","heart flutter",
        "heart beating fast","dil ki dhadkan","dhadkan tez","dil tez chal raha",
        "irregular heartbeat","heart pounding","heart skipping","missed beat",
        "fluttering heart","thumping heart","heart going fast","rapid heart",
        "heart palpitation","dil ki dhadkan tez hai","dhadkan badh gayi","arrhythmia",
    ],
    # ── Stomach / Gut ──────────────────────────────────────────────────────────
    "abdominal_pain": [
        "stomach pain","pet dard","abdominal pain","belly pain","stomach ache",
        "pet mein dard","pait dard","tummy pain","abdomen pain","stomache pain",
        "stomachache","stomach is paining","pait mein dard","pet dukh raha",
        "mera pet dard kar raha","stomach cramps","cramping","lower abdominal pain",
        "upper abdominal pain","abdominal cramps","stomach spasm","stomach hurts",
        "gut pain","intestinal pain","naval pain","navel pain","belly hurts",
    ],
    "nausea": [
        "nausea","nauseous","sick feeling","ulti jaisi","queasy","nausha","naushea",
        "feel like vomiting","want to vomit","mataana","ulti aane wali","jee ghubra raha",
        "ghubra raha hai","feel sick","stomach upset","feel like throwing up",
        "nausiated","natious","motion sickness","ulti ka mann","jee mataana",
        "gagging","stomach turning","feeling of vomiting","heaving",
    ],
    "vomiting": [
        "vomiting","vomit","throwing up","ulti","puking","vommiting","vomitting",
        "throw up","puke","ulti ho rahi","ulti aa rahi","mujhe ulti ho rahi",
        "i vomited","i threw up","threw up","vomited","been vomiting","kept vomiting",
        "regurgitation","vomit blood","blood in vomit","projectile vomiting",
    ],
    "diarrhea": [
        "diarrhea","loose stool","loose motion","dast","stomach loose","diarhea",
        "diarrhoea","daiarrhea","loose motions","watery stool","runny stomach",
        "motions","frequent motions","dast ho rahe","latrine ho rahi","patlaa potty",
        "watery potty","potty pani wali","mujhe dast hain","dast lag rahe",
        "upset stomach motions","stomach running","diarrhea problem","stomach going",
        "frequent bowel","liquid stool","running stomach",
    ],
    "constipation": [
        "constipation","kabz","hard stool","no bowel movement","cant poop","no motion",
        "kabaj","kabjiyat","potty nahi aa rahi","latrine nahi","no potty","no latrine",
        "havent pooped","stomach stuck","hard potty","cant pass stool","straining",
        "difficulty passing stool","blocked bowel","no motion since","no stool",
    ],
    "indigestion": [
        "indigestion","gas","bloating","acidity","tezab","burping","acidity problem",
        "gas problem","pet mein gas","heartburn","acid reflux","tezaab","gerd",
        "acidic","sour belching","burp","belching","gastritis","stomach acid",
        "pet phool raha","bloated","pet mein jalan","jalan pet mein","burning stomach",
        "gastric","gas formation","gastric problem","acidity ho rahi","acidity hai",
        "pet mein acidity","tezab ho raha hai","sour taste","sour in mouth",
    ],
    "loss_of_appetite": [
        "no appetite","not hungry","bhook nahi","loss of appetite","cant eat",
        "not eating","no hunger","appetite loss","bhook nahi lag rahi","khana nahi khaya",
        "dont feel like eating","food not going in","nothing going in","skip meals",
        "anorexia","not wanting to eat","food aversion","off food","off my food",
        "cant face food","put off food","lost appetite","appetite gone",
    ],
    # ── Body / Muscle / Joints ─────────────────────────────────────────────────
    "fatigue": [
        "tired","fatigue","weakness","exhausted","kamzori","no energy","thakaan",
        "thakawat","lethargy","lethargic","tierd","weekness","weaknes","thaka",
        "very tired","extremely tired","weak","body weak","kamzor","zyada thaka",
        "kuch karne ki shakti nahi","no strength","feeling weak","weakness in body",
        "energy nahi","bahut thaka","badan mein kamzori","low energy","drained",
        "always tired","constantly tired","chronically tired","no power in body",
    ],
    "muscle_pain": [
        "muscle pain","body ache","badan dard","muscle ache","myalgia","body pain",
        "badan mein dard","muscel pain","all over pain","aching","sore muscles",
        "muscle soreness","badan dukh raha","badan mein dard ho raha","body hurts",
        "my body is aching","muscles hurt","muscle cramps","cramps in body",
        "leg cramps","calf pain","thigh pain","arm pain","pain all over",
    ],
    "joint_pain": [
        "joint pain","arthritis","jodo mein dard","knee pain","joints hurt","joint ache",
        "jodo dard","joint pian","ghutne mein dard","knee ache","knee hurts",
        "elbow pain","shoulder pain","ankle pain","wrist pain","hip pain","joint swelling",
        "stiff joints","joint stiffness","joints stiff","painful joints","gout",
        "rheumatism","joints aching","jodo mein akad",
    ],
    "back_pain": [
        "back pain","kamar dard","lower back","spine pain","back ache","backache",
        "back hurts","kamar mein dard","lower back pain","kamar dard ho raha",
        "meri kamar dard kar rahi","spine ache","disc pain","lumbar pain","sciatic",
        "sciatica","back is killing me","back spasm","back stiff","upper back pain",
        "middle back pain","ribs pain","rib pain","kidney area pain",
    ],
    "swelling": [
        "swelling","soojan","swollen","edema","puffiness","sujan","face swollen",
        "leg swollen","ankle swollen","foot swollen","hand swollen","swelling on face",
        "swelling on leg","swollen leg","puffy","soojan aa gayi","soojan hai",
        "inflammation","inflamed","ankles swollen","bloated limbs","water retention",
        "body swelling","swollen feet","lymph node swelling","neck swelling",
    ],
    # ── Skin ──────────────────────────────────────────────────────────────────
    "itching": [
        "itch","itchy","scratching","khujli","khujali","itching","khujli ho rahi",
        "khujli ho rahi hai","mujhe khujli hai","skin itching","itching all over",
        "itchy skin","cant stop itching","itchy rash","pruritus","urge to scratch",
        "skin crawling","tingling and itching",
    ],
    "skin_rash": [
        "rash","skin rash","red spots","eruption","hives","urticaria","skin eruption",
        "spots on skin","pimples all over","breakout","allergic rash","rashes",
        "rash on body","rash on face","rash on arms","skin marks","skin spots",
        "chickenpox like","measles like","skin allergy","daane","daane nikal aaye",
        "daane aa gaye","skin problem","skin disorder",
    ],
    "skin_peeling": [
        "peeling","dry skin","flaking","scaling skin","skin peeling","skin falling off",
        "skin flaking","dried skin","cracked skin","chapped skin","rough skin",
    ],
    "redness": [
        "red","redness","lal","redness on skin","reddish","skin red","red skin",
        "face red","skin turned red","redness on face","blushing","flushing",
        "red patches","red area","lali","lal ho gaya",
    ],
    "yellowish_skin": [
        "yellow skin","jaundice","yellowing","yellow eyes","skin yellow","aankhein peeli",
        "aankhein yellow","peeli skin","peeli aankhein","body yellow","paila hona",
        "peela ho gaya","liver problem jaundice","yellow tinge","icterus",
    ],
    # ── Eyes / Ears ────────────────────────────────────────────────────────────
    "eye_pain": [
        "eye pain","aankh mein dard","red eyes","eyes hurt","eye irritation","watering eyes",
        "aankh dukh rahi","aankh mein jalan","eye burning","burning eyes","eye discharge",
        "sticky eye","eye infection","conjunctivitis","pink eye","aankh lal hai",
        "aankh lal ho gayi","aankh se paani aa raha","eyes watering","dry eyes",
        "eye swollen","swollen eye","can't open eye","painful eye",
    ],
    "ear_pain": [
        "ear pain","kaan dard","ear ache","earache","kaan mein dard","kaan dard hai",
        "kaan dukh raha","ear hurts","my ear hurts","kaan se paani","ear discharge",
        "ear infection","kaan mein kuch","ear blocked","ear ringing","tinnitus",
        "buzzing in ear","kaan mein sunn sunn","hearing problem","muffled hearing",
    ],
    # ── Mental Health ──────────────────────────────────────────────────────────
    "anxiety": [
        "anxious","anxiety","panic","nervous","tension","gharabaahat","ghabhrana",
        "anxety","anxxiety","panic attack","heart racing anxiety","worry","worried",
        "overthinking","cant stop thinking","restless","restlessness","uneasy",
        "fearful","scared all the time","phobia","stress","stressed out","wound up",
        "on edge","jittery","mujhe ghabra raha hai","ghabrat","man mein dar",
    ],
    "depression": [
        "depressed","sad","hopeless","depression","udaas","dukhi","low mood",
        "no motivation","dont want to do anything","feeling empty","feeling useless",
        "want to cry","crying all the time","cant get out of bed","no interest",
        "lost interest","worthless","everything feels pointless","mujhe sab bekaar lagta",
        "bahut udaas hun","jine ka mann nahi","no will to live","dark thoughts",
        "suicidal","suicide","self harm","hurt myself",
    ],
    # ── Urinary ───────────────────────────────────────────────────────────────
    "urination_pain": [
        "burning urination","pain urination","peshab mein jalan","urine pain","burning pee",
        "stinging urination","pee pain","painful urination","dysuria","peshab mein dard",
        "jalan peshab mein","burning when peeing","hurts to pee","pee burns",
        "urine jalan","urinary burning","peshab karte waqt jalan",
    ],
    "frequent_urination": [
        "frequent urination","urinating often","baar baar peshab","urinate a lot",
        "peeing a lot","going to toilet often","frequent peeing","cant hold urine",
        "baar baar toilet","baar baar bathroom","urine frequency","keep needing to pee",
        "running to toilet","nocturia","peeing at night","night urination",
    ],
    # ── Other ─────────────────────────────────────────────────────────────────
    "chills": [
        "chills","shivering","kaanpna","cold shiver","body shaking","shiver","shaking",
        "kamp","thand lag rahi","feeling cold","feeling chilly","body trembling",
        "chattering teeth","shaking with cold","rigors","rigour","icy feeling",
        "kamp raha hun","kaampna","kaanp raha hun","thand mujhe aa rahi",
    ],
    "sweating": [
        "sweating","paseena","excessive sweat","night sweats","perspiration","sweaty",
        "sweat a lot","pasinaa","bahut paseena","bahut paseena aa raha","drenched in sweat",
        "soaked in sweat","cold sweat","cold sweat at night","hyperhidrosis",
        "paseena aa raha hai","heavy sweating","sweating without reason",
    ],
    "bleeding": [
        "bleeding","khoon","blood","hemorrhage","khoon aana","blood coming","khoon aa raha",
        "blood in stool","blood in urine","blood in vomit","rectal bleeding",
        "nose bleeding","nosebleed","epistaxis","cut bleeding","wound bleeding",
        "heavy period","blood clot","khoon aa raha hai","bleeding nahi ruk raha",
        "internal bleeding","haematuria","hematemesis","coughing blood","blood clots",
    ],
    "weight_loss": [
        "weight loss","losing weight","wajan kam","getting thin","lost weight",
        "weight reduce","wajan ghaat raha","wajan ghata","weight down","getting thinner",
        "losing body weight","unexplained weight loss","clothes loose","getting slim",
    ],
    "stiff_neck": [
        "stiff neck","neck stiff","gardan akad","neck pain","gardan dard","neck stiffness",
        "cant move neck","gardan nahi ghoom rahi","neck locked","rigid neck",
        "neck is stiff","gardan akad gayi","tight neck","neck cramp",
    ],
}
