import streamlit as st
import requests
import random
import time
import os
import base64

# --- SECURE APPS SCRIPT LINK ---
API_URL = st.secrets["API_URL"]

# Aligned exactly to match the columns in your updated master_sheet (12 Medallions)
MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

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

def load_fresh_medallion_meta():
    """Fetches real-time parameters straight from the Medallions sheet tab."""
    backend_res = sync_cloud_data("fetchData")
    meta_map = {}
    if backend_res.get("status") == "success":
        for item in backend_res.get("medallions", []):
            m_name = item.get("Medallion")
            if m_name:
                meta_map[m_name] = {
                    "Rarity": item.get("Rarity", "Common"),
                    "Probability": item.get("Probability", "0%"),
                    "Availability": str(item.get("Availability", "0")),
                    "Value": item.get("Value") or item.get("Asset Price", "$0"),
                    "raw_object": item 
                }
    return meta_map

# --- TRACK SESSION GLOBAL VARIABLES ---
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
    base_cards = ["🪚 Saw", "🔨 Hammer", "📐 Square", "🪵 Timber"] * 2
    random.shuffle(base_cards)
    st.session_state.memory_cards = base_cards
    st.session_state.revealed_cards = []
    st.session_state.matched_pairs = []
    st.session_state.pending_job_payout = payout_value
    st.session_state.game_mode = "MemoryGame"

# --- HELPER FUNCTION: CONVERT LOCAL IMAGE TO BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- CONTEMPORARY UI STYLING & RESET ---
st.set_page_config(page_title="Apprentice Studio Hub", page_icon="🪵", layout="wide")

