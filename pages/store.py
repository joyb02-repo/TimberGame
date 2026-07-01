# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/store.py (DYNAMIC POINTS REWARDS CATALOG)
# ====================================================================

import streamlit as st
import requests
import json
import os
import re

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("login.py")

st.set_page_config(page_title="Timber Reward Store", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; height: 0px; }
    div.block-container { padding-top: 20px !important; padding-bottom: 100px !important; }
    
    div.stButton > button[key="sys_back_dashboard_btn"] {
        background-color: #161925 !important;
        border: 1px solid #23273A !important;
        color: #E2E8F0 !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        padding: 0.45rem 1.5rem !important;
        width: 240px !important;
    }
    div.stButton > button[key="sys_back_dashboard_btn"]:hover {
        background-color: #23273A !important;
        border-color: #718096 !important;
        color: #FFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 🔄 NATIVE REFRESH ACTUATOR TRIGGER
if st.button("Refresh Cache Data 🔄", key="sys_store_internal_refresh"):
    st.cache_data.clear()
    st.rerun()

if st.button("Back to Portfolio ↩️", key="sys_back_dashboard_btn"):
    st.switch_page("pages/dashboard.py")

API_URL = st.secrets["API_URL"]
user_passcode = st.session_state.get("user_passcode", "DEFAULT_DEMO_KEY")

if "store_refresh_token" not in st.session_state:
    st.session_state["store_refresh_token"] = 0

@st.cache_data(ttl=10)
def fetch_sheet_records(passcode, refresh_trigger):
    try:
        r = requests.get(API_URL, params={"action": "fetchData", "passcode": passcode}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                m_map = {str(m.get("Medallion", "")).strip().lower(): m for m in d.get("medallions", [])}
                summary = d.get("master_summary", {})
                catalog = d.get("catalog", [])
                return m_map, summary.get("Inventory", {}), summary.get("CollectionValue", "0 PTS"), summary.get("MedallionsCollected", "0"), catalog
    except: pass
    return {}, {}, "0 PTS", "0", []

live_data, live_inventory, summary_value, summary_collected, dynamic_catalog = fetch_sheet_records(
    user_passcode, st.session_state["store_refresh_token"]
)

def determine_asset_filename(reward_key, index_fallback):
    """
    Tries to grab numeric values safely. If anything fails or formats weirdly, 
    it falls back cleanly to the layout grid sequence number (index_fallback + 1).
    """
    raw_str = str(reward_key).strip().lower()
    
    # Extract only clean numerical digits from string if possible
    digits = re.findall(r'\d+', raw_str)
    
    if digits:
        num_id = digits[0]
    else:
        # Secure safety net fallback matching items sequentially: Reward1, Reward2...
        num_id = str(index_fallback + 1)
        
    github_user = "joyb02-repo"
    github_repo = "MedallionManager"
    
    return f"https://raw.githubusercontent.com/{github_user}/{github_repo}/main/assets/Reward{num_id}.jpg"

STORE_ITEMS = []
for idx, item in enumerate(dynamic_catalog):
    STORE_ITEMS.append({
        "id": item.get("reward_key", f"fallback_{idx}"), 
        "title": item.get("title", "Unknown Reward"),
        "cost": item.get("cost", 0),
        "desc": item.get("description", ""),
        "img_filename": determine_asset_filename(item.get("reward_key", ""), idx)
    })

items_json = json.dumps(STORE_ITEMS)
inventory_json = json.dumps({k: int(v) for k, v in live_inventory.items() if int(v) > 0})

medallion_details = {}
for k, v in live_data.items():
    medallion_details[k] = {"name": v.get("Medallion", k.capitalize()), "value": int(v.get("Value", 0))}
medallions_json = json.dumps(medallion_details)

html_store_template = """
<style>
    body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; color: #FFFFFF; }
    .store-header-wrapper { width: 100%; text-align: center; margin-bottom: 25px; box-sizing: border-box; padding: 0 10px; }
    .store-title { font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; letter-spacing: -0.5px; }
    .store-title span { color: #10B981; }
    .store-intro { max-width: 850px; margin: 0 auto; font-size: 13.5px; line-height: 1.6; color: rgba(255, 255, 255, 0.4); }

    .dashboard-row { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; padding: 0 10px; }
    .stat-card { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 12px 24px; min-width: 190px; text-align: center; flex: 1; max-width: 240px; }
    .stat-label { font-size: 11px; text-transform: uppercase; color: #718096; margin-bottom: 4px; letter-spacing: 0.5px; }
    .stat-value { font-size: 20px; font-weight: 700; color: #F4D068; }

    .store-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; width: 100%; box-sizing: border-box; padding: 0 10px; margin-bottom: 35px; }
    .store-card { background: #161925; border: 1px solid #23273A; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: space-between; }
    
    .item-image-frame { width: 100%; height: 140px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; background: #0E1117; border-radius: 6px; overflow: hidden; border: 1px solid #1E2235; }
    .item-image-frame img { height: 100%; width: 100%; object-fit: cover; }
    
    .item-title { font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
    .item-desc { font-size: 12px; color: rgba(255, 255, 255, 0.4); line-height: 1.4; margin-bottom: 15px; min-height: 34px; }
    .item-cost-badge { font-size: 13px; font-weight: 700; color: #10B981; margin-bottom: 15px; }
    
    .qty-container { display: flex; align-items: center; gap: 12px; background: #0E1117; border: 1px solid #23273A; border-radius: 6px; padding: 4px 10px; margin-bottom: 5px; }
    .qty-btn { background: transparent; border: none; color: #718096; font-size: 16px; font-weight: bold; cursor: pointer; padding: 0 6px; user-select: none; }
    .qty-btn:hover { color: #FFF; }
    .qty-display { font-size: 14px; font-weight: 700; color: #FFF; min-width: 20px; text-align: center; }

    .floating-checkout-anchor { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(22, 25, 37, 0.96); backdrop-filter: blur(10px); border-top: 1px solid #23273A; padding: 14px 20px; box-sizing: border-box; display: flex; justify-content: center; align-items: center; z-index: 9999; box-shadow: 0 -10px 35px rgba(0,0,0,0.6); }
    .checkout-trigger-btn { width: 460px; max-width: 100%; height: 46px; background: linear-gradient(135deg, #10B981 0%, #059669 100%); border: none; border-radius: 6px; color: #FFF; font-size: 13px; font-weight: 700; text-transform: uppercase; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 12px; }
    .checkout-trigger-btn:disabled { opacity: 0.35; cursor: not-allowed; background: #161925; box-shadow: none; border: 1px solid #23273A; }
    .basket-tally-pill { background: rgba(255, 255, 255, 0.18); padding: 3px 9px; border-radius: 4px; font-size: 11px; font-weight: 800; color: #FFF; }

    .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(14, 17, 23, 0.94); backdrop-filter: blur(6px); display: none; align-items: flex-start; justify-content: center; z-index: 99999; padding-top: 30px; overflow-y: auto; box-sizing: border-box; }
    .modal-box { background: #0E1117; border: 1px solid #23273A; border-radius: 12px; width: 520px; max-width: 95%; padding: 25px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); box-sizing: border-box; margin-bottom: 50px; }
    .modal-title { font-size: 19px; font-weight: 700; color: #FFF; margin-bottom: 15px; text-align: center; }
    
    .summary-section { background: #161925; border: 1px solid #23273A; border-radius: 6px; padding: 14px; margin-bottom: 20px; text-align: left; }
    .summary-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: rgba(255,255,255,0.6); margin-bottom: 8px; }
    
    .inventory-barter-list { max-height: 180px; overflow-y: auto; text-align: left; margin-bottom: 20px; background: #0E1117; border: 1px solid #23273A; border-radius: 6px; padding: 6px; }
    .barter-item-row { display: flex; align-items: center; justify-content: space-between; padding: 8px; border-bottom: 1px solid #161925; }
    .barter-label-group { display: flex; flex-direction: column; }
    .barter-title { font-size: 13px; font-weight: 600; color: #FFF; }
    .barter-meta { font-size: 11px; color: #718096; }
    .barter-select { background: #161925; border: 1px solid #23273A; color: #FFF; border-radius: 4px; padding: 4px; font-size: 12px; outline: none; }

    .error-log-banner { color: #EF4444; font-size: 12px; font-weight: 600; min-height: 18px; margin-bottom: 15px; text-align: center; }
    .finalize-btn { width: 100%; height: 44px; background: #F4D068; color: #0E1117; border: none; border-radius: 6px; font-size: 13px; font-weight: 700; text-transform: uppercase; cursor: pointer; }
    .finalize-btn:disabled { background: #161925 !important; color: #3D4563 !important; border: 1px solid #23273A; cursor: not-allowed; }
    .close-modal-link { color: #718096; font-size: 12px; margin-top: 14px; display: inline-block; cursor: pointer; text-decoration: underline; }
    @media (max-width: 992px) { .store-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 600px) { .store-grid { grid-template-columns: repeat(1, 1fr); } }
</style>

<div class="store-header-wrapper">
    <div class="store-title">Timber Reward <span>Store</span></div>
    <div class="store-intro">Exchange your earned portfolio asset values for real-world rewards.</div>
</div>

<div class="dashboard-row">
    <div class="stat-card"><div class="stat-label">Portfolio Balance</div><div class="stat-value">__VALUE_PLACEHOLDER__</div></div>
    <div class="stat-card"><div class="stat-label">Total Medallions</div><div class="stat-value">__COLLECTED_PLACEHOLDER__</div></div>
</div>

<div class="store-grid">__STORE_ITEMS_PLACEHOLDER__</div>

<div class="floating-checkout-anchor">
    <button class="checkout-trigger-btn" id="basketCheckoutBtn" disabled onclick="openCheckoutBale()">
        <span>Open Verification Checkout</span>
        <span class="basket-tally-pill" id="floatingTallyPill">0 PTS</span>
    </button>
</div>

<div class="modal-overlay" id="checkoutModal">
    <div class="modal-box">
        <div class="modal-title">Verify Trade Voucher</div>
        <div style="text-align:left; font-size:12px; font-weight:700; color:#718096; text-transform:uppercase; margin-bottom:8px;">Review Claims:</div>
        <div class="summary-section" id="cartSummaryContainer"></div>
        
        <div style="text-align:left; font-size:12px; font-weight:700; color:#718096; text-transform:uppercase; margin-bottom:8px;">Select Medallions to Exchange (Barter Coverage):</div>
        <div class="inventory-barter-list" id="barterListDom"></div>
        
        <div class="summary-section">
            <div class="summary-row"><span>Total Cart Cost:</span><span id="labelSummaryCost" style="font-weight:700;">0 PTS</span></div>
            <div class="summary-row"><span>Exchanged Barter Value:</span><span id="labelSummaryBarter" style="color:#F4D068; font-weight:700;">0 PTS</span></div>
        </div>

        <div class="error-log-banner" id="checkoutErrLog"></div>
        <button class="finalize-btn" id="finalTradeBtn" disabled onclick="executeFinalTransaction()">Finalise Trade Voucher</button>
        <div class="close-modal-link" onclick="closeCheckoutBale()">Back to Store Grid</div>
    </div>
</div>

<script>
    const itemCatalog = __CATALOG_JSON__;
    const userInventory = __INVENTORY_JSON__;
    const medallionMetadata = __MEDALLIONS_JSON__;
    const endpoint = "__API_URL_PLACEHOLDER__";
    
    let cart = {};

    function updateItemQuantity(itemId, adjustment) {
        if (!cart[itemId]) cart[itemId] = 0;
        cart[itemId] = Math.max(0, cart[itemId] + adjustment);
        document.getElementById("qty_val_" + itemId).innerText = cart[itemId];
        evaluateBasketStatus();
    }

    function evaluateBasketStatus() {
        let totalCount = 0;
        let totalPoints = 0;
        for (let itemId in cart) { 
            totalCount += cart[itemId];
            if (cart[itemId] > 0) {
                const item = itemCatalog.find(i => i.id === itemId);
                if(item) {
                    totalPoints += (item.cost * cart[itemId]);
                }
            }
        }
        document.getElementById("basketCheckoutBtn").disabled = (totalCount === 0);
        document.getElementById("floatingTallyPill").innerText = totalPoints + " PTS";
    }

    function openCheckoutBale() {
        const container = document.getElementById("cartSummaryContainer");
        container.innerHTML = "";
        for (let itemId in cart) {
            if (cart[itemId] > 0) {
                const item = itemCatalog.find(i => i.id === itemId);
                if(item) {
                    container.innerHTML += `<div class="summary-row"><span>${item.title}</span><strong>x${cart[itemId]} (${item.cost * cart[itemId]} PTS)</strong></div>`;
                }
            }
        }
        buildBarterInventoryList();
        recalculateBarterMath();
        document.getElementById("checkoutModal").style.display = "flex";
    }

    function closeCheckoutBale() { document.getElementById("checkoutModal").style.display = "none"; }

    function buildBarterInventoryList() {
        const target = document.getElementById("barterListDom");
        target.innerHTML = "";
        let empty = true;
        for (let key in userInventory) {
            if (userInventory[key] > 0) {
                empty = false;
                const meta = medallionMetadata[key] || {name: key.toUpperCase(), value: 0};
                let optionsHtml = "";
                for (let i = 0; i <= userInventory[key]; i++) { optionsHtml += `<option value="${i}">${i}</option>`; }
                target.innerHTML += `
                    <div class="barter-item-row">
                        <div class="barter-label-group">
                            <span class="barter-title">${meta.name}</span>
                            <span class="barter-meta">Value: ${meta.value} PTS | Available: x${userInventory[key]}</span>
                        </div>
                        <select class="barter-select" data-key="${key}" data-value="${meta.value}" onchange="recalculateBarterMath()">
                            ${optionsHtml}
                        </select>
                    </div>`;
            }
        }
        if (empty) target.innerHTML = '<div style="padding:15px; text-align:center; color:#718096;">No tradeable assets available.</div>';
    }

    function recalculateBarterMath() {
        let totalCost = 0;
        for (let itemId in cart) {
            if (cart[itemId] > 0) { 
                const item = itemCatalog.find(i => i.id === itemId);
                if(item) { totalCost += (item.cost * cart[itemId]); }
            }
        }
        let totalBarter = 0;
        document.querySelectorAll(".barter-select").forEach(sel => {
            totalBarter += (parseInt(sel.value) * parseInt(sel.getAttribute("data-value")));
        });

        document.getElementById("labelSummaryCost").innerText = totalCost + " PTS";
        document.getElementById("labelSummaryBarter").innerText = totalBarter + " PTS";
        
        const err = document.getElementById("checkoutErrLog");
        const btn = document.getElementById("finalTradeBtn");
        
        if (totalBarter >= totalCost) { err.innerText = ""; btn.disabled = false; }
        else { err.innerText = "Insufficient barter coverage. Add more medallions."; btn.disabled = true; }
    }

    function executeFinalTransaction() {
        const tradeBtn = document.getElementById("finalTradeBtn");
        tradeBtn.disabled = true;
        tradeBtn.innerText = "Saving to Google Sheets...";

        let itemsSpentMap = {};
        document.querySelectorAll(".barter-select").forEach(sel => {
            let q = parseInt(sel.value) || 0;
            if (q > 0) itemsSpentMap[sel.getAttribute("data-key")] = q;
        });

        let finalBasketItems = {};
        for (let key in cart) {
            if (cart[key] > 0) {
                finalBasketItems[key] = cart[key];
                let cleanedKey = String(key).replace(/\s+/g, '');
                finalBasketItems[cleanedKey] = cart[key];
            }
        }

        const payload = { basket: finalBasketItems, barter_spent: itemsSpentMap };
        const dispatchUrl = endpoint + "?action=executeStoreTrade&passcode=" + encodeURIComponent("__PASSCODE_RAW__") + "&payload=" + encodeURIComponent(JSON.stringify(payload));
        
        const imgPing = new Image();
        imgPing.onload = imgPing.onerror = function() {
            setTimeout(() => {
                const parentDoc = window.parent.document;
                const refreshActuator = Array.from(parentDoc.querySelectorAll('button')).find(el => el.innerText.includes('Refresh Cache Data 🔄'));
                if (refreshActuator) {
                    refreshActuator.click();
                } else {
                    window.parent.location.reload();
                }
            }, 600);
        };
        imgPing.src = dispatchUrl;
    }
</script>
"""

CARD_TEMPLATE = """
<div class="store-card">
    <div style="width: 100%;">
        <div class="item-image-frame">
            <img src="__IMG__" />
        </div>
        <div class="item-title">__TITLE__</div>
        <div class="item-desc">__DESC__</div>
    </div>
    <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
        <div class="item-cost-badge">__COST__ PTS</div>
        <div class="qty-container">
            <button class="qty-btn" onclick="updateItemQuantity('__ID__', -1)">-</button>
            <div class="qty-display" id="qty_val___ID__">0</div>
            <button class="qty-btn" onclick="updateItemQuantity('__ID__', 1)">+</button>
        </div>
    </div>
</div>
"""

grid_items_html = ""
for item in STORE_ITEMS:
    raw_desc = item['desc']
    desc_html = raw_desc.replace("**", "<strong>", 1).replace("**", "</strong>", 1) if "**" in raw_desc else raw_desc
    
    card_piece = CARD_TEMPLATE.replace("__IMG__", item['img_filename'])
    card_piece = card_piece.replace("__TITLE__", item['title'])
    card_piece = card_piece.replace("__DESC__", desc_html)
    card_piece = card_piece.replace("__COST__", str(item['cost']))
    card_piece = card_piece.replace("__ID__", str(item['id']))
    
    grid_items_html += card_piece

html_store_elements = html_store_template.replace("__STORE_ITEMS_PLACEHOLDER__", grid_items_html)
html_store_elements = html_store_elements.replace("__VALUE_PLACEHOLDER__", summary_value)
html_store_elements = html_store_elements.replace("__COLLECTED_PLACEHOLDER__", summary_collected)
html_store_elements = html_store_elements.replace("__CATALOG_JSON__", items_json)
html_store_elements = html_store_elements.replace("__INVENTORY_JSON__", inventory_json)
html_store_elements = html_store_elements.replace("__MEDALLIONS_JSON__", medallions_json)
html_store_elements = html_store_elements.replace("__PASSCODE_RAW__", user_passcode)
html_store_elements = html_store_elements.replace("__API_URL_PLACEHOLDER__", API_URL)

st.components.v1.html(html_store_elements, height=1050, scrolling=True)
