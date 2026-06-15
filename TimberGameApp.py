import streamlit as st
import requests
import random
import time

# --- PULL HIDDEN API URL FROM STREAMLIT SECRETS ---
API_URL = st.secrets["API_URL"]
# 10 Unique Wood Medallions mapped exactly to Columns E through N in your Google Sheet
MEDALLION_COLUMNS = ["Spruce", "Pine", "Meranti", "Oak", "Maple", "Walnut", "Cherry", "Mahogany", "Rosewood", "Ebony"]

# --- API CORE BACKEND ROUTERS ---
def sync_cloud_data(action_type, payload_data=None):
    """Handles secure backend pipeline requests to Google Sheets via Apps Script"""
    try:
        payload = {"action": action_type}
        if payload_data:
            payload["data"] = payload_data
            
        response = requests.post(API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Database Sync Error: {str(e)}")
    return {"status": "error", "users": [], "medallions": []}

# --- TRACK SESSION GLOBAL VARIABLES ---
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- SLEEK LAYOUT STYLING ---
st.set_page_config(page_title="Apprentice Hub", page_icon="🪵", layout="wide")
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; font-weight: 800; font-size: 2.3rem; color: #f4d068; }
    .card { background: #1a1c24; border: 1px solid #2d313f; padding: 20px; border-radius: 12px; text-align: center; }
    .metric-val { font-size: 1.8rem; font-weight: bold; margin-top: 5px; }
    .slot-vacant { background: #16171d; border: 2px dashed #3a3f50; padding: 20px; border-radius: 10px; text-align: center; color: #58617a; }
    .slot-earned { background: linear-gradient(135deg, #2b2318, #1a140e); border: 2px solid #f4d068; padding: 20px; border-radius: 10px; text-align: center; color: #f4d068; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# PHASE 1: LOGIN / SIGNUP PORTAL
# ==========================================
if not st.session_state.user_authenticated:
    st.markdown("<div class='main-header'>🪵 Apprentice Workshop Sign-In</div>", unsafe_allow_html=True)
    st.write("Access your save profile via Google Sheets using your secure apprentice card credentials.")
    
    tab_login, tab_signup = st.tabs(["🔒 Existing Apprentice Login", "🛠️ Register New Account"])
    
    with tab_login:
        login_user = st.text_input("Username Input", key="lin_user").strip()
        login_pin = st.text_input("6-Digit Unique PIN", type="password", max_chars=6, key="lin_pin").strip()
        
        if st.button("Access Workbench", type="primary"):
            with st.spinner("Downloading sheets database records..."):
                backend_res = sync_cloud_data("fetchData")
                
            if backend_res.get("status") == "success":
                users_list = backend_res.get("users", [])
                match = next((u for u in users_list if u['Username'].lower() == login_user.lower() and str(u['PIN']) == str(login_pin)), None)
                
                if match:
                    st.session_state.current_user = match
                    st.session_state.user_authenticated = True
                    st.success(f"Welcome back, {match['Username']}! Initializing shop modules...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Authentication rejected. Credentials do not match our database.")
            else:
                st.error("Failed to connect to spreadsheet server.")
                
    with tab_signup:
        new_user = st.text_input("Choose Your Apprentice Username", key="reg_user").strip()
        
        if st.button("Generate Apprenticeship Contract"):
            if not new_user:
                st.warning("Please provide a valid username.")
            else:
                with st.spinner("Verifying naming uniqueness..."):
                    backend_res = sync_cloud_data("fetchData")
                    
                users_list = backend_res.get("users", [])
                name_exists = any(u['Username'].lower() == new_user.lower() for u in users_list)
                
                if name_exists:
                    st.error("This username is already taken. Please try another variant.")
                else:
                    # Generate a completely unique random 6 digit security token
                    existing_pins = [str(u['PIN']) for u in users_list]
                    while True:
                        generated_pin = str(random.randint(100000, 999999))
                        if generated_pin not in existing_pins:
                            break
                    
                    # Create dictionary structure mapping rows exactly to image_90fa0b.png columns
                    new_user_data = {
                        "Username": new_user, "PIN": generated_pin,
                        "Bank Balance": 250, "Jobs Completed": 0
                    }
                    for m in MEDALLION_COLUMNS:
                        new_user_data[m] = 0
                        
                    with st.spinner("Writing new apprentice credentials onto master_sheet..."):
                        save_res = sync_cloud_data("saveUser", new_user_data)
                        
                    if save_res.get("status") == "success":
                        st.markdown(f"""
                        ### 🎉 Registration Successful!
                        Keep this secure access card handy to load your stats next time:
                        * **Apprentice Username:** `{new_user}`
                        * **6-Digit Security Access PIN:** `{generated_pin}`
                        """)
                    else:
                        st.error("Database connection dropped. Account registration aborted.")
    st.stop()

# ==========================================
# PHASE 2: CORE WORKSPACE & USER INTERFACE
# ==========================================
user = st.session_state.current_user

st.markdown(f"<div class='main-header'>🪵 Workspace Hub: {user['Username']}</div>", unsafe_allow_html=True)
st.write("---")

# Metrics Display Dashboard Row
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='card'><div style='color:#8a92a6;'>WALLET BALANCE</div><div class='metric-val' style='color:#00ffcc;'>${user['Bank Balance']}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='card'><div style='color:#8a92a6;'>COMPLETED WORK COMMISSIONS</div><div class='metric-val' style='color:#b388ff;'>{user['Jobs Completed']} Done</div></div>", unsafe_allow_html=True)
with m3:
    if st.button("🔒 Securely Log Out & Exit Workstation", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.write("")

# ==========================================
# PHASE 3: CONTRACT MINI-GAMES PANEL
# ==========================================
st.subheader("📋 Open Workshop Contracts Board")

col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    st.markdown("### 🎴 Pairs Matching Game")
    st.caption("Complete a structural alignment memory test assignment.")
    if st.button("Execute Pairs Contract", use_container_width=True):
        user['Bank Balance'] = int(user['Bank Balance']) + 60
        user['Jobs Completed'] = int(user['Jobs Completed']) + 1
        st.session_state.reward_pending = True
        st.rerun()

with col_g2:
    st.markdown("### 🎲 Dice Wager Game")
    st.caption("Calculate machine calibration variations.")
    st.button("Execute Dice Contract", disabled=True, use_container_width=True)

with col_g3:
    st.markdown("### ❓ Mystery Wood Challenge")
    st.caption("Deconstruct a random client carpentry specification request.")
    st.button("Execute Mystery Contract", disabled=True, use_container_width=True)

# ==========================================
# PHASE 4: THE SHUFFLE LOOT MEDALLION DROP ENGINE
# ==========================================
if st.session_state.get('reward_pending', False):
    st.write("---")
    st.subheader("🏅 Job Complete! Pull Your Random Medallion Reward")
    
    if st.button("⚡ SHUFFLE & RECEIVE MEDALLION", type="primary", use_container_width=True):
        with st.spinner("Downloading medallion drop rates from tab..."):
            backend_res = sync_cloud_data("fetchData")
            
        medallion_pool = backend_res.get("medallions", [])
        
        # Visual Shuffle UI Simulation Placeholder
        shuffle_box = st.empty()
        for _ in range(10):
            mock_pick = random.choice(MEDALLION_COLUMNS)
            shuffle_box.markdown(f"<h2 style='text-align:center; color:#fffae6;'>🔄 Shuffling Loom: {mock_pick}</h2>", unsafe_allow_html=True)
            time.sleep(0.1)
            
        # Extract name lists and probabilities from sheet config variables
        med_names = [m['Medallion'] for m in medallion_pool if m['Medallion'] in MEDALLION_COLUMNS]
        med_weights = [float(m['Weight']) for m in medallion_pool if m['Medallion'] in MEDALLION_COLUMNS]
        
        # Safe fallback default weights if the sheet tab is empty
        if not med_names:
            med_names = MEDALLION_COLUMNS
            med_weights = [10.0] * 10
            
        final_award = random.choices(med_names, weights=med_weights, k=1)[0]
        shuffle_box.markdown(f"<h1 style='text-align:center; color:#f4d068;'>🏆 Acquired: {final_award} Medallion!</h1>", unsafe_allow_html=True)
        
        # Update user's active session state data dictionary values
        user[final_award] = int(user.get(final_award, 0)) + 1
        st.session_state.reward_pending = False
        
        # --- UPLOAD UPDATED USER PROGRESS TO GOOGLE SHEETS ---
        with st.spinner("Saving changes safely to cloud master_sheet database..."):
            save_status = sync_cloud_data("saveUser", user)
            
        if save_status.get("status") == "success":
            st.toast("Progress secured in Google Sheet!")
        else:
            st.error("Failed to sync progress to cloud.")
            
        time.sleep(1.5)
        st.rerun()

st.write("---")

# ==========================================
# PHASE 5: THE 10 DISPLAY MATRIX SHOWROOM GRID
# ==========================================
st.subheader("📦 Acquired Wood Medallions Rack (10 Showcase Slots)")
st.write("Real-time visual tracker matching row inventory metrics recorded in your Google Sheet spreadsheet.")

row1_meds = MEDALLION_COLUMNS[:5]
row2_meds = MEDALLION_COLUMNS[5:]

col_r1 = st.columns(5)
for i, med in enumerate(row1_meds):
    count = int(user.get(med, 0))
    with col_r1[i]:
        if count > 0:
            st.markdown(f"<div class='slot-earned'>🪵 {med}<br><span style='font-size:1.5rem;'>x{count}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='slot-vacant'>{med}<br><span style='font-size:0.8rem; color:#444;'>LOCKED</span></div>", unsafe_allow_html=True)

st.write("")

col_r2 = st.columns(5)
for i, med in enumerate(row2_meds):
    count = int(user.get(med, 0))
    with col_r2[i]:
        if count > 0:
            st.markdown(f"<div class='slot-earned'>🪵 {med}<br><span style='font-size:1.5rem;'>x{count}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='slot-vacant'>{med}<br><span style='font-size:0.8rem; color:#444;'>LOCKED</span></div>", unsafe_allow_html=True)
