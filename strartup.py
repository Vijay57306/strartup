import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 🌙 Dark Theme Setup
# -----------------------------
plt.style.use("dark_background")
sns.set_theme(style="darkgrid")

# -----------------------------
# 📄 Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="startup data", layout="wide")

# -----------------------------
# 🚢 Page Title
# -----------------------------
st.title("Startup data project")

# -----------------------------
# 📊 Load Dataset
# -----------------------------
df = pd.read_csv("cleaned Startup_project.csv")

# -----------------------------
# 🎚 Sidebar Filters
# -----------------------------
st.sidebar.header("🎚 Filter Options")

Year = st.sidebar.multiselect(
    "Select Year",
    options=df["year"].dropna().unique(),
    default=df["year"].dropna().unique()
)

# -----------------------------
# 🔍 Filter the Data
# -----------------------------
filtered_df = df[
    (df["Year"].isin(Year)) 
    
]

# -----------------------------
# 🧾 Optional: Show Raw Data
# -----------------------------
if st.checkbox("📂 Show Filtered Raw Data"):
    st.dataframe(filtered_df)

# -----------------------------
# 🧪 Preview Table
# -----------------------------
st.subheader("📌 Filtered Data Preview")
st.write(filtered_df.head())

# -----------------------------

# -----------------------------
# ❤ Footer
# -----------------------------
st.markdown("---")
st.markdown("Made with ❤ using Streamlit", unsafe_allow_html=True)