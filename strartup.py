import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🚀 Startup Funding Dashboard", layout="wide")
st.title("🚀 Startup Funding Analysis")

# --- Load Dataset ---
df = pd.read_csv("cleaned startup_project.csv")

# --- Normalize column names (important fix) ---
df.columns = df.columns.str.strip().str.lower()

# Map similar column names
col_map = {
    "city location": "City location",
    "city  location": "City location",
    "city_location": "City location",
    "city location ": "City location",
    "industry vertical": "Industry Vertical",
    "investors name": "Investors Name",
    "startup name": "Startup Name",
    "amount in usd": "Amount in USD",
    "date": "Date",
}
df.rename(columns=col_map, inplace=True)

# --- Clean & Enrich ---
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Amount in USD", "City location", "Startup Name", "Investors Name", "Industry Vertical", "Date"], inplace=True)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# --- Sidebar Filters ---
st.sidebar.header("📍 Filter Options")

city_list = sorted(df["City location"].dropna().unique())
industry_list = sorted(df["Industry Vertical"].dropna().unique())
year_list = sorted(df["Year"].dropna().unique())

selected_cities = st.sidebar.multiselect("Select City(s)", city_list, default=city_list[:5])
selected_industries = st.sidebar.multiselect("Select Industry(s)", industry_list, default=industry_list[:5])
selected_years = st.sidebar.slider("Select Year Range", min_value=int(min(year_list)), max_value=int(max(year_list)), value=(int(min(year_list)), int(max(year_list))))
amount_min = int(df["Amount in USD"].min())
amount_max = int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Funding Amount Range (USD)", min_value=amount_min, max_value=amount_max, value=(amount_min, amount_max))

show_top_10 = st.sidebar.checkbox("Show only Top 10 in charts", value=True)
show_data = st.sidebar.checkbox("📄 Show Data Records", value=True)

# --- Apply Filters ---
filtered_df = df[
    (df["City location"].isin(selected_cities))
    & (df["Industry Vertical"].isin(selected_industries))
    & (df["Year"].between(selected_years[0], selected_years[1]))
    & (df["Amount in USD"].between(amount_range[0], amount_range[1]))
]

# --- Chart Helpers ---
def render_bar_chart(data, x, y, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=data, x=x, y=y, ax=ax)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

def render_line_chart(data, x, y, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(data=data, x=x, y=y, marker="o", ax=ax)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

# --- Data Display ---
st.markdown(f"### 📊 Showing {len(filtered_df)} Records After Filtering")

if show_data:
    st.dataframe(filtered_df, use_container_width=True, height=400)

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Try adjusting filters or column names.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top Funded Startups")
        top_startups = filtered_df.groupby("Startup Name")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_startups = top_startups.head(10)
        render_bar_chart(top_startups.reset_index(), "Amount in USD", "Startup Name", "Top Funded Startups")

    with col2:
        st.subheader("💰 Top Investors")
        top_investors = filtered_df.groupby("Investors Name")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_investors = top_investors.head(10)
        render_bar_chart(top_investors.reset_index(), "Amount in USD", "Investors Name", "Top Investors")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📈 Monthly Funding Trend")
        monthly = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"].sum().reset_index()
        monthly["Date"] = monthly["Date"].astype(str)
        render_line_chart(monthly, "Date", "Amount in USD", "Monthly Funding Trend")

    with col4:
        st.subheader("🏭 Industry Funding")
        top_industry = filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_industry = top_industry.head(10)
        render_bar_chart(top_industry.reset_index(), "Amount in USD", "Industry Vertical", "Funding by Industry")

