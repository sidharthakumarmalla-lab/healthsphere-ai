import streamlit as st
import os
import requests
import json
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="HealthSphere AI - Rural Healthcare Portal",
    page_icon="❇️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL config
BACKEND_URL = "http://127.0.0.1:8000/api"
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "healthsphere_secure_api_token_2026")

# Helper to load CSS
def load_css(file_path):
    try:
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("frontend/style.css")

# --- BACKEND API CALLS ---
def api_get(endpoint):
    try:
        r = requests.get(f"{BACKEND_URL}/{endpoint}", headers={"X-API-KEY": BACKEND_API_KEY})
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        return None
    return None

def api_post(endpoint, data):
    try:
        r = requests.post(f"{BACKEND_URL}/{endpoint}", json=data, headers={"X-API-KEY": BACKEND_API_KEY})
        if r.status_code in [200, 201]:
            return r.json()
        else:
            st.error(f"Error: {r.status_code} - {r.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to HealthSphere API.")
    return None

def api_put(endpoint, data):
    try:
        r = requests.put(f"{BACKEND_URL}/{endpoint}", json=data, headers={"X-API-KEY": BACKEND_API_KEY})
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to HealthSphere API.")
    return None

def api_delete(endpoint):
    try:
        r = requests.delete(f"{BACKEND_URL}/{endpoint}", headers={"X-API-KEY": BACKEND_API_KEY})
        if r.status_code == 204:
            return True
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to HealthSphere API.")
    return False


