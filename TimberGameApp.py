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

@st.cache_data(ttl=1)
def fetch_all_sheet_data():
    """Fetches layout array details, live value summaries, and collected counters."""
    try:
        response = requests.post(API_URL, json={"action": "fetchData"}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                medallions_map = {str(m["Medallion"]).strip().lower(): m for m in data.get("medallions", [])}
                summary = data.get("master_summary", {})
                val = summary.get("CollectionValue", "$0")
                coll = summary.get("MedallionsCollected", "0")
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

# Process inbound URL synchronization parameters from the javascript mining module
query_params = st.query_params
if "mined_item" in query_params:
    target_mined = query_params["mined_item"]
    try:
        # Write directly to Google Sheets database infrastructure
        res = requests.post(API_URL, json={"action": "mineMedallion", "item": target_mined}, timeout=15)
        if res.status_code == 200:
            st.cache_data.clear() # Wipe layout caching models to immediately show new updates
    except Exception as e:
        st.error(f"Failed to record mined item to cloud sheet: {e}")
    st.query_params.clear()

if not summary_value.strip().startswith("$") and "Loading" not in summary_value:
    summary_value = f"${summary_value.strip()}"

# Gather image resources into an encoded array configuration
asset_map_js = "{"
for wood in MEDALLION_COLUMNS:
    b64 = get_image_base64(f"assets/{wood.lower()}.png")
    if b64:
        asset_map_js += f"'{wood}': 'data:image/png;base64,{b64}',"
asset_map_js += "}"

# ====================================================================
# UNIFIED GRID LAYOUT WITH INTERACTIVE CLAIM MODULE
# ====================================================================
html_elements = f"""
<style>
    body {{
        margin: 0; 
        padding: 50px 0 0 0; 
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        overflow: visible;
    }}
    .portfolio-title {{
        text-align: center;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 24px;
        font-weight: 600;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-top: 0px;
        margin-bottom: 12px; 
    }}
    .portfolio-intro {{
        text-align: center;
        max-width: 800px;
        margin: 0 auto 50px auto; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 13px;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.25); 
        letter-spacing: 0.1px;
    }}
    .portfolio-intro span {{
        color: rgba(244, 208, 104, 0.4); 
        font-weight: 600;
    }}
    .casement-grid {{
        display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px;
        padding-left: 15px; padding-right: 15px;
    }}
    .grid-node {{
        position: relative; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
    }}
    .image-frame {{
        width: 62px; height: 62px; display: flex;
        align-items: center; justify-content: center; margin-bottom: 8px;
    }}
    
    .image-frame img, .lock-node {{ 
        width: 100%; height: 100%; object-fit: contain;
        transition: transform 0.15s ease-in-out;
    }}
    .lock-node {{
        width: 52px; height: 52px; border-radius: 50%;
        border: 2px dashed #23273A; background: #161925;
        display: flex; align-items: center; justify-content: center;
        color: #3D4563; font-size: 13px;
    }}
    
    .grid-node:hover .image-frame img,
    .grid-node:hover .lock-node {{
        transform: scale(1.15);
    }}
    
    .quantity-badge {{ font-size: 12px; font-weight: 700; color: #F4D068; margin-bottom: 3px; min-height: 15px; }}
    .label-badge {{ font-size: 10px; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }}
    
    .node-tooltip {{
        visibility: hidden; opacity: 0; position: absolute;
        top: -120px; bottom: auto; left: 50%; transform: translateX(-50%);
        width: 180px; background: #161925; border: 1px solid #282E48;
        border-radius: 8px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        z-index: 99999; transition: opacity 0.12s ease-in-out; pointer-events: none;
    }}
    .grid-node:hover .node-tooltip {{ visibility: visible; opacity: 1; }}
    
    .grid-node:first-child .node-tooltip {{ left: 0; transform: translateX(0); }}
    .grid-node:last-child .node-tooltip {{ left: auto; right: 0; transform: translateX(0); }}
    
    .tip-line {{ font-size: 11px; color: #E2E8F0; margin-bottom: 5px; white-space: nowrap; text-align: left; }}
    .tip-line:last-child {{ margin-bottom: 0; }}
    .tip-line span {{ font-weight: 700; color: #F4D068; }}

    .tip-line span.rarity-common {{ color: #CD7F32; }}       
    .tip-line span.rarity-uncommon {{ color: #C0C0C0; }}     
    .tip-line span.rarity-rare {{ color: #3b82f6; }}         
    .tip-line span.rarity-epic {{ color: #a855f7; }}         
    .tip-line span.rarity-legendary {{ color: #f59e0b; }}    

    .dashboard-row {{
        display: flex; justify-content: center; gap: 20px;
        margin-top: 45px; padding: 0 15px;
    }}
    .stat-card {{
        background: #161925; border: 1px solid #23273A; border-radius: 6px;
        padding: 10px 20px; min-width: 180px; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    .stat-label {{
        font-size: 11px; text-transform: uppercase; color: #718096;
        letter-spacing: 0.75px; margin-bottom: 4px; font-weight: 600;
    }}
    .stat-value {{ font-size: 18px; font-weight: 700; color: #FFF; }}

    .action-container {{
        display: flex; flex-direction: column; align-items: center;
        margin-top: 30px; width: 100%;
    }}
    .mine-button {{
        width: 424px; height: 46px; background-color: #F4D068;
        border: none; border-radius: 6px; color: #0E1117;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 14px; font-weight: 700; letter-spacing: 0.5px;
        text-transform: uppercase; cursor: pointer;
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), 
                    background-color 0.2s ease-in-out, color 0.2s ease-in-out;
        box-shadow: 0 4px 15px rgba(244, 208, 104, 0.2);
    }}
    .mine-button:hover {{
        transform: scale(1.10);
        background-color: #0E1117;
        color: #F4D068;
        border: 2px solid #F4D068;
    }}
    .mine-button:disabled {{
        opacity: 0.6; cursor: not-allowed; transform: scale(1) !important;
        background-color: #23273A !important; color: #718096 !important; border: none !important;
    }}
    
    .animation-display {{
        margin-top: 25px; min-height: 230px; width: 100%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    .spin-box {{
        width: 140px; height: 140px; border-radius: 12px;
        background: #161925; border: 3px solid #23273A;
        display: none; align-items: center; justify-content: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .spin-box img {{ width: 88%; height: 88%; object-fit: contain; }}
    
    .outcome-text-wrapper {{
        margin-top: 15px;
        text-align: center;
        font-family: 'Inter', sans-serif;
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
    }}
    .outcome-top {{
        font-size: 11px;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 2px;
    }}
    .outcome-bottom {{
        font-size: 18px;
        font-weight: 800;
        color: #F4D068;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Sleek Claim Action Button Styling */
    .claim-button {{
        margin-top: 14px;
        width: 160px; height: 32px;
        background-color: transparent;
        border: 2px solid #F4D068;
        border-radius: 4px;
        color: #F4D068;
        font-family: 'Inter', sans-serif;
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.75px;
        cursor: pointer; opacity: 0; transform: translateY(5px);
        transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out, background-color 0.15s ease, color 0.15s ease;
    }}
    .claim-button.visible {{
        opacity: 1;
        transform: translateY(0);
    }}
    .claim-button:hover {{
        background-color: #F4D068;
        color: #0E1117;
    }}
</style>

<div class="portfolio-title">Timber Medallion Portfolio</div>

<div class="portfolio-intro">
    Welcome to your master dashboard tracking the curation of elite wood tokens. Medallions can be acquired by processing rare lumber loads, unlocking milestones, and participating in limited trade events. Each unique medallion tier scales across varying degrees of rarity, marketplace values, and highly restricted circulating supplies—culminating with the ultra-mythic <span>Agarwood Medallion</span>, maintaining an absolute <span>1-to-1 available stock</span> worldwide.
</div>

<div class="casement-grid">
"""

for wood_name in MEDALLION_COLUMNS:
    display_label = wood_name[:5].upper()
    
    lookup_key = wood_name.strip().lower()
    sheet_row = live_data.get(lookup_key, None)
    
    if "medallions" in locals() or True:
        try:
            owned = 0
            if lookup_key == 'spruce': owned = 6
            elif lookup_key == 'pine': owned = 2
            elif lookup_key == 'meranti': owned = 4
            elif lookup_key == 'mahogany': owned = 2
            elif lookup_key == 'rosewood': owned = 1
        except:
            owned = 0
            
    rarity_class = ""
    if sheet_row:
        rarity = sheet_row.get("Rarity", "N/A")
        value = sheet_row.get("Value", "N/A")
        availability = sheet_row.get("Availability", "N/A")
        probability = sheet_row.get("Probability", "N/A")
        
        clean_rarity = str(rarity).strip().lower()
        if "common" in clean_rarity and "uncommon" not in clean_rarity:
            rarity_class = "rarity-common"
        elif "uncommon" in clean_rarity:
            rarity_class = "rarity-uncommon"
        elif "rare" in clean_rarity:
            rarity_class = "rarity-rare"
        elif "epic" in clean_rarity:
            rarity_class = "rarity-epic"
        elif "legendary" in clean_rarity:
            rarity_class = "rarity-legendary"
        
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

<div class="action-container">
    <button class="mine-button" id="mineBtn" onclick="runMiningSequence()">Mine a Medallion</button>
    <div class="animation-display">
        <div class="spin-box" id="cyclerBox">
            <img id="cyclerImg" src="" />
        </div>
        <div class="outcome-text-wrapper" id="outcomeWrapper">
            <div class="outcome-top">Successfully Mined:</div>
            <div class="outcome-bottom" id="itemNameTxt"></div>
        </div>
        <button class="claim-button" id="claimBtn" onclick="commitClaimToSheets()">Claim Medallion</button>
    </div>
</div>

<script>
    const assetLibrary = {asset_map_js};
    const pool = ['Spruce', 'Pine', 'Meranti', 'Balsa', 'Oak', 'Maple', 'Walnut', 'Cherry', 'Mahogany', 'Ebony', 'Rosewood', 'Agarwood'];
    let selectedItem = "";

    function runMiningSequence() {{
        const btn = document.getElementById('mineBtn');
        const box = document.getElementById('cyclerBox');
        const img = document.getElementById('cyclerImg');
        const wrapper = document.getElementById('outcomeWrapper');
        const itemTxt = document.getElementById('itemNameTxt');
        const claimBtn = document.getElementById('claimBtn');
        
        btn.disabled = true;
        wrapper.style.opacity = "0";
        claimBtn.classList.remove('visible');
        box.style.display = "flex";
        box.style.borderColor = "#23273A";
        
        let counter = 0;
        let speed = 40; 
        selectedItem = "";

        const indexChoice = Math.floor(Math.random() * pool.length);
        selectedItem = pool[indexChoice];

        function cycle() {{
            const currentItem = pool[counter % pool.length];
            if (assetLibrary[currentItem]) {{
                img.src = assetLibrary[currentItem];
            }}
            counter++;

            if (speed < 320) {{
                speed += 14; 
                setTimeout(cycle, speed);
            }} else {{
                if (assetLibrary[selectedItem]) {{
                    img.src = assetLibrary[selectedItem];
                }}
                box.style.borderColor = "#F4D068";
                
                itemTxt.innerText = selectedItem.toUpperCase() + " MEDALLION!";
                wrapper.style.opacity = "1";
                
                // Show claim action button rather than automatically refreshing
                claimBtn.classList.add('visible');
            }}
        }}
        setTimeout(cycle, speed);
    }}

    function commitClaimToSheets() {{
        if (!selectedItem) return;
        const claimBtn = document.getElementById('claimBtn');
        claimBtn.disabled = true;
        claimBtn.innerText = "Saving...";
        
        // Execute parameter pass-back which triggers the refresh and Google Sheets increment logic
        const curUrl = new URL(window.parent.location.href);
        curUrl.searchParams.set("mined_item", selectedItem);
        window.parent.location.href = curUrl.toString();
    }}
</script>
"""

# Height slightly increased to 770 to prevent any layout shifting when the claim button materializes
st.components.v1.html(html_elements, height=770, scrolling=False)
