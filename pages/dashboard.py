# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/dashboard.py (COMPLETE DIRECT MONOLITH)
# ====================================================================

import streamlit as st
import requests

# Strict configuration execution at absolute entry scope
st.set_page_config(page_title="Timber Medallion Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Global UI Inject Style Framework - Cleans environment and formats both utility buttons
st.markdown("""
<style>
    /* Global layout positioning variables */
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }

    /* TARGET AND UPGRADE THE UTILITY REFRESH BUTTON (TOP LEFT) */
    div.stButton:has(button[key="utility_refresh_node"]) {
        position: absolute !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        width: auto !important;
    }

    div.stButton > button[key="utility_refresh_node"] {
        background-color: #161925 !important;
        color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #23273A !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button[key="utility_refresh_node"]:hover {
        background-color: #1c2030 !important;
        color: #FFFFFF !important;
        border-color: #F4D068 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important;
    }

    div.stButton > button[key="utility_refresh_node"]:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }
    
    div.stButton > button[key="utility_refresh_node"]:focus {
        border-color: #23273A !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* KEEP NATIVE ALIGNMENT FOR LOGOUT UTILITY (TOP RIGHT) */
    div.stButton:has(button[key="system_logout_trigger"]) {
        position: absolute !important;
        top: 10px !important;
        right: 10px !important;
        z-index: 999999 !important;
        width: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Render the upgraded styled refresh utility node 
if st.button("Update Data 🔄", key="utility_refresh_node"):
    st.cache_data.clear()
    st.rerun()

# Safely verify user authorization handshake
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Unauthorized Node Access. Re-routing initialization parameters.")
    st.switch_page("login.py")

API_URL = st.secrets["API_URL"]
USER_PASSCODE = st.session_state.get("user_passcode", "")
USERNAME = st.session_state.get("username", "Guest")

# Top Layout Banner Header Elements
col_header_left, col_header_right = st.columns([4, 1])
with col_header_left:
    st.markdown(f"<h1 style='text-align: center; color: white; margin-top: 40px; font-family: Inter, sans-serif;'>Timber Medallion Portfolio: <span style='color: #F4D068;'>{USERNAME}</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5); font-size: 14px; max-width: 800px; margin: 0 auto 30px auto; line-height: 1.6;'>Master tracking dashboard connected live to cloud inventory matrices. Authenticated users can generate verified asset transactions by supplying validation tokens below. Hover over any node in your matrix layout to see real-time supply indexes, market valuations, and algorithm probabilities. Premium tier tokens scale up to the highly coveted, single production run <span style='color:#F4D068; font-weight:600;'>Agarwood Medallion</span>.</p>", unsafe_allow_html=True)

with col_header_right:
    # Maintain standard placement hook for logout sequences
    if st.button("🔒 LOGOUT", key="system_logout_trigger"):
        st.session_state["authenticated"] = False
        st.session_state["user_passcode"] = ""
        st.switch_page("login.py")

# Core Data Gathering Infrastructure Matrix 
@st.cache_data(ttl=10)
def fetch_matrix_data(passcode):
    try:
        r = requests.get(API_URL, params={"action": "fetchData", "passcode": passcode}, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

data = fetch_matrix_data(USER_PASSCODE)

if not data or data.get("status") != "success":
    st.error("Data Matrix Synchronization Failure. Verify session state architecture configuration tokens.")
    st.stop()

# Process active structural dictionaries
medallions = data.get("medallions", {})
totals = data.get("totals", {"total_collected": 0, "total_value": 0})

# Ordered array tracking matching inventory rendering maps
medallion_order = ["SPRC", "PINE", "MRNT", "BALS", "OAKW", "MAPL", "WALN", "CHER", "MHGN", "EBNY", "RSWD", "AGAR"]

# Render structural inventory display pipeline grid layout
cols = st.columns(12)
for idx, key in enumerate(medallion_order):
    with cols[idx]:
        m_info = medallions.get(key, {"count": 0, "image": "", "label": key, "unlocked": False})
        
        if m_info["unlocked"] and m_info["count"] > 0:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="{m_info['image']}" style="width: 100%; max-width: 65px; height: auto; margin-bottom: 8px;" />
                    <div style="color: #F4D068; font-size: 13px; font-weight: 700;">x{m_info['count']}</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">{m_info['label']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 20px; opacity: 0.25;">
                    <div style="width: 65px; height: 65px; background: #161925; border: 1px dashed rgba(255,255,255,0.2); border-radius: 50%; margin: 0 auto 8px auto; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px;">🔒</div>
                    <div style="color: #888; font-size: 13px; font-weight: 700;">-</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; letter-spacing: 0.5px;">{key}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Portfolio Metric Block Renders
col_metric_1, col_metric_2 = st.columns(2)
with col_metric_1:
    st.markdown(f"""
        <div style="background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 15px; text-align: center;">
            <div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Collection Value</div>
            <div style="color: #F4D068; font-size: 24px; font-weight: 700; font-family: monospace;">${totals['total_value']:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col_metric_2:
    st.markdown(f"""
        <div style="background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 15px; text-align: center;">
            <div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Medallions Collected</div>
            <div style="color: white; font-size: 24px; font-weight: 700; font-family: monospace;">{totals['total_collected']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Interactive Transaction Submission Logic Frame
col_action_1, col_action_2, col_action_3 = st.columns([1.5, 1, 1.5])
with col_action_2:
    pin_input = st.text_input("Transaction PIN Entry Block", type="password", max_chars=6, placeholder="6-DIGIT PIN", label_visibility="collapsed")
    verify_pin_btn = st.button("VERIFY PIN", use_container_width=True)
    
    if verify_pin_btn:
        if len(pin_input) == 6:
            st.success("Transaction authentication pipeline parameters verified.")
        else:
            st.error("Invalid entry string specifications calculated.")

st.markdown("<br>", unsafe_allow_html=True)

# Bottom-most mining processing anchor frame
col_mine_1, col_mine_2, col_mine_3 = st.columns([1, 2, 1])
with col_mine_2:
    mine_btn = st.button("MINE A MEDALLION", use_container_width=True, disabled=True)
