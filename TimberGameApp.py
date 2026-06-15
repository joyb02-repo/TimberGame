import streamlit as st
import requests
import os
import base64

# --- SECURE APPS SCRIPT LINK ---
API_URL = st.secrets["API_URL"]

# Master Order list matching your Google Sheet rows exactly
MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

# Set clean dark dashboard background configuration
st.set_page_config(page_title="Medallion Casement Core", page_icon="🏅", layout="wide")

# --- DATA SYNC ENGINE ---
def load_perfect_metadata():
    """Fetches real-time parameters straight from the Medallions sheet tab."""
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            backend_res = response.json()
            
            # Map items using the exact column keys matching your spreadsheet
            meta_map = {}
            for item in backend_res.get("medallions", []):
                m_name = item.get("Medallion")
                if m_name:
                    meta_map[m_name] = {
                        "Rarity": item.get("Rarity", "Common"),
                        "Probability": str(item.get("Probability", "0%")),
                        "Availability": int(item.get("Availability", 0)),
                        "Value": item.get("Asset Price") or item.get("Value") or "$0"
                    }
            return meta_map, backend_res.get("users", [])
    except Exception as e:
        st.error(f"Sync Engine Error: {str(e)}")
    return {}, []

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- LOAD FRESH MOUNT DATA ---
live_metadata, users_list = load_perfect_metadata()

# Pick a mock profile structure or hook your active session state user row here
# (Using a temporary placeholder profile to track inventory counts matching your asset sheet)
mock_user = {
    "Username": "joyb02",
    "Spruce": 6, "Pine": 2, "Meranti": 0, "Balsa": 0, "Oak": 0, "Maple": 0,
    "Walnut": 0, "Cherry": 0, "Mahogany": 2, "Ebony": 0, "Rosewood": 1, "Agarwood": 0
}

# --- HEADER RENDER ---
st.markdown(f"""
    <h2 style='font-family: system-ui; font-weight: 800; color: #FFFFFF; margin-bottom: 5px;'>🪵 Medallion Showcase Casement</h2>
    <p style='font-family: system-ui; color: #A0AEC0; font-size: 0.95rem; margin-bottom: 30px;'>Live structural synchronization matrix.</p>
""", unsafe_allow_html=True)

# ====================================================================
# UNIFIED GRID HOVER ENGINE (Single Iframe HTML Generator)
# ====================================================================

# 1. Base Global Styles for the Iframe Environment
html_elements = """
<style>
    body {
        margin: 0;
        padding: 0;
        background-color: #0E1117; /* Matches seamless Streamlit canvas */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        overflow: hidden;
    }
    .casement-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 12px;
        padding-top: 130px; /* Generates a dedicated safety ceiling for tooltips to expand into */
        padding-left: 10px;
        padding-right: 10px;
    }
    .grid-node {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .image-frame {
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
    }
    .image-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .lock-node {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 2px dashed #23273A;
        background: #161925;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3D4563;
        font-size: 14px;
    }
    .quantity-badge {
        font-size: 12px;
        font-weight: 700;
        color: #F4D068;
        margin-bottom: 2px;
        min-height: 15px;
    }
    .label-badge {
        font-size: 10px;
        font-weight: 700;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Absolute Positioning Tooltip Logic */
    .node-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 105px; /* Safely floats above the image icon asset */
        left: 50%;
        transform: translateX(-50%);
        width: 160px;
        background: #161925;
        border: 1px solid #282E48;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        z-index: 99999;
        transition: opacity 0.15s ease, transform 0.15s ease;
        pointer-events: none;
    }
    .grid-node:hover .node-tooltip {
        visibility: visible;
        opacity: 1;
    }
    .tip-line {
        font-size: 11px;
        color: #E2E8F0;
        margin-bottom: 4px;
        white-space: nowrap;
    }
    .tip-line span {
        font-weight: 700;
        color: #F4D068;
    }
</style>
<div class="casement-grid">
"""

# 2. Dynamic Structural Loop Processing
for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    owned = int(mock_user.get(wood_name, 0))
    
    # Extract spreadsheet metadata definitions with hard coded defaults
    meta = live_metadata.get(wood_name, {"Rarity": "Common", "Probability": "0%", "Availability": 0, "Value": "$0"})
    
    rarity = meta["Rarity"]
    prob = meta["Probability"] if "%" in meta["Probability"] else f"{meta['Probability']}%"
    val = meta["Value"]
    
    # Availability deduction engine matching sheet values minus inventory ownership counts
    avail_left = max(0, meta["Availability"] - owned)
    
    # Process local path mapping strings
    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    
    # Build item component segment
    html_elements += f"""
    <div class="grid-node">
        <div class="node-tooltip">
            <div class="tip-line">💎 Name: <span>{wood_name}</span></div>
            <div class="tip-line">🏷️ Rarity: <span>{rarity}</span></div>
            <div class="tip-line">🎲 Prob: <span>{prob}</span></div>
            <div class="tip-line">📦 Avail: <span>{avail_left} left</span></div>
            <div class="tip-line">💰 Value: <span>{val}</span></div>
        </div>
        
        <div class="image-frame">
            {"<img src='data:image/png;base64," + img_b64 + "' />" if (owned > 0 and img_b64) else "<div class='lock-node'>🔒</div>"}
        </div>
        
        <div class="quantity-badge">{"x" + str(owned) if owned > 0 else "&nbsp;"}</div>
        <div class="label-badge">{display_label}</div>
    </div>
    """

html_elements += "</div>"

# 3. Mount single components to viewport frame with unified height boundaries
st.components.v1.html(html_elements, height=260, scrolling=False)
