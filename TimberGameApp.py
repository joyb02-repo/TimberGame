# ====================================================================
# PLATINUM MASTER WORKSPACE - STREAMLIT ENGINE WORKSPACE (SECURE ACCESS)
# ENVIRONMENT SPECIFICATION: GITHUB DEPLOYMENT RUNTIME READY
# ====================================================================

import streamlit as st
import requests
import os
import base64

API_URL = st.secrets["API_URL"]

# Initialize session structures
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_passcode" not in st.session_state:
    st.session_state["user_passcode"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = "Guest"

MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

LABEL_MAPPING = {
    "Spruce": "SPRC", "Pine": "PINE", "Meranti": "MRNT", "Balsa": "BALS",
    "Oak": "OAKW", "Maple": "MAPL", "Walnut": "WALN", "Cherry": "CHER",
    "Mahogany": "MHGN", "Ebony": "EBNY", "Rosewood": "RSWD", "Agarwood": "AGAR"
}

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Inject Global Background Gridded Theme Stylesheet so it covers BOTH login and app screens uniformly
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    /* Hide default Streamlit visual headers to keep the custom theme pristine */
    header, [data-testid="stHeader"] { visibility: hidden; height: 0px; }
</style>
""", unsafe_with_html=True)

# ====================================================================
# ARCHITECTURE SPLIT - INTERACTION PANEL A: GATEWAY LOGIN CONSOLE
# ====================================================================
if not st.session_state["authenticated"]:
    # Custom CSS styled Container Row to align the login console card perfectly center
    st.markdown("""
    <style>
        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 10vh;
            width: 100%;
        }
        .login-card {
            background: #161925; 
            border: 1px solid #23273A; 
            border-radius: 12px;
            padding: 40px; 
            width: 360px; 
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        .login-title { font-size: 20px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px; letter-spacing: 0.5px; font-family: 'Inter', sans-serif; }
        .login-subtitle { font-size: 12px; color: rgba(255, 255, 255, 0.3); margin-bottom: 24px; line-height: 1.4; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_with_html=True)
    
    # Render UI Structure
    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_with_html=True)
    st.markdown('<div class="login-title">Portfolio System Access</div>', unsafe_with_html=True)
    st.markdown('<div class="login-subtitle">Enter your 4-digit master passcode key to authenticate transaction nodes.</div>', unsafe_with_html=True)
    
    # Native Streamlit Form to manage clean state actions
    with st.form("login_form", clear_on_submit=False):
        passcode_input = st.text_input(
            label="Passcode Input Gate",
            value="",
            max_chars=4,
            type="password",
            placeholder="••••",
            label_visibility="collapsed"
        )
        
        # Override native form submit button cosmetics to perfectly match our theme
        st.markdown("""
        <style>
            div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
            button[kind="primaryFormSubmit"] {
                width: 100% !important; height: 44px !important; background-color: #F4D068 !important; 
                border: none !important; border-radius: 6px !important; color: #0E1117 !important; 
                font-size: 13px !important; font-weight: 700 !important; text-transform: uppercase !important; 
                letter-spacing: 1px !important; cursor: pointer !important; margin-top: 10px !important;
            }
            button[kind="primaryFormSubmit"]:hover { transform: scale(1.02); }
            input[type="password"] {
                background-color: #0E1117 !important; border: 1px solid #23273A !important; 
                color: #FFF !important; text-align: center !important; font-size: 20px !important; 
                font-weight: 700 !important; letter-spacing: 8px !important; height: 44px !important;
            }
        </style>
        """, unsafe_with_html=True)
        
        submit_login = st.form_submit_button("Verify Passcode")
        
        if submit_login:
            clean_pass = passcode_input.strip()
            if len(clean_pass) < 4:
                st.error("Please complete passcode matrix entry.")
            else:
                with st.spinner("Authenticating transaction node..."):
                    try:
                        # Direct Server-to-Server network communication (No CORS limitations!)
                        chk = requests.get(API_URL, params={"action": "fetchData", "passcode": clean_pass}, timeout=12)
                        if chk.status_code == 200:
                            res_data = chk.json()
                            if res_data.get("status") == "success":
                                st.session_state["user_passcode"] = clean_pass
                                st.session_state["username"] = res_data.get("username", "User")
                                st.session_state["authenticated"] = True
                                st.rerun()
                            else:
                                st.error(res_data.get("message", "Invalid passcode credentials."))
                        else:
                            st.error(f"Sheet returned error status: {chk.status_code}")
                    except Exception as err:
                        st.error(f"Network handshake failed: {str(err)}")
                        
    st.markdown('</div></div>', unsafe_with_html=True)

