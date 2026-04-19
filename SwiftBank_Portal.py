import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta

# --- 1. DATABASE CONNECTION (SMART CLOUD/LOCAL SETUP) ---
# --- 1. DATABASE CONNECTION (FORCE CLOUD) ---
@st.cache_resource
def _get_raw_connection():
    # We are pulling these directly from the Secrets you just saved
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"])  # Ensures the port is an integer
    )

def get_db_connection():
    try:
        db = _get_raw_connection()
        db.ping(reconnect=True, attempts=3, delay=1)
        return db
    except Exception as e:
        # This will tell us EXACTLY what address the code is still trying to use
        st.error(f"Current Host in Code: {st.secrets.get('DB_HOST', 'Not Found')}")
        st.error(f"Connection Error: {e}")
        return None
# --- 2. MULTI-THEME ENGINE ---
if 'theme' not in st.session_state:
    st.session_state.theme = "Midnight Blue"

t_colors = {
    "Midnight Blue": {"p": "#00C9FF", "s": "#92FE9D", "bg": "rgba(4, 11, 22, 0.88)"},
    "SBI Gold": {"p": "#D4AF37", "s": "#F4DF4E", "bg": "rgba(25, 20, 5, 0.88)"},
    "Cyber Dark": {"p": "#FF0055", "s": "#00FFDD", "bg": "rgba(8, 8, 12, 0.92)"},
    "Obsidian Reserve": {"p": "#E5E4E2", "s": "#8A9A5B", "bg": "rgba(5, 5, 5, 0.95)"}
}
tc = t_colors[st.session_state.theme]

st.set_page_config(page_title="SwiftBank YONO", layout="wide", initial_sidebar_state="expanded")

