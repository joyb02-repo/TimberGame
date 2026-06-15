import streamlit as st
import requests
import os
import base64

# --- SECURE APPS SCRIPT LINK ---
API_URL = st.secrets["API_URL"]

# Exact 12-medallion order matching your sheet rows
MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

st.set_page_config(page_title="Medallion Core Showcase", page_icon="🏅", layout="wide")

# --- FOOLPROOF DATA FETCH ENGINE ---
def load_perfect_metadata():
    """Fetches real-time parameters and normalizes keys to prevent sheet mismatches."""
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            backend_res = response.json()
            meta_map = {}
            
            for item in backend_res.get("medallions", []):
                raw_name = item.get("Medallion")
                if raw_name:
                    # Normalize the key name (lowercase, no trailing spaces) to guarantee alignment
                    clean_name = str(raw_name).strip().lower()
                    
                    # Dynamically catch "Asset Price" or "Value" columns seamlessly
                    price_val = item.get("Asset Price") or item.get("Value") or "$0"
                    
                    meta_map[clean_name] = {
                        "RealName": str(raw_name).strip(),
                        "Rarity": item.get("Rarity", "Common"),
                        "Probability": str(item.get("Probability", "0%")),
                        "Availability": str(item.get("Availability", "0")),
                        "Value": str(price_val)
                    }
            return meta_map
    except Exception as e:
        st.error(f"Google Sheet Sync Error: {str(e)}")
    return {}

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Fetch the live, sanitized database records
live_metadata = load_perfect_metadata()

# Mock user stock metrics (replace with your dynamic session user variables as needed)
mock_user = {
    "Spruce": 6, "Pine": 2, "Meranti": 0, "Balsa": 0, "Oak": 0, "Maple": 0,
    "Walnut": 0, "Cherry": 0, "Mahogany": 2, "Ebony": 0, "Rosewood": 1, "Agarwood": 0
}

# --- HEADER TITLE DISPLAY ---
st.markdown("""
    <h2 style='font-family: system-ui; font-weight: 800; color: #FFFFFF; margin-bottom: 5px;'>🪵 Medallion Showcase Casement</h2>
    <p style='font-family: system-ui; color: #A0AEC0; font-size: 0.95rem; margin-bottom: 25px;'>Hover over unlocked components to inspect live spreadsheet parameters.</p>
""", unsafe_allow_html=True)


# ====================================================================
# UNIFIED GRID RENDERER (Single HTML Iframe Engine)
# ====================================================================

# Global stylesheet setup to create a dedicated safety headroom for expanding tooltips
html_elements = """
<style>
    body {
        margin: 0;
        padding: 0;
        background-color: #0E1117; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        overflow: hidden;
    }
    .casement-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 12px;
        padding-top: 140px; /* Provides ample vertical headroom for hover containers */
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
    
    /* Clean, Floating Tooltip Containers positioned safely above components */
    .node-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 110px; 
        left: 50%;
        transform: translateX(-50%);
        width: 165px;
        background: #161925;
        border: 1px solid #282E48;
        border-radius: 8px;
        padding: 12px;
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
        margin-bottom: 5px;
        white-space: nowrap;
        text-align: left;
    }
    .tip-line span {
        font-weight: 700;
        color: #F4D068;
    }
</style>
<div class="casement-grid">
"""

# Structural mapping loop
for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    owned = int(mock_user.get(wood_name, 0))
    
    # Use our normalized string to fetch matching metrics from the sheet dictionary
    lookup_key = wood_name.strip().lower()
    
    if lookup_key in live_metadata:
        meta = live_metadata[lookup_key]
        rarity = meta["Rarity"]
        prob = meta["Probability"] if "%" in meta["Probability"] else f"{meta['Probability']}%"
        avail = meta["Availability"]
        val = meta["Value"]
    else:
        # Secure fallbacks in case row completely disappears from spreadsheet tracking
        rarity = "Unknown"
        prob = "0%"
        avail = "0"
        val = "$0"

    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    
    # Inject item variables into the single frame
    html_elements += f"""
    <div class="grid-node">
        <div class="node-tooltip">
            <div class="tip-line">💎 Name: <span>{wood_name}</span></div>
            <div class="tip-line">🏷️ Rarity: <span>{rarity}</span></div>
            <div class="tip-line">🎲 Prob: <span>{prob}</span></div>
            <div class="tip-line">📦 Avail: <span>{avail} left</span></div>
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

# Deploy our single, unified, scroll-free component
st.components.v1.html(html_elements, height=270, scrolling=False)
