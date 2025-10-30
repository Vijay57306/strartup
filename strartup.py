# app.py
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Indian Startup Funding Dashboard", layout="wide")

# -----------------------------------------------
# Sidebar Section
# -----------------------------------------------
st.sidebar.title("📊 Startup Funding Dashboard")
st.sidebar.write("Explore the insights from Indian Startup Dataset")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("Startup_Data.csv")

    # Data cleaning steps
    df.rename(columns={"Date dd/mm/yyyy": "Date", "City  Location": "City location"}, inplace=True)
    df.drop(["Sr No", "Remarks"], axis=1, inplace=True)

    # Convert date to datetime
    df["Date"] = df["Date"].str.replace("05/072018", "05/07/2018")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", dayfirst=True, errors="coerce")
    df.dropna(subset=["Date"], inplace=True)

    # Create year, month, day columns
    df["Year"] = df["Date"].dt.year.astype(int)
    df["Month"] = df["Date"].dt.month.astype(int)
    df["Day"] = df["Date"].dt.day.astype(int)

    # Clean Amount
    df["Amount in USD"] = df["Amount in USD"].str.replace(r"[^\d]", "", regex=True)
    df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
    df["Amount in USD"].fillna(df["Amount in USD"].mean(), inplace=True)
    df["Amount in USD"] = df["Amount in USD"].astype("int64")

    # Clean text columns
    text_cols = ["Startup Name", "City location", "Investors Name", "Industry Vertical"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.replace("xa0|xc2|\\\\", "", regex=True).str.strip()

    return df

df = load_data()

# -----------------------------------------------
# Main Page
# -----------------------------------------------
st.title("🚀 Indian Startup Funding Analysis (2015–2020)")

st.markdown("""
This dashboard explores trends and insights from Indian Startup funding data.
Use the filters in the sidebar to explore data across **cities, industries, and investors**.
""")

# Filters
selected_year = st.sidebar.multiselect("Select Year(s):", sorted(df["Year"].unique()), default=df["Year"].unique())
selected_city = st.sidebar.multiselect("Select City:", sorted(df["City location"].unique()))
selected_industry = st.sidebar.multiselect("Select Industry:", sorted(df["Industry Vertical"].unique()))

filtered_df = df[df["Year"].isin(selected_year)]
if selected_city:
    filtered_df = filtered_df[filtered_df["City location"].isin(selected_city)]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry Vertical"].isin(selected_industry)]

st.write(f"### Showing {len(filtered_df)} records after filtering")

# -----------------------------------------------
# Charts Section
# -----------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Top Cities",
    "🏭 Industry Verticals",
    "💰 Funding Trends",
    "👨‍💼 Top Investors"
])

# --- TAB 1: Top Cities ---
with tab1:
    st.subheader("Top 10 Cities by Total Funding")
    top_c = filtered_df.groupby("City location")["Amount in USD"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_c.values, y=top_c.index, palette="viridis", ax=ax)
    ax.set_xlabel("Total Funding (USD)")
    ax.set_ylabel("City")
    st.pyplot(fig)

# --- TAB 2: Top Industry Verticals ---
with tab2:
    st.subheader("Top 10 Industry Verticals by Number of Startups")
    top_In = filtered_df["Industry Vertical"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_In.values, y=top_In.index, palette="Set2", ax=ax)
    ax.set_xlabel("Number of Startups")
    st.pyplot(fig)

# --- TAB 3: Funding Trends ---
with tab3:
    st.subheader("Funding Trends by Year and Month")
    funding_by_year = filtered_df.groupby("Year")["Amount in USD"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=funding_by_year, x="Year", y="Amount in USD", marker="o", ax=ax)
    ax.set_title("Yearly Funding Trend")
    st.pyplot(fig)

    funding_by_month = filtered_df.groupby("Month")["Amount in USD"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=funding_by_month, x="Month", y="Amount in USD", marker="o", color="green", ax=ax)
    ax.set_title("Monthly Funding Distribution")
    st.pyplot(fig)

# --- TAB 4: Top Investors ---
with tab4:
    st.subheader("Top 10 Investors by Number of Investments")
    top_investors = filtered_df["Investors Name"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_investors.values, y=top_investors.index, palette="Set3", ax=ax)
    ax.set_xlabel("Number of Investments")
    st.pyplot(fig)

# -----------------------------------------------
# Insights Summary
# -----------------------------------------------
st.markdown("## 📈 Key Insights")
st.markdown(f"""
- 💸 **Total Funding (USD):** {round(filtered_df["Amount in USD"].sum()):,}
- 🏙️ **City with Most Funding:** {filtered_df.groupby("City location")["Amount in USD"].sum().idxmax()}
- 🏭 **Top Industry:** {filtered_df["Industry Vertical"].mode()[0]}
- 👨‍💼 **Most Active Investor:** {filtered_df["Investors Name"].mode()[0]}
""")
