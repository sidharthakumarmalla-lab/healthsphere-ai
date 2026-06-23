import streamlit as st
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
        r = requests.get(f"{BACKEND_URL}/{endpoint}")
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        return None
    return None

def api_post(endpoint, data):
    try:
        r = requests.post(f"{BACKEND_URL}/{endpoint}", json=data)
        if r.status_code in [200, 201]:
            return r.json()
        else:
            st.error(f"Error: {r.status_code} - {r.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to HealthSphere API.")
    return None

def api_put(endpoint, data):
    try:
        r = requests.put(f"{BACKEND_URL}/{endpoint}", json=data)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to HealthSphere API.")
    return None

def api_delete(endpoint):
    try:
        r = requests.delete(f"{BACKEND_URL}/{endpoint}")
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