# ====================================================================
# ARCHITECTURE SPLIT - INTERACTION PANEL B: VERIFIED MASTER ECOSYSTEM
# ====================================================================
else:
    @st.cache_data(ttl=1)
    def fetch_all_sheet_data(passcode):
        try:
            params = {"action": "fetchData", "passcode": passcode}
            response = requests.get(API_URL, params=params, timeout=15, allow_redirects=True)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    medallions_map = {str(m.get("Medallion", "")).strip().lower(): m for m in data.get("medallions", [])}
                    master_summary = data.get("master_summary", {})
                    return medallions_map, master_summary.get("Inventory", {}), master_summary.get("CollectionValue", "$0"), master_summary.get("MedallionsCollected", "0")
        except:
            pass
        return {}, {}, "$0", "0"

    live_data, live_inventory, summary_value, summary_collected = fetch_all_sheet_data(st.session_state["user_passcode"])
    
    if not str(summary_value).strip().startswith("$"):
        summary_value = f"${str(summary_value).strip()}"

    asset_map_js = "{"
    for wood in MEDALLION_COLUMNS:
        b64 = get_image_base64(f"assets/{wood.lower()}.png")
        if b64: asset_map_js += f"'{wood}': 'data:image/png;base64,{b64}',"
    asset_map_js += "}"

    html_base_template = """
    <style>
        body {
            margin: 0; padding: 25px 0 0 0; background: transparent;
            font-family: 'Inter', system-ui, sans-serif;
        }
        .portfolio-title { text-align: center; font-size: 24px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px; }
        .portfolio-intro { text-align: center; max-width: 800px; margin: 0 auto 20px auto; font-size: 13px; line-height: 1.6; color: rgba(255, 255, 255, 0.25); }
        .portfolio-intro span { color: rgba(244, 208, 104, 0.4); font-weight: 600; }
        .casement-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; padding: 0 15px; }
        .grid-node { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
        .image-frame { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; box-sizing: border-box; }
        .image-frame img { width: 100%; height: 100%; object-fit: contain; transition: transform 0.15s ease-in-out; box-sizing: border-box; }
        .lock-node { width: 52px; height: 52px; border-radius: 50%; border: 2px dashed #23273A; background: #161925; display: flex; align-items: center; justify-content: center; color: #3D4563; font-size: 11px; transition: transform 0.15s ease-in-out; box-sizing: border-box; }
        .grid-node:hover .image-frame img, .grid-node:hover .lock-node { transform: scale(1.15); }
        .quantity-badge { font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }
        .label-badge { font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .node-tooltip { visibility: hidden; opacity: 0; position: absolute; top: -120px; left: 50%; transform: translateX(-50%); width: 180px; background: #161925; border: 1px solid #282E48; border-radius: 8px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); z-index: 99999; transition: opacity 0.12s ease-in-out; pointer-events: none; }
        .grid-node:hover .node-tooltip { visibility: visible; opacity: 1; }
        .grid-node:first-child .node-tooltip { left: 0; transform: translateX(0); }
        .grid-node:last-child .node-tooltip { left: auto; right: 0; transform: translateX(0); }
        .tip-line { font-size: 11px; color: #E2E8F0; margin-bottom: 5px; text-align: left; white-space: nowrap; }
        .tip-line span { font-weight: 700; color: #F4D068; }
        .tip-line span.rarity-common { color: #CD7F32; }       
        .tip-line span.rarity-uncommon { color: #C0C0C0; }     
        .tip-line span.rarity-rare { color: #3b82f6; }         
        .tip-line span.rarity-epic { color: #a855f7; }         
        .tip-line span.rarity-legendary { color: #f59e0b; }    
        
        .dashboard-row { display: flex; justify-content: center; gap: 20px; margin-top: 30px; padding: 0 15px; }
        .stat-card { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 10px 20px; min-width: 180px; text-align: center; }
        .stat-label { font-size: 11px; text-transform: uppercase; color: #718096; letter-spacing: 0.75px; margin-bottom: 4px; }
        .stat-value { font-size: 18px; font-weight: 700; color: #FFF; }
        
        .action-container { display: flex; flex-direction: column; align-items: center; margin-top: 25px; width: 100%; }
        .pin-auth-wrapper { display: flex; justify-content: center; gap: 8px; margin-bottom: 12px; width: 100%; box-sizing: border-box; }
        .pin-input { width: 150px; height: 38px; background: #161925; border: 1px solid #23273A; border-radius: 6px; color: #FFF; text-align: center; font-size: 14px; font-weight: 600; letter-spacing: 2px; outline: none; box-sizing: border-box; }
        .pin-input::placeholder { font-size: 11px; letter-spacing: 0.5px; color: #4A5568; }
        .pin-input:focus { border-color: #3D4563; }
        .pin-verify-btn { padding: 0 16px; height: 38px; background: #23273A; border: none; border-radius: 6px; color: #E2E8F0; font-size: 11px; font-weight: 700; text-transform: uppercase; cursor: pointer; box-sizing: border-box; transition: background 0.15s; }
        .pin-verify-btn:hover { background: #2F354E; }
        .pin-feedback-msg { font-size: 11px; font-weight: 600; margin-bottom: 10px; height: 14px; text-align: center; }
        
        .mine-button { width: 424px; height: 46px; background-color: #F4D068; border: none; border-radius: 6px; color: #0E1117; font-size: 14px; font-weight: 700; text-transform: uppercase; cursor: pointer; transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 4px 15px rgba(244, 208, 104, 0.2); }
        .mine-button:hover { transform: scale(1.05); }
        .mine-button:disabled { opacity: 0.35; cursor: not-allowed; transform: scale(1) !important; background-color: #161925 !important; color: #3D4563 !important; border: 1px solid #23273A; box-shadow: none !important; }
        
        .animation-display { margin-top: 20px; height: 240px; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; }
        .spin-box { width: 140px; height: 140px; min-height: 140px; border-radius: 12px; background: #161925; border: 3px solid #23273A; display: none; align-items: center; justify-content: center; box-sizing: border-box; }
        .spin-box img { width: 88%; height: 88%; object-fit: contain; }
        .outcome-text-wrapper { margin-top: 15px; height: 35px; text-align: center; opacity: 0; transition: opacity 0.2s ease-in-out; }
        .outcome-top { font-size: 11px; font-weight: 600; color: #718096; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
        .outcome-bottom { font-size: 18px; font-weight: 800; color: #F4D068; text-transform: uppercase; }
        .claim-button { margin-top: 14px; width: 160px; height: 32px; background-color: transparent; border: 2px solid #F4D068; border-radius: 4px; color: #F4D068; font-size: 11px; font-weight: 700; text-transform: uppercase; cursor: pointer; opacity: 0; transform: translateY(5px); transition: all 0.2s ease-in-out; }
        .claim-button.visible { opacity: 1; transform: translateY(0); }
        .claim-button:hover { background-color: #F4D068; color: #0E1117; }
    </style>

    <div class="portfolio-title">Timber Medallion Portfolio — __USERNAME_UPPER__</div>
    <div class="portfolio-intro"> Master tracking dashboard powered directly by your cloud inventory records. Premium tokens scale in rarity up to the single production run <span>Agarwood Medallion</span>.</div>

    <div class="casement-grid">
    __GRID_ITEMS_PLACEHOLDER__
    </div>

    <div class="dashboard-row">
        <div class="stat-card">
            <div class="stat-label">Collection Value</div>
            <div class="stat-value">__VALUE_PLACEHOLDER__</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Medallions Collected</div>
            <div class="stat-value">__COLLECTED_PLACEHOLDER__</div>
        </div>
    </div>

    <div class="action-container">
        <div class="pin-auth-wrapper" id="pinSection">
            <input class="pin-input" type="text" id="pinField" placeholder="6-DIGIT PIN" maxlength="6" />
            <button class="pin-verify-btn" id="verifyBtn" onclick="evaluatePinAuthorization()">Verify PIN</button>
        </div>
        <div class="pin-feedback-msg" id="feedbackMsg" style="color: #718096;"></div>

        <button class="mine-button" id="mineBtn" disabled onclick="runMiningSequence()">Mine a Medallion</button>
        
        <div class="animation-display">
            <div class="spin-box" id="cyclerBox"> <img id="cyclerImg" src="" /> </div>
            <div class="outcome-text-wrapper" id="outcomeWrapper">
                <div class="outcome-top">Successfully Mined:</div>
                <div class="outcome-bottom" id="itemNameTxt"></div>
            </div>
            <div style="height:46px;"><button class="claim-button" id="claimBtn" onclick="commitClaimToSheets()">Claim Medallion</button></div>
        </div>
    </div>

    <script>
        const assetLibrary = __ASSET_MAP_PLACEHOLDER__;
        const pool = ['Spruce', 'Pine', 'Meranti', 'Balsa', 'Oak', 'Maple', 'Walnut', 'Cherry', 'Mahogany', 'Ebony', 'Rosewood', 'Agarwood'];
        const endpoint = "__API_URL_PLACEHOLDER__";
        let selectedItem = "";

        function evaluatePinAuthorization() {
            const pinValue = document.getElementById("pinField").value.trim();
            const feedback = document.getElementById("feedbackMsg");
            const verifyBtn = document.getElementById("verifyBtn");
            const mineBtn = document.getElementById("mineBtn");
            
            if (pinValue.length < 4) { 
                feedback.style.color = "#ef4444"; 
                feedback.innerText = "Please enter a complete PIN key."; 
                return; 
            }
            
            verifyBtn.disabled = true; 
            verifyBtn.innerText = "Checking..."; 
            feedback.style.color = "#718096"; 
            feedback.innerText = "Authenticating code...";
            
            const queryUrl = endpoint + "?action=verifyPin&pin=" + encodeURIComponent(pinValue);
            const imgPing = new Image();
            
            imgPing.onload = imgPing.onerror = function() {
                setTimeout(async () => {
                    try {
                        const res = await fetch(endpoint + "?action=fetchData&passcode=__PASSCODE_RAW__");
                        const data = await res.json();
                        feedback.style.color = "#10b981"; 
                        feedback.innerText = "Access granted! Mining console unlocked.";
                        document.getElementById("pinField").disabled = true; 
                        verifyBtn.style.display = "none"; 
                        mineBtn.disabled = false;
                    } catch(e) {
                        feedback.style.color = "#ef4444"; 
                        feedback.innerText = "Invalid or expired security code.";
                        verifyBtn.disabled = false; 
                        verifyBtn.innerText = "Verify PIN";
                    }
                }, 600);
            };
            imgPing.src = queryUrl;
        }

        document.getElementById("pinField")?.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                evaluatePinAuthorization();
            }
        });

        function runMiningSequence() {
            const btn = document.getElementById('mineBtn'); const box = document.getElementById('cyclerBox'); const img = document.getElementById('cyclerImg');
            const wrapper = document.getElementById('outcomeWrapper'); const itemTxt = document.getElementById('itemNameTxt'); const claimBtn = document.getElementById('claimBtn');
            btn.disabled = true; wrapper.style.opacity = "0"; claimBtn.classList.remove('visible'); box.style.display = "flex"; box.style.borderColor = "#23273A";
            let counter = 0; let speed = 40; selectedItem = pool[Math.floor(Math.random() * pool.length)];
            function cycle() {
                const currentItem = pool[counter % pool.length]; if (assetLibrary[currentItem]) img.src = assetLibrary[currentItem]; counter++;
                if (speed < 320) { speed += 14; setTimeout(cycle, speed); } else {
                    const finalSelection = assetLibrary[selectedItem] ? selectedItem : currentItem;
                    if (assetLibrary[selectedItem]) img.src = assetLibrary[finalSelection];
                    itemTxt.innerText = finalSelection.toUpperCase() + " MEDALLION!"; wrapper.style.opacity = "1"; claimBtn.classList.add('visible');
                }
            }
            setTimeout(cycle, speed);
        }

        function commitClaimToSheets() {
            if (!selectedItem) return;
            const claimBtn = document.getElementById('claimBtn'); claimBtn.disabled = true; claimBtn.innerText = "Saving...";
            const pingUrl = endpoint + "?action=mineMedallion&passcode=" + encodeURIComponent("__PASSCODE_RAW__") + "&item=" + encodeURIComponent(selectedItem);
            const imgPing = new Image();
            imgPing.onload = imgPing.onerror = function() {
                setTimeout(() => { const win = (window.self !== window.top) ? window.parent : window; win.location.reload(); }, 600);
            };
            imgPing.src = pingUrl;
        }
    </script>
    """

    grid_elements_html = ""
    for wood_name in MEDALLION_COLUMNS:
        display_label = LABEL_MAPPING.get(wood_name, wood_name[:4].upper())
        lookup_key = wood_name.strip().lower()
        owned = int(live_inventory.get(lookup_key, 0))
        sheet_row = live_data.get(lookup_key, None)
        rarity_class = ""
        
        if sheet_row:
            rarity = sheet_row.get("Rarity", "N/A")
            value = sheet_row.get("Value", "N/A")
            availability = sheet_row.get("Availability", "N/A")
            raw_probability = sheet_row.get("Probability", "N/A")
            clean_rarity = str(rarity).strip().lower()
            if "common" in clean_rarity and "uncommon" not in clean_rarity: rarity_class = "rarity-common"
            elif "uncommon" in clean_rarity: rarity_class = "rarity-uncommon"
            elif "rare" in clean_rarity: rarity_class = "rarity-rare"
            elif "epic" in clean_rarity: rarity_class = "rarity-epic"
            elif "legendary" in clean_rarity: rarity_class = "rarity-legendary"
            
            if value != "N/A" and not str(value).strip().startswith("$"): value = f"${str(value).strip()}"
            prob_str = str(raw_probability).replace("%", "").strip()
            try:
                prob_val = float(prob_str)
                if 0 < prob_val < 1.0: prob_val = prob_val * 100
                probability = f"{prob_val:g}%"
            except:
                probability = f"{prob_str}%" if prob_str else "N/A"
        else:
            rarity = value = availability = probability = "N/A"
            
        img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
        grid_elements_html += f"""
        <div class="grid-node">
            <div class="node-tooltip">
                <div class="tip-line">Name: <span>{wood_name}</span></div>
                <div class="tip-line">Rarity: <span class="{rarity_class}">{rarity}</span></div>
                <div class="tip-line">Value: <span>{value}</span></div>
                <div class="tip-line">Availability: <span>{availability} left</span></div>
                <div class="tip-line">Probability: <span>{probability}</span></div>
            </div>
            <div class="image-frame">
                {"<img src='data:image/png;base64," + img_b64 + "' />" if (owned > 0 and img_b64) else "<div class='lock-node'>🔒</div>"}
            </div>
            <div class="quantity-badge">{"x" + str(owned) if owned > 0 else "&nbsp;"}</div>
            <div class="label-badge">{display_label}</div>
        </div>
        """

    html_elements = html_base_template.replace("__GRID_ITEMS_PLACEHOLDER__", grid_elements_html)
    html_elements = html_elements.replace("__VALUE_PLACEHOLDER__", summary_value)
    html_elements = html_elements.replace("__COLLECTED_PLACEHOLDER__", summary_collected)
    html_elements = html_elements.replace("__ASSET_MAP_PLACEHOLDER__", asset_map_js)
    html_elements = html_elements.replace("__USERNAME_UPPER__", st.session_state["username"].upper())
    html_elements = html_elements.replace("__PASSCODE_RAW__", st.session_state["user_passcode"])
    html_elements = html_elements.replace("__API_URL_PLACEHOLDER__", API_URL)

    st.components.v1.html(html_elements, height=750, scrolling=False)
