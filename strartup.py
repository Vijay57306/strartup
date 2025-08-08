import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the cleaned startup data
df = pd.read_csv("cleaned startup_project", encoding='latin1')  # or utf-8 if needed

# Set Streamlit app title
st.title("Startup Funding Analysis")

# Show raw data
if st.checkbox("Show Raw Data"):
    st.write(df.head(20))

# Filter Options
st.sidebar.header("Filter Options")

selected_city = st.sidebar.multiselect("Select City", options=df['City location'].dropna().unique())
selected_industry = st.sidebar.multiselect("Select Industry", options=df['Industry Vertical'].dropna().unique())
selected_year = st.sidebar.multiselect("Select Year", options=df['Year'].dropna().unique())

filtered_df = df.copy()

if selected_city:
    filtered_df = filtered_df[filtered_df['City'].isin(selected_city)]
if selected_industry:
    filtered_df = filtered_df[filtered_df['Industry Vertical'].isin(selected_industry)]
if selected_year:
    filtered_df = filtered_df[filtered_df['Year'].isin(selected_year)]

st.subheader("Filtered Data")
st.write(filtered_df.head(20))

# --- Visual 1: Top 10 Funded Startups ---
st.subheader("Top 10 Funded Startups")
top_funded = filtered_df.groupby('Startup Name')['Amount in USD'].sum().nlargest(10).sort_values(ascending=True)

fig1, ax1 = plt.subplots()
top_funded.plot(kind='barh', ax=ax1)
ax1.set_xlabel("Total Funding (USD)")
ax1.set_title("Top 10 Funded Startups")
st.pyplot(fig1)

# --- Visual 2: Funding over Years ---
st.subheader("Funding Over the Years")
funding_by_year = filtered_df.groupby('Year')['Amount in USD'].sum()

fig2, ax2 = plt.subplots()
sns.lineplot(x=funding_by_year.index, y=funding_by_year.values, marker="o", ax=ax2)
ax2.set_ylabel("Total Funding (USD)")
ax2.set_title("Total Funding by Year")
st.pyplot(fig2)

# --- Visual 3: Top Cities by Funding Count ---
st.subheader("Top Cities by Funding Count")
city_counts = filtered_df['City'].value_counts().nlargest(10)

fig3, ax3 = plt.subplots()
sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax3)
ax3.set_xlabel("Number of Fundings")
ax3.set_title("Top 10 Cities with Most Funded Startups")
st.pyplot(fig3)

# --- Visual 4: Industry Wise Funding ---
st.subheader("Industry Wise Funding")
industry_funding = filtered_df.groupby('Industry Vertical')['Amount in USD'].sum().nlargest(10)

fig4, ax4 = plt.subplots()
industry_funding.plot(kind='bar', ax=ax4)
ax4.set_ylabel("Total Funding (USD)")
ax4.set_title("Top 10 Funded Industries")
st.pyplot(fig4)

# Footer
st.markdown("---")
st.markdown("✅ **Created by Vi Jay | Cleaned Startup Dataset Visualization**")

