# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(page_title="Startup Funding Dashboard", layout="wide", initial_sidebar_state="expanded")

# ------------------------ Utility functions ------------------------
@st.cache_data
def load_data(path="cleaned_startup_project.csv"):
    df = pd.read_csv(path, encoding="latin1")
    return df

def clean_amount(col):
    # convert amounts like "650,000" or "USD 650000" to numeric
    if col.dtype == object:
        s = col.astype(str).str.replace(r'[^\d.]', '', regex=True)
        s = s.replace('', np.nan)
        return pd.to_numeric(s, errors='coerce')
    else:
        return pd.to_numeric(col, errors='coerce')

def get_download_link_df(df, filename="data.csv"):
    towrite = io.BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    return towrite

def get_excel_bytes(df):
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="filtered")
        writer.save()
    towrite.seek(0)
    return towrite

def export_markdown(df, title="Startup Funding Snapshot"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"# {title}\n\nGenerated: {now}\n\n"
    md += f"## Top 10 Startups by Funding (Filtered)\n\n"
    top = df.groupby('Startup Name', dropna=True)['Amount in USD'].sum().nlargest(10)
    md += top.reset_index().to_markdown(index=False) + "\n\n"
    md += "## Summary Table (first 20 rows)\n\n"
    md += df.head(20).to_markdown(index=False)
    return md.encode('utf-8')

# ------------------------ Load dataset ------------------------
try:
    df_raw = load_data()
except FileNotFoundError:
    st.error("CSV file not found. Please place `cleaned_startup_project.csv` in the app folder.")
    st.stop()

df = df_raw.copy()

# ------------------------ Basic cleaning ------------------------
# Normalizing column names (helpful if names differ slightly)
df.columns = [c.strip() for c in df.columns]

# Ensure required columns exist; create placeholders if not
if 'Amount in USD' not in df.columns:
    df['Amount in USD'] = np.nan

if 'Year' not in df.columns:
    # try to extract year from a 'Date' column
    if 'Date' in df.columns:
        try:
            df['Year'] = pd.to_datetime(df['Date'], errors='coerce').dt.year
        except Exception:
            df['Year'] = np.nan
    else:
        df['Year'] = np.nan

# Clean numeric amount
df['Amount in USD'] = clean_amount(df['Amount in USD'])

# Year -> int where possible
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

# Fill or normalize city column
city_col = None
for candidate in ['City location', 'City', 'Location', 'Headquarters']:
    if candidate in df.columns:
        city_col = candidate
        break
if city_col is None:
    df['City location'] = np.nan
    city_col = 'City location'
else:
    df.rename(columns={city_col: 'City location'}, inplace=True)
    city_col = 'City location'

# Optional lat/lon columns
has_geo = ('Latitude' in df.columns and 'Longitude' in df.columns)

# ------------------------ Sidebar controls ------------------------
with st.sidebar:
    st.title("Filters & Options")
    # Theme toggle
    theme = st.selectbox("Theme", options=["Light", "Dark"], index=0)
    if theme == "Dark":
        st.markdown(
            """
            <style>
            .reportview-container, .main {background-color: #0e1117;}
            .stButton>button {background-color: #262730; color: white;}
            </style>
            """, unsafe_allow_html=True
        )

    # Background image upload
    bg_file = st.file_uploader("Upload background image (optional)", type=["png", "jpg", "jpeg"])
    if bg_file:
        data = bg_file.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: cover;
                background-position: center;
            }}
            </style>
            """, unsafe_allow_html=True)

    # Filters
    st.markdown("---")
    years = sorted(df['Year'].dropna().unique().astype(str).tolist())
    selected_years = st.multiselect("Year", options=years, default=years if years else None)

    cities = sorted(df['City location'].dropna().unique().tolist())
    selected_cities = st.multiselect("City", options=cities, default=None)

    industries = []
    if 'Industry Vertical' in df.columns:
        industries = sorted(df['Industry Vertical'].dropna().unique().tolist())
    selected_industries = st.multiselect("Industry Vertical", options=industries, default=None)

    investors = []
    if 'Investors Name' in df.columns:
        investors = sorted(df['Investors Name'].dropna().unique().tolist())
    selected_investors = st.multiselect("Investor", options=investors, default=None)

    round_options = []
    if 'Funding Round' in df.columns:
        round_options = sorted(df['Funding Round'].dropna().unique().tolist())
    selected_rounds = st.multiselect("Funding Round", options=round_options, default=None)

    st.markdown("---")
    st.caption("Export & Deploy")
    st.markdown("**Deployment tips**\n\n1. Push this repo to GitHub.\n2. Link it in Streamlit Cloud and set `cleaned_startup_project.csv` in repo.\n3. Add secrets if you use Mapbox tokens.\n\n")

# ------------------------ Apply filters ------------------------
filtered = df.copy()

if selected_years:
    # convert to numeric list
    years_sel = [int(y) for y in selected_years]
    filtered = filtered[filtered['Year'].isin(years_sel)]

if selected_cities:
    filtered = filtered[filtered['City location'].isin(selected_cities)]

if selected_industries:
    filtered = filtered[filtered['Industry Vertical'].isin(selected_industries)]

if selected_investors:
    filtered = filtered[filtered['Investors Name'].isin(selected_investors)]

if selected_rounds:
    filtered = filtered[filtered['Funding Round'].isin(selected_rounds)]

# ------------------------ Top row metrics ------------------------
st.title("🚀 Startup Funding Analysis")
left, mid, right = st.columns(3)

total_funding = filtered['Amount in USD'].sum(min_count=1)
startup_count = filtered['Startup Name'].nunique() if 'Startup Name' in filtered.columns else filtered.shape[0]
avg_ticket = (filtered['Amount in USD'].mean()) if not filtered['Amount in USD'].isna().all() else np.nan
top_city = (filtered.groupby('City location')['Amount in USD'].sum().idxmax()) if not filtered['Amount in USD'].isna().all() else "N/A"

left.metric("Total Funding (USD)", f"{total_funding:,.0f}" if not np.isnan(total_funding) else "N/A")
mid.metric("Number of Startups", f"{startup_count}")
right.metric("Average Ticket (USD)", f"{avg_ticket:,.0f}" if not np.isnan(avg_ticket) else "N/A")

st.markdown("---")

# ------------------------ Layout: charts ------------------------
col1, col2 = st.columns([2,1])

with col1:
    # Top funded startups
    st.subheader("Top 10 Funded Startups")
    if 'Startup Name' in filtered.columns:
        top = filtered.groupby('Startup Name', dropna=True)['Amount in USD'].sum().nlargest(10).reset_index()
        if not top.empty:
            fig = px.bar(top.sort_values('Amount in USD'), x='Amount in USD', y='Startup Name', orientation='h',
                         title="Top 10 Funded Startups", labels={'Amount in USD':'Total Funding (USD)'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No funding data available for selected filters.")
    else:
        st.info("No 'Startup Name' column in dataset.")

    st.markdown("---")

    # Funding over years
    st.subheader("Funding Over Years")
    if 'Year' in filtered.columns:
        by_year = filtered.groupby('Year', dropna=True)['Amount in USD'].sum().reset_index().sort_values('Year')
        if not by_year.empty:
            fig2 = px.line(by_year, x='Year', y='Amount in USD', markers=True, title="Total Funding by Year")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Not enough year/funding data to plot.")
    else:
        st.info("No 'Year' column in dataset.")

    st.markdown("---")

    # Industry treemap
    st.subheader("Industry Treemap (Top 20)")
    if 'Industry Vertical' in filtered.columns:
        treemap = filtered.groupby('Industry Vertical', dropna=True)['Amount in USD'].sum().nlargest(20).reset_index()
        if not treemap.empty:
            fig3 = px.treemap(treemap, path=['Industry Vertical'], values='Amount in USD', title="Top Industries by Funding")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No industry funding data to show.")
    else:
        st.info("No 'Industry Vertical' column found.")

with col2:
    st.subheader("Top Cities by Funding Count")
    city_counts = filtered['City location'].value_counts().nlargest(10).reset_index()
    city_counts.columns = ['City', 'Fundings']
    if not city_counts.empty:
        figc = px.bar(city_counts, x='Fundings', y='City', orientation='h', title="Cities with Most Funding Rounds")
        st.plotly_chart(figc, use_container_width=True)
    else:
        st.info("No city data to show.")

    st.markdown("---")
    st.subheader("Summary Table (sample)")
    st.dataframe(filtered.head(20), use_container_width=True)

st.markdown("---")

# ------------------------ Map (if geo available) ------------------------
st.subheader("Funding Map (requires Latitude & Longitude columns)")
if has_geo:
    geo = filtered.dropna(subset=['Latitude', 'Longitude'])
    if not geo.empty:
        fig_map = px.scatter_geo(geo, lon="Longitude", lat="Latitude", hover_name="Startup Name",
                                 size="Amount in USD", projection="natural earth",
                                 title="Geographical Distribution of Funding (size ~ amount)")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No rows with both Latitude and Longitude after filtering.")
else:
    st.info("Latitude/Longitude columns not found. If you want a map, add 'Latitude' and 'Longitude' columns to the CSV.")

st.markdown("---")

# ------------------------ Downloads & report export ------------------------
st.subheader("Export Filtered Data / Report")

col_a, col_b, col_c = st.columns(3)
with col_a:
    csv_bytes = get_download_link_df(filtered)
    st.download_button(label="📥 Download CSV", data=csv_bytes, file_name="filtered_startups.csv", mime="text/csv")
with col_b:
    xls_bytes = get_excel_bytes(filtered)
    st.download_button(label="📥 Download Excel", data=xls_bytes, file_name="filtered_startups.xlsx", mime="application/vnd.ms-excel")
with col_c:
    md = export_markdown(filtered)
    st.download_button("📄 Download Snapshot (Markdown)", data=md, file_name="startup_snapshot.md", mime="text/markdown")

st.markdown("---")
st.caption("Made by **ViJay** — Full feature Streamlit dashboard. Customize further on request.")
