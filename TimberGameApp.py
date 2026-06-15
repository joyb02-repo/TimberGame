import streamlit as st
import requests
import os
import base64

API_URL = st.secrets["API_URL"]

MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

st.set_page_config(page_title="Medallion Core", layout="wide")

def load_sheet_medallions():
    """Fetches real-time parameters from the explicit Google Apps Script JSON structure."""
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {str(m["Medallion"]).strip().lower(): m for m in data.get("medallions", [])}
    except Exception as e:
        st.error(f"Data Connection Failure: {str(e)}")
    return {}

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Pull synchronized data records
live_data = load_sheet_medallions()

# Mock user stock balance matrix
mock_user = {
    "Spruce": 6, "Pine": 2, "Meranti": 0, "Balsa": 0, "Oak": 0, "Maple":, 0,
    "Walnut": 0, "Cherry": 0, "Mahogany": 2, "Ebony": 0, "Rosewood": 1, "Agarwood": 0
}

st.markdown("<h3 style='font-family:system-ui; color:#FFF;'>MEDALLION SHOWCASE</h3>", unsafe_allow_html=True)

# ====================================================================
# UNIFIED GRID LAYOUT WITH TEXT & SYMBOL ADJUSTMENTS
# ====================================================================
html_elements = """
<style>
    body {
        margin: 0; padding: 0; background-color: #0E1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        overflow: hidden;
    }
    .casement-grid {
        display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px;
        padding-top: 150px; 
        padding-left: 15px; padding-right: 15px;
    }
    .grid-node {
        position: relative; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
    }
    .image-frame {
        width: 62px; height: 62px; display: flex;
        align-items: center; justify-content: center; margin-bottom: 8px;
    }
    .image-frame img { width: 100%; height: 100%; object-fit: contain; }
    .lock-node {
        width: 52px; height: 52px; border-radius: 50%;
        border: 2px dashed #23273A; background: #161925;
        display: flex; align-items: center; justify-content: center;
        color: #3D4563; font-size: 13px;
    }
    .quantity-badge { font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }
    .label-badge { font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Absolute Floating Tooltip Card Layout */
    .node-tooltip {
        visibility: hidden; opacity: 0; position: absolute;
        bottom: 110px; left: 50%; transform: translateX(-50%);
        width: 180px; background: #161925; border: 1px solid #282E48;
        border-radius: 8px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        z-index: 99999; transition: opacity 0.12s ease-in-out; pointer-events: none;
    }
    .grid-node:hover .node-tooltip { visibility: visible; opacity: 1; }
    
    /* Edge Clip Protection Rules */
    .grid-node:first-child .node-tooltip {
        left: 0;
        transform: translateX(0);
    }
    .grid-node:last-child .node-tooltip {
        left: auto;
        right: 0;
        transform: translateX(0);
    }
    
    .tip-line { font-size: 11px; color: #E2E8F0; margin-bottom: 5px; white-space: nowrap; text-align: left; }
    .tip-line:last-child { margin-bottom: 0; }
    .tip-line span { font-weight: 700; color: #F4D068; }
</style>
<div class="casement-grid">
"""

for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    owned = int(mock_user.get(wood_name, 0))
    
    lookup_key = wood_name.strip().lower()
    sheet_row = live_data.get(lookup_key, None)
    
    if sheet_row:
        rarity = sheet_row.get("Rarity", "N/A")
        value = sheet_row.get("Value", "N/A")
        availability = sheet_row.get("Availability", "N/A")
        probability = sheet_row.get("Probability", "N/A")
        
        # String safety check to guarantee percentage symbols are appended to numbers
        if probability != "N/A" and not str(probability).endswith("%"):
            probability = f"{probability}%"
    else:
        rarity, value, availability, probability = "Sync Err", "Sync Err", "Sync Err", "Sync Err"
        
    img_b64 = get_image_base64(f"assets/{wood_name.lower()}.png")
    
    html_elements += f"""
    <div class="grid-node">
        <div class="node-tooltip">
            <div class="tip-line">Name: <span>{wood_name}</span></div>
            <div class="tip-line">Rarity: <span>{rarity}</span></div>
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

html_elements += "</div>"
st.components.v1.html(html_elements, height=280, scrolling=False)
