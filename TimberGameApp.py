import streamlit as pd
import streamlit as st
import random

# Initialize session states for the game
if 'step' not in st.session_state:
    st.session_state.step = "Intro"
if 'coins' not in st.session_state:
    st.session_state.coins = 100
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'safety_passed' not in st.session_state:
    st.session_state.safety_passed = False

# Set page config
st.set_page_config(page_title="Wood Shop Tycoon", page_icon="🪵", layout="centered")

# --- CUSTOM THEME STYLING ---
st.markdown("""
    <style>
    .main-title { font-size: 2.8rem; font-weight: 800; color: #8B5A2B; text-align: center; margin-bottom: 10px; }
    .sub-title { font-size: 1.2rem; text-align: center; color: #555; margin-bottom: 30px; }
    .stat-box { background-color: #F5F5DC; padding: 15px; border-radius: 10px; border: 2px solid #8B5A2B; text-align: center; font-weight: bold; font-size: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

# --- GAME HEADER ---
st.markdown("<div class='main-title'>🪵 Wood Shop Tycoon</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Year 8 Timber Technology Challenge</div>", unsafe_allow_html=True)

# Display stats sidebar if the player is past the intro
if st.session_state.step != "Intro":
    st.sidebar.markdown(f"### 🎒 Player Dashboard")
    st.sidebar.markdown(f"**Wallet:** {st.session_state.coins} Timber Credits")
    st.sidebar.markdown(f"**Safety Status:** {'✅ Certified' if st.session_state.safety_passed else '❌ Uncertified'}")
    if st.session_state.inventory:
        st.sidebar.markdown(f"**Materials:** {', '.join(st.session_state.inventory)}")
    else:
        st.sidebar.markdown("**Materials:** Empty")
    
    if st.sidebar.button("Restart Game"):
        st.session_state.clear()
        st.rerun()

# --- MODULES ---

# STEP 1: INTRO SCREEN
if st.session_state.step == "Intro":
    st.markdown("""
    ### Welcome Apprentice! 🛠️
    Before you can build high-end projects and run your own successful woodworking business, you need to prove your skills. 
    
    **Your Journey:**
    1. **Earn your Safety License:** You can't touch the tools without passing the safety check.
    2. **Identify your Tools:** Prove you know your Try Squares from your Tenon Saws.
    3. **Run the Wood Shop:** Buy raw wood, manufacture projects cleanly, manage your sustainability impact, and try to make a fortune!
    """)
    
    if st.button("Start My Apprenticeship", type="primary"):
        st.session_state.step = "Safety"
        st.rerun()

# STEP 2: SAFETY LICENSE EXAM
elif st.session_state.step == "Safety":
    st.header("⚠️ Module 1: The Safety Induction")
    st.write("Answer all safety questions correctly to enter the workshop floor.")
    
    q1 = st.radio("1. What is the standard safety margin (distance) your fingers should keep from a moving blade or machine?", 
                  ["0mm - live on the edge", "20mm", "50mm", "100mm"])
    
    q2 = st.radio("2. If a machine sounds strange or isn't working properly, what should you do?", 
                  ["Try to fix it yourself with a hammer", "Turn it off immediately and tell the teacher", "Ignore it and keep working", "Leave it running and walk away"])
    
    q3 = st.radio("3. What is the correct Personal Protective Equipment (PPE) combination for using the drill press?", 
                  ["Safety glasses, hair tied back, enclosed shoes", "Loose clothing, apron, sunglasses", "Gloves, safety glasses, scarf", "Enclosed shoes only"])

    if st.button("Submit Safety Assessment", type="primary"):
        if q1 == "50mm" and q2 == "Turn it off immediately and tell the teacher" and q3 == "Safety glasses, hair tied back, enclosed shoes":
            st.success("🎉 100% Correct! You've earned your Workshop Safety License.")
            st.session_state.safety_passed = True
            st.session_state.step = "Tool Identification"
            st.rerun()
        else:
            st.error("❌ You missed a safety rule! In a real workshop, this causes accidents. Re-read the choices carefully and try again.")

# STEP 3: TOOL IDENTIFICATION
elif st.session_state.step == "Tool Identification":
    st.header("🪚 Module 2: Tool Master Match-Up")
    st.write("Match the woodworking process to the correct Year 8 hand tool.")

    tool_score = 0
    
    t1 = st.selectbox("Which tool is designed to accurately mark out right angles (90 degrees) on timber grains?", 
                      ["", "Tenon Saw", "Try Square", "Chisel", "Marking Gauge"])
    t2 = st.selectbox("Which saw has a rigid brass or steel back and is best suited for making straight, clean cuts in joints?", 
                      ["", "Coping Saw", "Crosscut Hand Saw", "Tenon Saw"])
    t3 = st.selectbox("Which tool features a thin, flexible blade and is used for cutting tight curves and shapes in thin wood?", 
                      ["", "Jigsaw", "Coping Saw", "Band Saw"])

    if st.button("Verify Tool Selection", type="primary"):
        if t1 == "Try Square" and t2 == "Tenon Saw" and t3 == "Coping Saw":
            st.success("🎯 Masterful! You know your tools. You are now cleared to use the manufacturing floor.")
            st.session_state.step = "Marketplace"
            st.rerun()
        else:
            st.error("❌ Some tools are mismatched. Double check your definitions!")

# STEP 4: THE TYCOON MARKETPLACE & MANUFACTURING
elif st.session_state.step == "Marketplace":
    st.header("💰 Module 3: Wood Shop Tycoon")
    st.write("Welcome to the business simulation! Your goal is to keep making products until you grow your money or test your engineering choices.")
    
    # Game Over Conditions
    if st.session_state.coins <= 0:
        st.error("😭 Bankrupt! You ran out of timber credits. Better luck next time!")
        if st.button("Reset Game"):
            st.session_state.clear()
            st.rerun()
        st.stop()
        
    if st.session_state.coins >= 300:
        st.balloons()
        st.success("🏆 Wood Shop Tycoon Elite! You grew your shop to over 300 credits responsibly. Outstanding business management!")
        if st.button("Play Again"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    st.subheader("Step 1: Buy Your Timber Material")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Radiata Pine (Softwood)**")
        st.write("Fast growing, sustainable plantation timber. Easy to work with.")
        st.write("Cost: **20 Credits**")
        if st.button("Buy Radiata Pine"):
            if st.session_state.coins >= 20:
                st.session_state.coins -= 20
                st.session_state.inventory.append("Pine")
                st.success("Added Pine to your timber rack!")
                st.rerun()
            else:
                st.error("Not enough credits!")

    with col2:
        st.markdown("**Tasmanian Oak (Hardwood)**")
        st.write("Dense, beautiful grain structure. High quality but takes longer to mature.")
        st.write("Cost: **40 Credits**")
        if st.button("Buy Tasmanian Oak"):
            if st.session_state.coins >= 40:
                st.session_state.coins -= 40
                st.session_state.inventory.append("Tas Oak")
                st.success("Added Tas Oak to your timber rack!")
                st.rerun()
            else:
                st.error("Not enough credits!")

    st.markdown("---")
    
    # Manufacturing Section
    st.subheader("Step 2: Manufacture a Project")
    if not st.session_state.inventory:
        st.warning("⚠️ You need to buy raw timber material from the marketplace above before starting a build!")
    else:
        chosen_material = st.selectbox("Select material to build with:", st.session_state.inventory)
        project_type = st.radio("What project do you want to build?", ["Simple Coaster", "Premium Pencil Box"])
        
        st.markdown("**Select your Manufacturing Steps:**")
        step_1_tool = st.selectbox("1. Squaring and Marking material edge:", ["", "Hand", "Try Square & Pencil", "Chisel"])
        step_2_tool = st.selectbox("2. Cutting pieces to size:", ["", "Tenon Saw", "Coping Saw", "Hammer"])
        step_3_finish = st.selectbox("3. Surface Finish Technique:", ["", "Leave it rough", "Sandpaper (120 to 240 grit) then Linseed Oil", "Spray Paint without sanding"])

        if st.button("Hammer & Build!", type="primary"):
            # Check correctness of chosen methods
            if step_1_tool == "Try Square & Pencil" and step_2_tool == "Tenon Saw" and step_3_finish == "Sandpaper (120 to 240 grit) then Linseed Oil":
                
                # Base valuation algorithm
                base_value = 50 if project_type == "Simple Coaster" else 95
                
                # Boost if hardwood premium quality used
                if chosen_material == "Tas Oak":
                    base_value += 35
                    quality_mod = "Premium Hardwood Finish"
                else:
                    quality_mod = "Standard Softwood Build"
                
                # Payout 
                st.session_state.coins += base_value
                st.session_state.inventory.remove(chosen_material)
                
                st.balloons()
                st.success(f"📦 Successfully manufactured! Sold your {project_type} ({quality_mod}) for **{base_value} Credits**!")
                st.rerun()
            else:
                # Poor processing results in lost investment or reduced valuation
                st.session_state.inventory.remove(chosen_material)
                penalty = 10
                st.session_state.coins += penalty
                st.error(f"❌ Manufacturing Faults! You skipped proper procedures (e.g., didn't use a Try Square, rough finish, or poor tool choices). The project cracked and only sold as firewood scrap for **{penalty} Credits**.")
                st.rerun()