# --- BILINGUAL DICTIONARY ---
LANG_DICT = {
    "English": {
        "title": "HealthSphere AI",
        "subtitle": "Multi-Agent AI Healthcare Platform for Rural & Underserved Communities",
        "emergency_title": "Rural Emergency Contacts",
        "emergency_contacts": "Ambulance: **108** (Medical Emergency) / **102** (Maternity)\n\nNational Emergency: **112**\n\nHealth Helpline: **104** (Medical Advice)",
        "menu_dashboard": "📈 Dashboard & Insights",
        "menu_profiles": "👥 Family Profiles",
        "menu_assessment": "⚕️ Symptom Assessment",
        "menu_reminders": "⏰ Medication Reminders",
        "menu_history": "📜 Consultation History",
        "profile_header": "Manage Family Health Profiles",
        "add_profile": "Add New Family Member Profile",
        "fullname": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "relationship": "Relationship",
        "zip": "ZIP Code / PIN Code",
        "income": "Monthly Family Income (INR)",
        "pre_existing": "Pre-existing Medical Conditions",
        "allergies": "Known Allergies (comma separated)",
        "create_profile": "Create Profile",
        "assess_header": "Multi-Agent AI Symptom Triage",
        "select_member": "Select Family Member to Assess",
        "describe_symptoms": "Describe Symptoms in detail",
        "duration": "Duration of Symptoms",
        "start_consultation": "Start Multi-Agent Consultation",
        "emergency_banner": "IMMEDIATE EMERGENCY ALERT",
        "emergency_subtitle": "Severe clinical markers found. Follow the instructions below and go to the nearest emergency health center immediately.",
        "reminders_header": "Family Medication Reminders & Schedules",
        "reminders_manual": "Add Reminder Manually",
        "med_name": "Medicine Name",
        "dosage": "Dosage",
        "frequency": "Frequency",
        "time_of_day": "Time of Day (HH:MM format, comma separated)",
        "add_reminder": "Add Reminder",
        "active_schedules": "Active Schedules",
        "history_header": "Health Guardian Medical Records & History",
        "encounter_logs": "Medical Encounter Logs",
        "dashboard_header": "Platform Metrics & Analytics",
        "gender_opts": ["Male", "Female", "Other"],
        "rel_opts": ["Self", "Spouse", "Son", "Daughter", "Father", "Mother", "Grandfather", "Grandmother"],
        "freq_opts": ["Daily", "Twice Daily", "Three times daily", "Weekly"],
        "delete_btn": "Delete",
        "connecting": "Connecting to HealthSphere AI backend services... Make sure the backend server (FastAPI) is running."
    },
    "Hindi": {
        "title": "हेल्थस्फेयर एआई (HealthSphere AI)",
        "subtitle": "ग्रामीण और वंचित क्षेत्रों के लिए मल्टी-एजेंट एआई स्वास्थ्य सेवा मंच",
        "emergency_title": "ग्रामीण आपातकालीन संपर्क",
        "emergency_contacts": "एम्बुलेंस: **108** (चिकित्सा आपातकाल) / **102** (गर्भवती महिला)\n\nराष्ट्रीय आपातकाल: **112**\n\nस्वास्थ्य हेल्पलाइन: **104** (चिकित्सा सलाह)",
        "menu_dashboard": "📈 डैशबोर्ड और आंकड़े",
        "menu_profiles": "👥 परिवार के सदस्य",
        "menu_assessment": "⚕️ लक्षण जांच और निदान",
        "menu_reminders": "⏰ दवा अनुस्मारक",
        "menu_history": "📜 परामर्श इतिहास",
        "profile_header": "पारिवारिक स्वास्थ्य प्रोफाइल प्रबंधित करें",
        "add_profile": "परिवार के नए सदस्य की प्रोफाइल जोड़ें",
        "fullname": "पूरा नाम",
        "age": "आयु (Age)",
        "gender": "लिंग",
        "relationship": "संबंध (Relationship)",
        "zip": "पिन कोड (PIN Code)",
        "income": "मासिक पारिवारिक आय (रुपये में)",
        "pre_existing": "पहले से मौजूद बीमारियां",
        "allergies": "ज्ञात एलर्जी (कोमा से अलग करें)",
        "create_profile": "प्रोफाइल बनाएं",
        "assess_header": "मल्टी-एजेंट एआई लक्षण निदान",
        "select_member": "जांच के लिए परिवार के सदस्य का चयन करें",
        "describe_symptoms": "लक्षणों का विवरण विस्तार से लिखें",
        "duration": "लक्षणों की अवधि (उदा. 2 दिन, 1 हफ्ता)",
        "start_consultation": "मल्टी-एजेंट परामर्श शुरू करें",
        "emergency_banner": "तत्काल आपातकालीन चेतावनी (EMERGENCY ALERT)",
        "emergency_subtitle": "गंभीर लक्षण पाए गए हैं। कृपया नीचे दिए गए निर्देशों का पालन करें और तुरंत नजदीकी आपातकालीन स्वास्थ्य केंद्र जाएं।",
        "reminders_header": "पारिवारिक दवा अनुस्मारक और समय सारिणी",
        "reminders_manual": "दवा का समय खुद से जोड़ें",
        "med_name": "दवा का नाम",
        "dosage": "खुराक (उदा. 1 गोली, 5ml)",
        "frequency": "बारंबारता (दिन में कितनी बार)",
        "time_of_day": "दवा का समय (HH:MM प्रारूप, कोमा से अलग)",
        "add_reminder": "अनुस्मारक जोड़ें",
        "active_schedules": "सक्रिय समय सारिणी",
        "history_header": "हेल्थ गार्जियन मेडिकल रिकॉर्ड और इतिहास",
        "encounter_logs": "चिकित्सीय परामर्श इतिहास",
        "dashboard_header": "मंच के आंकड़े और विश्लेषण",
        "gender_opts": ["पुरुष (Male)", "महिला (Female)", "अन्य (Other)"],
        "rel_opts": ["स्वयं (Self)", "पति/पत्नी (Spouse)", "बेटा (Son)", "बेटी (Daughter)", "पिता (Father)", "माता (Mother)", "दादा/नाना (Grandfather)", "दादी/नानी (Grandmother)"],
        "freq_opts": ["रोजाना (Daily)", "दिन में दो बार (Twice Daily)", "दिन में तीन बार (Three times daily)", "साप्ताहिक (Weekly)"],
        "delete_btn": "हटाएं (Delete)",
        "connecting": "हेल्थस्फेयर एआई बैकएंड सेवाओं से जुड़ रहा है... सुनिश्चित करें कि बैकएंड सर्वर (FastAPI) चालू है।"
    },
    "Bengali": {
        "title": "হেলথস্ফিয়ার এআই (HealthSphere AI)",
        "subtitle": "গ্রামীণ ও সুবিধাবঞ্চিত এলাকার জন্য মাল্টি-এজেন্ট এআই স্বাস্থ্যসেবা মঞ্চ",
        "emergency_title": "গ্রামীণ জরুরি যোগাযোগ",
        "emergency_contacts": "অ্যাম্বুলেন্স: **108** (চিকিৎসা জরুরি) / **102** (মাতৃত্ব)\n\nজাতীয় জরুরি অবস্থা: **112**\n\nহেলথ হেল্পলাইন: **104** (চিকিৎসা পরামর্শ)",
        "menu_dashboard": "📈 ড্যাশবোর্ড ও পরিসংখ্যান",
        "menu_profiles": "👥 পরিবারের সদস্যদের প্রোফাইল",
        "menu_assessment": "⚕️ লক্ষণ মূল্যায়ন",
        "menu_reminders": "⏰ ওষুধের রিমাইন্ডার",
        "menu_history": "📜 পরামর্শের ইতিহাস",
        "profile_header": "পারিবারিক স্বাস্থ্য প্রোফাইল পরিচালনা করুন",
        "add_profile": "নতুন সদস্যের প্রোফাইল যুক্ত করুন",
        "fullname": "পুরো নাম",
        "age": "বয়স",
        "gender": "লিঙ্গ",
        "relationship": "সম্পর্ক",
        "zip": "পিন কোড (PIN Code)",
        "income": "মাসিক পারিবারিক আয় (INR)",
        "pre_existing": "পূর্ববর্তী রোগ বা সমস্যা",
        "allergies": "পরিচিত অ্যালার্জি (কমা দিয়ে আলাদা করুন)",
        "create_profile": "প্রোফাইল তৈরি করুন",
        "assess_header": "মাল্টি-এজেন্ট এআই লক্ষণ ডায়াগনসিস",
        "select_member": "মূল্যায়নের জন্য সদস্য নির্বাচন করুন",
        "describe_symptoms": "বিস্তারিতভাবে লক্ষণের বর্ণনা দিন",
        "duration": "লক্ষণের সময়কাল (যেমন: ২ দিন, ১ সপ্তাহ)",
        "start_consultation": "মাল্টি-এজেন্ট পরামর্শ শুরু করুন",
        "emergency_banner": "জরুরি সতর্কতা (EMERGENCY ALERT)",
        "emergency_subtitle": "গুরুতর লক্ষণ দেখা গেছে। নিচের নির্দেশাবলী অনুসরণ করে অবিলম্বে নিকটস্থ জরুরি হাসপাতালে যান।",
        "reminders_header": "পারিবারিক ওষুধের রিমাইন্ডার ও সময়সূচী",
        "reminders_manual": "ম্যানুয়ালি রিমাইন্ডার যুক্ত করুন",
        "med_name": "ওষুধের নাম",
        "dosage": "ডোজ (যেমন: ১টি ট্যাবলেট, 5ml)",
        "frequency": "ওষুধ খাওয়ার ফ্রিকোয়েন্সি",
        "time_of_day": "সময়সূচী (HH:MM ফরম্যাট, কমা দিয়ে আলাদা করুন)",
        "add_reminder": "রিমাইন্ডার যোগ করুন",
        "active_schedules": "সক্রিয় সময়সূচী",
        "history_header": "হেলথ গার্ডিয়ান মেডিকেল রেকর্ড ও ইতিহাস",
        "encounter_logs": "চিকিৎসা ইতিহাসের লগ",
        "dashboard_header": "ড্যাশবোর্ড মেট্রিক্স ও বিশ্লেষণ",
        "gender_opts": ["পুরুষ (Male)", "মহিলা (Female)", "অন্যান্য (Other)"],
        "rel_opts": ["স্বয়ং (Self)", "স্বামী/স্ত্রী (Spouse)", "পুত্র (Son)", "কন্যা (Daughter)", "পিতা (Father)", "মাতা (Mother)", "দাদা/নানা (Grandfather)", "দিদিমা/নানি (Grandmother)"],
        "freq_opts": ["প্রতিদিন (Daily)", "দিনে দুবার (Twice Daily)", "দিনে তিনবার (Three times daily)", "সাপ্তাহিক (Weekly)"],
        "delete_btn": "মুছে ফেলুন (Delete)",
        "connecting": "হেলথস্ফিয়ার ব্যাকএন্ডের সাথে সংযোগ স্থাপন করা হচ্ছে... অনুগ্রহ করে নিশ্চিত করুন ব্যাকএন্ড চলছে।"
    },
    "Telugu": {
        "title": "హెల్త్‌స్పియర్ ఏఐ (HealthSphere AI)",
        "subtitle": "గ్రామీణ మరియు వెనుకబడిన ప్రాంతాల కోసం మల్టీ-ఏజెంట్ ఏఐ ఆరోగ్య వేదిక",
        "emergency_title": "గ్రామీణ అత్యవసర పరిచయాలు",
        "emergency_contacts": "అంబులెన్స్: **108** (వైద్య అత్యవసరం) / **102** (గర్భిణీ సేవలు)\n\nజాతీయ అత్యవసర నంబర్: **112**\n\nఆరోగ్య హెల్ప్‌లైన్: **104** (వైద్య సలహా)",
        "menu_dashboard": "📈 డ్యాష్‌బోర్డ్ & గణాంకాలు",
        "menu_profiles": "👥 కుటుంబ సభ్యుల ప్రొఫైల్స్",
        "menu_assessment": "⚕️ లక్షణాల విశ్లేషణ",
        "menu_reminders": "⏰ మందుల రిమైండర్లు",
        "menu_history": "📜 సంప్రదింపుల చరిత్ర",
        "profile_header": "కుటుంబ ఆరోగ్య ప్రొఫైల్స్ నిర్వహణ",
        "add_profile": "కుటుంబ కొత్త సభ్యుడి ప్రొఫైల్ జోడించు",
        "fullname": "పూర్తి పేరు",
        "age": "వయస్సు",
        "gender": "లింగం",
        "relationship": "సంబంధం",
        "zip": "పిన్ కోడ్ (PIN Code)",
        "income": "కుటుంబ నెలవారీ ఆదాయం (INR)",
        "pre_existing": "మునుపటి వైద్య పరిస్థితులు",
        "allergies": "అలర్జీలు (కామాలతో విభజించండి)",
        "create_profile": "ప్రొఫైల్ సృష్టించు",
        "assess_header": "మల్టీ-ఏజెంట్ ఏఐ లక్షణాల నిర్ధారణ",
        "select_member": "పరీక్షించాల్సిన కుటుంబ సభ్యుడిని ఎంచుకోండి",
        "describe_symptoms": "లక్షణాలను వివరంగా రాయండి",
        "duration": "లక్షణాల వ్యవధి (ఉదా: 2 రోజులు, 1 వారం)",
        "start_consultation": "మల్టీ-ఏజెంట్ సంప్రదింపులు ప్రారంభించు",
        "emergency_banner": "అత్యవసర హెచ్చరిక (EMERGENCY ALERT)",
        "emergency_subtitle": "తీవ్రమైన లక్షణాలు కనుగొనబడ్డాయి. కింద ఉన్న సూచనలను పాటించి తక్షణమే సమీపంలోని అత్యవసర ఆసుపత్రికి వెళ్ళండి.",
        "reminders_header": "కుటుంబ మందుల రిమైండర్లు & షెడ్యూల్స్",
        "reminders_manual": "రిమైండర్ మాన్యువల్‌గా జోడించు",
        "med_name": "మందు పేరు",
        "dosage": "మోతాదు (ఉదా: 1 మాత్ర, 5ml)",
        "frequency": "మందుల నియమం (ఫ్రీక్వెన్సీ)",
        "time_of_day": "మందు తీసుకునే సమయం (HH:MM ఫార్మాట్, కామాలతో విభజించండి)",
        "add_reminder": "రిమైండర్ జోడించు",
        "active_schedules": "ప్రస్తుత షెడ్యూల్స్",
        "history_header": "హెల్త్ గార్డియన్ వైద్య రికార్డులు & చరిత్ర",
        "encounter_logs": "వైద్య సంప్రదింపుల లాగ్స్",
        "dashboard_header": "వేదిక మెట్రిక్స్ & విశ్లేషణ",
        "gender_opts": ["పురుషుడు (Male)", "స్త్రీ (Female)", "ఇతర (Other)"],
        "rel_opts": ["స్వయంగా (Self)", "భర్త/భార్య (Spouse)", "కుమారుడు (Son)", "కుమార్తె (Daughter)", "తండ్రి (Father)", "తల్లి (Mother)", "తాతయ్య (Grandfather)", "నానమ్మ/అమ్మమ్మ (Grandmother)"],
        "freq_opts": ["రోజువారీ (Daily)", "రోజుకు రెండుసార్లు (Twice Daily)", "రోజుకు మూడుసార్లు (Three times daily)", "వారానికి ఒకసారి (Weekly)"],
        "delete_btn": "తొలగించు (Delete)",
        "connecting": "హెల్త్‌స్పియర్ బ్యాకెండ్ సేవలతో కనెక్ట్ అవుతోంది... బ్యాకెండ్ సర్వర్ రన్ అవుతోందో లేదో సరిచూసుకోండి."
    },
    "Tamil": {
        "title": "ஹெல்த்ஸ்பியர் ஏஐ (HealthSphere AI)",
        "subtitle": "கிராமப்புற மற்றும் பின்தங்கிய மக்களுக்கான மல்டி-ஏஜென்ட் ஏஐ சுகாதார தளம்",
        "emergency_title": "கிராமப்புற அவசர தொடர்புகள்",
        "emergency_contacts": "ஆம்புலன்ஸ்: **108** (மருத்துவ அவசரம்) / **102** (மகப்பேறு)\n\nதேசிய அவசர எண்: **112**\n\nசுகாதார உதவி எண்: **104** (மருத்துவ ஆலோசனை)",
        "menu_dashboard": "📈 டாஷ்போர்டு & புள்ளிவிவரங்கள்",
        "menu_profiles": "👥 குடும்ப உறுப்பினர்களின் சுயவிவரங்கள்",
        "menu_assessment": "⚕️ அறிகுறி மதிப்பீடு",
        "menu_reminders": "⏰ மருந்து நினைவூட்டல்கள்",
        "menu_history": "📜 ஆலோசனை வரலாறு",
        "profile_header": "குடும்ப சுகாதார சுயவிவரங்களை நிர்வகிக்கவும்",
        "add_profile": "புதிய குடும்ப உறுப்பினரைச் சேர்க்கவும்",
        "fullname": "முழு பெயர்",
        "age": "வயது",
        "gender": "பாலினம்",
        "relationship": "உறவுமுறை",
        "zip": "அஞ்சல் குறியீடு (PIN Code)",
        "income": "மாதாந்திர குடும்ப வருமானம் (INR)",
        "pre_existing": "முந்தைய மருத்துவ நிலைகள்",
        "allergies": "அலெர்ஜிகள் (கமா மூலம் பிரிக்கவும்)",
        "create_profile": "சுயவிவரத்தை உருவாக்கவும்",
        "assess_header": "மல்டி-ஏஜென்ட் ஏஐ அறிகுறி பரிசோதனை",
        "select_member": "பரிசோதிக்க வேண்டிய உறுப்பினரைத் தேர்ந்தெடுக்கவும்",
        "describe_symptoms": "அறிகுறிகளை விரிவாக விவரிக்கவும்",
        "duration": "அறிகுறிகளின் காலம் (எ.கா: 2 நாட்கள், 1 வாரம்)",
        "start_consultation": "மல்டி-ஏஜென்ட் ஆலோசனையைத் தொடங்கவும்",
        "emergency_banner": "உடனடி அவசர எச்சரிக்கை (EMERGENCY ALERT)",
        "emergency_subtitle": "தீவிர அறிகுறிகள் கண்டறியப்பட்டுள்ளன. கீழே உள்ள வழிமுறைகளைப் பின்பற்றி உடனடியாக அருகில் உள்ள அவசர மருத்துவமனைக்குச் செல்லவும்.",
        "reminders_header": "குடும்ப மருந்து நினைவூட்டல்கள் & கால அட்டவணைகள்",
        "reminders_manual": "நினைவூட்டலை கைமுறையாகச் சேர்க்கவும்",
        "med_name": "மருந்தின் பெயர்",
        "dosage": "அளவு (எ.கா: 1 மாத்திரை, 5ml)",
        "frequency": "மருந்து உட்கொள்ளும் அதிர்வெண்",
        "time_of_day": "நேரம் (HH:MM வடிவம், கமா மூலம் பிரிக்கவும்)",
        "add_reminder": "நினைவூட்டலைச் சேர்க்கவும்",
        "active_schedules": "செயலில் உள்ள கால அட்டவணைகள்",
        "history_header": "ஹெல்த் கார்டியன் மருத்துவ பதிவுகள் & வரலாறு",
        "encounter_logs": "மருத்துவ ஆலோசனை பதிவுகள்",
        "dashboard_header": "டாஷ்போர்டு பகுப்பாய்வு",
        "gender_opts": ["ஆண் (Male)", "பெண் (Female)", "இதர (Other)"],
        "rel_opts": ["சுய (Self)", "கணவன்/மனைவி (Spouse)", "மகன் (Son)", "மகள் (Daughter)", "தந்தை (Father)", "தாய் (Mother)", "தாத்தா (Grandfather)", "பாட்டி (Grandmother)"],
        "freq_opts": ["தினமும் (Daily)", "நாளைக்கு இருமுறை (Twice Daily)", "நாளைக்கு மூன்று முறை (Three times daily)", "வாரத்திற்கு ஒருமுறை (Weekly)"],
        "delete_btn": "நீக்கு (Delete)",
        "connecting": "ஹெல்த்ஸ்பியர் பேக்எண்ட் சேவைகளுடன் இணைகிறது... பேக்எண்ட் சர்வர் இயங்குகிறதா என்பதை உறுதிப்படுத்தவும்."
    },
    "Marathi": {
        "title": "हेल्थस्फीअर एआय (HealthSphere AI)",
        "subtitle": "ग्रामीण आणि वंचित भागांसाठी मल्टी-एजंट एआय आरोग्य सेवा मंच",
        "emergency_title": "ग्रामीण आपत्कालीन संपर्क",
        "emergency_contacts": "रुग्णवाहिका: **108** (वैद्यकीय आणीबाणी) / **102** (प्रसूती)\n\nराष्ट्रीय आणीबाणी: **112**\n\nआरोग्य हेल्पलाइन: **104** (वैद्यकीय सल्ला)",
        "menu_dashboard": "📈 डॅशबोर्ड आणि आकडेवारी",
        "menu_profiles": "👥 कौटुंबिक प्रोफाइल",
        "menu_assessment": "⚕️ लक्षण तपासणी आणि निदान",
        "menu_reminders": "⏰ औषधांचे स्मरणपत्रे",
        "menu_history": "📜 सल्लामसलत इतिहास",
        "profile_header": "कौटुंबिक आरोग्य प्रोफाइल व्यवस्थापित करा",
        "add_profile": "नवीन कौटुंबिक सदस्य जोडा",
        "fullname": "पूर्ण नाव",
        "age": "वय",
        "gender": "लिंग",
        "relationship": "नाते",
        "zip": "पिन कोड (PIN Code)",
        "income": "मासिक कौटुंबिक उत्पन्न (INR)",
        "pre_existing": "आधीचे आजार/वैद्यकीय इतिहास",
        "allergies": "माहित असलेली ॲलर्जी (कॉमाने वेगळी करा)",
        "create_profile": "प्रोफाईल तयार करा",
        "assess_header": "मल्टी-एजंट एआय लक्षण निदान",
        "select_member": "तपासणीसाठी कौटुंबिक सदस्य निवडा",
        "describe_symptoms": "लक्षणे सविस्तर लिहा",
        "duration": "लक्षणांचा कालावधी (उदा. २ दिवस, १ आठवडा)",
        "start_consultation": "मल्टी-एजंट सल्लामसलत सुरू करा",
        "emergency_banner": "तातडीची आणीबाणी चेतावणी (EMERGENCY ALERT)",
        "emergency_subtitle": "गंभीर लक्षणे आढळली आहेत. कृपया खालील सूचनांचे पालन करा आणि ताबडतोब जवळच्या आणीबाणीच्या आरोग्य केंद्रात जा.",
        "reminders_header": "कौटुंबिक औषध स्मरणपत्रे आणि वेळापत्रक",
        "reminders_manual": "औषधांची वेळ स्वतः जोडा",
        "med_name": "औषधाचे नाव",
        "dosage": "डोस (उदा. १ गोळी, ५ मिली)",
        "frequency": "औषध घेण्याची वारंवारता",
        "time_of_day": "वेळ (HH:MM स्वरूप, कॉमाने वेगळे करा)",
        "add_reminder": "स्मरणपत्र जोडा",
        "active_schedules": "सक्रिय वेळापत्रक",
        "history_header": "हेल्थ गार्डियन वैद्यकीय रेकॉर्ड आणि इतिहास",
        "encounter_logs": "वैद्यकीय इतिहास लॉग",
        "dashboard_header": "डॅशबोर्ड मेट्रिक्स आणि विश्लेषण",
        "gender_opts": ["पुरुष (Male)", "महिला (Female)", "इतर (Other)"],
        "rel_opts": ["स्वतः (Self)", "पती/पत्नी (Spouse)", "मुलगा (Son)", "मुलगी (Daughter)", "वडील (Father)", "आई (Mother)", "आजोबा (Grandfather)", "आजी (Grandmother)"],
        "freq_opts": ["रोज (Daily)", "दिवसातून दोनदा (Twice Daily)", "दिवसातून तीनदा (Three times daily)", "साप्ताहिक (Weekly)"],
        "delete_btn": "हटवा (Delete)",
        "connecting": "हेल्थस्फीअर बॅकएंड सेवांशी जोडले जात आहे... बॅकएंड सर्व्हर सुरू असल्याची खात्री करा."
    },
    "Kannada": {
        "title": "ಹೆಲ್ತ್‌ಸ್ಫಿಯರ್ ಎಐ (HealthSphere AI)",
        "subtitle": "ಗ್ರಾಮೀಣ ಮತ್ತು ಹಿಂದುಳಿದ ಸಮುದಾಯಗಳಿಗಾಗಿ ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಎಐ ಆರೋಗ್ಯ ವೇದಿಕೆ",
        "emergency_title": "ಗ್ರಾಮೀಣ ತುರ್ತು ಸಂಪರ್ಕಗಳು",
        "emergency_contacts": "ಆಂಬ್ಯುಲೆನ್ಸ್: **108** (ವೈದ್ಯಕೀಯ ತುರ್ತು) / **102** (ಹೆರಿಗೆ ಸೇವೆಗಳು)\n\nರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಂಖ್ಯೆ: **112**\n\nಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ: **104** (ವೈದ್ಯಕೀಯ ಸಲಹೆ)",
        "menu_dashboard": "📈 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಮತ್ತು ಅಂಕಿಅಂಶಗಳು",
        "menu_profiles": "👥 ಕೌಟುಂಬಿಕ ಪ್ರೊಫೈಲ್‌ಗಳು",
        "menu_assessment": "⚕️ ರೋಗಲಕ್ಷಣಗಳ ವಿಶ್ಲೇಷಣೆ",
        "menu_reminders": "⏰ ಔಷಧಿ ನೆನಪೋಲೆಗಳು (Reminders)",
        "menu_history": "📜 ಸಮಾಲೋಚನೆ ಇತಿಹಾಸ",
        "profile_header": "ಕೌಟುಂಬಿಕ ಆರೋಗ್ಯ ಪ್ರೊಫೈಲ್‌ಗಳ ನಿರ್ವಹಣೆ",
        "add_profile": "ಹೊಸ ಕೌಟುಂಬಿಕ ಸದಸ್ಯರ ಪ್ರೊಫೈಲ್ ಸೇರಿಸಿ",
        "fullname": "ಪೂರ್ಣ ಹೆಸರು",
        "age": "ವಯಸ್ಸು",
        "gender": "ಲಿಂಗ",
        "relationship": "ಸಂಬಂಧ",
        "zip": "ಪಿನ್ ಕೋಡ್ (PIN Code)",
        "income": "ಮಾಸಿಕ ಕೌಟುಂಬಿಕ ಆದಾಯ (INR)",
        "pre_existing": "ಹಿಂದಿನ ವೈದ್ಯಕೀಯ ಸ್ಥಿತಿಗಳು",
        "allergies": "ತಿಳಿದಿರುವ ಅಲರ್ಜಿಗಳು (ಕಾಮಾದಿಂದ ಬೇರ್ಪಡಿಸಿ)",
        "create_profile": "ಪ್ರೊಫೈಲ್ ರಚಿಸಿ",
        "assess_header": "ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಎಐ ರೋಗಲಕ್ಷಣಗಳ ಪತ್ತೆ",
        "select_member": "ವಿಶ್ಲೇಷಿಸಲು ಕೌಟುಂಬಿಕ ಸದಸ್ಯರನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "describe_symptoms": "ರೋಗಲಕ್ಷಣಗಳನ್ನು ವಿವರವಾಗಿ ವಿವರಿಸಿ",
        "duration": "ರೋಗಲಕ್ಷಣಗಳ ಅವಧಿ (ಉದಾ: 2 ದಿನಗಳು, 1 ವಾರ)",
        "start_consultation": "ಮಲ್ಟಿ-ಏಜೆಂಟ್ ಸಮಾಲೋಚನೆ ಪ್ರಾರಂಭಿಸಿ",
        "emergency_banner": "ತುರ್ತು ಎಚ್ಚರಿಕೆ (EMERGENCY ALERT)",
        "emergency_subtitle": "ಗಂಭೀರ ರೋಗಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ. ಕೆಳಗಿನ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ ತಕ್ಷಣವೇ ಹತ್ತಿರದ ತುರ್ತು ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ.",
        "reminders_header": "ಕೌಟುಂಬಿಕ ಔಷಧಿ ನೆನಪೋಲೆಗಳು & ವೇಳಾಪಟ್ಟಿಗಳು",
        "reminders_manual": "ನೆನಪೋಲೆಯನ್ನು ಹಸ್ತಚಾಲಿತವಾಗಿ ಸೇರಿಸಿ",
        "med_name": "ಔಷಧಿಯ ಹೆಸರು",
        "dosage": "ಡೋಸೇಜ್ (ಉದಾ: 1 ಮಾತ್ರೆ, 5ml)",
        "frequency": "ಔಷಧಿ ತೆಗೆದುಕೊಳ್ಳುವ ಸಮಯಗಳು",
        "time_of_day": "ಸಮಯ (HH:MM ಸ್ವರೂಪ, ಕಾಮಾದಿಂದ ಬೇರ್ಪಡಿಸಿ)",
        "add_reminder": "ನೆನಪೋಲೆ ಸೇರಿಸಿ",
        "active_schedules": "ಸಕ್ರಿಯ ವೇಳಾಪಟ್ಟಿಗಳು",
        "history_header": "ಹೆಲ್ತ್ ಗಾರ್ಡಿಯನ್ ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳು & ಇತಿಹಾಸ",
        "encounter_logs": "ವೈದ್ಯಕೀಯ ಸಮಾಲೋಚನೆ ದಾಖಲೆಗಳು",
        "dashboard_header": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಅಂಕಿಅಂಶಗಳು ಮತ್ತು ವಿಶ್ಲೇಷಣೆ",
        "gender_opts": ["ಪುರುಷ (Male)", "ಮಹಿಳೆ (Female)", "ಇತರೆ (Other)"],
        "rel_opts": ["ಸ್ವತಃ (Self)", "ಪತಿ/ಪತ್ನಿ (Spouse)", "ಮಗ (Son)", "ಮಗಳು (Daughter)", "ತಂದೆ (Father)", "ತಾಯಿ (Mother)", "ತಾತ (Grandfather)", "ಅಜ್ಜಿ (Grandmother)"],
        "freq_opts": ["ಪ್ರತಿದಿನ (Daily)", "ದಿನಕ್ಕೆ ಎರಡು ಬಾರಿ (Twice Daily)", "ದಿನಕ್ಕೆ ಮೂರು ಬಾರಿ (Three times daily)", "ವಾರಕ್ಕೊಮ್ಮೆ (Weekly)"],
        "delete_btn": "ಅಳಿಸಿ (Delete)",
        "connecting": "ಹೆಲ್ತ್‌ಸ್ಫಿಯರ್ ಬ್ಯಾಕೆಂಡ್ ಸೇವೆಗಳೊಂದಿಗೆ ಸಂಪರ್ಕ ಹೊಂದುತ್ತಿದೆ... ಬ್ಯಾಕೆಂಡ್ ಸರ್ವರ್ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
    },
    "Malayalam": {
        "title": "ഹെൽത്ത്സ്ഫിയർ എഐ (HealthSphere AI)",
        "subtitle": "ഗ്രാമപ്രദേശങ്ങൾക്കും പാർശ്വവൽക്കരിക്കപ്പെട്ടവർക്കും വേണ്ടിയുള്ള മൾട്ടി-ഏജന്റ് എഐ ആരോഗ്യ വേദി",
        "emergency_title": "ഗ്രാമീണ അടിയന്തിര ബന്ധപ്പെടലുകൾ",
        "emergency_contacts": "ആംബുലൻസ്: **108** (മെഡിക്കൽ അടിയന്തിരാവസ്ഥ) / **102** (പ്രസവ സേവനങ്ങൾ)\n\nദേശീയ അടിയന്തിര നമ്പർ: **112**\n\nആരോഗ്യ ഹെൽപ്പ്‌ലൈൻ: **104** (മെഡിക്കൽ ഉപദേശം)",
        "menu_dashboard": "📈 ഡാഷ്‌ബോർഡും സ്ഥിതിവിവരക്കണക്കുകളും",
        "menu_profiles": "👥 കുടുംബാംഗങ്ങളുടെ പ്രൊഫൈലുകൾ",
        "menu_assessment": "⚕️ രോഗലക്ഷണ വിലയിരുത്തൽ",
        "menu_reminders": "⏰ മരുന്ന് ഓർമ്മപ്പെടുത്തലുകൾ",
        "menu_history": "📜 സന്ദർശന ചരിത്രം",
        "profile_header": "കുടുംബ ആരോഗ്യ പ്രൊഫൈലുകൾ നിയന്ത്രിക്കുക",
        "add_profile": "പുതിയ കുടുംബാംഗത്തെ ചേർക്കുക",
        "fullname": "പൂർണ്ണമായ പേര്",
        "age": "വയസ്സ്",
        "gender": "ലിംഗഭേദം",
        "relationship": "ബന്ധം",
        "zip": "പിൻ കോഡ് (PIN Code)",
        "income": "പ്രതിമാസ കുടുംബ വരുമാനം (INR)",
        "pre_existing": "മുൻകാല ആരോഗ്യ പ്രശ്നങ്ങൾ",
        "allergies": "അലർജികൾ (കോമ ഉപയോഗിച്ച് വേർതിരിക്കുക)",
        "create_profile": "പ്രൊഫൈൽ നിർമ്മിക്കുക",
        "assess_header": "മൾട്ടി-ഏജന്റ് എഐ രോഗലക്ഷണ നിർണ്ണയം",
        "select_member": "പരിശോധിക്കേണ്ട കുടുംബാംഗത്തെ തിരഞ്ഞെടുക്കുക",
        "describe_symptoms": "രോഗലക്ഷണങ്ങൾ വിശദമായി വിവരിക്കുക",
        "duration": "രോഗലക്ഷണങ്ങളുടെ കാലയളവ് (ഉദാ: 2 ദിവസം, 1 ആഴ്ച)",
        "start_consultation": "മൾട്ടി-ഏജന്റ് രോഗനിർണ്ണയം ആരംഭിക്കുക",
        "emergency_banner": "അടിയന്തിര മുന്നറിയിപ്പ് (EMERGENCY ALERT)",
        "emergency_subtitle": "ഗുരുതരമായ രോഗലക്ഷണങ്ങൾ കണ്ടെത്തിയിരിക്കുന്നു. താഴെ പറയുന്ന നിർദ്ദേശങ്ങൾ പാലിച്ച് ഉടൻ തന്നെ അടുത്തുള്ള അടിയന്തിര വിഭാഗത്തിലേക്ക് പോകുക.",
        "reminders_header": "കുടുംബ മരുന്ന് ഓർമ്മപ്പെടുത്തലുകളും സമയക്രമങ്ങളും",
        "reminders_manual": "ഓർമ്മപ്പെടുത്തൽ സ്വമേധയാ ചേർക്കുക",
        "med_name": "മരുന്നിന്റെ പേര്",
        "dosage": "അളവ് (ഉദാ: 1 ഗുളിക, 5ml)",
        "frequency": "മരുന്നിന്റെ ആവൃത്തി (Frequency)",
        "time_of_day": "സമയം (HH:MM രൂപത്തിൽ, കോമ ഉപയോഗിച്ച് വേർതിരിക്കുക)",
        "add_reminder": "ഓർമ്മപ്പെടുത്തൽ ചേർക്കുക",
        "active_schedules": "നിലവിലുള്ള സമയക്രമങ്ങൾ",
        "history_header": "ഹെൽത്ത് ഗാർഡിയൻ മെഡിക്കൽ റെക്കോർഡുകളും ചരിത്രവും",
        "encounter_logs": "മെഡിക്കൽ സന്ദർശന ലോഗുകൾ",
        "dashboard_header": "പ്ലാറ്റ്ഫോം വിശകലനം",
        "gender_opts": ["പുരുഷൻ (Male)", "സ്ത്രീ (Female)", "മറ്റുള്ളവ (Other)"],
        "rel_opts": ["സ്വയം (Self)", "ഭർത്താവ്/ഭാര്യ (Spouse)", "മകൻ (Son)", "മകൾ (Daughter)", "അച്ഛൻ (Father)", "അമ്മ (Mother)", "മുത്തശ്ശൻ (Grandfather)", "മുത്തശ്ശി (Grandmother)"],
        "freq_opts": ["ദിവസേന (Daily)", "ദിവസത്തിൽ രണ്ടുതവണ (Twice Daily)", "ദിവസത്തിൽ മൂന്നുതവണ (Three times daily)", "ആഴ്ചയിലൊരിക്കൽ (Weekly)"],
        "delete_btn": "ഒഴിവാക്കുക (Delete)",
        "connecting": "ഹെൽത്ത്സ്ഫിയർ ബാക്ക്എൻഡുമായി ബന്ധപ്പെടുന്നു... ബാക്ക്എൻഡ് സെർവർ പ്രവർത്തിക്കുന്നുണ്ടെന്ന് ഉറപ്പാക്കുക."
    },
    "Gujarati": {
        "title": "હેલ્થસ્ફિયર એઆઈ (HealthSphere AI)",
        "subtitle": "ગ્રામીણ અને વંચિત સમુદાયો માટે મલ્ટી-એજન્ટ એઆઈ આરોગ્ય સેવા મંચ",
        "emergency_title": "ગ્રામીણ કટોકટી સંપર્કો",
        "emergency_contacts": "એમ્બ્યુલન્સ: **108** (મેડિકલ કટોકટી) / **102** (પ્રસૂતિ સહાય)\n\nરાષ્ટ્રીય કટોકટી નંબર: **112**\n\nઆરોગ્ય હેલ્પલાઇન: **104** (તબીબી સલાહ)",
        "menu_dashboard": "📈 ડેશબોર્ડ અને આંકડા",
        "menu_profiles": "👥 પારિવારિક પ્રોફાઇલ્સ",
        "menu_assessment": "⚕️ લક્ષણ તપાસ અને નિદાન",
        "menu_reminders": "⏰ દવા રીમાઇન્ડર્સ",
        "menu_history": "📜 પરામર્શ ઇતિહાસ",
        "profile_header": "પારિવારિક આરોગ્ય પ્રોફાઇલ સંચાલન",
        "add_profile": "નવા સભ્યની પ્રોફાઇલ ઉમેરો",
        "fullname": "પૂરું નામ",
        "age": "ઉંમર",
        "gender": "જાતિ",
        "relationship": "સંબંધ",
        "zip": "પિન કોડ (PIN Code)",
        "income": "માસિક પારિવારિક આવક (INR)",
        "pre_existing": "પહેલાની તબીબી સ્થિતિઓ",
        "allergies": "જાણીતી એલર્જી (કોમા વડે અલગ કરો)",
        "create_profile": "પ્રોફાઇલ બનાવો",
        "assess_header": "મલ્ટી-એજન્ટ એઆઈ લક્ષણ નિદાન",
        "select_member": "તપાસ માટે પારિવારિક સભ્ય પસંદ કરો",
        "describe_symptoms": "લક્ષણોનું વિગતવાર વર્ણન કરો",
        "duration": "લક્ષણોનો સમયગાળો (દા.ત. ૨ દિવસ, ૧ અઠવાડિયું)",
        "start_consultation": "મલ્ટી-એજન્ટ પરામર્શ શરૂ કરો",
        "emergency_banner": "તાત્કાલિક કટોકટી ચેતવણી (EMERGENCY ALERT)",
        "emergency_subtitle": "ગંભીર લક્ષણો જોવા મળ્યા છે. કૃપા કરીને નીચેની સૂચનાઓનું પાલન કરો અને તરત જ નજીકના ઇમરજન્સી હેલ્થ સેન્ટર પર જાઓ.",
        "reminders_header": "પારિવારિક દવા રીમાઇન્ડર્સ અને સમયપત્રક",
        "reminders_manual": "મેન્યુઅલી રીમાઇન્ડર ઉમેરો",
        "med_name": "દવાનું નામ",
        "dosage": "માત્રા (દા.ત. ૧ ગોળી, ૫ મિલી)",
        "frequency": "દવા લેવાની વારંવારતા",
        "time_of_day": "દવા લેવાનો સમય (HH:MM ફોર્મેટ, કોમા વડે અલગ કરો)",
        "add_reminder": "રીમાઇન્ડર ઉમેરો",
        "active_schedules": "સક્રિય સમયપત્રક",
        "history_header": "હેલ્થ ગાર્ડિયન તબીબી રેકોર્ડ અને ઇતિહાસ",
        "encounter_logs": "તબીબી પરામર્શ હિસાબ",
        "dashboard_header": "મંચ વિશ્લેષણ અને આંકડા",
        "gender_opts": ["પુરુષ (Male)", "સ્ત્રી (Female)", "અન્ય (Other)"],
        "rel_opts": ["પોતે (Self)", "પતિ/પત્ની (Spouse)", "પુત્ર (Son)", "પુત્રી (Daughter)", "પિતા (Father)", "માતા (Mother)", "દાદા/નાના (Grandfather)", "દાદી/નાની (Grandmother)"],
        "freq_opts": ["રોજ (Daily)", "દિવસમાં બે વાર (Twice Daily)", "દિવસમાં ત્રણ વાર (Three times daily)", "સાપ્તાહિક (Weekly)"],
        "delete_btn": "દૂર કરો (Delete)",
        "connecting": "હેલ્થસ્ફિયર બેકએન્ડ સેવાઓ સાથે જોડાઈ રહ્યું છે... ખાતરી કરો કે બેકએન્ડ સર્વર ચાલુ છે."
    },
    "Punjabi": {
        "title": "ਹੈਲਥਸਫੀਅਰ ਏਆਈ (HealthSphere AI)",
        "subtitle": "ਪੇਂਡੂ ਅਤੇ ਲੋੜਵੰਦ ਖੇਤਰਾਂ ਲਈ ਮਲਟੀ-ਏਜੰਟ ਏਆਈ ਸਿਹਤ ਸੇਵਾ ਮੰਚ",
        "emergency_title": "ਪੇਂਡੂ ਐਮਰਜੈਂਸੀ ਸੰਪਰਕ",
        "emergency_contacts": "ਐਂਬੂਲੈਂਸ: **108** (ਮੈਡੀਕਲ ਐਮਰਜੈਂਸੀ) / **102** (ਗਰਭਵਤੀ ਸੇਵਾਵਾਂ)\n\nਰਾਸ਼ਟਰੀ ਐਮਰਜੈਂਸੀ: **112**\n\nਸਿਹਤ ਹੈਲਪਲਾਈਨ: **104** (ਮੈਡੀਕਲ ਸਲਾਹ)",
        "menu_dashboard": "📈 ਡੈਸ਼ਬੋਰਡ ਅਤੇ ਅੰਕੜੇ",
        "menu_profiles": "👥 ਪਰਿਵਾਰਕ ਪ੍ਰੋਫਾਈਲ",
        "menu_assessment": "⚕️ ਲੱਛਣ ਜਾਂਚ ਅਤੇ ਨਿਦਾਨ",
        "menu_reminders": "⏰ ਦਵਾਈਆਂ ਦੇ ਰੀਮਾਈਂਡਰ",
        "menu_history": "📜 ਸਲਾਹ-ਮਸ਼ਵਰੇ ਦਾ ਇਤਿਹਾਸ",
        "profile_header": "ਪਰਿਵਾਰਕ ਸਿਹਤ ਪ੍ਰੋਫਾਈਲ ਪ੍ਰਬੰਧਿਤ ਕਰੋ",
        "add_profile": "ਨਵੇਂ ਪਰਿਵਾਰਕ ਮੈਂਬਰ ਦਾ ਪ੍ਰੋਫਾਈਲ ਜੋੜੋ",
        "fullname": "ਪੂਰਾ ਨਾਮ",
        "age": "ਉਮਰ",
        "gender": "ਲਿੰਗ",
        "relationship": "ਸੰਬੰਧ",
        "zip": "ਪਿੰਨ ਕੋਡ (PIN Code)",
        "income": "ਮਾਸਿਕ ਪਰਿਵਾਰਕ ਆਮਦਨ (INR)",
        "pre_existing": "ਪਹਿਲਾਂ ਤੋਂ ਮੌਜੂਦ ਬੀਮਾਰੀਆਂ",
        "allergies": "ਜਾਣੀਆਂ ਜਾਂਦੀਆਂ ਐਲਰਜੀ (ਕੌਮੇ ਨਾਲ ਵੱਖ ਕਰੋ)",
        "create_profile": "ਪ੍ਰੋਫਾਈਲ ਬਣਾਓ",
        "assess_header": "ਮਲਟੀ-ਏਜੰਟ ਏਆਈ ਲੱਛਣ ਜਾਂਚ",
        "select_member": "ਜਾਂਚ ਲਈ ਪਰਿਵਾਰਕ ਮੈਂਬਰ ਦੀ ਚੋਣ ਕਰੋ",
        "describe_symptoms": "ਲੱਛਣਾਂ ਦਾ ਵੇਰਵਾ ਵਿਸਥਾਰ ਨਾਲ ਲਿਖੋ",
        "duration": "ਲੱਛਣਾਂ ਦੀ ਮਿਆਦ (ਜਿਵੇਂ: 2 ਦਿਨ, 1 ਹਫ਼ਤਾ)",
        "start_consultation": "ਮਲਟੀ-ਏਜੰਟ ਸਲਾਹ-ਮਸ਼ਵਰਾ ਸ਼ੁਰੂ ਕਰੋ",
        "emergency_banner": "ਤੁਰੰਤ ਐਮਰਜੈਂਸੀ ਚੇਤਾਵਨੀ (EMERGENCY ALERT)",
        "emergency_subtitle": "ਗੰਭੀਰ ਲੱਛਣ ਮਿਲੇ ਹਨ। ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਦਿੱਤੇ ਨਿਰਦੇਸ਼ਾਂ ਦੀ ਪਾਲਣਾ ਕਰੋ ਅਤੇ ਤੁਰੰਤ ਨਜ਼ਦੀਕੀ ਐਮਰਜੈਂਸੀ ਸਿਹਤ ਕੇਂਦਰ ਜਾਓ।",
        "reminders_header": "ਪਰਿਵਾਰਕ ਦਵਾਈਆਂ ਦੇ ਰੀਮਾਈਂਡਰ ਅਤੇ ਸਮਾਂ ਸਾਰਣੀ",
        "reminders_manual": "ਦਵਾਈ ਦਾ ਸਮਾਂ ਖੁਦ ਜੋੜੋ",
        "med_name": "ਦਵਾਈ ਦਾ ਨਾਮ",
        "dosage": "ਖੁਰਾਕ (ਜਿਵੇਂ: 1 ਗੋਲੀ, 5ml)",
        "frequency": "ਦਵਾਈ ਲੈਣ ਦੀ ਵਾਰ-ਵਾਰਤਾ",
        "time_of_day": "ਸਮਾਂ (HH:MM ਫਾਰਮੈਟ, ਕੌਮੇ ਨਾਲ ਵੱਖ ਕਰੋ)",
        "add_reminder": "ਰੀਮਾਈਂਡਰ ਜੋੜੋ",
        "active_schedules": "ਸਰਗਰਮ ਸਮਾਂ ਸਾਰਣੀ",
        "history_header": "ਹੈਲਥ ਗਾਰਡੀਅਨ ਮੈਡੀਕਲ ਰਿਕਾਰਡ ਅਤੇ ਇਤਿਹਾਸ",
        "encounter_logs": "ਮੈਡੀਕਲ ਸਲਾਹ-ਮਸ਼ਵਰਾ ਲੌਗਸ",
        "dashboard_header": "ਮੰਚ ਦੇ ਅੰਕੜੇ ਅਤੇ ਵਿਸ਼ਲੇਸ਼ਣ",
        "gender_opts": ["ਪੁਰਸ਼ (Male)", "ਮਹਿਲਾ (Female)", "ਹੋਰ (Other)"],
        "rel_opts": ["ਖੁਦ (Self)", "ਪਤੀ/ਪਤਨੀ (Spouse)", "ਬੇਟਾ (Son)", "ਬੇਟੀ (Daughter)", "ਪਿਤਾ (Father)", "ਮਾਤਾ (Mother)", "ਦਾਦਾ/ਨਾਣਾ (Grandfather)", "ਦਾਦੀ/ਨਾਣੀ (Grandmother)"],
        "freq_opts": ["ਰੋਜ਼ਾਨਾ (Daily)", "ਦਿਨ ਵਿੱਚ ਦੋ ਵਾਰ (Twice Daily)", "ਦਿਨ ਵਿੱਚ ਤਿੰਨ ਵਾਰ (Three times daily)", "ਹਫ਼ਤਾਵਾਰੀ (Weekly)"],
        "delete_btn": "ਹਟਾਓ (Delete)",
        "connecting": "ਹੈਲਥਸਫੀਅਰ ਬੈਕਐਂਡ ਸੇਵਾਵਾਂ ਨਾਲ ਜੁੜ ਰਿਹਾ ਹੈ... ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਬੈਕਐਂਡ ਸਰਵਰ ਚੱਲ ਰਿਹਾ ਹੈ।"
    },
    "Odia": {
        "title": "ହେଲ୍ଥସ୍ଫିଅର ଏଆଇ (HealthSphere AI)",
        "subtitle": "ଗ୍ରାମୀଣ ଏବଂ ବଞ୍ଚିତ ଅଞ୍ଚଳ ପାଇଁ ମଲ୍ଟି-ଏଜେଣ୍ଟ ଏଆଇ ସ୍ୱାସ୍ଥ୍ୟ ସେବା ମଞ୍ଚ",
        "emergency_title": "ଗ୍ରାମୀଣ ଜରୁରୀକାଳୀନ ଯୋଗାଯୋଗ",
        "emergency_contacts": "ଆମ୍ବୁଲାନ୍ସ: **108** (ଡାକ୍ତରୀ ଜରୁରୀ) / **102** (ମାତୃତ୍ୱ କଲ୍ୟାଣ)\n\nଜାତୀୟ ଜରୁରୀକାଳୀନ ନମ୍ବର: **112**\n\nସ୍ୱାସ୍ଥ୍ୟ ହେଲ୍ପଲାଇନ: **104** (ଡାକ୍ତରୀ ପରାମର୍ଶ)",
        "menu_dashboard": "📈 ଡ୍ୟାସବୋର୍ଡ ଏବଂ ପରିସଂଖ୍ୟାନ",
        "menu_profiles": "👥 ପାରିବାରିକ ପ୍ରୋଫାଇଲ୍",
        "menu_assessment": "⚕️ ଲକ୍ଷଣ ଯାଞ୍ଚ ଏବଂ ନିଦାନ",
        "menu_reminders": "⏰ ଔଷଧ ସ୍ମାରକୀ",
        "menu_history": "📜 ପରାମର୍ଶ ଇତିହାସ",
        "profile_header": "ପାରିବାରିକ ସ୍ୱାସ୍ଥ୍ୟ ପ୍ରୋଫାଇଲ୍ ପରିଚାଳନା କରନ୍ତୁ",
        "add_profile": "ନୂତନ ସଦସ୍ୟଙ୍କ ପ୍ରୋଫାଇଲ୍ ଯୋଡନ୍ତୁ",
        "fullname": "ପୂରା ନାମ",
        "age": "ବୟସ",
        "gender": "ଲିଙ୍ଗ",
        "relationship": "ସମ୍ପର୍କ",
        "zip": "ପିନ୍ କୋଡ୍ (PIN Code)",
        "income": "ମାସିକ ପାରିବାରିକ ଆୟ (INR)",
        "pre_existing": "ପୂର୍ବରୁ ଥିବା ରୋଗ/ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟା",
        "allergies": "ଜଣାଶୁଣା ଆଲର୍ଜି (କମା ଦେଇ ଅଲଗା କରନ୍ତୁ)",
        "create_profile": "ପ୍ରୋଫାଇଲ୍ ତିଆରି କରନ୍ତୁ",
        "assess_header": "ମଲ୍ଟି-ଏଜେଣ୍ଟ ଏଆଇ ଲକ୍ଷଣ ନିଦାନ",
        "select_member": "ଯାଞ୍ଚ ପାଇଁ ପରିବାର ସଦସ୍ୟ ବାଛନ୍ତୁ",
        "describe_symptoms": "ଲକ୍ଷଣଗୁଡିକ ବିସ୍ତୃତ ଭାବରେ ବର୍ଣ୍ଣନା କରନ୍ତୁ",
        "duration": "ଲକ୍ଷଣର ଅବଧି (ଯେପରିକି: 2 ଦିନ, 1 ସପ୍ତାହ)",
        "start_consultation": "ମଲ୍ଟି-ଏଜେଣ୍ଟ ପରାମର୍ଶ ଆରମ୍ଭ କରନ୍ତୁ",
        "emergency_banner": "ଜରୁରୀକାଳୀନ ସତର୍କତା (EMERGENCY ALERT)",
        "emergency_subtitle": "ଗୁରୁତର ଲକ୍ଷଣ ମିଳିଛି। ଦୟାକରି ନିମ୍ନଲିଖିତ ନିର୍ଦ୍ଦେଶାବଳୀ ପାଳନ କରନ୍ତୁ ଏବଂ ତୁରନ୍ତ ନିକଟସ୍ଥ ଜରຸରୀକାଳୀନ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ରକୁ ଯାଆନ୍ତୁ।",
        "reminders_header": "ପାରିବାରିକ ଔଷଧ ସ୍ମାରକୀ ଏବଂ ସମୟ ସାରଣୀ",
        "reminders_manual": "ଔଷଧ ସମୟ ନିଜେ ଯୋଡନ୍ତୁ",
        "med_name": "ଔ઼ଷଧର ନାମ",
        "dosage": "ଡୋଜ୍ (ଯେପରିକି: 1ଟି ଟାବଲେଟ୍, 5ml)",
        "frequency": "ଔଷଧ ଖାଇବାର ବାରମ୍ବାରତା",
        "time_of_day": "ଔଷଧ ଖାଇବାର ସମୟ (HH:MM ଫର୍ମାଟ୍, କମା ଦେଇ ଅଲଗା କରନ୍ତୁ)",
        "add_reminder": "ସ୍ମାରକୀ ଯୋଡନ୍ତୁ",
        "active_schedules": "ସକ୍ରିୟ ସମୟ ସାରଣୀ",
        "history_header": "ହେଲ୍ଥ ଗାର୍ଡିଆନ୍ ମେଡିକାଲ୍ ରେକର୍ଡ ଏବଂ ଇତିହାସ",
        "encounter_logs": "ଡାକ୍ତରୀ ପରାମର୍ଶ ଲଗ୍",
        "dashboard_header": "ମଞ୍ଚର ଆକଳନ ଏବଂ ବିଶ୍ଳେଷଣ",
        "gender_opts": ["ପୁରୁଷ (Male)", "ମହିଳା (Female)", "ଅନ୍ୟାନ୍ୟ (Other)"],
        "rel_opts": ["ନିଜେ (Self)", "ସ୍ୱାମୀ/ସ୍ତ୍ରୀ (Spouse)", "ପୁଅ (Son)", "ଝିଅ (Daughter)", "ବାପା (Father)", "ମାଆ (Mother)", "ଜେଜେବାପା/ଅଜା (Grandfather)", "ଜେଜେମା/ଆଈ (Grandmother)"],
        "freq_opts": ["ପ୍ରତିଦିન (Daily)", "ଦିନକୁ ଦୁଇଥର (Twice Daily)", "ଦିନକୁ ତିନିଥର (Three times daily)", "ସାପ୍ତାହିକ (Weekly)"],
        "delete_btn": "କାଢି ଦିଅନ୍ତୁ (Delete)",
        "connecting": "ହେଲ୍ଥସ୍ଫିଅର ବ୍ୟାକଏଣ୍ଡ ସେବା ସହିତ ସଂଯୋଗ ହେଉଛି... ବ୍ୟାକଏଣ୍ଡ ସର୍ଭର ଚାଲୁଥିବା ନିଶ୍ଚିତ କରନ୍ତୁ।"
    }
}

