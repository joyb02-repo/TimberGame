# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: login.py (TOTAL STRUCTURAL LAYOUT RESET)
# ====================================================================

import streamlit as st
import requests
import os
import base64

API_URL = st.secrets["API_URL"]

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide", initial_sidebar_state="collapsed")

# Initialize session structures safely
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_passcode" not in st.session_state:
    st.session_state["user_passcode"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = "Guest"

# Route immediately if already authenticated
if st.session_state["authenticated"]:
    st.switch_page("pages/dashboard.py")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

logo_b64 = get_image_base64("assets/login_logo.png")
logo_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

# Persistent connection pooling to eliminate first-click false timeout anomalies
@st.cache_resource(ttl=600)
def get_http_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# Base styling for global layout framework
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    
    /* Center the structural HTML component frame container on the screen */
    div.element-container:has(iframe) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin-top: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# Process backend submission directly from the custom component frame
if "form_passcode_payload" in st.query_params:
    submitted_code = st.query_params.get("form_passcode_payload")
    st.query_params.clear()
    
    if len(submitted_code) < 4:
        st.error("Please complete passcode entry.")
    else:
        try:
            http_client = get_http_session()
            chk = http_client.get(API_URL, params={"action": "fetchData", "passcode": submitted_code}, timeout=15)
            
            if chk.status_code == 200 and chk.json().get("status") == "success":
                st.session_state["user_passcode"] = submitted_code
                st.session_state["username"] = chk.json().get("username", "User")
                st.session_state["authenticated"] = True
                st.switch_page("pages/dashboard.py")
            else:
                st.error("Access Denied: Passcode signature validation rejected.")
        except Exception as e:
            st.error("System Matrix Timeout. Please check your network connection.")

# ====================================================================
# UNIFIED HTML ARCHITECTURE COMPONENT (ABSOLUTE LAYOUT SYMMETRY)
# ====================================================================
html_login_template = f"""
<style>
    body {{
        margin: 0; padding: 0; background: transparent;
        font-family: 'Inter', -apple-system, sans-serif;
        display: flex; justify-content: center; align-items: flex-start;
    }}
    
    .login-card-frame {{
        background: #161925;
        border: 1px solid #23273A;
        border-radius: 12px;
        padding: 40px 45px;
        width: 440px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.5);
        box-sizing: border-box;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    
    .logo-wrapper {{
        width: 100%; display: flex; justify-content: center; margin-bottom: 25px;
    }}
    .logo-wrapper img {{
        max-height: 140px; width: auto; object-fit: contain;
    }}
    
    .header-text {{
        font-size: 22px; font-weight: 600; color: #FFFFFF; margin-bottom: 10px; letter-spacing: 0.5px;
    }}
    .sub-text {{
        font-size: 13px; color: rgba(255, 255, 255, 0.4); margin-bottom: 30px; line-height: 1.5;
    }}
    
    .input-row-container {{
        position: relative; width: 160px; height: 46px; margin-bottom: 25px;
    }}
    .passcode-field {{
        width: 100%; height: 100%; background-color: #0E1117; border: 1px solid #23273A; border-radius: 6px;
        color: #FFF; text-align: center; font-size: 28px; font-weight: 700; letter-spacing: 6px;
        box-sizing: border-box; padding: 0 35px 0 10px; outline: none; transition: border-color 0.15s;
    }}
    .passcode-field:focus {{ border-color: #F4D068; }}
    
    .visibility-toggle-btn {{
        position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
        background: none; border: none; cursor: pointer; color: rgba(255, 255, 255, 0.4);
        padding: 0; display: flex; align-items: center; justify-content: center;
    }}
    .visibility-toggle-btn:hover {{ color: #FFF; }}
    .visibility-toggle-btn svg {{ width: 18px; height: 18px; fill: currentColor; }}
    
    /* THE FIX: Absolute stretch layout rule matching the login card perfectly */
    .submit-action-button {{
        width: 100%; height: 46px; background-color: #F4D068; border: none; border-radius: 6px;
        color: #0E1117; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;
        text-align: center; cursor: pointer; box-sizing: border-box; transition: opacity 0.15s;
    }}
    .submit-action-button:hover {{ opacity: 0.9; }}
</style>

<form class="login-card-frame" id="gatewayForm" method="GET" action="" target="_parent">
    <div class="logo-wrapper">
        <img src="{logo_src}" alt="Logo" style="{ 'display:none;' if not logo_src else '' }" />
    </div>
    <div class="header-text">Portfolio System Access</div>
    <div class="sub-text">Enter your 4-digit master passcode key to authenticate transaction nodes.</div>
    
    <div class="input-row-container">
        <input class="passcode-field" type="password" id="passInput" name="form_passcode_payload" maxlength="4" autocomplete="off" />
        <button class="visibility-toggle-btn" type="button" onclick="togglePasscodeMask()" id="toggleEyeBtn">
            <svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
        </button>
    </div>
    
    <button class="submit-action-button" type="submit">Verify Passcode</button>
</form>

<script>
    // Ensure parent pathname handles multi-page deployment environments cleanly
    document.getElementById('gatewayForm').action = window.parent.location.origin + window.parent.location.pathname;

    function togglePasscodeMask() {{
        const field = document.getElementById('passInput');
        const btn = document.getElementById('toggleEyeBtn');
        if (field.type === "password") {{
            field.type = "text";
            btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.82l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.74-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.01-.16c0-1.66-1.34-3-3-3l-.16.01z"/></svg>';
        }} else {{
            field.type = "password";
            btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>';
        }}
    }}
</script>
"""

st.components.v1.html(html_login_template, height=480, scrolling=False)
