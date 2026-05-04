import streamlit as st
import pandas as pd

# Load the data from your uploaded Excel file
@st.cache_data
def load_data():
    # We use the 'All Kerb' sheet from your file
    df = pd.read_csv('Kerbside_Address_Search_Final2 (1).xlsx - All Kerb.csv')
    return df

df = load_data()

st.title("Glasgow Bin Finder 🚛")

# Address Selector Logic
postcode_input = st.text_input("Enter Postcode", value="G404EA").upper().strip()

if postcode_input:
    # Filter the Excel data for that postcode
    filtered_df = df[df['Postcode1'] == postcode_input.replace(" ", "")]
    
    if not filtered_df.empty:
        address = st.selectbox("Select your address", filtered_df['Address 1'])
        
        # Grab the specific row for the selected address
        user_row = filtered_df[filtered_df['Address 1'] == address].iloc[0]
        cal_code = user_row['Calendar Code']
        
        st.info(f"Your Address uses Calendar Code: **{cal_code}**")
        
        # Link to the official PDF found in your Excel
        st.link_button("Open Official PDF Schedule", user_row['Calendar URL'])
    else:
        st.error("Postcode not found in the local database.")
