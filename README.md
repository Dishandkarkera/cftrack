# 🌿 CFTrack - Carbon Footprint Tracker for Supply Chains

CFTrack is a cloud-based data science dashboard built using **Streamlit** to analyze and visualize **greenhouse gas (GHG) emissions** across various supply chain activities. It enables users to upload, filter, compare, and download emission data using NAICS classification codes.

---

## 📊 Features

- 📂 Upload your own CSV data or use built-in datasets
- 🔍 Filter emissions by **NAICS Code** and **GHG Type**
- 📈 Visualize emission factors, GHG distributions, and comparisons
- ⬇️ Download the filtered dataset
- 💡 Suggestions for reducing carbon emissions in supply chains
- 🧪 Easily extendable with Machine Learning and SHAP for explainability

---

## 📁 Folder Structure

cftrack/
├── app/
│ └── streamlit_app.py # Main Streamlit UI app
├── data/
│ └── cleaned_supply_chain_emissions.csv # Default dataset
├── .streamlit/
│ └── config.toml # Streamlit UI theme config
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## Create Virtual Environment (optional but recommended)

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # on Linux/Mac
venv\Scripts\activate     # on Windows

---

## install Dependencies

bash
Copy
Edit
pip install -r requirements.txt

---

## Launch the App

bash
Copy
Edit
streamlit run app/streamlit_app.py

---

## Sample Dataset

The included dataset cleaned_supply_chain_emissions.csv contains:
2017 NAICS Code: North American Industry Classification
2017 NAICS Title: Description of the activity
GHG: Greenhouse Gas type (e.g., CO₂, CH₄)
Supply Chain Emission Factors with Margins: Estimated emissions data

---

## Requirements

Python 3.8+
Streamlit
Pandas
Matplotlib
Seaborn
All are listed in requirements.txt.

---

## Use Case

This project helps microfinance institutions, logistics providers, and supply chain analysts:
Assess environmental impact
Report emissions across activities
Improve sustainability decisions

---

## License

This project is open-source and licensed under the MIT License.