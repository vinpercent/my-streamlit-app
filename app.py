import streamlit as st
import pandas as pd
from database import engine
from model import train_lifespan_model, predict_months

st.set_page_config(page_title="Equity Afya Lifespan Tool", layout="wide")
st.title("🏥 Equity Afya Franchise Predictive Lifespan App")
st.write("Manage franchise records, input operational profiles, and analyze survival trajectories across Kenya.")

# Load database metrics and train model parameters
model = train_lifespan_model()

# Fetch existing records to use for the autofill selection tool
try:
    existing_clinics_df = pd.read_sql("SELECT * FROM franchise_metrics", engine)
except Exception:
    existing_clinics_df = pd.DataFrame()

# Create navigation tabs
tab1, tab2 = st.tabs(["🔮 Lifespan Predictor", "⚙️ Administrative Data Portal"])

# --- TAB 1: PREDICTIVE DASHBOARD (WITH AUTOFILL) ---
with tab1:
    st.subheader("Simulate Clinic Baseline Statistics")
    
    # Initialize default form values
    default_name = "Equity Afya - Siaya"
    default_county = "Nairobi"
    default_capital = 5000000
    default_cost = 600000
    default_patients = 450
    default_competitors = 4

    # 🛠️ Smart Dropdown Option
    if not existing_clinics_df.empty:
        # Create a list of names and add a clean manual option at the top
        clinic_options = ["-- Select an Existing Backend Clinic (Autofill) --"] + list(existing_clinics_df['clinic_name'].unique())
        selected_clinic = st.selectbox("📂 Optional: Load Data directly from Backend Tables", clinic_options)
        
        # If the user selects an actual clinic, overwrite our default variables instantly
        if selected_clinic != "-- Select an Existing Backend Clinic (Autofill) --":
            clinic_row = existing_clinics_df[existing_clinics_df['clinic_name'] == selected_clinic].iloc[0]
            default_name = str(clinic_row['clinic_name'])
            default_county = str(clinic_row['county'])
            default_capital = int(clinic_row['initial_capital_kes'])
            default_cost = int(clinic_row['monthly_operating_cost_kes'])
            default_patients = int(clinic_row['average_monthly_patients'])
            default_competitors = int(clinic_row['competitor_count_radius_5km'])
            st.success(f"⚡ Loaded details for '{default_name}' from the backend database!")

    # Standard form wrapped around values
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            clinic_name = st.text_input("Franchise / Clinic Name", value=default_name)
            
            # Map county string to its index in the selection list safely
            counties_list = ["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Siaya", "Kisumu", "Uasin Gishu", "Meru"]
            county_index = counties_list.index(default_county) if default_county in counties_list else 0
            county = st.selectbox("County Location", counties_list, index=county_index)
            
            initial_capital = st.number_input("Initial Capital Infusion (KES)", min_value=100000, value=default_capital, step=50000)
        
        with col2:
            monthly_cost = st.number_input("Fixed Monthly Operating Costs (KES)", min_value=50000, value=default_cost, step=10000)
            patients = st.number_input("Projected Monthly Patient Volume", min_value=10, value=default_patients, step=10)
            competitors = st.slider("Competitor Facilities within 5KM Radius", 0, 20, value=default_competitors)

        submit = st.form_submit_button("Calculate Projected Lifespan")

    if submit:
        feature_vector = [initial_capital, monthly_cost, patients, competitors]
        projected_months = predict_months(model, feature_vector)
        
        st.markdown("---")
        st.subheader(f"Results for {clinic_name} ({county} County)")
        if projected_months < 12.0:
            st.error(f"⚠️ High Risk Profile: Estimated Operational Lifespan is **{projected_months} months**.")
        elif projected_months < 36.0:
            st.warning(f"⚠️ Moderate Risk Profile: Estimated Operational Lifespan is **{projected_months} months**.")
        else:
            st.success(f"✅ Stable Profile: Estimated Operational Lifespan is **{projected_months} months** (+3 Years).")

# --- TAB 2: BACKEND ADMIN DATA PORTAL ---
with tab2:
    st.subheader("📝 Key In New Historical Franchise Records")
    st.info("Adding records here trains the underlying Machine Learning model to make better calculations.")
    
    with st.form("admin_input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Historical Clinic Name", placeholder="e.g., Equity Afya - Meru")
            new_county = st.selectbox("County Location", ["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Siaya", "Kisumu", "Uasin Gishu", "Meru"], key="adm_county")
            new_capital = st.number_input("Actual Initial Capital (KES)", min_value=100000, value=4000000, step=50000)
            new_cost = st.number_input("Average Monthly Operating Cost (KES)", min_value=50000, value=500000, step=10000)
        with col2:
            new_patients = st.number_input("Average Monthly Patient Volume", min_value=10, value=380, step=10)
            new_competitors = st.slider("Competitor Facilities within 5KM", 0, 20, 3)
            new_survival = st.number_input("Historical Survival Timeline (Months)", min_value=1, value=24, step=1)
            
        save_button = st.form_submit_button("💾 Save Record to Database")
        
    if save_button:
        if not new_name.strip():
            st.error("Please enter a valid Clinic Name before saving.")
        else:
            new_record = pd.DataFrame({
                'clinic_name': [new_name],
                'county': [new_county],
                'initial_capital_kes': [float(new_capital)],
                'monthly_operating_cost_kes': [float(new_cost)],
                'average_monthly_patients': [int(new_patients)],
                'competitor_count_radius_5km': [int(new_competitors)],
                'historical_survival_months': [int(new_survival)]
            })
            try:
                new_record.to_sql('franchise_metrics', con=engine, if_exists='append', index=False)
                st.success(f"🎉 '{new_name}' permanently saved to the backend database!")
                st.rerun()  # Forces a clean page update so the dropdown picks up the new name instantly
            except Exception as e:
                st.error(f"Database insertion failed: {e}")

    # Live Backend View
    st.markdown("---")
    st.subheader("🔍 Live Database Table View (Backend Records)")
    
    if not existing_clinics_df.empty:
        st.markdown(f"Total Database Rows Found: **{len(existing_clinics_df)}**")
        st.dataframe(existing_clinics_df, use_container_width=True, hide_index=True)
    else:
        st.warning("The database is currently empty.")
