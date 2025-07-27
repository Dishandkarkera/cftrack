# cftrack/app/streamlit_app.py

import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
        }
        .block-container {
            padding: 2rem 1rem;
        }
        h1, h2, h3 {
            color: #007bff;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Load model and raw dataset
@st.cache_resource
def load_assets():
    model = joblib.load('../model/emission_model.pkl')
    df = pd.read_csv('../data/SupplyChainGHGEmissionFactors.csv')
    return model, df

model, raw_df = load_assets()

# Clean and prepare dataset
raw_df.columns = raw_df.columns.str.strip()
df_clean = raw_df.rename(columns={
    '2017 NAICS Title': 'NAICS_Title',
    'GHG': 'GHG_Type',
    'Supply Chain Emission Factors without Margins': 'Emission_Factor'
})
df_clean = df_clean.dropna(subset=['NAICS_Title', 'GHG_Type', 'Emission_Factor'])
df_encoded = pd.get_dummies(df_clean[['NAICS_Title', 'GHG_Type']], drop_first=True)

# Sidebar Filters
st.sidebar.header("Filter Dataset")

naics_filter_options = df_clean['NAICS_Title'].dropna().unique()
ghg_filter_options = df_clean['GHG_Type'].dropna().unique()

selected_naics_filter = st.sidebar.multiselect("Select NAICS Sector", options=naics_filter_options, default=naics_filter_options)
selected_ghg_filter = st.sidebar.multiselect("Select GHG Type", options=ghg_filter_options, default=ghg_filter_options)

min_val = df_clean['Emission_Factor'].min()
max_val = df_clean['Emission_Factor'].max()
emission_range = st.sidebar.slider("Emission Factor Range", float(min_val), float(max_val), (float(min_val), float(max_val)))

filtered_df = df_clean[
    (df_clean['NAICS_Title'].isin(selected_naics_filter)) &
    (df_clean['GHG_Type'].isin(selected_ghg_filter)) &
    (df_clean['Emission_Factor'] >= emission_range[0]) &
    (df_clean['Emission_Factor'] <= emission_range[1])
]

# Streamlit UI
st.set_page_config(page_title="CFTrack – Carbon Emission Estimator", layout="centered")
st.title("🌍 CFTrack – Carbon Footprint Tracker for Supply Chains")

# Sidebar inputs
st.sidebar.header("📅 Input Parameters")
naics_options = sorted(df_clean['NAICS_Title'].unique())
ghg_options = sorted(df_clean['GHG_Type'].unique())

selected_naics = st.sidebar.selectbox("Select Industry (NAICS)", naics_options)
selected_ghg = st.sidebar.selectbox("Select GHG Type", ghg_options)

# Prepare user input
user_input = pd.DataFrame(columns=df_encoded.columns)
user_input.loc[0] = 0

naics_col = f'NAICS_Title_{selected_naics}'
ghg_col = f'GHG_Type_{selected_ghg}'

if naics_col in user_input.columns:
    user_input.loc[0, naics_col] = 1
if ghg_col in user_input.columns:
    user_input.loc[0, ghg_col] = 1

# Predict and display
if st.sidebar.button("🔍 Predict Emission"):
    prediction = model.predict(user_input)[0]

    if prediction < 50:
        severity = "Low 🟢"
        tip = "✅ Great job! You’re already in the low emission zone. Maintain efficient practices."
    elif 50 <= prediction < 150:
        severity = "Moderate 🟠"
        tip = "⚠️ Consider switching to energy-efficient equipment or greener logistics partners."
    else:
        severity = "High 🔴"
        tip = "❌ Urgent! Explore renewable energy, optimize supply routes, or switch suppliers."

    st.subheader("📊 Prediction Results")
    st.metric("Predicted Emission", f"{prediction:.2f} kg CO₂e/unit")
    st.metric("Severity Level", severity)
    st.info(f"♻️ **Emission Reduction Tip**:\n{tip}")

    st.subheader("📉 Emission Factor Distribution")
    fig, ax = plt.subplots()
    ax.hist(filtered_df['Emission_Factor'], bins=50, color='skyblue', edgecolor='black')
    ax.axvline(prediction, color='red', linestyle='--', label='Your Prediction')
    ax.set_xlabel("Emission Factor (kg CO₂e/unit)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Emission Factors")
    ax.legend()
    st.pyplot(fig)

    st.subheader("📊 Severity Distribution in Dataset")
    def classify(val):
        if val < 50:
            return 'Low'
        elif 50 <= val < 150:
            return 'Moderate'
        else:
            return 'High'

    filtered_df['Severity'] = filtered_df['Emission_Factor'].apply(classify)
    severity_counts = filtered_df['Severity'].value_counts()
    st.plotly_chart(severity_counts.plot.pie(autopct='%1.1f%%', labels=severity_counts.index, ylabel='').get_figure())

    st.subheader("🛆 Emission by GHG Type")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered_df, x='GHG_Type', y='Emission_Factor', palette='Set2', ax=ax2)
    ax2.set_title("GHG Type vs Emission Factor")
    st.pyplot(fig2)

    result_df = pd.DataFrame({
        'Industry': [selected_naics],
        'GHG Type': [selected_ghg],
        'Predicted Emission (kg CO2e/unit)': [round(prediction, 2)],
        'Severity': [severity.replace("🟢", "").replace("🟠", "").replace("🔴", "")],
        'Suggestion': [tip]
    })

    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Result as CSV", csv, "cftrack_prediction.csv", "text/csv")

st.markdown("---")
st.header("🌐 Understanding GHG Types")

st.markdown("""
| GHG Type | Full Name              | Global Warming Potential (GWP)* | Description |
|----------|------------------------|-------------------------------|-------------|
| CO₂      | Carbon Dioxide         | 1                             | Main gas from fossil fuel burning |
| CH₄      | Methane                | 25                            | Emitted by livestock, landfills |
| N₂O      | Nitrous Oxide          | 298                           | From fertilizers, industry |
| SF₆      | Sulfur Hexafluoride    | 23,500                        | Used in electrical insulators |
| HFCs     | Hydrofluorocarbons     | 100–12,000                   | Used in refrigeration |
| PFCs     | Perfluorocarbons       | 6,500–9,200                  | From aluminum production |

*GWP: How much heat the gas traps compared to CO₂ over 100 years.
""")

st.info("📘 Use this to understand how GHG type selection impacts total emissions!")

st.subheader("📈 GHG Type Distribution in Dataset")
ghg_freq = filtered_df['GHG_Type'].value_counts()
fig3, ax3 = plt.subplots()
ghg_freq.plot(kind='bar', color='teal', ax=ax3)
ax3.set_title("Frequency of GHG Types in Dataset")
ax3.set_xlabel("GHG Type")
ax3.set_ylabel("Count")
st.pyplot(fig3)

st.subheader("📄 Export Processed Results")
csv = df_clean.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='cftrack_processed_emissions.csv',
    mime='text/csv',
)

st.subheader("🌱 Tips to Reduce Supply Chain Emissions")
tips = [
    "Use energy-efficient machinery and logistics partners.",
    "Switch to renewable energy sources for manufacturing and transport.",
    "Consolidate shipments to reduce transportation emissions.",
    "Collaborate with suppliers to track and reduce their emissions.",
    "Prefer local suppliers to minimize carbon from long-distance transport.",
    "Optimize packaging to reduce material usage and weight.",
]
for tip in tips:
    st.markdown(f"✅ {tip}")