# CSS Injection: Luxury Dark-Mode & Hyper-Realistic Glassmorphism
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient({tc['bg']}, {tc['bg']}), 
                    url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .yono-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 30px; 
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 25px; 
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .yono-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
    }}
    .ecosystem-card {{
        background: linear-gradient(145deg, rgba(20,20,20,0.8), rgba(5,5,5,0.9));
        border-left: 4px solid {tc['p']};
    }}
    .main-title {{
        font-size: 48px; 
        font-weight: 900;
        letter-spacing: -1px;
        background: -webkit-linear-gradient(45deg, {tc['p']}, {tc['s']});
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }}
    .sub-text {{ color: #A0AEC0; font-size: 14px; margin-bottom: 5px; }}
    .highlight-val {{ font-size: 24px; font-weight: 700; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'card_active' not in st.session_state:
    st.session_state.card_active = True
if 'daily_limit' not in st.session_state:
    st.session_state.daily_limit = 50000

# --- 4. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="yono-card" style="margin-top: 100px; text-align: center;">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">SWIFT BANK</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #A0AEC0; margin-bottom: 30px;">Secure Enterprise Portal</p>', unsafe_allow_html=True)
        acc = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")
        
        if st.button("Authenticate", use_container_width=True):
            db = get_db_connection()
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT * FROM customers WHERE account_number = %s AND pin = %s", (acc, pin))
                user = cursor.fetchone()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    st.rerun()
                else: 
                    st.error("Authentication Failed. Invalid Credentials.")
                cursor.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. ENTERPRISE DASHBOARD ---
else:
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE account_number = %s", (st.session_state.user_data['account_number'],))
    user_live = cursor.fetchone()

    if 'mobile_no' not in user_live: user_live['mobile_no'] = "+91 98765 43210"
    if 'branch' not in user_live: user_live['branch'] = "Mumbai Nariman Point (Premium)"

    with st.sidebar:
        st.markdown(f"### 👤 {user_live['name']}")
        st.write(f"Acc: `{user_live['account_number']}`")
        st.divider()
        menu = st.radio("NAVIGATION", [
            "🏠 Dashboard", 
            "💰 Banking Services", 
            "📊 Investments", 
            "💎 Lifestyle Vaults",   
            "🌐 Swift Ecosystem",    
            "💳 Premium Cards",      
            "📜 Mini Statement",     
            "🛎️ Concierge Support",  
            "👤 My Profile", 
            "⚙️ Settings"
        ])
        st.divider()
        st.session_state.theme = st.selectbox("Interface Aesthetic", list(t_colors.keys()))
        if st.button("Secure Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- TAB 1: HOME ---
    if menu == "🏠 Dashboard":
        st.markdown('<h1 class="main-title">Financial Overview</h1>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="yono-card"><div class="sub-text">Liquid Assets</div><div class="highlight-val">₹{user_live.get("balance", 0):,.2f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="yono-card"><div class="sub-text">Active Liabilities</div><div class="highlight-val">₹{user_live.get("debt", 0):,.2f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="yono-card"><div class="sub-text">Card Status</div><div class="highlight-val">{"Active 🟢" if st.session_state.card_active else "Secured 🔴"}</div></div>', unsafe_allow_html=True)

    # --- TAB 2: BANKING SERVICES ---
    elif menu == "💰 Banking Services":
        st.markdown('<h1 class="main-title">Transfers & Cash</h1>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["💵 Cash Operations", "📲 Wire Transfer"])
        
        with t1:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            mode = st.radio("Action", ["Deposit", "Withdraw"], horizontal=True)
            amt = st.number_input("Amount (₹)", min_value=1.0, step=500.0)
            if st.button("Process Transaction"):
                if mode == "Withdraw" and amt > user_live.get('balance', 0): st.error("Insufficient Funds!")
                else:
                    change = amt if mode == "Deposit" else -amt
                    cursor.execute("UPDATE customers SET balance = balance + %s WHERE account_number = %s", (change, user_live['account_number']))
                    try: cursor.execute("INSERT INTO transactions (account_number, type, amount) VALUES (%s, %s, %s)", (user_live['account_number'], mode, amt))
                    except: pass 
                    db.commit()
                    st.success("Transaction Cleared Successfully.")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            target = st.text_input("Beneficiary Account Number")
            t_amt = st.number_input("Transfer Amount (₹)", min_value=1.0, step=1000.0)
            if st.button("Initiate Wire"):
                st.success("Wire Transfer Complete.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 3: INVESTMENTS ---
    elif menu == "📊 Investments":
        st.markdown('<h1 class="main-title">Wealth Management</h1>', unsafe_allow_html=True)
        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        st.subheader("Active Portfolio")
        mf_data = pd.DataFrame({"Asset Class": ["Bluechip Equity", "Mid-Cap Growth", "Nifty 50 Index"], "Allocated (₹)": [50000, 25000, 100000], "ROI": ["+16.0%", "+24.0%", "+12.0%"]})
        st.dataframe(mf_data, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: LIFESTYLE VAULTS ---
    elif menu == "💎 Lifestyle Vaults":
        st.markdown('<h1 class="main-title">Capital Transformations</h1>', unsafe_allow_html=True)
        st.write("*Feature lists don't build wealth. Visions do. Allocate your capital toward your ultimate lifestyle goals.*")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            st.subheader("🚀 Tech Syndicate Fund")
            st.write("Angel allocation for AI and Web3 startups.")
            st.progress(0.65)
            st.write("**₹6,500,000** / ₹10,000,000 Target")
            st.button("Deploy More Capital", key="v1")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            st.subheader("🏔️ Alpine Retreat Acquisition")
            st.write("Real estate reserve for your Swiss Chalet.")
            st.progress(0.30)
            st.write("**₹15,000,000** / ₹50,000,000 Target")
            st.button("Deploy More Capital", key="v2")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 5: SWIFT ECOSYSTEM ---
    elif menu == "🌐 Swift Ecosystem":
        st.markdown('<h1 class="main-title">Integrated Reality</h1>', unsafe_allow_html=True)
        st.write("*True luxury is invisible. Expand your financial control across our cinematic hardware ecosystem.*")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="yono-card ecosystem-card">', unsafe_allow_html=True)
            st.subheader("⌚ Swift Chronos")
            st.write("**The Biometric Timepiece**")
            st.write("Seamlessly authorize million-dollar wire transfers via continuous heart-rate biometrics and spatial UI gestures. No cards. No phones. Just flawless execution wrapped in sapphire glass and brushed titanium.")
            st.button("Join the Waitlist")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="yono-card ecosystem-card">', unsafe_allow_html=True)
            st.subheader("🎧 Swift Aura Earbuds")
            st.write("**AI Financial Concierge**")
            st.write("Whisper to your wealth. Execute trades, review market analytics, and manage your luxury portfolio through a highly secure, voice-activated spatial audio interface. God-level convenience in your ear.")
            st.button("Explore Specifications")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 6: PREMIUM CARDS ---
    elif menu == "💳 Premium Cards":
        st.markdown('<h1 class="main-title">The Swift Collection</h1>', unsafe_allow_html=True)
        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        st.subheader("Current Active Card")
        st.write(f"**Name on Card:** {user_live['name'].upper()}")
        st.write("**Card No:** •••• •••• •••• 4092")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 7: MINI STATEMENT ---
    elif menu == "📜 Mini Statement":
        st.markdown('<h1 class="main-title">Transaction Ledger</h1>', unsafe_allow_html=True)
        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        mock_history = pd.DataFrame({"Date": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)], "Description": ["UPI/Zomato", "ATM Withdrawal", "NEFT/Salary", "UPI/Uber", "Spotify Premium"], "Amount (₹)": [450.00, 5000.00, 85000.00, 320.00, 119.00]})
        st.dataframe(mock_history, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 8: CONCIERGE SUPPORT ---
    elif menu == "🛎️ Concierge Support":
        st.markdown('<h1 class="main-title">Priority Support</h1>', unsafe_allow_html=True)
        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        st.write("Your time is your most valuable asset. Skip the queues and connect directly with your dedicated wealth manager.")
        st.button("📞 Request Callback within 5 Mins", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 9: MY PROFILE ---
    elif menu == "👤 My Profile":
        st.markdown('<h1 class="main-title">Client Identity</h1>', unsafe_allow_html=True)
        
        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        st.subheader("Current Registered Details")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Full Legal Name:** {user_live['name']}")
            st.write(f"**Mobile Number:** {user_live.get('mobile_no', '+91 XXXXX XXXXX')}")
        with c2:
            st.write(f"**Account Number:** {user_live['account_number']}")
            st.write(f"**Home Branch:** {user_live.get('branch', 'Main Branch')}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="yono-card">', unsafe_allow_html=True)
        st.subheader("Update Information")
        
        new_name = st.text_input("Update Name", value=user_live['name'])
        # The syntax error from line 287 is permanently fixed right here!
        new_mob = st.text_input("Update Mobile Number", value=user_live.get('mobile_no', ''))
        new_acc = st.text_input("Update Account Number (Caution!)", value=user_live['account_number'])
        
        if st.button("Commit Identity Updates"):
            try:
                query = "UPDATE customers SET name = %s, account_number = %s"
                params = [new_name, new_acc]
                
                try:
                    cursor.execute("UPDATE customers SET mobile_no = %s WHERE account_number = %s", (new_mob, user_live['account_number']))
                except mysql.connector.Error:
                    st.warning("Mobile Number column 'mobile_no' missing in MySQL 'customers' table. Only Name/Acc updated.")
                
                query += " WHERE account_number = %s"
                params.append(user_live['account_number'])
                
                cursor.execute(query, tuple(params))
                db.commit()
                
                st.session_state.user_data['account_number'] = new_acc
                st.success("Profile Identity Updated Successfully!")
                st.rerun()
            except Exception as e:
                db.rollback()
                st.error(f"Update failed. (If updating account number, check for Foreign Key constraints in transaction tables). Error: {e}")

        st.divider()
        new_pin = st.text_input("Reset Security PIN (4-Digits)", type="password", maxlength=4)
        if st.button("Enforce New PIN"):
            cursor.execute("UPDATE customers SET pin = %s WHERE account_number = %s", (new_pin, user_live['account_number']))
            db.commit()
            st.success("Security Credentials Updated!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 10: SETTINGS ---
    elif menu == "⚙️ Settings":
        st.markdown('<h1 class="main-title">System Controls</h1>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            st.subheader("💳 Hardware Control")
            st.write("Instantly sever connection to your physical debit card.")
            if st.session_state.card_active:
                if st.button("Initiate Card Lockdown 🔴", use_container_width=True):
                    st.session_state.card_active = False
                    st.rerun()
            else:
                if st.button("Restore Card Access 🟢", use_container_width=True):
                    st.session_state.card_active = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="yono-card">', unsafe_allow_html=True)
            st.subheader("🛑 Flow Limits")
            st.write("Govern maximum daily capital outflow.")
            limit = st.slider("Max Outflow (₹)", 10000, 500000, st.session_state.daily_limit, step=10000)
            if st.button("Apply Parameters"):
                st.session_state.daily_limit = limit
                st.success("Outflow limits synchronized.")
            st.markdown('</div>', unsafe_allow_html=True)

    cursor.close()
