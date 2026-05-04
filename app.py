import streamlit as st
import pandas as pd

st.title("Glasgow Bin Finder 🚛")

# 1. THE PORTAL: Upload the Excel file
uploaded_file = st.file_uploader("Admin: Upload Kerbside Excel", type="xlsx")

if uploaded_file:
    # Read the data (like fetching from a DB)
    df = pd.read_excel(uploaded_file, sheet_name="All Kerb")
    
    # 2. ADDRESS SELECTOR: Postcode search
    postcode = st.text_input("Enter Postcode (e.g., G404EA)").upper().replace(" ", "")
    
    if postcode:
        # Filter data (The 'SELECT * FROM df WHERE...' equivalent)
        results = df[df['Postcode1'] == postcode]
        
        if not results.empty:
            address = st.selectbox("Select your address", results['Address 1'])
            
            # 3. DASHBOARD: Show the info
            st.success(f"Selected: {address}")
            cal_code = results.iloc[0]['Calendar Code']
            st.write(f"Your Bin Group is: **{cal_code}**")
            
            # Link to the PDF you found earlier
            url = results.iloc[0]['Calendar URL']
            st.link_button("View Official PDF", url)