# Sidebar Language Selection
with st.sidebar:
    st.markdown("### 🌐 Language / भाषा")
    selected_language = st.selectbox("Choose Language", ["English", "Hindi"], label_visibility="collapsed")
    
t = LANG_DICT[selected_language]

# --- HEADER & NAVIGATION ---
st.markdown(f'<h1 class="main-title">{t["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)

# Check API health
backend_status = api_get("")
if not backend_status:
    st.warning(f"⚠️ {t['connecting']}")
    st.info("💡 You can launch both services together using: `python run.py`")
    st.stop()

# Sidebar Navigation continue
with st.sidebar:
    st.markdown(f"### ❇️ {t['menu_dashboard'].split()[-1] if len(t['menu_dashboard'].split()) > 1 else 'Navigation'}")
    menu = st.radio(
        "Select Workspace",
        [t["menu_dashboard"], t["menu_profiles"], t["menu_assessment"], t["menu_reminders"], t["menu_history"]],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(f"### 📞 {t['emergency_title']}")
    st.error(t["emergency_contacts"])
    
    st.markdown("---")
    st.caption("Powered by Gemini 2.5 Flash & SQLite/ChromaDB")

# Map localized menu back to English keys
menu_key = "dashboard"
if menu == t["menu_profiles"]:
    menu_key = "profiles"
elif menu == t["menu_assessment"]:
    menu_key = "assessment"
elif menu == t["menu_reminders"]:
    menu_key = "reminders"
elif menu == t["menu_history"]:
    menu_key = "history"

# Initialize vault lock state
if "vault_unlocked" not in st.session_state:
    st.session_state.vault_unlocked = False

# Vault lock verification for private pages
if menu_key in ["profiles", "assessment", "reminders", "history"]:
    if not st.session_state.vault_unlocked:
        st.markdown("---")
        
        # Vault Lock Translations
        vault_trans = {
            "English": {"header": "🔒 Family Health Vault", "desc": "Enter the 4-digit passcode to unlock private family health records.", "btn": "Unlock Vault", "pass": "Enter Vault Passcode", "err": "Invalid Passcode!"},
            "Hindi": {"header": "🔒 पारिवारिक स्वास्थ्य तिजोरी", "desc": "निजी स्वास्थ्य रिकॉर्ड अनलॉक करने के लिए ४-अंकीय पासकोड दर्ज करें।", "btn": "तिजोरी खोलें", "pass": "पासकोड दर्ज करें", "err": "अमान्य पासकोड!"},
            "Bengali": {"header": "🔒 পারিবারিক স্বাস্থ্য ভল্ট", "desc": "ব্যক্তিগত স্বাস্থ্য রেকর্ড আনলক করতে ৪-সংখ্যার পাসকোড লিখুন।", "btn": "ভল্ট আনলক করুন", "pass": "পাসকোড লিখুন", "err": "ভুল পাসকোড!"},
            "Telugu": {"header": "🔒 కుటుంబ ఆరోగ్య వాల్ట్", "desc": "వ్యక్తిగत ఆరోగ్య రికార్డులను అన్‌లాక్ చేయడానికి 4-అంకెల పాస్‌కోడ్‌ను నమోదు చేయండి.", "btn": "వాల్ట్‌ను అన్‌లాక్ చేయి", "pass": "పాస్‌కోడ్‌ను నమోదు చేయండి", "err": "చెల్లని పాస్‌కోడ్!"},
            "Tamil": {"header": "🔒 குடும்ப சுகாதார பெட்டகம்", "desc": "தனிப்பட்ட சுகாதார பதிவுகளைத் திறக்க 4-இலக்க கடவுச்சொல்லை உள்ளிடவும்.", "btn": "பெட்டகத்தைத் திற", "pass": "கடவுச்சொல்லை உள்ளிடவும்", "err": "தவறான கடவுச்சொல்!"},
            "Marathi": {"header": "🔒 कौटुंबिक आरोग्य तिजोरी", "desc": "खाजगी आरोग्य रेकॉर्ड अनलॉक करण्यासाठी ४-अंकी पासकोड प्रविष्ट करा.", "btn": "तिजोरी अनलॉक करा", "pass": "पासकोड प्रविष्ट करा", "err": "अमान्य पासकोड!"},
            "Kannada": {"header": "🔒 ಕೌಟುಂಬಿಕ ಆರೋಗ್ಯ ವಾಲ್ಟ್", "desc": "ಖಾಸಗಿ ಆರೋಗ್ಯ ದಾಖಲೆಗಳನ್ನು ಅನ್‌ಲಾಕ್ ಮಾಡಲು 4-ಅಂಕಿಯ ಪಾಸ್‌ಕೋಡ್ ನಮೂದಿಸಿ.", "btn": "ವಾಲ್ಟ್ ಅನ್ಲಾಕ್ ಮಾಡಿ", "pass": "ಪಾಸ್ಕೋಡ್ ನಮೂದಿಸಿ", "err": "ಅಮಾನ್ಯ ಪಾಸ್‌ಕೋಡ್!"},
            "Malayalam": {"header": "🔒 കുടുംബ ആരോഗ്യ വോൾട്ട്", "desc": "സ്വകാര്യ ആരോഗ്യ രേഖകൾ അൺലോക്ക് ചെയ്യാൻ 4-അക്ക പാസ്‌കോഡ് നൽകുക.", "btn": "വോൾട്ട് അൺലോക്ക് ചെയ്യുക", "pass": "പാസ്‌കോഡ് നൽകുക", "err": "തെറ്റായ പാസ്‌കോഡ്!"},
            "Gujarati": {"header": "🔒 પારિવારિક આરોગ્ય તિજોરી", "desc": "ખાનગી આરોગ્ય રેકોર્ડ્સ અનલોક કરવા માટે 4-અંકનો પાસકોડ દાખલ કરો.", "btn": "તિજોરી અનલોક કરો", "pass": "પાસકોડ દાખલ કરો", "err": "અમાન્ય પાસકોડ!"},
            "Punjabi": {"header": "🔒 ਪਰਿਵਾਰਕ ਸਿਹਤ ਵਾਲਟ", "desc": "ਨਿੱਜੀ ਸਿਹਤ ਰਿਕਾਰਡ ਖੋਲ੍ਹਣ ਲਈ 4-ਅੰਕਾਂ ਦਾ ਪਾਸਕੋਡ ਦਰਜ ਕਰੋ।", "btn": "ਵਾਲਟ ਖੋਲ੍ਹੋ", "pass": "ਪਾਸਕੋਡ ਦਰਜ ਕਰੋ", "err": "ਗਲਤ ਪਾਸਕੋਡ!"},
            "Odia": {"header": "🔒 ପାରିବାରିକ ସ୍ୱାସ୍ଥ୍ୟ ଭଲ୍ଟ", "desc": "ବ୍ୟକ୍ତିଗତ ସ୍ୱାସ୍ଥ୍ୟ ରେକର୍ଡ ଅନଲକ କରିବାକୁ 4-ଅଙ୍କ ବିଶିษฐ ପାସକୋଡ୍ ପ୍ରବେଶ କରନ୍ତୁ।", "btn": "ଭଲ୍ଟ ଅନଲକ୍ କରନ୍ତୁ", "pass": "ପାସକୋଡ୍ ପ୍ରବେଶ କରନ୍ତୁ", "err": "ଅବୈଧ ପାସକୋଡ୍!"}
        }
        
        vt = vault_trans.get(selected_language, vault_trans["English"])
        
        st.markdown(f"""
        <div class="vault-box">
            <div class="vault-icon">🔒</div>
            <h2 style="color: #a855f7; margin-top:0; font-family:'Outfit';">{vt["header"]}</h2>
            <p style="color: #94a3b8; font-size: 1rem; margin-bottom: 20px;">{vt["desc"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c, _ = st.columns([2, 3])
        with col_c:
            entered_passcode = st.text_input(vt["pass"], type="password", key="family_vault_passcode")
            if st.button(vt["btn"]):
                correct_passcode = os.getenv("FAMILY_VAULT_PASSCODE", "1234")
                if entered_passcode == correct_passcode:
                    st.session_state.vault_unlocked = True
                    st.success("Vault Unlocked!")
                    st.rerun()
                else:
                    st.error(vt["err"])
        st.stop()

# --- DASHBOARD & INSIGHTS ---
if menu_key == "dashboard":
    st.markdown(f"## {t['dashboard_header']}")
    
    stats = api_get("dashboard/stats")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats['total_profiles']}</div>
                <div class="stat-label">{"पारिवारिक प्रोफाइल" if selected_language=="Hindi" else "Family Profiles"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-color: rgba(5, 117, 230, 0.3)">
                <div class="stat-value" style="color: #0575E6">{stats['total_encounters']}</div>
                <div class="stat-label">{"लक्षण जांच" if selected_language=="Hindi" else "Symptom Checks"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-color: rgba(229, 62, 62, 0.3)">
                <div class="stat-value" style="color: #E53E3E">{stats['emergency_alerts_count']}</div>
                <div class="stat-label">{"आपातकालीन चेतावनियां" if selected_language=="Hindi" else "Emergency Alerts"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="stat-card" style="border-color: rgba(236, 201, 75, 0.3)">
                <div class="stat-value" style="color: #ECC94B">{stats['active_reminders_count']}</div>
                <div class="stat-label">{"सक्रिय अनुस्मारक" if selected_language=="Hindi" else "Active Reminders"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk Trends chart
        st.markdown("### " + ("जोखिम स्तर का इतिहास (Triage History Timeline)" if selected_language=="Hindi" else "Risk Trends (Historical Triage Timeline)"))
        if stats['risk_trends']:
            df = pd.DataFrame(stats['risk_trends'])
            df['risk_score'] = df['risk_score'].astype(float)
            st.line_chart(df.set_index('date')['risk_score'])
        else:
            st.info("No consultation logs yet to plot trends. Complete a Symptom Assessment to see details here.")
            
        # Recent consultations table
        st.markdown("### " + ("हाल के चिकित्सकीय परामर्श" if selected_language=="Hindi" else "Recent Consultations"))
        if stats['recent_encounters']:
            recent_df = pd.DataFrame(stats['recent_encounters'])
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No consultation logs available.")
    else:
        st.info("Waiting for database connection...")

# --- FAMILY PROFILES ---
elif menu_key == "profiles":
    st.markdown(f"## 👥 {t['profile_header']}")
    
    # Form to add a profile
    with st.expander(f"➕ {t['add_profile']}", expanded=False):
        with st.form("add_profile_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input(t["fullname"], placeholder="e.g. Ramesh Kumar")
                age = st.number_input(t["age"], min_value=0, max_value=120, value=30)
            with col2:
                gender_selected = st.selectbox(t["gender"], t["gender_opts"])
                # Extract English value for DB
                gender = "Male" if "Male" in gender_selected or "पुरुष" in gender_selected else "Female" if "Female" in gender_selected or "महिला" in gender_selected else "Other"
                
                rel_selected = st.selectbox(t["relationship"], t["rel_opts"])
                # Extract English value for DB mapping
                relationship_map = {
                    t["rel_opts"][0]: "Self", t["rel_opts"][1]: "Spouse", t["rel_opts"][2]: "Son", t["rel_opts"][3]: "Daughter",
                    t["rel_opts"][4]: "Father", t["rel_opts"][5]: "Mother", t["rel_opts"][6]: "Grandfather", t["rel_opts"][7]: "Grandmother"
                }
                relationship = relationship_map.get(rel_selected, "Self")
            with col3:
                zip_code = st.text_input(t["zip"], placeholder="e.g. 302001 (PIN Code)")
                income = st.number_input(t["income"], min_value=0.0, value=15000.0, step=500.0)
                
            col_med, col_all = st.columns(2)
            with col_med:
                med_conditions_opts = ["Diabetes", "Hypertension (High BP)", "Asthma", "Tuberculosis", "Chronic Heart Disease", "Kidney Disease", "Pregnancy", "Anemia"]
                if selected_language == "Hindi":
                    med_conditions_opts_translated = ["मधुमेह (Diabetes)", "उच्च रक्तचाप (High BP)", "दमा (Asthma)", "तपेदिक (Tuberculosis)", "हृदय रोग (Heart Disease)", "गुर्दे की बीमारी (Kidney Disease)", "गर्भावस्था (Pregnancy)", "रक्तहीनता (Anemia)"]
                    med_conditions_selected = st.multiselect(t["pre_existing"], med_conditions_opts_translated)
                    # Map back
                    trans_map = dict(zip(med_conditions_opts_translated, med_conditions_opts))
                    med_conditions = [trans_map[c] for c in med_conditions_selected]
                else:
                    med_conditions = st.multiselect(t["pre_existing"], med_conditions_opts)
            with col_all:
                allergies = st.text_input(t["allergies"], placeholder="e.g. Penicillin, Dust")
                
            submitted = st.form_submit_button(t["create_profile"])
            if submitted:
                if not name or not zip_code:
                    st.error("Please fill in Name and PIN Code." if selected_language=="English" else "कृपया नाम और पिन कोड दर्ज करें।")
                else:
                    allergies_list = [a.strip() for a in allergies.split(",") if a.strip()]
                    payload = {
                        "name": name,
                        "age": int(age),
                        "gender": gender,
                        "relationship": relationship,
                        "medical_history": med_conditions,
                        "allergies": allergies_list,
                        "location_zip": zip_code,
                        "monthly_income": float(income)
                    }
                    res = api_post("profiles", payload)
                    if res:
                        st.success(f"Successfully created profile for {name} ({relationship})!" if selected_language=="English" else f"{name} ({relationship}) के लिए सफलतापूर्वक प्रोफाइल बनाई गई!")
                        st.rerun()

    # List Profiles
    profiles = api_get("profiles")
    if profiles:
        st.markdown("### " + ("सक्रिय पारिवारिक सदस्य" if selected_language=="Hindi" else "Active Family Members"))
        for p in profiles:
            with st.container():
                history_str = ", ".join(p['medical_history']) if p['medical_history'] else ("कोई नहीं" if selected_language=="Hindi" else "None")
                allergies_str = ", ".join(p['allergies']) if p['allergies'] else ("कोई नहीं" if selected_language=="Hindi" else "None")
                
                # Show relationship in localized language
                rel_localized = p['relationship']
                if selected_language == "Hindi":
                    rel_trans = {"Self": "स्वयं", "Spouse": "पति/पत्नी", "Son": "बेटा", "Daughter": "बेटी", "Father": "पिता", "Mother": "माता", "Grandfather": "दादा/नाना", "Grandmother": "दादी/नानी"}
                    rel_localized = rel_trans.get(p['relationship'], p['relationship'])

                st.markdown(f"""
                <div class="card">
                    <h3 style="margin-top:0; color: #00F260;">👤 {p['name']} ({rel_localized})</h3>
                    <div style="display:flex; gap: 40px; flex-wrap: wrap; margin-bottom: 10px;">
                        <div><strong>{"आयु (Age)" if selected_language=="Hindi" else "Age"}:</strong> {p['age']}</div>
                        <div><strong>{"लिंग" if selected_language=="Hindi" else "Gender"}:</strong> {p['gender']}</div>
                        <div><strong>{"पिन कोड" if selected_language=="Hindi" else "PIN Code"}:</strong> {p['location_zip']}</div>
                        <div><strong>{"मासिक पारिवारिक आय" if selected_language=="Hindi" else "Monthly Income"}:</strong> Rs. {p['monthly_income']:,}</div>
                    </div>
                    <div><strong>{"पहले से मौजूद बीमारियां" if selected_language=="Hindi" else "Pre-existing Conditions"}:</strong> {history_str}</div>
                    <div><strong>{"ज्ञात एलर्जी" if selected_language=="Hindi" else "Known Allergies"}:</strong> {allergies_str}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_del, _ = st.columns([1, 10])
                with col_del:
                    if st.button(t["delete_btn"], key=f"del_{p['id']}"):
                        if api_delete(f"profiles/{p['id']}"):
                            st.success(f"Deleted profile." if selected_language=="English" else "प्रोफाइल हटा दी गई है।")
                            st.rerun()
    else:
        st.info("No family profiles found. Please add a profile to get started." if selected_language=="English" else "कोई पारिवारिक प्रोफाइल नहीं मिली। शुरू करने के लिए कृपया एक प्रोफाइल जोड़ें।")

# --- SYMPTOM ASSESSMENT ---
elif menu_key == "assessment":
    st.markdown(f"## ⚕️ {t['assess_header']}")
    
    profiles = api_get("profiles")
    if not profiles:
        st.warning(f"⚠️ {t['connecting']}")
        st.stop()
        
    profile_options = {p['id']: f"{p['name']} ({p['relationship']})" for p in profiles}
    selected_profile_id = st.selectbox(t["select_member"], options=list(profile_options.keys()), format_func=lambda x: profile_options[x])
    
    symptoms = st.text_area(t["describe_symptoms"], placeholder="e.g. Ramesh is having a high fever since last night, severe cough... " if selected_language=="English" else "उदा. रमेश को कल रात से तेज बुखार, गंभीर खांसी और सांस लेने में कठिनाई हो रही है...")
    duration = st.text_input(t["duration"], placeholder="e.g. 2 days, 1 week" if selected_language=="English" else "उदा. 2 दिन, 1 हफ्ता")
    
    if st.button(t["start_consultation"]):
        if not symptoms:
            st.error("Please enter symptoms before initiating." if selected_language=="English" else "परामर्श शुरू करने से पहले कृपया लक्षण दर्ज करें।")
        else:
            st.markdown("---")
            st.markdown("### ⚙️ " + ("मल्टी-एजेंट एआई इंजन (Orchestration Engine)" if selected_language=="Hindi" else "Multi-Agent Orchestration Engine"))
            
            # Placeholders for progress steps
            status_hg = st.empty()
            status_em = st.empty()
            status_sa = st.empty()
            status_ra = st.empty()
            status_mr = st.empty()
            status_hd = st.empty()
            status_gb = st.empty()
            status_tg = st.empty()
            status_mr2 = st.empty()
            
            status_hg.info("🔄 Health Guardian Memory Agent: Querying history..." if selected_language=="English" else "🔄 हेल्थ गार्जियन मेमोरी एजेंट: रोगी के चिकित्सा इतिहास की जांच की जा रही है...")
            import time
            time.sleep(0.5)
            
            status_em.info("🔄 Emergency Agent: Checking emergency alerts..." if selected_language=="English" else "🔄 आपातकालीन एजेंट: गंभीर लक्षणों और चेतावनी संकेतों की जांच की जा रही है...")
            time.sleep(0.5)
            
            payload = {
                "profile_id": selected_profile_id,
                "raw_symptoms": symptoms,
                "duration": duration if duration else "unknown",
                "language": selected_language
            }
            
            res = api_post("consult", payload)
            
            if res:
                status_hg.success("✅ Health Guardian Memory Agent: History context loaded." if selected_language=="English" else "✅ हेल्थ गार्जियन मेमोरी एजेंट: पूर्व चिकित्सा इतिहास संकलित कर लिया गया है।")
                
                if res['severity_level'] == "EMERGENCY":
                    status_em.error("🚨 Emergency Agent: EMERGENCY DETECTED! Escalating." if selected_language=="English" else "🚨 आपातकालीन एजेंट: गंभीर आपातकाल का पता चला है! सामान्य प्रवाह रोका गया।")
                    status_sa.write("⚠️ Symptom Analysis: Suspended" if selected_language=="English" else "⚠️ लक्षण विश्लेषण: निलंबित (आपातकालीन मोड)")
                    status_ra.write("⚠️ Risk Assessment: Suspended" if selected_language=="English" else "⚠️ जोखिम मूल्यांकन: निलंबित (आपातकालीन मोड)")
                    status_mr.write("⚠️ Medical Research: Suspended" if selected_language=="English" else "⚠️ चिकित्सा अनुसंधान: निलंबित (आपातकालीन मोड)")
                    status_hd.success("✅ Hospital Discovery Agent: Emergency Clinics Found." if selected_language=="English" else "✅ अस्पताल खोज एजेंट: आपातकालीन क्लीनिकों की पहचान कर ली गई है।")
                    status_gb.write("⚠️ Government Benefits: Suspended" if selected_language=="English" else "⚠️ सरकारी योजनाएं: निलंबित (आपातकालीन मोड)")
                    status_tg.success("✅ Treatment Guidance Agent: Emergency Triage Ready." if selected_language=="English" else "✅ उपचार मार्गदर्शन एजेंट: प्राथमिक उपचार निर्देश तैयार हैं।")
                    status_mr2.write("⚠️ Medicine Reminder: Suspended" if selected_language=="English" else "⚠️ दवा अनुस्मारक: निलंबित (आपातकालीन मोड)")
                else:
                    status_em.success("✅ Emergency Agent: No emergency triggers." if selected_language=="English" else "✅ आपातकालीन एजेंट: कोई गंभीर जीवन-घातक संकेत नहीं मिले।")
                    status_sa.success("✅ Symptom Analysis Agent: Symptoms parsed." if selected_language=="English" else "✅ लक्षण विश्लेषण एजेंट: लक्षणों का वर्गीकरण पूर्ण हुआ।")
                    status_ra.success(f"✅ Risk Assessment Agent: Score = {res['risk_score']}/10.0" if selected_language=="English" else f"✅ जोखिम मूल्यांकन एजेंट: अनुमानित जोखिम स्कोर = {res['risk_score']} / 10.0")
                    status_mr.success("✅ Medical Research Agent: Knowledge retrieved." if selected_language=="English" else "✅ चिकित्सा अनुसंधान एजेंट: नैदानिक ज्ञान डेटाबेस लोड किया गया।")
                    status_hd.success("✅ Hospital Discovery Agent: Clinics matched." if selected_language=="English" else "✅ अस्पताल खोज एजेंट: नजदीकी स्वास्थ्य केंद्रों का मिलान पूर्ण हुआ।")
                    status_gb.success("✅ Government Benefits Agent: Schemes checked." if selected_language=="English" else "✅ सरकारी योजना एजेंट: कल्याणकारी योजनाओं की जांच पूरी हुई।")
                    status_tg.success("✅ Treatment Guidance Agent: Plan formulated." if selected_language=="English" else "✅ उपचार मार्गदर्शन एजेंट: सुरक्षात्मक उपाय तैयार हैं।")
                    status_mr2.success("✅ Medicine Reminder Agent: Reminders generated." if selected_language=="English" else "✅ दवा अनुस्मारक एजेंट: दवा समय सारिणी का मसौदा तैयार है।")

                st.markdown("---")
                
                # Severity Box
                sev = res['severity_level'].upper()
                if sev == "EMERGENCY":
                    st.markdown(f"""
                    <div class="emergency-banner">
                        <h2 style="margin: 0; font-size: 2.2rem;">{t["emergency_banner"]}</h2>
                        <p style="margin: 5px 0 0 0; font-size: 1.1rem;">{t["emergency_subtitle"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    border_cls = "severity-low"
                    if sev == "MEDIUM":
                        border_cls = "severity-medium"
                    elif sev == "HIGH":
                        border_cls = "severity-high"
                    elif sev == "EMERGENCY":
                        border_cls = "severity-emergency"
                        
                    st.markdown(f"""
                    <div class="card {border_cls}">
                        <h3 style="margin-top:0;">📋 {"नैदानिक आकलन (Assessment Details)" if selected_language=="Hindi" else "Diagnostic Assessment"}</h3>
                        <div style="font-size: 1.1rem; margin-bottom: 8px;"><strong>{"गंभीरता स्तर (Severity Level)" if selected_language=="Hindi" else "Severity Level"}:</strong> <span style="font-weight:700; color:{'#E53E3E' if sev=='EMERGENCY' else '#ED8936' if sev=='HIGH' else '#ECC94B' if sev=='MEDIUM' else '#00F260'}">{sev}</span></div>
                        <div style="font-size: 1.1rem; margin-bottom: 8px;"><strong>{"जोखिम स्कोर (Risk Score)" if selected_language=="Hindi" else "Risk Score"}:</strong> <b>{res['risk_score']:.1f} / 10.0</b></div>
                        <div><strong>{"लक्षणों का संक्षेप (Summary)" if selected_language=="Hindi" else "Symptom Summary"}:</strong> {res['symptom_summary']}</div>
                        <br>
                        <div><strong>{"चिकित्सा अनुसंधान संदर्भ (Clinical Notes)" if selected_language=="Hindi" else "Clinical Research References"}:</strong></div>
                        <p style="color: #cbd5e0; font-size: 0.95rem; font-style: italic;">{res['clinical_notes']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Government Schemes
                    st.markdown("### " + ("🎗️ सरकारी स्वास्थ्य योजना पात्रता (Government Benefits)" if selected_language=="Hindi" else "🇮🇳 Government Healthcare Scheme Matching"))
                    if res['benefits_identified']:
                        for b in res['benefits_identified']:
                            st.markdown(f"""
                            <div class="card" style="border: 1px solid rgba(255, 153, 51, 0.3)">
                                <h4 style="margin-top:0; color: #FF9933;">🎗️ {b['name']}</h4>
                                <p style="font-size: 0.9rem; color: #a0aec0; margin-bottom: 8px;">{b['description']}</p>
                                <div><strong>{"मुख्य लाभ (Benefits)" if selected_language=="Hindi" else "Benefits"}:</strong> {b['benefits_summary']}</div>
                                <div><strong>{"पात्रता मापदंड (Eligibility Reason)" if selected_language=="Hindi" else "Eligibility check"}:</strong> {b['eligibility_reason']}</div>
                                <div style="margin-top: 8px;"><strong>{"पंजीकरण प्रक्रिया (How to Register)" if selected_language=="Hindi" else "How to Register"}:</strong></div>
                                <ul style="margin: 0; padding-left: 20px; font-size: 0.9rem;">
                                    {"".join([f"<li>{step}</li>" for step in b['application_steps']])}
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No matching government schemes discovered based on this patient's profile age or family income." if selected_language=="English" else "इस पारिवारिक सदस्य की आयु या पारिवारिक आय के आधार पर कोई सरकारी कल्याणकारी योजना नहीं मिली।")
                        
                with col_right:
                    st.markdown("### " + ("🏥 उपचार मार्गदर्शन और योजना (Care Guidance)" if selected_language=="Hindi" else "🏥 Treatment Guidance & Action Plan"))
                    st.markdown(res['home_care_guidance'])

                st.markdown("---")
                
                # Hospital Discovery
                st.markdown("### " + ("🏥 अनुशंसित नजदीकी स्वास्थ्य केंद्र (Healthcare Centers)" if selected_language=="Hindi" else "🏥 Recommended Local Healthcare Centers"))
                if res['hospitals_recommended']:
                    cols = st.columns(len(res['hospitals_recommended']))
                    for idx, h in enumerate(res['hospitals_recommended']):
                        with cols[idx]:
                            spec_str = ", ".join(h['specialties'])
                            st.markdown(f"""
                            <div class="card" style="min-height: 250px;">
                                <h4 style="margin-top:0; color: #4facfe;">📍 {h['name']}</h4>
                                <div style="font-size: 0.9rem; margin-bottom: 5px;"><b>{"दूरी (Distance)" if selected_language=="Hindi" else "Distance"}:</b> {h['distance_miles']:.1f} miles</div>
                                <div style="font-size: 0.9rem; margin-bottom: 5px;"><b>{"फ़ोन (Phone)" if selected_language=="Hindi" else "Phone"}:</b> {h['contact_number']}</div>
                                <div style="font-size: 0.9rem; margin-bottom: 5px;"><b>{"पता (Address)" if selected_language=="Hindi" else "Address"}:</b> {h['address']}</div>
                                <div style="font-size: 0.9rem; margin-bottom: 8px;"><b>{"विभाग (Specialties)" if selected_language=="Hindi" else "Departments"}:</b> {spec_str}</div>
                                <p style="font-size: 0.85rem; color: #a0aec0; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;"><b>{"सुझाव कारण" if selected_language=="Hindi" else "Why"}:</b> {h['routing_reason']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No local hospitals found.")

                # Proposed Reminders Scheduler
                if res['medications_suggested']:
                    st.markdown(f"### {t['menu_reminders']}")
                    st.info("The multi-agent system parsed medications from clinical guidance. Click the checkbox next to the ones you want to add, then select 'Confirm and Schedule'." if selected_language=="English" else "एआई सिस्टम ने उपचार से कुछ दवाएं चुनी हैं। जिन दवाओं को आप अपनी दैनिक दिनचर्या में जोड़ना चाहते हैं, उनके आगे का बॉक्स टिक करें और पुष्टि करें।")
                    
                    with st.form("reminders_scheduler_form"):
                        checklist = []
                        for idx, med in enumerate(res['medications_suggested']):
                            st.markdown(f"**{"दवा का नाम" if selected_language=="Hindi" else "Medicine"}:** {med['medication_name']} | **{"खुराक (Dose)" if selected_language=="Hindi" else "Dose"}:** {med['dosage']} | **{"बारंबारता (Freq)" if selected_language=="Hindi" else "Frequency"}:** {med['frequency']} ({med['time_of_day']})")
                            to_add = st.checkbox("Select to schedule" if selected_language=="English" else "अनुसूची में जोड़ें", value=True, key=f"chk_med_{idx}")
                            checklist.append((med, to_add))
                            st.markdown("---")
                            
                        schedule_btn = st.form_submit_button("Confirm and Schedule Selected Reminders" if selected_language=="English" else "चयनित दवाओं की अनुसूची निर्धारित करें")
                        if schedule_btn:
                            added_count = 0
                            for item, check in checklist:
                                if check:
                                    reminder_payload = {
                                        "profile_id": selected_profile_id,
                                        "medication_name": item['medication_name'],
                                        "dosage": item['dosage'],
                                        "frequency": item['frequency'],
                                        "time_of_day": item['time_of_day']
                                    }
                                    res_rem = api_post("reminders", reminder_payload)
                                    if res_rem:
                                        added_count += 1
                            if added_count > 0:
                                st.success(f"Successfully scheduled {added_count} medication reminders for {profile_options[selected_profile_id]}!" if selected_language=="English" else f"सफलतापूर्वक {profile_options[selected_profile_id]} के लिए {added_count} दवा अनुस्मारक जोड़ दिए गए हैं!")
                                time.sleep(1.0)
                                st.rerun()

# --- MEDICATION REMINDERS ---
elif menu_key == "reminders":
    st.markdown(f"## ⏰ {t['reminders_header']}")
    
    profiles = api_get("profiles")
    if not profiles:
        st.warning(f"⚠️ {t['connecting']}")
        st.stop()
        
    profile_options = {p['id']: f"{p['name']} ({p['relationship']})" for p in profiles}
    selected_profile_id = st.selectbox(t["select_member"], options=list(profile_options.keys()), format_func=lambda x: profile_options[x])

    # Form to add reminder manually
    with st.expander(f"➕ {t['reminders_manual']}"):
        with st.form("manual_reminder_form"):
            col1, col2 = st.columns(2)
            with col1:
                med_name = st.text_input(t["med_name"], placeholder="e.g. Dolo 650")
                dosage = st.text_input(t["dosage"], placeholder="e.g. 500mg or 1 tablet")
            with col2:
                freq_selected = st.selectbox(t["frequency"], t["freq_opts"])
                # Extract English frequency for DB consistency
                freq_map = {t["freq_opts"][0]: "Daily", t["freq_opts"][1]: "Twice Daily", t["freq_opts"][2]: "Three times daily", t["freq_opts"][3]: "Weekly"}
                frequency = freq_map.get(freq_selected, "Daily")
                
                time_of_day = st.text_input(t["time_of_day"], placeholder="e.g. 08:00, 20:00")
                
            submitted = st.form_submit_button(t["add_reminder"])
            if submitted:
                if not med_name or not time_of_day:
                    st.error("Please fill in Medicine Name and Time of Day." if selected_language=="English" else "कृपया दवा का नाम और समय दर्ज करें।")
                else:
                    payload = {
                        "profile_id": selected_profile_id,
                        "medication_name": med_name,
                        "dosage": dosage,
                        "frequency": frequency,
                        "time_of_day": time_of_day
                    }
                    res = api_post("reminders", payload)
                    if res:
                        st.success("Medication reminder added!" if selected_language=="English" else "दवा अनुस्मारक सफलतापूर्वक जोड़ा गया!")
                        st.rerun()

    # Get reminders
    reminders = api_get(f"profiles/{selected_profile_id}/reminders")
    if reminders:
        st.markdown(f"### {t['active_schedules']}")
        
        for r in reminders:
            col_card, col_act = st.columns([5, 1])
            
            status_text = "🟢 सक्रिय (ACTIVE)" if r['is_active'] else "🔴 निष्क्रिय (INACTIVE)" if selected_language=="Hindi" else "🟢 ACTIVE" if r['is_active'] else "🔴 INACTIVE"
            btn_text = ("निष्क्रिय करें" if r['is_active'] else "सक्रिय करें") if selected_language=="Hindi" else ("Deactivate" if r['is_active'] else "Activate")
            
            with col_card:
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {'#00F260' if r['is_active'] else '#E53E3E'}; padding-top: 10px; padding-bottom: 10px; margin-bottom: 5px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin: 0; color: #4facfe;">💊 {r['medication_name']} ({r['dosage']})</h4>
                        <span><b>Status:</b> {status_text}</span>
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 5px; color: #a0aec0;">
                        <b>Timing:</b> {r['frequency']} at {r['time_of_day']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_act:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button(btn_text, key=f"tgl_{r['id']}"):
                    api_put(f"reminders/{r['id']}", {"is_active": not r['is_active']})
                    st.rerun()
                if st.button(t["delete_btn"], key=f"rem_del_{r['id']}"):
                    if api_delete(f"reminders/{r['id']}"):
                        st.rerun()
    else:
        st.info("No active medication reminders found for this profile." if selected_language=="English" else "इस प्रोफाइल के लिए कोई सक्रिय दवा अनुस्मारक नहीं मिला।")

# --- CONSULTATION HISTORY ---
elif menu_key == "history":
    st.markdown(f"## 📜 {t['history_header']}")
    
    profiles = api_get("profiles")
    if not profiles:
        st.warning(f"⚠️ {t['connecting']}")
        st.stop()
        
    profile_options = {p['id']: f"{p['name']} ({p['relationship']})" for p in profiles}
    selected_profile_id = st.selectbox(t["select_member"], options=list(profile_options.keys()), format_func=lambda x: profile_options[x])

    encounters = api_get(f"encounters/profile/{selected_profile_id}")
    
    if encounters:
        st.markdown(f"### {t['encounter_logs']} ({len(encounters)} records)")
        
        for idx, e in enumerate(encounters):
            date_formatted = datetime.fromisoformat(e['created_at'].replace('Z', '')).strftime('%B %d, %Y - %I:%M %p')
            severity = e['severity_level']
            
            border_cls = "severity-low"
            if severity == "MEDIUM":
                border_cls = "severity-medium"
            elif severity == "HIGH":
                border_cls = "severity-high"
            elif severity == "EMERGENCY":
                border_cls = "severity-emergency"

            with st.expander(f"📅 Encounter on {date_formatted} | Severity: {severity} | Risk Score: {e['risk_score']:.1f}", expanded=(idx==0)):
                st.markdown(f"""
                <div class="card {border_cls}">
                    <h4>{"मरीज के शब्द (Raw Symptoms):" if selected_language=="Hindi" else "Raw Symptoms reported:"}</h4>
                    <p style="color: #e2e8f0; font-size: 0.95rem;">"{e['raw_symptoms']}" ({"अवधि" if selected_language=="Hindi" else "Duration"}: {e['duration']})</p>
                    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">
                    <h4>{"लक्षण विश्लेषण संक्षेप (Symptom Summary):" if selected_language=="Hindi" else "Symptom Analyzer Summary:"}</h4>
                    <p style="color: #cbd5e0; font-size: 0.95rem;">{e['symptom_summary']}</p>
                    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">
                    <h4>{"नैदानिक संदर्भ टिप्पणी (Clinical Reference):" if selected_language=="Hindi" else "Medical Research & Evidence Notes:"}</h4>
                    <p style="color: #cbd5e0; font-size: 0.95rem;">{e['clinical_notes']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("### " + ("उपचार योजना (Action Plan)" if selected_language=="Hindi" else "Action Plan & Care Guidance"))
                    st.markdown(e['home_care_guidance'])
                with col2:
                    st.markdown("### " + ("सुझाए गए केंद्र (Recommended Clinics)" if selected_language=="Hindi" else "Recommended Clinics"))
                    for h in e['hospitals_recommended']:
                        spec_str = ", ".join(h['specialties'])
                        st.markdown(f"""
                        <div class="card" style="padding: 10px; margin-bottom: 8px;">
                            <h5 style="margin: 0; color: #4facfe;">📍 {h['name']} ({h['distance_miles']:.1f} miles)</h5>
                            <div style="font-size: 0.85rem; margin-top: 3px; color: #a0aec0;">{h['address']} | Ph: {h['contact_number']}</div>
                            <p style="font-size: 0.85rem; color: #cbd5e0; margin-top: 5px; margin-bottom:0;">Why: {h['routing_reason']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if e['benefits_identified']:
                        st.markdown("### " + ("पात्र सरकारी योजनाएं" if selected_language=="Hindi" else "Identified Welfare Benefits"))
                        for b in e['benefits_identified']:
                            st.markdown(f"""
                            <div class="card" style="padding: 10px; border: 1px solid rgba(255, 153, 51, 0.3)">
                                <h5 style="margin: 0; color: #FF9933;">🎗️ {b['name']}</h5>
                                <p style="font-size: 0.85rem; color: #cbd5e0; margin-top: 5px; margin-bottom:0;">{b['benefits_summary']}</p>
                            </div>
                            """, unsafe_allow_html=True)
    else:
        st.info("No historical encounter records found for this profile. Use **Symptom Assessment** to perform a consultation." if selected_language=="English" else "इस प्रोफाइल के लिए कोई पुराना चिकित्सा इतिहास नहीं मिला। परामर्श करने के लिए **लक्षण जांच और निदान** का उपयोग करें।")
