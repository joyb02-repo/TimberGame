import streamlit as st
import requests
import random
import time

# --- SECURE APPS SCRIPT LINK ---
API_URL = st.secrets["API_URL"]

MEDALLION_COLUMNS = ["Spruce", "Pine", "Meranti", "Oak", "Maple", "Walnut", "Cherry", "Mahogany", "Rosewood", "Ebony"]

# --- API CORE BACKEND ROUTERS ---
def sync_cloud_data(action_type, payload_data=None):
    try:
        payload = {"action": action_type}
        if payload_data:
            payload["data"] = payload_data
            
        response = requests.post(API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Database Connection Error: {str(e)}")
    return {"status": "error", "users": [], "medallions": []}

# --- RECOVERY SESSION CONTROLLER STATE ---
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = "Dashboard"

# --- TIMBER RELATED CONTRACT GENERATOR POOL ---
TIMBER_JOBS = [
    {"title": "🪵 Sanding Premium Meranti Bookcase", "pay": 85},
    {"title": "🪓 Hand-Carving Walnut Salad Bowls", "pay": 120},
    {"title": "🛹 Shaping Radiata Pine Skateboard Deck", "pay": 65},
    {"title": "🪑 Assembling Mahogany Dowel Stool", "pay": 140},
    {"title": "🎨 Applying Lacquer Finish to Cherry Desk", "pay": 95},
    {"title": "🐦 Constructing Weatherproof Oak Birdhouses", "pay": 50}
]

if 'active_jobs' not in st.session_state:
    st.session_state.active_jobs = random.sample(TIMBER_JOBS, 2)

# --- MEMORY GAME STATE CONTROLLER ---
if 'memory_cards' not in st.session_state:
    st.session_state.memory_cards = []
if 'revealed_cards' not in st.session_state:
    st.session_state.revealed_cards = []
if 'matched_pairs' not in st.session_state:
    st.session_state.matched_pairs = []
if 'pending_job_payout' not in st.session_state:
    st.session_state.pending_job_payout = 0

def init_memory_game(payout_value):
    # 4 distinct wood pairs (8 cards total)
    base_cards = ["🪚 Saw", "🔨 Hammer", "📐 Square", "🪵 Timber"] * 2
    random.shuffle(base_cards)
    st.session_state.memory_cards = base_cards
    st.session_state.revealed_cards = []
    st.session_state.matched_pairs = []
    st.session_state.pending_job_payout = payout_value
    st.session_state.game_mode = "MemoryGame"

# --- APPLICATION THEME STYLING ---
st.set_page_config(page_title="Apprentice Control Hub", page_icon="🪵", layout="wide")
st.markdown("""
    <style>
    .main-header { font-family: 'Helvetica Neue', sans-serif; font-weight: 800; font-size: 2.3rem; color: #f4d068; }
    .card { background: #1a1c24; border: 1px solid #2d313f; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    .metric-val { font-size: 1.8rem; font-weight: bold; margin-top: 5px; }
    .game-card { background: #1e212b; border: 2px solid #3a3f50; border-radius: 8px; padding: 20px; text-align: center; }
    .slot-vacant { background: #16171d; border: 2px dashed #3a3f50; padding: 20px; border-radius: 10px; text-align: center; color: #58617a; }
    .slot-earned { background: linear-gradient(135deg, #2b2318, #1a140e); border: 2px solid #f4d068; padding: 20px; border-radius: 10px; text-align: center; color: #f4d068; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# PHASE 1: PIN PORTAL ROUTER
# ==========================================
if not st.session_state.user_authenticated:
    st.markdown("<div class='main-header'>🪵 Apprentice Workshop Gate</div>", unsafe_allow_html=True)
    st.write("Enter your security PIN or create a fresh apprentice contract portfolio.")
    
    tab_login, tab_signup = st.tabs(["🔒 Secure PIN Access", "🛠️ Sign Up New Apprentice"])
    
    with tab_login:
        # User input requirement reduced purely to secure PIN identification lookup
        login_pin = st.text_input("Enter 6-Digit Security PIN", type="password", max_chars=6, key="login_pin_input").strip()
        
        if st.button("Unlock Workbench Door", type="primary", use_container_width=True):
            if len(login_pin) != 6:
                st.warning("PIN numbers must contain exactly 6 digits.")
            else:
                with st.spinner("Accessing server registry records..."):
                    backend_res = sync_cloud_data("fetchData")
                    
                if backend_res.get("status") == "success":
                    users_list = backend_res.get("users", [])
                    match = next((u for u in users_list if str(u['PIN']) == str(login_pin)), None)
                    
                    if match:
                        st.session_state.current_user = match
                        st.session_state.user_authenticated = True
                        st.success(f"Access Authorized! Welcome back, Apprentice {match['Username']}.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("No apprentice account is registered under that security PIN.")
                else:
                    st.error("Failed to interface with Google Sheets core server database.")
                    
    with tab_signup:
        new_user = st.text_input("Apprentice Full Name / ID Handle", key="reg_user").strip()
        
        if st.button("Issue New Apprentice Contract", use_container_width=True):
            if not new_user:
                st.warning("Please provide a valid signature name.")
            else:
                with st.spinner("Checking records..."):
                    backend_res = sync_cloud_data("fetchData")
                    
                users_list = backend_res.get("users", [])
                name_exists = any(u['Username'].lower() == new_user.lower() for u in users_list)
                
                if name_exists:
                    st.error("This username signature is already active on the floor.")
                else:
                    # Formulate unique 6 digit system sequence token
                    existing_pins = [str(u['PIN']) for u in users_list]
                    while True:
                        generated_pin = str(random.randint(100000, 999999))
                        if generated_pin not in existing_pins:
                            break
                    
                    # Core configuration initializing new users with 0 dollars balance
                    new_user_data = {
                        "Username": new_user, "PIN": generated_pin,
                        "Bank Balance": 0, "Jobs Completed": 0
                    }
                    for m in MEDALLION_COLUMNS:
                        new_user_data[m] = 0
                        
                    with st.spinner("Carving data slots into database..."):
                        save_res = sync_cloud_data("saveUser", new_user_data)
                        
                    if save_res.get("status") == "success":
                        st.markdown(f"""
                        ### 🎉 Setup Fully Finalized!
                        Your profile row is live on your sheet records. Use this PIN to log in from now on:
                        * **Apprentice Username Reference:** `{new_user}`
                        * **🔑 YOUR EXCLUSIVE LOGIN PIN:** `{generated_pin}`
                        """)
                    else:
                        st.error("Save transaction tracking connection timed out.")
    st.stop()

# ==========================================
# PHASE 2: SYSTEM GLOBAL REFRESH HOOKS
# ==========================================
user = st.session_state.current_user

# ==========================================
# SUB-PHASE A: MEMORY CARD COUPLING SYSTEM
# ==========================================
if st.session_state.game_mode == "MemoryGame":
    st.markdown(f"<div class='main-header'>🎴 Memory Matching Quality Inspection</div>", unsafe_allow_html=True)
    st.write(f"Match processing tool components correctly to successfully secure your code work order payout (**+${st.session_state.pending_job_payout}**).")
    st.write("---")
    
    # Process matched tracking counts
    if len(st.session_state.revealed_cards) == 2:
        idx1, idx2 = st.session_state.revealed_cards
        if st.session_state.memory_cards[idx1] == st.session_state.memory_cards[idx2]:
            st.session_state.matched_pairs.append(st.session_state.memory_cards[idx1])
        time.sleep(0.8)
        st.session_state.revealed_cards = []
        st.rerun()

    # Render 2 rows of 4 cards
    cols = st.columns(4)
    for i in range(8):
        col_idx = i % 4
        with cols[col_idx]:
            card_item = st.session_state.memory_cards[i]
            is_matched = card_item in st.session_state.matched_pairs
            is_flipped = i in st.session_state.revealed_cards
            
            if is_matched:
                st.button(f"✅ {card_item}", key=f"mem_{i}", disabled=True, use_container_width=True)
            elif is_flipped:
                st.button(f"👀 {card_item}", key=f"mem_{i}", disabled=True, use_container_width=True)
            else:
                if st.button("❓ Reveal", key=f"mem_{i}", use_container_width=True):
                    if len(st.session_state.revealed_cards) < 2 and i not in st.session_state.revealed_cards:
                        st.session_state.revealed_cards.append(i)
                        st.rerun()

    # Match Win State Checking
    if len(st.session_state.matched_pairs) == 4:
        st.balloons()
        st.success(f"🔧 Material Assessment Check Completed! Payout added to your workshop bank ledger: +${st.session_state.pending_job_payout}")
        
        user['Bank Balance'] = int(user['Bank Balance']) + st.session_state.pending_job_payout
        user['Jobs Completed'] = int(user['Jobs Completed']) + 1
        st.session_state.reward_pending = True
        st.session_state.game_mode = "Dashboard"
        
        # Cycle job lists options instantly
        st.session_state.active_jobs = random.sample(TIMBER_JOBS, 2)
        st.rerun()
        
    if st.button("放弃 Return to Workshop Floor"):
        st.session_state.game_mode = "Dashboard"
        st.rerun()
    st.stop()

# ==========================================
# MAIN APPLICATION INTERFACE FRAMEWORK
# ==========================================
st.markdown(f"<div class='main-header'>🪵 Main Station Dashboard: {user['Username']}</div>", unsafe_allow_html=True)
st.write("---")

# Metrics Overview Banner Row
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='card'><div style='color:#8a92a6;'>WALLET BANK LEDGER</div><div class='metric-val' style='color:#00ffcc;'>${user['Bank Balance']}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='card'><div style='color:#8a92a6;'>COMPLETED WORK COMMISSIONS</div><div class='metric-val' style='color:#b388ff;'>{user['Jobs Completed']} Projects</div></div>", unsafe_allow_html=True)
with m3:
    if st.button("🔒 Save Progress & Safely Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- LOOT DROPS SYNC PIPELINE ---
if st.session_state.get('reward_pending', False):
    st.write("---")
    st.subheader("🏅 Contract Milestone Reached! Pull Medallion Drop")
    if st.button("⚡ EXECUTE SHUFFLE & SAVE SEQUENCE", type="primary", use_container_width=True):
        with st.spinner("Paging drop weight parameters..."):
            backend_res = sync_cloud_data("fetchData")
        medallion_pool = backend_res.get("medallions", [])
        
        med_names = [m['Medallion'] for m in medallion_pool if m['Medallion'] in MEDALLION_COLUMNS]
        med_weights = [float(m['Weight']) for m in medallion_pool if m['Medallion'] in MEDALLION_COLUMNS]
        
        if not med_names:
            med_names = MEDALLION_COLUMNS
            med_weights = [10.0] * 10
            
        final_award = random.choices(med_names, weights=med_weights, k=1)[0]
        st.success(f"🏆 Acquired Drop Reward: **{final_award} Medallion** has been logged!")
        user[final_award] = int(user.get(final_award, 0)) + 1
        st.session_state.reward_pending = False
        
        with st.spinner("Syncing secure records up to cloud..."):
            sync_cloud_data("saveUser", user)
        time.sleep(1.5)
        st.rerun()

st.write("---")

# ==========================================
# THE THREE APPLICATION WORKSPACE SECTIONS
# ==========================================
panel_left, panel_center, panel_right = st.columns(3)

# SECTION 1: WORK ORDER COMMISSIONS (JOB BOARD)
with panel_left:
    st.markdown("### 📋 Active Open Work Orders")
    st.write("Accepting contracts launches a memory retention pairs matching configuration check to clear the payout balance.")
    st.write("")
    
    for idx, job in enumerate(st.session_state.active_jobs):
        with st.container():
            st.markdown(f"**{job['title']}**")
            st.markdown(f"<span style='color:#00ffcc; font-weight:bold;'>Payout Value: +${job['pay']}</span>", unsafe_allow_html=True)
            if st.button(f"Accept Assignment Contract", key=f"job_btn_{idx}", use_container_width=True):
                init_memory_game(job['pay'])
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

# SECTION 2: SHOWCASE INVENTORY DRAWER
with panel_center:
    st.markdown("### 📦 Workshop Showroom Storage")
    st.write("Review collected assets and organized wood specimens.")
    st.write("")
    
    # Isolated inventory route redirect button
    if st.button("🧰 Open Inventory Control Dashboard Panel", type="primary", use_container_width=True):
        st.toast("Inventory sub-system pages are under production construction profiles!")
        
    st.write("---")
    # Quick display overview visualization matrix matching spreadsheet data lines
    st.markdown("**Specimens Portfolio Counter Overview:**")
    for med in MEDALLION_COLUMNS[:5]:
        st.text(f"🪵 {med} Medallions: x{user.get(med, 0)}")

# SECTION 3: DICE WAGER MARKET & RETAIL STORE
with panel_right:
    st.markdown("### 🎲 Wager Matrix & Market Square")
    
    # Sub-Block A: Medallion Dice Stake Game
    st.markdown("#### Dice Medallion Stake Wager")
    st.caption("Risk an acquired medallion asset. Roll an even number (2, 4, 6) to double it; roll an odd number to break your build down into scrap.")
    
    wager_med = st.selectbox("Select Target Medallion to Risk", [""] + [m for m in MEDALLION_COLUMNS if int(user.get(m, 0)) > 0])
    if st.button("🎲 Roll High-Stakes Wager", use_container_width=True, disabled=not wager_med):
        user[wager_med] = int(user[wager_med]) - 1
        dice_result = random.randint(1, 6)
        
        st.markdown(f"**Dice outcome landed on: `{dice_result}`**")
        if dice_result % 2 == 0:
            user[wager_med] = int(user[wager_med]) + 2
            st.success(f"🎯 Perfect Calibration! Doubled your target asset count! Obtained +2 {wager_med} Medallions.")
        else:
            st.error("💥 Machine Stress Fracture! Your medallion shattered in the process.")
            
        with st.spinner("Saving changes..."):
            sync_cloud_data("saveUser", user)
        time.sleep(2)
        st.rerun()
        
    st.markdown("---")
    
    # Sub-Block B: Wood Shop Retail Store
    st.markdown("#### 🛒 Wood Shop Retail Store")
    st.caption("Trade cash balances to purchase raw inventory materials.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("**Spruce Stock Supply**")
        st.markdown("<span style='color:#ff4d4d;'>Cost: $40</span>", unsafe_allow_html=True)
        if st.button("Purchase Spruce Stock", use_container_width=True, disabled=int(user['Bank Balance']) < 40):
            user['Bank Balance'] = int(user['Bank Balance']) - 40
            user['Spruce'] = int(user.get('Spruce', 0)) + 1
            sync_cloud_data("saveUser", user)
            st.rerun()
            
    with col_b2:
        st.markdown("**Pine Stock Supply**")
        st.markdown("<span style='color:#ff4d4d;'>Cost: $50</span>", unsafe_allow_html=True)
        if st.button("Purchase Pine Stock", use_container_width=True, disabled=int(user['Bank Balance']) < 50):
            user['Bank Balance'] = int(user['Bank Balance']) - 50
            user['Pine'] = int(user.get('Pine', 0)) + 1
            sync_cloud_data("saveUser", user)
            st.rerun()
