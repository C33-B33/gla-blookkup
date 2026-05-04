import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 1. THE LOGIC ENGINE (Math & ICS Generator)
# ==========================================

def get_next_collection(anchor_date, interval_weeks):
    """Calculates the next collection date based on an anchor."""
    today = datetime.now().date()
    if anchor_date >= today:
        return anchor_date
    
    delta = today - anchor_date
    days_in_cycle = interval_weeks * 7
    days_past_last = delta.days % days_in_cycle
    
    if days_past_last == 0:
        return today
        
    days_until_next = days_in_cycle - days_past_last
    return today + timedelta(days=days_until_next)

def generate_ics_content(collections):
    """Generates the text for an .ics file."""
    ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Glasgow Bin Schedule Finder//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    for name, date, freq in collections:
        start_date = date.strftime('%Y%m%d')
        ics.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{start_date}",
            f"DTEND;VALUE=DATE:{start_date}",
            f"SUMMARY:{name}",
            f"RRULE:FREQ=WEEKLY;INTERVAL={freq}",
            "BEGIN:VALARM",
            "TRIGGER:-PT12H",
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder: Put the bin out!",
            "END:VALARM",
            "END:VEVENT"
        ])
    ics.append("END:VCALENDAR")
    return "\n".join(ics)

# ==========================================
# 2. DATABASE & CONFIGURATION
# ==========================================

# st.cache_data prevents the app from reloading the Excel file on every click
@st.cache_data
def load_data():
    # Make sure this matches the exact filename you uploaded!
    return pd.read_excel('Kerbside_Address_Search_Final2.xlsx', sheet_name='All Kerb')

# This is your "config.php". For now, we just have EQ_67, but you can add more later.
AREA_CONFIG = {
    "EQ_67": {
        "blue_anchor": datetime(2026, 1, 23).date(),
        "purple_anchor": datetime(2026, 2, 9).date()
    }
}

# Dictionary mapping bin types to emojis and hex colors
BIN_STYLES = {
    "Blue Bin (Paper/Card)": {"icon": "🟦", "color": "#007BFF"},     # Council Blue
    "Grey Bin (Plastics/Cans)": {"icon": "🩶", "color": "#6C757D"},  # Slate Grey
    "Green Bin (General Waste)": {"icon": "🟩", "color": "#28A745"}, # Emerald Green
    "Brown Bin (Food/Garden)": {"icon": "🟫", "color": "#8B4513"},   # Earth Brown
    "Purple Bin (Glass)": {"icon": "🟪", "color": "#6F42C1"}         # Deep Purple
}



# ==========================================
# 3. STATE MANAGEMENT (The "Cookie")
# ==========================================

st.set_page_config(page_title="Glasgow Bin Finder", page_icon="🚛", layout="centered")

# Initialize the session state if it doesn't exist yet
if 'cal_code' not in st.session_state:
    st.session_state['cal_code'] = None

# ==========================================
# 4. THE VIEWS (The User Interface)
# ==========================================

# --- VIEW A: THE DASHBOARD (User is "Logged In") ---
if st.session_state['cal_code']:
    user_code = st.session_state['cal_code']
    
    st.title("Your Bin Schedule 🚛")
    
    # Check if we have the math configuration for their area
    if user_code in AREA_CONFIG:
        config = AREA_CONFIG[user_code]
        friday_anchor = config["blue_anchor"]
        monday_anchor = config["purple_anchor"]
        
        # Calculate upcoming dates
        collections = [
            ("Blue Bin (Paper/Card)", get_next_collection(friday_anchor, 4), 4),
            ("Grey Bin (Plastics/Cans)", get_next_collection(friday_anchor + timedelta(weeks=2), 4), 4),
            ("Green Bin (General Waste)", get_next_collection(friday_anchor - timedelta(weeks=1), 3), 3),
            ("Brown Bin (Food/Garden)", get_next_collection(friday_anchor + timedelta(weeks=1), 2), 2),
            ("Purple Bin (Glass)", get_next_collection(monday_anchor, 8), 8)
        ]
        
        # Sort by closest date
        collections.sort(key=lambda x: x[1])
        
        st.subheader("Upcoming Collections")
        
        for name, date, freq in collections:
            days_away = (date - datetime.now().date()).days
            
            # Grab the specific color and icon for this bin
            style = BIN_STYLES.get(name, {"icon": "🗑️", "color": "#333333"})
            
            # Format the "Days Away" text dynamically
            if days_away == 0:
                time_text = "🚨 **TODAY!** Put it out now!"
                bg_color = "#ffeeba" # Slight yellow highlight for today
            elif days_away == 1:
                time_text = f"⏰ Tomorrow ({date.strftime('%d %b')})"
                bg_color = "#f8f9fa"
            else:
                time_text = f"📅 {date.strftime('%A, %d %b')} ({days_away} days away)"
                bg_color = "#ffffff"

            # Inject custom HTML/CSS to create a beautiful "Card"
            st.markdown(
                f"""
                <div style="
                    padding: 15px; 
                    border-left: 8px solid {style['color']}; 
                    background-color: {bg_color}; 
                    border-radius: 8px; 
                    margin-bottom: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <h4 style="margin: 0; color: #31333F;">
                        {style['icon']} <span style="color: {style['color']};">{name}</span>
                    </h4>
                    <p style="margin: 5px 0 0 0; font-size: 16px; color: #555;">
                        {time_text}
                    </p>
                </div>
                """, 
                unsafe_allow_html=True # This tells Streamlit it's okay to render your HTML
            )
                
        st.divider()
        
        # Actions Row
        col1, col2 = st.columns(2)
        with col1:
            ics_data = generate_ics_content(collections)
            st.download_button("📥 Download Calendar (.ics)", data=ics_data, file_name="Glasgow_Bins.ics", mime="text/calendar")
        with col2:
            st.link_button("🔗 Verify with Council", "https://onlineservices.glasgow.gov.uk/forms/refuseandrecyclingcalendar/")
            
    else:
        st.warning(f"We know you are in area **{user_code}**, but we don't have the starting dates mapped for this zone yet!")
    
    st.divider()
    if st.button("⚙️ Change Address"):
        st.session_state['cal_code'] = None
        st.rerun()

# --- VIEW B: THE ONBOARDING (Search & Save) ---
else:
    st.title("Find Your Bin Schedule 🚛")
    st.write("Enter your postcode to find your personalized Glasgow recycling rotation.")
    
    try:
        df = load_data()
        postcode_input = st.text_input("Enter Postcode (e.g., G404EA)").upper().replace(" ", "")
        
        if postcode_input:
            results = df[df['Postcode1'] == postcode_input]
            
            if not results.empty:
                address = st.selectbox("Select your address", results['Address 1'])
                user_row = results[results['Address 1'] == address].iloc[0]
                found_code = user_row['Calendar Code']
                
                st.success(f"Address found! You are in Zone: **{found_code}**")
                
                if st.button("Save & View Schedule"):
                    st.session_state['cal_code'] = found_code
                    st.rerun()
            else:
                st.error("Postcode not found. Make sure it's an exact match without spaces.")
    except FileNotFoundError:
        st.error("Database file missing! Please ensure 'Kerbside_Address_Search_Final2 (1).xlsx' is in the same folder as this script.")