# Global CSS Injector
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .dashboard-header {
        font-weight: 800; 
        font-size: 2.6rem; 
        color: #FFFFFF; 
        letter-spacing: -1.5px;
        margin-bottom: 5px;
    }
    
    .dashboard-subtitle {
        color: #A0AEC0;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    
    .medallion-row-container {
        display: flex;
        flex-wrap: nowrap;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        width: 100%;
        background: #0E1017;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #1E2235;
        margin-bottom: 30px;
        box-sizing: border-box;
    }
    
    .badge-item-slot {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex: 1;
        position: relative;
    }
    
    .img-wrapper-frame {
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .img-wrapper-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    
    .lock-placeholder-frame {
        width: 55px;
        height: 55px;
        border-radius: 50%;
        border: 2px dashed #23273A;
        background: #121522;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #383F58;
        font-size: 0.95rem;
    }
    
    .hover-spec-card {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 130%;
        left: 50%;
        transform: translateX(-50%) translateY(6px);
        width: 190px;
        background: #161926;
        border: 1px solid #2C324A;
        border-radius: 10px;
        padding: 12px;
        text-align: left;
        box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        z-index: 100000;
        transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
        pointer-events: none;
    }
    
    .badge-item-slot:hover .hover-spec-card {
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
    
    .spec-card-line {
        font-size: 0.78rem;
        color: #E2E8F0;
        margin-bottom: 5px;
        line-height: 1.3;
    }
    
    .spec-card-line span {
        font-weight: 700;
        color: #F4D068;
    }
    
    .lbl-text-under {
        font-size: 0.68rem;
        font-weight: 700;
        color: #5C6479;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-top: 8px;
    }
    
    .qty-text-under {
        font-size: 0.75rem;
        font-weight: bold;
        color: #F4D068;
        margin-top: 5px;
    }
    
    .panel-box {
        background: #12141C;
        border: 1px solid #1E2235;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .panel-title {
        font-weight: 600;
        font-size: 1.25rem;
        color: #F4D068;
        margin-bottom: 12px;
    }
    
    .panel-desc {
        color: #718096;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    
    .job-item {
        background: #1A1D2C;
        border: 1px solid #2D3250;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    
    .job-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #E2E8F0;
        margin-bottom: 6px;
    }
    
    .showroom-preview-row {
        background: #161925;
        border: 1px solid #23283D;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# PHASE 1: LOGIN / SIGNUP PORTAL
# ==========================================
if not st.session_state.user_authenticated:
    st.markdown("<div class='dashboard-header' style='text-align: center; margin-top: 40px;'>🪵 Woodshop Floor Entry</div>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-subtitle' style='text-align: center;'>Unlock your progress dashboard or request an apprentice license.</div>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        tab_login, tab_signup = st.tabs(["🔒 Secure PIN Access", "🛠️ Sign Up New Apprentice"])
        
        with tab_login:
            login_pin = st.text_input("Enter 6-Digit Security PIN", type="password", max_chars=6, key="login_pin_input").strip()
            st.write("")
            if st.button("Unlock Studio Door", type="primary", use_container_width=True):
                if len(login_pin) != 6:
                    st.warning("PIN numbers must contain exactly 6 digits.")
                else:
                    with st.spinner("Downloading secure ledger records..."):
                        backend_res = sync_cloud_data("fetchData")
                        
                    if backend_res.get("status") == "success":
                        users_list = backend_res.get("users", [])
                        match = next((u for u in users_list if str(u['PIN']) == str(login_pin)), None)
                        
                        if match:
                            st.session_state.current_user = match
                            st.session_state.user_authenticated = True
                            st.success(f"Welcome back, {match['Username']}!")
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.error("No apprentice account registered under that security PIN.")
                    else:
                        st.error("Failed to interface with server database.")
                        
        with tab_signup:
            new_user = st.text_input("Apprentice Signature Name", key="reg_user", placeholder="e.g. Alex Mitchell").strip()
            st.write("")
            if st.button("Issue New Apprenticeship Portfolio", use_container_width=True):
                if not new_user:
                    st.warning("Please provide a valid registration name.")
                else:
                    with st.spinner("Checking roster indexes..."):
                        backend_res = sync_cloud_data("fetchData")
                        
                    users_list = backend_res.get("users", [])
                    name_exists = any(u['Username'].lower() == new_user.lower() for u in users_list)
                    
                    if name_exists:
                        st.error("This username signature is already active on the shop floor.")
                    else:
                        while True:
                            generated_pin = str(random.randint(100000, 999999))
                            if not any(str(u['PIN']) == generated_pin for u in users_list):
                                break
                        
                        new_user_data = {
                            "Username": new_user, "PIN": generated_pin,
                            "Bank Balance": 0, "Jobs Completed": 0
                        }
                        for m in MEDALLION_COLUMNS:
                            new_user_data[m] = 0
                            
                        with st.spinner("Writing portfolio row into cloud database..."):
                            save_res = sync_cloud_data("saveUser", new_user_data)
                            
                        if save_res.get("status") == "success":
                            st.markdown(f"""
                            <div style="background: #1C231A; border: 1px solid #385E30; padding: 20px; border-radius: 12px; margin-top: 15px;">
                                <h4 style="color: #6EE7B7; margin-top:0;">🎉 Portfolio Formed Successfully!</h4>
                                <p style="color: #D1FAE5; font-size:0.95rem;">Your account is ready in the directory sheet. Write your login PIN down safely:</p>
                                <code style="font-size: 1.8rem; font-weight: bold; color: #FFFFFF; background: #243321; padding: 4px 14px; border-radius: 6px; letter-spacing: 2px;">{generated_pin}</code>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Save transaction tracking connection timed out.")
    st.stop()

# ==========================================
# PHASE 2: ACTIVE GAME RE-ROUTER
# ==========================================
user = st.session_state.current_user

if st.session_state.game_mode == "MemoryGame":
    st.markdown(f"<div class='dashboard-header' style='text-align:center;'>🎴 Material Inspection Loop</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='dashboard-subtitle' style='text-align:center;'>Pair the core production components to complete the active contract order (+${st.session_state.pending_job_payout}).</div>", unsafe_allow_html=True)
    st.write("---")
    
    if len(st.session_state.revealed_cards) == 2:
        idx1, idx2 = st.session_state.revealed_cards
        if st.session_state.memory_cards[idx1] == st.session_state.memory_cards[idx2]:
            st.session_state.matched_pairs.append(st.session_state.memory_cards[idx1])
        time.sleep(0.6)
        st.session_state.revealed_cards = []
        st.rerun()

    col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
    with col_m2:
        grid_cols = st.columns(4)
        for i in range(8):
            col_idx = i % 4
            with grid_cols[col_idx]:
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
                            
        st.write("")
        st.write("---")
        if st.button("Abort Assignment & Terminate Contract", use_container_width=True):
            st.session_state.game_mode = "Dashboard"
            st.rerun()

    if len(st.session_state.matched_pairs) == 4:
        st.balloons()
        user['Bank Balance'] = int(user['Bank Balance']) + st.session_state.pending_job_payout
        user['Jobs Completed'] = int(user['Jobs Completed']) + 1
        st.session_state.reward_pending = True
        st.session_state.game_mode = "Dashboard"
        st.session_state.active_jobs = random.sample(TIMBER_JOBS, 2)
        st.rerun()
    st.stop()

# ==========================================
# PHASE 3: MAIN TYCOON STUDIO DASHBOARD UI
# ==========================================
live_metadata = load_fresh_medallion_meta()

col_title, col_logout = st.columns([3, 1])
with col_title:
    st.markdown(f"<div class='dashboard-header'>🪵 {user['Username']}'s Studio Platform</div>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-subtitle'>Track lumber balances, accept incoming customer orders, and manage wood stocks.</div>", unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("🔒 Save & Securely Log Out", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()

# ------------------------------------------------------------
# 🏅 FIXED SINGLE-BLOCK ENGINE (No layout leakage/code strings)
# ------------------------------------------------------------
st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #A0AEC0; margin-bottom: 14px; letter-spacing:0.5px;'>MEDALLION SHOWCASE CASEMENT</p>", unsafe_allow_html=True)

# Generate inner layout as a clean text object list to keep strings distinct from processing loops
row_items = []

for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    owned_count = int(user.get(wood_name, 0))
    
    meta = live_metadata.get(wood_name, {"Rarity": "Common", "Probability": "10%", "Availability": "0", "Value": "$0"})
    rarity_val = meta.get("Rarity", "Common")
    prob_raw = str(meta.get("Probability", "10"))
    prob_val = prob_raw if "%" in prob_raw else f"{prob_raw}%"
    
    # DEDUCTION ENGINE: Live sheet stock value minus amount owned by portfolio
    sheet_stock = int(meta.get("Availability", "0"))
    adjusted_availability = max(0, sheet_stock - owned_count)
    val_cost = str(meta.get("Value", "$0"))
    
    img_filename = f"assets/{wood_name.lower()}.png"
    img_base64 = get_image_base64(img_filename)
    
    tooltip_html = f"""
        <div class='hover-spec-card'>
            <div class='spec-card-line'>💎 Name: <span>{wood_name}</span></div>
            <div class='spec-card-line'>🏷️ Rarity: <span>{rarity_val}</span></div>
            <div class='spec-card-line'>🎲 Prob: <span>{prob_val}</span></div>
            <div class='spec-card-line'>📦 Avail: <span>{adjusted_availability} left</span></div>
            <div class='spec-card-line'>💰 Value: <span>{val_cost}</span></div>
        </div>
    """
    
    if owned_count > 0 and img_base64:
        item_html = f"""
        <div class='badge-item-slot'>
            {tooltip_html}
            <div class='img-wrapper-frame'>
                <img src='data:image/png;base64,{img_base64}' />
            </div>
            <div class='qty-text-under'>x{owned_count}</div>
            <div class='lbl-text-under'>{display_label}</div>
        </div>
        """
    else:
        item_html = f"""
        <div class='badge-item-slot'>
            {tooltip_html}
            <div class='img-wrapper-frame'>
                <div class='lock-placeholder-frame'>🔒</div>
            </div>
            <div class='qty-text-under' style='visibility: hidden;'>x0</div>
            <div class='lbl-text-under'>{display_label}</div>
        </div>
        """
    row_items.append(item_html)

# Combined into a single plain text assignment block to fix interpretation glitches
compiled_row_html = f"""
<div class='medallion-row-container'>
    {"".join(row_items)}
</div>
"""
st.markdown(compiled_row_html, unsafe_allow_html=True)

# --- REAL-TIME HIGHER LEVEL METRIC BANNER ---
col_met1, col_met2 = st.columns(2)
with col_met1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #161A2E, #0E111F); border: 1px solid #232B4E; border-radius: 14px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="color: #8F9CAE; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Liquid Bank Balance</div>
            <div style="color: #10B981; font-size: 2rem; font-weight: 800; margin-top: 2px;">${user['Bank Balance']}</div>
        </div>
        <div style="font-size: 2.2rem;">💳</div>
    </div>
    """, unsafe_allow_html=True)
with col_met2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1C162E, #110E1F); border: 1px solid #2D234E; border-radius: 14px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="color: #9C8FAE; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Completed Commissions</div>
            <div style="color: #A78BFA; font-size: 2rem; font-weight: 800; margin-top: 2px;">{user['Jobs Completed']} Active Builds</div>
        </div>
        <div style="font-size: 2.2rem;">🛠️</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- LOOT DROPS REWARD MODAL WITH STOCK DEPLOYMENT ---
if st.session_state.get('reward_pending', False):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2B2114, #1A140C); border: 1px solid #D4AF37; padding: 24px; border-radius: 16px; margin-bottom: 25px; text-align: center;">
        <h3 style="color: #F4D068; margin-top: 0; font-weight: 700; letter-spacing: -0.5px;">🏅 Project Commission Accomplished!</h3>
        <p style="color: #CBB48E; font-size: 0.95rem; margin-bottom: 15px;">Your quality inspection passed. Click below to shuffle and pull a random wood medallion drop.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⚡ SHUFFLE LOOM & SECURE DATA IN CLOUD", type="primary", use_container_width=True):
        with st.spinner("Paging drop weight parameters..."):
            backend_res = sync_cloud_data("fetchData")
        medallion_pool = backend_res.get("medallions", [])
        
        valid_pool = []
        for m in medallion_pool:
            m_name = m.get("Medallion")
            m_stock = int(m.get("Availability", 0))
            if m_name in MEDALLION_COLUMNS and m_stock > 0:
                valid_pool.append(m)
        
        if not valid_pool:
            st.error("All available medallion stock reserves across the studio network are fully depleted!")
        else:
            med_names = [m.get("Medallion") for m in valid_pool]
            med_weights = [float(str(m.get("Probability", "10")).replace('%', '')) for m in valid_pool]
            
            final_award = random.choices(med_names, weights=med_weights, k=1)[0]
            target_sheet_row = next(m for m in valid_pool if m.get("Medallion") == final_award)
            
            new_availability = max(0, int(target_sheet_row.get("Availability", 1)) - 1)
            target_sheet_row["Availability"] = new_availability
            
            st.success(f"🏆 Premium Drop Acquired: Added 1x [{final_award} Medallion] onto your studio rack sheet!")
            
            user[final_award] = int(user.get(final_award, 0)) + 1
            st.session_state.reward_pending = False
            
            with st.spinner("Synchronizing server stock reserves & wallet metrics..."):
                sync_cloud_data("saveUser", user)
                sync_cloud_data("saveMedallion", target_sheet_row)
                
            time.sleep(1.8)
            st.rerun()
    st.write("---")

# ==========================================
# THE THREE-COLUMN DASHBOARD HUB LAYOUT ENGINE
# ==========================================
panel_left, panel_center, panel_right = st.columns(3)

# --- PANEL 1: CLIENT WORK ORDERS ---
with panel_left:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>📋 Open Work Contracts</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-desc'>Accepting client orders spins up a material check. Complete it to secure the cash ledger.</div>", unsafe_allow_html=True)
    
    for idx, job in enumerate(st.session_state.active_jobs):
        st.markdown(f"""
        <div class='job-item'>
            <div class='job-title'>{job['title']}</div>
            <div style='color: #10B981; font-weight: 600; font-size: 0.85rem;'>Value Payout: +${job['pay']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Initialize Assessment Contract", key=f"job_btn_{idx}", use_container_width=True):
            init_memory_game(job['pay'])
            st.rerun()
        st.write("")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL 2: SHOWROOM SYSTEM RECONSTRUCTS ---
with panel_center:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>📦 Studio Showcase Inventory</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-desc'>Review verified lumber specimens and advanced trade assets earned across completed milestones.</div>", unsafe_allow_html=True)
    
    if st.button("🧰 Open Showroom Space Management", type="primary", use_container_width=True):
        st.toast("Inventory page module routing configurations are running on internal frameworks!")
        
    st.markdown("<div style='margin-top: 20px; margin-bottom: 5px; font-size: 0.8rem; font-weight: 600; color: #4A5568; letter-spacing: 0.5px; text-transform: uppercase;'>Specimen Counter Overview</div>", unsafe_allow_html=True)
    
    for med in MEDALLION_COLUMNS[:5]:
        count = user.get(med, 0)
        st.markdown(f"""
        <div class='showroom-preview-row'>
            <span style='color: #CBD5E0; font-weight: 500;'>🪵 {med} Medallion</span>
            <span style='color: #F4D068; font-weight: 700; background: #1F2438; padding: 2px 8px; border-radius: 4px;'>x{count}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PANEL 3: DICE WAGER MATRIX & MARKET SQUARE ---
with panel_right:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>🎲 Wager Arena & Market</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #E2E8F0; margin-bottom: 4px;'>Medallion Stake Machine</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.75rem; color: #718096; line-height: 1.4; margin-bottom: 12px;'>Risk an earned medallion item. Roll Even (2, 4, 6) to double its value. Roll Odd and it shatters into scrap wood.</div>", unsafe_allow_html=True)
    
    valid_options = [""] + [m for m in MEDALLION_COLUMNS if int(user.get(m, 0)) > 0]
    wager_med = st.selectbox("Select Target Medallion Asset", valid_options, label_visibility="collapsed")
    
    st.write("")
    if st.button("Roll High-Stakes Stake", use_container_width=True, disabled=not wager_med):
        user[wager_med] = int(user[wager_med]) - 1
        dice_result = random.randint(1, 6)
        
        st.markdown(f"<div style='text-align: center; margin: 10px 0; font-weight: bold; font-size: 1rem; color:#FFFFFF;'>Die landed on: [{dice_result}]</div>", unsafe_allow_html=True)
        if dice_result % 2 == 0:
            user[wager_med] = int(user[wager_med]) + 2
            st.success(f"🎯 Perfect cut! Doubled into +2 {wager_med} Medallions!")
        else:
            st.error("💥 Splinter fracture! The asset broke during processing.")
            
        with st.spinner("Saving transaction metrics..."):
            sync_cloud_data("saveUser", user)
        time.sleep(2)
        st.rerun()
        
    st.markdown("<hr style='border-color: #1E2235; margin: 20px 0;'>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 0.9rem; font-weight: 600; color: #E2E8F0; margin-bottom: 4px;'>🛒 Material Stock Procurement</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.75rem; color: #718096; margin-bottom: 12px;'>Trade liquid capital balances to source component lines directly. Sourcing a stock item depletes the global availability pool.</div>", unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        spruce_meta = live_metadata.get("Spruce", {"Availability": "0"})
        spruce_avail = int(spruce_meta.get("Availability", 0)) - int(user.get("Spruce", 0))
        st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#CBD5E0;'>Spruce Lumber</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; color:#EF4444; margin-bottom:6px;'>Cost: $40 | {max(0, spruce_avail)} left</div>", unsafe_allow_html=True)
        
        if st.button("Buy Spruce Stock", use_container_width=True, disabled=(int(user['Bank Balance']) < 40 or spruce_avail <= 0)):
            user['Bank Balance'] = int(user['Bank Balance']) - 40
            user['Spruce'] = int(user.get('Spruce', 0)) + 1
            
            backend_res = sync_cloud_data("fetchData")
            m_pool = backend_res.get("medallions", [])
            target_row = next((m for m in m_pool if m.get("Medallion") == "Spruce"), None)
            if target_row:
                target_row["Availability"] = max(0, int(target_row.get("Availability", 1)) - 1)
                sync_cloud_data("saveMedallion", target_row)
                
            sync_cloud_data("saveUser", user)
            st.rerun()
            
    with col_b2:
        pine_meta = live_metadata.get("Pine", {"Availability": "0"})
        pine_avail = int(pine_meta.get("Pine", 0) if "Pine" in live_metadata else pine_meta.get("Availability", 0)) - int(user.get("Pine", 0))
        st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#CBD5E0;'>Pine Lumber</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; color:#EF4444; margin-bottom:6px;'>Cost: $50 | {max(0, pine_avail)} left</div>", unsafe_allow_html=True)
        
        if st.button("Buy Pine Stock", use_container_width=True, disabled=(int(user['Bank Balance']) < 50 or pine_avail <= 0)):
            user['Bank Balance'] = int(user['Bank Balance']) - 50
            user['Pine'] = int(user.get('Pine', 0)) + 1
            
            backend_res = sync_cloud_data("fetchData")
            m_pool = backend_res.get("medallions", [])
            target_row = next((m for m in m_pool if m.get("Medallion") == "Pine"), None)
            if target_row:
                target_row["Availability"] = max(0, int(target_row.get("Availability", 1)) - 1)
                sync_cloud_data("saveMedallion", target_row)
                
            sync_cloud_data("saveUser", user)
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    
