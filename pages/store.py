# ====================================================================
# PROJECT: TIMBER MEDALLION PORTFOLIO SYSTEM
# FILE: pages/store.py (COMPACT ITEM MARKETPLACE & ASSET TRADE ENGINE)
# ====================================================================

import streamlit as st
import requests

# Security Guard Wall
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("login.py")

st.set_page_config(page_title="Timber Marketplace", layout="wide", initial_sidebar_state="collapsed")
API_URL = st.secrets["API_URL"]

# Unified CSS Themes directly tracking parent styling frameworks
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        background-image: linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 24px 24px;
    }
    header, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; visibility: hidden; }
    div.block-container { padding-top: 20px !important; max-width: 1200px !important; }
    
    /* Premium Store Card Elements */
    .store-header { text-align: center; margin-bottom: 30px; position: relative; }
    .store-title { font-size: 26px; font-weight: 700; color: #FFFFFF; }
    .store-title span { color: #F4D068; }
    .store-subtitle { font-size: 13px; color: rgba(255,255,255,0.35); margin-top: 5px; }
    
    .summary-bar { display: flex; justify-content: space-between; background: #161925; border: 1px solid #23273A; border-radius: 8px; padding: 15px 25px; margin-bottom: 25px; align-items: center; }
    .summary-meta { color: #718096; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
    .summary-val { font-size: 20px; font-weight: 700; color: #F4D068; }
</style>
""", unsafe_allow_html=True)

# 1. Fetch live system states
@st.cache_data(ttl=5)
def get_store_profile(passcode):
    try:
        r = requests.get(API_URL, params={"action": "fetchData", "passcode": passcode}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                m_map = {str(m.get("Medallion", "")).strip().lower(): m for m in d.get("medallions", [])}
                summary = d.get("master_summary", {})
                return m_map, summary.get("Inventory", {}), summary.get("CollectionValue", "$0")
    except: pass
    return {}, {}, "$0"

live_data, inventory, portfolio_value = get_store_profile(st.session_state["user_passcode"])

# 2. Header Elements Layout
st.markdown(f"""
<div class="store-header">
    <div class="store-title">Timber Marketplace: <span>Trade Hub</span></div>
    <div class="store-subtitle">Convert your accrued medallion inventory items straight into high-tier procurement upgrades.</div>
</div>
<div class="summary-bar">
    <div>
        <div class="summary-meta">Your Portfolio Value</div>
        <div class="summary-val">{portfolio_value}</div>
    </div>
    <div style="text-align: right;">
        <div class="summary-meta">Operator Identity</div>
        <div style="color: #FFF; font-weight:700; font-size:14px;">{st.session_state["username"].upper()}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation link back to dashboard layout matrices
if st.button("⬅️ Return to Portfolio Dashboard", use_container_width=False):
    st.switch_page("pages/dashboard.py")

st.write("---")

# 3. Marketplace Grid Initialization Setup
STORE_ITEMS = [
    {"id": "item_1", "name": "Item #1 - Alpha Access Pack", "price": 100},
    {"id": "item_2", "name": "Item #2 - Delta Optimization Module", "price": 100},
    {"id": "item_3", "name": "Item #3 - Premium Framework Token", "price": 250},
    {"id": "item_4", "name": "Item #4 - Executive Vault License", "price": 500},
    {"id": "item_5", "name": "Item #5 - Legacy Overlord Matrix", "price": 1000},
    {"id": "item_6", "name": "Item #6 - Elite Quantum Syndicate", "price": 1500}
]

if "cart" not in st.session_state:
    st.session_state["cart"] = {item["id"]: 0 for item in STORE_ITEMS}

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Available Manifest Listings")
    # Generate 3x2 responsive application tile block nodes
    grid_cols = st.columns(3)
    for index, item in enumerate(STORE_ITEMS):
        with grid_cols[index % 3]:
            with st.container(border=True):
                # Placeholder thumbnail graphic component layout matching system design
                st.markdown(f"""
                <div style="background: #161925; border-radius: 6px; height: 110px; display:flex; align-items:center; justify-content:center; font-size:32px; border: 1px solid #23273A; margin-bottom:10px;">
                    📦
                </div>
                <div style="color:#FFF; font-weight:700; font-size:13px; min-height:36px; line-height:1.3;">{item['name']}</div>
                <div style="color:#F4D068; font-weight:800; font-size:16px; margin: 6px 0 12px 0;">${item['price']}</div>
                """, unsafe_allow_html=True)
                
                # Dynamic additive selection elements controls tracking setup
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    if st.button("Add ➕", key=f"add_{item['id']}", use_container_width=True):
                        st.session_state["cart"][item['id']] += 1
                        st.rerun()
                with sub_c2:
                    if st.button("Drop ➖", key=f"drop_{item['id']}", use_container_width=True):
                        if st.session_state["cart"][item['id']] > 0:
                            st.session_state["cart"][item['id']] -= 1
                            st.rerun()

# 4. Interactive Sidebar Cart Aggregator Calculation Engine
with col2:
    st.markdown("### Procurement Cart")
    total_cost = 0
    cart_payload = []
    
    with st.container(border=True):
        for item in STORE_ITEMS:
            qty = st.session_state["cart"][item["id"]]
            if qty > 0:
                cost = item["price"] * qty
                total_cost += cost
                st.markdown(f"**{item['name']}** \n`x{qty}` → **${cost}**")
                cart_payload.append({"id": item["id"], "qty": qty})
        
        if total_cost == 0:
            st.markdown("<div style='color:#718096; padding: 20px 0;'>Your shopping cart layout is currently empty.</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"### Total Cost: <span style='color:#F4D068;'>${total_cost}</span>", unsafe_allow_html=True)
        
        # Trigger modal verification selection flow
        trade_disabled = total_cost == 0
        if st.button("Trade Medallions 🫱🏾‍🫲🏼", type="primary", use_container_width=True, disabled=trade_disabled):
            st.session_state["checkout_open"] = True

# 5. Core Dialog Processing Overlay
if "checkout_open" in st.session_state and st.session_state["checkout_open"]:
    @st.dialog("Configure Trade Allotment")
    def render_trade_dialog():
        st.markdown(f"#### Order Valuation Required: :gold[${total_cost}]")
        st.markdown("Select which specific medallions you wish to surrender to cover this cost balance. *Note: No cash change can be remitted upon execution.*")
        st.write("---")
        
        allocated_trade_value = 0
        deduction_manifest = {}
        
        # Pull each medallion's true intrinsic market value row from live data mappings
        for key, m_info in live_data.items():
            name = m_info.get("Medallion", key.capitalize())
            raw_val = str(m_info.get("Value", "0")).replace("$", "").replace(",", "").strip()
            try: item_value = int(float(raw_val))
            except: item_value = 0
            
            user_has = int(inventory.get(key, 0))
            
            # Only render lines for wood types the operator actually holds in their stash
            if user_has > 0:
                c_lbl, c_sel = st.columns([3, 2])
                with c_lbl:
                    st.markdown(f"**{name}** (${item_value} ea)  \nAvailable: `x{user_has}`")
                with c_sel:
                    chosen_qty = st.number_input("Trade Qty", min_value=0, max_value=user_has, step=1, key=f"trade_alloc_{key}")
                    if chosen_qty > 0:
                        allocated_trade_value += (chosen_qty * item_value)
                        deduction_manifest[name] = chosen_qty
        
        st.write("---")
        st.markdown(f"Allocated Trade Capital: **${allocated_trade_value}**")
        
        # Balance delta feedback warning strings calculation logic
        if allocated_trade_value < total_cost:
            deficit = total_cost - allocated_trade_value
            st.error(f"Incomplete funding allocation. Please assign an additional ${deficit} worth of medallions.")
            st.button("Authorize Asset Transfer 🫱🏾‍🫲🏼", disabled=True, use_container_width=True)
        else:
            surplus = allocated_trade_value - total_cost
            if surplus > 0:
                st.warning(f"⚠️ Value Burn Warning: Surrendered configuration exceeds target by **${surplus}**. No change will be returned.")
            else:
                st.success("Perfect asset balance convergence met!")
                
            if st.button("Authorize Asset Transfer 🫱🏾‍🫲🏼", type="primary", use_container_width=True):
                with st.spinner("Processing cloud ledger sync allocations..."):
                    try:
                        # Fires request straight back to your established Sheets script handler endpoint
                        params = {
                            "action": "tradeMedallions",
                            "passcode": st.session_state["user_passcode"],
                            "deductions": json.dumps(deduction_manifest),
                            "items_purchased": json.dumps(cart_payload)
                        }
                        r = requests.post(API_URL, json=params, timeout=15)
                        # Fallback parsing strategy in case the web app script acts asynchronously via image ping setups
                        if r.status_code == 200 or r.status_code == 302:
                            st.session_state["cart"] = {item["id"]: 0 for item in STORE_ITEMS}
                            st.session_state["checkout_open"] = False
                            st.cache_data.clear()
                            st.toast("Transaction authorized successfully! Ledger modified.", icon="✅")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Cloud ledger connectivity failure: {str(e)}")
                        
    render_trade_dialog()