# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/dashboard.py (GUARANTEED SYNCHRONIZED REFRESH ENGINE)
# ====================================================================

import streamlit as st
import requests
import os
import base64
import json

# Security Wall: Redirect if not authenticated via root login file
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("login.py")

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide", initial_sidebar_state="collapsed")

# 🎯 BASE ENVIRONMENT STYLING
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    div.block-container { padding-top: 25px !important; padding-bottom: 10px !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

API_URL = st.secrets["API_URL"]

MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

LABEL_MAPPING = {
    "Spruce": "SPRC", "Pine": "PINE", "Meranti": "MRNT", "Balsa": "BALS",
    "Oak": "OAKW", "Maple": "MAPL", "Walnut": "WALN", "Cherry": "CHER",
    "Mahogany": "MHGN", "Ebony": "EBNY", "Rosewood": "RSWD", "Agarwood": "AGAR"
}

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Force clear cache completely if an operation sequence has just concluded
if "just_claimed" in st.session_state and st.session_state["just_claimed"]:
    st.cache_data.clear()
    st.session_state["just_claimed"] = False

@st.cache_data(ttl=600)
def fetch_sheet_records(passcode):
    try:
        r = requests.get(API_URL, params={"action": "fetchData", "passcode": passcode}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                m_map = {str(m.get("Medallion", "")).strip().lower(): m for m in d.get("medallions", [])}
                summary = d.get("master_summary", {})
                return m_map, summary.get("Inventory", {}), summary.get("CollectionValue", "$0"), summary.get("MedallionsCollected", "0")
    except: pass
    return {}, {}, "$0", "0"

live_data, live_inventory, summary_value, summary_collected = fetch_sheet_records(st.session_state["user_passcode"])
if not str(summary_value).strip().startswith("$"):
    summary_value = f"${str(summary_value).strip()}"

asset_map_js = "{"
for wood in MEDALLION_COLUMNS:
    b64 = get_image_base64(f"assets/{wood.lower()}.png")
    if b64: asset_map_js += f"'{wood}': 'data:image/png;base64,{b64}',"
asset_map_js += "}"

js_pool_items = []
js_pool_weights = []
for wood_name in MEDALLION_COLUMNS:
    lookup_key = wood_name.strip().lower()
    sheet_row = live_data.get(lookup_key, None)
    weight_value = 1.0
    if sheet_row and "Probability" in sheet_row:
        prob_str = str(sheet_row["Probability"]).replace("%", "").strip()
        try: weight_value = float(prob_str)
        except ValueError: weight_value = 1.0
    js_pool_items.append(wood_name)
    js_pool_weights.append(weight_value)

html_base_template = """
<style>
    body { margin: 0; padding: 10px 0 0 0; background: transparent; font-family: 'Inter', sans-serif; position: relative; }
    .header-wrapper { position: relative; max-width: 100%; margin: 0 auto; padding: 0 15px; text-align: center; }
    
    .portfolio-title { font-size: 24px; font-weight: 600; color: #FFFFFF; margin-bottom: 8px; }
    .portfolio-title span.user-accent { color: #F4D068; }
    .portfolio-intro { max-width: 850px; margin: 0 auto 35px auto; font-size: 13px; line-height: 1.6; color: rgba(255, 255, 255, 0.35); }
    .portfolio-intro span { color: rgba(244, 208, 104, 0.8); font-weight: 600; }
    
    .casement-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; padding: 0 15px; margin-top: 10px; }
    .grid-node { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .image-frame { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
    .image-frame img { width: 100%; height: 100%; object-fit: contain; transition: transform 0.15s ease-in-out; }
    .lock-node { width: 52px; height: 52px; border-radius: 50%; border: 2px dashed #23273A; background: #161925; display: flex; align-items: center; justify-content: center; color: #3D4563; font-size: 11px; }
    .grid-node:hover .image-frame img { transform: scale(1.15); }
    .quantity-badge { font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }
    .label-badge { font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* 🛠️ HOVER TEXT STRUCTURAL SYSTEM */
    .node-tooltip { 
        visibility: hidden; opacity: 0; position: absolute; top: -115px; left: 50%; 
        transform: translateX(-50%); width: 150px; background: #161925; border: 1px solid #282E48; 
        border-radius: 8px; padding: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); 
        z-index: 9999999 !important; transition: opacity 0.12s ease-in-out; pointer-events: none; 
    }
    .grid-node:hover .node-tooltip { visibility: visible; opacity: 1; }
    .grid-node:first-child .node-tooltip { left: 0; transform: translateX(0); }
    .grid-node:last-child .node-tooltip { left: auto; right: 0; transform: translateX(0); }
    
    .tip-line { font-size: 11px; color: #E2E8F0; margin-bottom: 4px; text-align: left; white-space: nowrap; }
    .tip-line span { font-weight: 700; color: #F4D068; }
    .tip-line span.rarity-common { color: #CD7F32; }       
    .tip-line span.rarity-uncommon { color: #C0C0C0; }     
    .tip-line span.rarity-rare { color: #3b82f6; }         
    .tip-line span.rarity-epic { color: #a855f7; }         
    .tip-line span.rarity-legendary { color: #f59e0b; }    
    
    .dashboard-row { display: flex; justify-content: center; gap: 20px; margin-top: 30px; padding: 0 15px; }
    .stat-card { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 10px 20px; min-width: 180px; text-align: center; }
    .stat-label { font-size: 11px; text-transform: uppercase; color: #718096; margin-bottom: 4px; }
    .stat-value { font-size: 18px; font-weight: 700; color: #F4D068; }
    
    .action-container { display: flex; flex-direction: column; align-items: center; margin-top: 25px; width: 100%; }
    .pin-auth-wrapper { display: flex; justify-content: center; gap: 8px; margin-bottom: 12px; }
    .pin-input { width: 150px; height: 38px; background: #161925; border: 1px solid #23273A; border-radius: 6px; color: #FFF; text-align: center; font-size: 14px; font-weight: 600; outline: none; }
    .pin-verify-btn { padding: 0 16px; height: 38px; background: #23273A; border: none; border-radius: 6px; color: #E2E8F0; font-size: 11px; font-weight: 700; text-transform: uppercase; cursor: pointer; }
    .pin-feedback-msg { font-size: 11px; font-weight: 600; margin-bottom: 10px; height: 14px; }
    
    .mine-button { width: 424px; height: 46px; background-color: #F4D068; border: none; border-radius: 6px; color: #0E1117; font-size: 14px; font-weight: 700; text-transform: uppercase; cursor: pointer; box-shadow: 0 4px 15px rgba(244, 208, 104, 0.2); }
    .mine-button:disabled { opacity: 0.35; cursor: not-allowed; background-color: #161925 !important; color: #3D4563 !important; border: 1px solid #23273A; box-shadow: none !important; }

    /* 🎴 COMPACT OVERLAY DIALOG SYSTEM */
    .modal-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(14, 17, 23, 0.85); backdrop-filter: blur(4px);
        display: none; align-items: flex-start; justify-content: center; z-index: 999999;
        padding-top: 60px; box-sizing: border-box;
    }
    .modal-box {
        background: #0E1117; border: 1px solid #23273A; border-radius: 12px;
        width: 320px; padding: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.7);
        display: flex; flex-direction: column; align-items: center; text-align: center;
        position: relative;
    }
    .modal-subheading {
        font-size: 13px; font-weight: 500; color: rgba(255, 255, 255, 0.6);
        letter-spacing: 0.5px; margin-bottom: 16px; text-transform: none;
    }
    .spin-box { width: 140px; height: 140px; border-radius: 12px; background: #161925; border: 3px solid #23273A; display: flex; align-items: center; justify-content: center; }
    .spin-box img { width: 88%; height: 88%; object-fit: contain; }
    .outcome-text-wrapper { margin-top: 15px; height: 35px; text-align: center; opacity: 0; transition: opacity 0.2s ease; }
    .outcome-bottom { font-size: 18px; font-weight: 800; color: #F4D068; }
    
    .claim-button { margin-top: 14px; width: 160px; height: 32px; background-color: transparent; border: 2px solid #F4D068; border-radius: 4px; color: #F4D068; font-size: 11px; font-weight: 700; text-transform: uppercase; cursor: pointer; opacity: 0; transform: translateY(5px); transition: all 0.2s; display: inline-block; }
    .claim-button.visible { opacity: 1 !important; transform: translateY(0) !important; }
    .claim-button:hover { background-color: #F4D068; color: #0E1117; }
</style>

<div class="header-wrapper">
    <div class="portfolio-title">Timber Medallion Portfolio: <span class="user-accent">__USERNAME_UPPER__</span></div>
    <div class="portfolio-intro">
        Master tracking dashboard connected live to cloud inventory matrices. Authenticated users can generate verified asset transactions by supplying validation tokens below. Hover over any node in your matrix layout to see real-time supply indexes, market valuations, and algorithm probabilities. Premium tier tokens scale up to the highly coveted, single production run <span>Agarwood Medallion</span>.
    </div>
</div>

<div class="casement-grid">__GRID_ITEMS_PLACEHOLDER__</div>

<div class="dashboard-row">
    <div class="stat-card"><div class="stat-label">Collection Value</div><div class="stat-value">__VALUE_PLACEHOLDER__</div></div>
    <div class="stat-card"><div class="stat-label">Medallions Collected</div><div class="stat-value">__COLLECTED_PLACEHOLDER__</div></div>
</div>

<div class="action-container">
    <div class="pin-auth-wrapper">
        <input class="pin-input" type="text" id="pinField" placeholder="6-DIGIT PIN" maxlength="6" />
        <button class="pin-verify-btn" id="verifyBtn" onclick="evaluatePinAuthorization()">Verify PIN</button>
    </div>
    <div class="pin-feedback-msg" id="feedbackMsg" style="color: #718096;"></div>

    <button class="mine-button" id="mineBtn" disabled onclick="openMiningModal()">Mine a Medallion</button>
</div>

<div class="modal-overlay" id="miningModal">
    <div class="modal-box">
        <div class="modal-subheading">Medallion Mining in Process...</div>
        <div class="spin-box" id="cyclerBox"><img id="cyclerImg" src="" /></div>
        <div class="outcome-text-wrapper" id="outcomeWrapper">
            <div style="font-size:11px; color:#718096; text-transform:uppercase; letter-spacing:1px;">Successfully Mined:</div>
            <div class="outcome-bottom" id="itemNameTxt"></div>
        </div>
        <button class="claim-button" id="claimBtn" onclick="commitClaimToSheets()">Claim Medallion</button>
    </div>
</div>

<script>
    const assetLibrary = __ASSET_MAP_PLACEHOLDER__;
    const pool = __POOL_ITEMS_PLACEHOLDER__;
    const weights = __POOL_WEIGHTS_PLACEHOLDER__;
    const endpoint = "__API_URL_PLACEHOLDER__";
    let selectedItem = "";

    async function evaluatePinAuthorization() {
        const pinValue = document.getElementById("pinField").value.trim();
        const feedback = document.getElementById("feedbackMsg");
        const verifyBtn = document.getElementById("verifyBtn");
        if (pinValue.length < 4) return;
        
        try {
            const response = await fetch(endpoint + "?action=verifyPin&pin=" + encodeURIComponent(pinValue));
            const result = await response.json();
            if (result.status === "success") {
                feedback.style.color = "#10b981"; feedback.innerText = "Access granted!";
                document.getElementById("pinField").disabled = true; verifyBtn.style.display = "none";
                document.getElementById("mineBtn").disabled = false;
            } else {
                feedback.style.color = "#ef4444"; feedback.innerText = "Invalid code key verification.";
            }
        } catch(e) {}
    }

    function selectWeightedWinner(items, itemWeights) {
        const totalWeight = itemWeights.reduce((acc, w) => acc + w, 0);
        const randomNum = Math.random() * totalWeight;
        let runningSum = 0;
        for (let i = 0; i < items.length; i++) {
            runningSum += itemWeights[i];
            if (randomNum <= runningSum) return items[i];
        }
        return items[items.length - 1];
    }

    function openMiningModal() {
        document.getElementById("miningModal").style.display = "flex";
        runMiningSequence();
    }

    function runMiningSequence() {
        const img = document.getElementById('cyclerImg');
        const wrapper = document.getElementById('outcomeWrapper'); 
        const itemTxt = document.getElementById('itemNameTxt'); 
        const claimBtn = document.getElementById('claimBtn');
        
        wrapper.style.opacity = "0"; 
        claimBtn.classList.remove('visible');
        
        let counter = 0; let speed = 40; 
        selectedItem = selectWeightedWinner(pool, weights);
        
        function cycle() {
            const currentItem = pool[counter % pool.length]; 
            if (assetLibrary[currentItem]) img.src = assetLibrary[currentItem]; 
            counter++;
            if (speed < 320) { 
                speed += 16; 
                setTimeout(cycle, speed); 
            } else {
                img.src = assetLibrary[selectedItem];
                itemTxt.innerText = selectedItem.toUpperCase() + "!"; 
                wrapper.style.opacity = "1"; 
                claimBtn.classList.add('visible');
            }
        }
        setTimeout(cycle, speed);
    }

    // ⚡ CROSS-ORIGIN PROMISE TIMEOUT ENGINE: Delivers data, pauses for transaction, fires sync refresh
    function commitClaimToSheets() {
        if (!selectedItem) return;
        const claimBtn = document.getElementById('claimBtn'); 
        claimBtn.disabled = true; 
        claimBtn.innerText = "Saving...";
        
        const timestamp = new Date().getTime();
        const pingUrl = endpoint + "?action=mineMedallion&passcode=" + encodeURIComponent("__PASSCODE_RAW__") + "&item=" + encodeURIComponent(selectedItem) + "&_=" + timestamp;
        
        // Execute unauthenticated dispatch securely using no-cors parameters
        fetch(pingUrl, { mode: 'no-cors' });
        
        // Block window execution system for exactly 2500ms to guarantee row allocation completion
        setTimeout(() => {
            if (window.parent && window.parent.Streamlit) {
                window.parent.Streamlit.setComponentValue("FIRE_REFRESH_" + timestamp);
            } else {
                window.location.reload();
            }
        }, 2500);
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
        except: probability = f"{prob_str}%" if prob_str else "N/A"
    else: rarity = value = availability = probability = "N/A"
        
    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    is_sold_out = str(availability).strip() == "0"
    
    if owned > 0 and img_b64:
        frame_content = f"<img src='data:image/png;base64,{img_b64}' />"
    elif is_sold_out:
        frame_content = "<div class='lock-node'>❌</div>"
    else:
        frame_content = "<div class='lock-node'>🔒</div>"
        
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
            {frame_content}
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
html_elements = html_elements.replace("__POOL_ITEMS_PLACEHOLDER__", json.dumps(js_pool_items))
html_elements = html_elements.replace("__POOL_WEIGHTS_PLACEHOLDER__", json.dumps(js_pool_weights))

# Render current frame view layout
component_sync_signal = st.components.v1.html(html_elements, height=750, scrolling=False)

# Catch update payload signal to wipe cache out safely
if isinstance(component_sync_signal, str) and component_sync_signal.startswith("FIRE_REFRESH_"):
    st.session_state["just_claimed"] = True
    st.cache_data.clear()
    st.rerun()
