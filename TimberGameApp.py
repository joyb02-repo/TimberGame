import streamlit as st
import random
import time

# --- INITIALIZE STATE ---
if 'coins' not in st.session_state:
    st.session_state.coins = 120
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'current_blueprint' not in st.session_state:
    st.session_state.current_blueprint = None
if 'game_logs' not in st.session_state:
    st.session_state.game_logs = ["Welcome to the Woodshop. Pull a blueprint to start!"]

st.set_page_config(page_title="Timber Tycoon: Overdrive", page_icon="🪚", layout="centered")

# --- UI STYLING ---
st.markdown("""
    <style>
    .title { font-family: 'Courier New', monospace; font-size: 3rem; text-align: center; color: #D2B48C; font-weight: bold; text-shadow: 2px 2px #5c4033; }
    .log-box { background-color: #1e1e24; color: #00ffcc; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; height: 150px; overflow-y: auto; border: 1px solid #333; }
    .stat-text { font-size: 1.5rem; font-weight: bold; color: #FFA500; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🪚 TIMBER TYCOON: OVERDRIVE</div>", unsafe_allow_html=True)
st.write("---")

# --- WIN / LOSE CONDITIONS ---
if st.session_state.coins <= 0:
    st.error("💀 BANKRUPT! You ran out of timber credits. Your workshop has closed down.")
    if st.button("Beg Teacher for an Extension (Reset)"):
        st.session_state.clear()
        st.rerun()
    st.stop()

if st.session_state.coins >= 500:
    st.balloons()
    st.success("👑 MASTER CRAFTSMAN! You hit 500+ credits and built a woodworking empire!")
    if st.button("Start a New Build"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# --- TOP DASHBOARD ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Timber Credits", value=f"{st.session_state.coins}💰")
with col2:
    st.metric(label="Reputation XP", value=f"{st.session_state.xp}⭐")
with col3:
    # Quick reset
    if st.button("🔄 Full Reset"):
        st.session_state.clear()
        st.rerun()

st.progress(min(st.session_state.coins / 500, 1.0), text=f"Progress to Master Craftsman (500 Credits)")

# --- THE BLUEPRINT SLOT MACHINE ---
st.header("🎰 1. The Blueprint Generator")
st.write("Spend **20 Credits** to roll the dice on a random design client assignment.")

# Available random project combinations
BLUEPRINTS = {
    "🛹 Skateboard Deck": {"wood": "Tasmanian Oak (Hardwood)", "cost": 40, "payout": 110, "difficulty": "Hard"},
    "🎸 Custom Ukulele": {"wood": "Mahogany (Premium)", "cost": 60, "payout": 160, "difficulty": "Expert"},
    "📥 Desktop Organizer": {"wood": "Radiata Pine (Softwood)", "cost": 15, "payout": 45, "difficulty": "Easy"},
    "🪑 Minimalist Stool": {"wood": "Radiata Pine (Softwood)", "cost": 25, "payout": 65, "difficulty": "Medium"},
    "🐦 Eco Birdhouse": {"wood": "Recycled Pallet Wood", "cost": 10, "payout": 35, "difficulty": "Easy"}
}

if st.button("🎰 Pull Design Lever (-20 Credits)", type="primary"):
    if st.session_state.coins >= 20:
        st.session_state.coins -= 20
        rolled_name = random.choice(list(BLUEPRINTS.keys()))
        st.session_state.current_blueprint = BLUEPRINTS[rolled_name]
        st.session_state.current_blueprint["name"] = rolled_name
        st.session_state.game_logs.append(f"Rolled Blueprint: {rolled_name}!")
        st.rerun()
    else:
        st.error("Not enough cash to buy a blueprint!")

# Display current active build details
if st.session_state.session_state.current_blueprint:
    bp = st.session_state.current_blueprint
    st.info(f"**Active Project:** {bp['name']} | **Requires:** {bp['wood']} (Costs {bp['cost']} to prep) | **Potential Payout:** {bp['payout']} 💰")
else:
    st.warning("No blueprint active. Pull the lever above!")

st.write("---")

# --- INTERACTIVE MANUFACTURING SECTION ---
st.header("🛠️ 2. The Interactive Workshop Floor")

if not st.session_state.current_blueprint:
    st.write("Waiting for a design contract...")
else:
    bp = st.session_state.current_blueprint
    
    st.write(f"### Crafting Steps for: {bp['name']}")
    
    # User Input 1: Risk Assessment Slider
    risk_level = st.select_slider(
        "Select your Crafting Speed / Risk Profile:",
        options=["Careful & Slow", "Standard Precision", "Rushed / Fast-Track"],
        value="Standard Precision"
    )
    
    # User Input 2: Tool choice strategy
    tool_choice = st.radio(
        "Choose your primary shaping tool for this build:",
        ["Traditional Hand Tools (High accuracy, low speed)", "Power Machinery (High speed, higher risk of splintering)"]
    )
    
    # The Action Button
    if st.button("🔥 START THE BUILD (Roll Luck Mechanics)", type="primary"):
        # Deduct physical wood material cost
        if st.session_state.coins < bp['cost']:
            st.error("You don't have enough money left to buy the physical wood for this project! Roll an easier blueprint.")
        else:
            st.session_state.coins -= bp['cost']
            
            # Base Success Calculations base on inputs
            success_chance = 75
            if risk_level == "Careful & Slow":
                success_chance += 15
            elif risk_level == "Rushed / Fast-Track":
                success_chance -= 30
                
            if "Hand Tools" in tool_choice and bp['difficulty'] in ["Hard", "Expert"]:
                success_chance -= 10 # Hand tools on hard wood is tough!
            
            # Execute Chance Roll
            luck_roll = random.randint(1, 100)
            
            # Trigger Random Workshop Disaster or Boon (1 in 4 chance)
            disaster_payout_modifier = 0
            if random.random() < 0.30:
                events = [
                    ("🪓 Knot in Wood!", -20, "Hit a hidden knot structural defect! Value reduced."),
                    ("🧯 Perfect Joinery!", 30, "The teacher loved your mortise & tenon joints! Bonus payout!"),
                    ("🩹 Minor Splinter!", -10, "Ouch! Lost time finding the first aid kit."),
                    ("♻️ Leftover Scraps!", 15, "Sanded efficiently and saved material. Money back!")
                ]
                ev_icon, ev_mod, ev_desc = random.choice(events)
                disaster_payout_modifier = ev_mod
                st.session_state.game_logs.append(f"EVENT: {ev_icon} {ev_desc} ({' +' if ev_mod > 0 else ''}{ev_mod} Credits)")

            # Determine Build Outcome
            if luck_roll <= success_chance:
                # Success!
                final_earnings = bp['payout'] + disaster_payout_modifier
                st.session_state.coins += final_earnings
                st.session_state.xp += 15
                st.session_state.game_logs.append(f"SUCCESS: Beautifully completed {bp['name']}! Earned {final_earnings} credits.")
            else:
                # Failure / Ruined project
                scrap_value = int(bp['cost'] * 0.3)
                st.session_state.coins += scrap_value
                st.session_state.game_logs.append(f"FAIL: Your hand slipped or the machine tore the wood grain. {bp['name']} ruined! Sold as firewood scrap for {scrap_value} credits.")
            
            # Clear project queue for next contract
            st.session_state.current_blueprint = None
            st.rerun()

st.write("---")

# --- GAME LOGS CONTAINER ---
st.subheader("📟 Workshop Live Telemetry Feed")
# Reverse logs to show newest at top
logs_html = "<br>".join([f"&gt; {log}" for log in reversed(st.session_state.game_logs)])
st.markdown(f"<div class='log-box'>{logs_html}</div>", unsafe_allow_html=True)
