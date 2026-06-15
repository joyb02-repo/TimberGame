import streamlit as st
import requests
import os
import base64

API_URL = st.secrets["API_URL"]

MEDALLION_COLUMNS = [
    "Spruce", "Pine", "Meranti", "Balsa", "Oak", "Maple", 
    "Walnut", "Cherry", "Mahogany", "Ebony", "Rosewood", "Agarwood"
]

st.set_page_config(page_title="Timber Medallion Portfolio", layout="wide")

@st.cache_data(ttl=5)
def fetch_all_sheet_data():
    """Fetches everything in a single optimized payload to keep UI responsive and sync intact."""
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                medallions_map = {str(m["Medallion"]).strip().lower(): m for m in data.get("medallions", [])}
                
                summary = data.get("master_summary", {})
                val = summary.get("CollectionValue", "$0")
                coll = summary.get("MedallionsCollected", "0 / 12")
                
                return medallions_map, val, coll
    except Exception as e:
        st.error(f"Sync Failure: {str(e)}")
    return {}, "Loading...", "Loading..."

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

live_data, summary_value, summary_collected = fetch_all_sheet_data()

mock_user = {
    "Spruce": 6, "Pine": 2, "Meranti", 0, "Balsa", 0, "Oak", 0, "Maple", 0,
    "Walnut": 0, "Cherry": 0, "Mahogany": 2, "Ebony": 0, "Rosewood": 1, "Agarwood": 0
}

if not summary_value.strip().startswith("$") and "Loading" not in summary_value:
    summary_value = f"${summary_value.strip()}"

# ====================================================================
# UNIFIED GRID LAYOUT WITH ADVANCED OVERFLOW SAFETY WINDOWS
# ====================================================================
html_elements = """
<style>
    body {
        margin: 0; 
        /* Generous top padding to completely clear any container cutoffs */
        padding: 130px 0 0 0; 
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        overflow: visible; /* Allows dropdown elements to spill gracefully */
    }
    .portfolio-title {
        text-align: center;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 22px;
        font-weight: 600;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-top: -95px; /* Pulls the title header up into the top padding zone */
        margin-bottom: 25px; 
    }
    .casement-grid {
        display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px;
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
    
    /* Animation Framework for Hover Scales */
    .image-frame img, .lock-node { 
        width: 100%; height: 100%; object-fit: contain;
        transition: transform 0.15s ease-in-out;
    }
    .lock-node {
        width: 52px; height: 52px; border-radius: 50%;
        border: 2px dashed #23273A; background: #161925;
        display: flex; align-items: center; justify-content: center;
        color: #3D4563; font-size: 13px;
    }
    
    /* Applies the 15% magnification on hover */
    .grid-node:hover .image-frame img,
    .grid-node:hover .lock-node {
        transform: scale(1.15);
    }
    
    .quantity-badge { font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }
    .label-badge { font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Top-Down Absolute Positioning Strategy to prevent Frame Clipping */
    .node-tooltip {
        visibility: hidden; opacity: 0; position: absolute;
        top: -115px; bottom: auto; left: 50%; transform: translateX(-50%);
        width: 180px; background: #161925; border: 1px solid #282E48;
        border-radius: 8px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        z-index: 99999; transition: opacity 0.12s ease-in-out; pointer-events: none;
    }
    .grid-node:hover .node-tooltip { visibility: visible; opacity: 1; }
    
    /* Horizontal boundary shifts for the edge elements */
    .grid-node:first-child .node-tooltip { left: 0; transform: translateX(0); }
    .grid-node:last-child .node-tooltip { left: auto; right: 0; transform: translateX(0); }
    
    .tip-line { font-size: 11px; color: #E2E8F0; margin-bottom: 5px; white-space: nowrap; text-align: left; }
    .tip-line:last-child { margin-bottom: 0; }
    .tip-line span { font-weight: 700; color: #F4D068; }

    .dashboard-row {
        display: flex; justify-content: center; gap: 20px;
        margin-top: 35px; padding: 0 15px;
    }
    .stat-card {
        background: #161925; border: 1px solid #23273A; border-radius: 6px;
        padding: 10px 20px; min-width: 180px; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stat-label {
        font-size: 11px; text-transform: uppercase; color: #718096;
        letter-spacing: 0.75px; margin-bottom: 4px; font-weight: 600;
    }
    .stat-value { font-size: 18px; font-weight: 700; color: #FFF; }
</style>

<div class="portfolio-title">Timber Medallion Portfolio</div>
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
        
        if value != "N/A" and not str(value).strip().startswith("$"):
            value = f"${str(value).strip()}"
        if probability != "N/A" and not str(probability).endswith("%"):
            probability = f"{probability}%"
    else:
        rarity = value = availability = probability = "Loading..."
        
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

html_elements += f"""
</div>

<div class="dashboard-row">
    <div class="stat-card">
        <div class="stat-label">Collection Value</div>
        <div class="stat-value">{summary_value}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Medallions Collected</div>
        <div class="stat-value">{summary_collected}</div>
    </div>
</div>
"""

# Expanded layout height parameter to allow ample space for animations and cards
st.components.v1.html(html_elements, height=420, scrolling=False)
