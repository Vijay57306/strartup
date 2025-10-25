import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("cleaned_startup_project.csv", encoding='latin1')

st.title("Startup Funding Analysis")

# Show raw data
if st.checkbox("Show Raw Data"):
    st.write(df.head(20))

# Sidebar Filters
st.sidebar.header("Filter Options")

# City Filter
if 'City location' in df.columns:
    selected_city = st.sidebar.multiselect("Select City", df['City location'].dropna().unique())
else:
    selected_city = []

# Industry Filter
if 'Industry Vertical' in df.columns:
    selected_industry = st.sidebar.multiselect("Select Industry", df['Industry Vertical'].dropna().unique())
else:
    selected_industry = []

# Year Filter
if 'Year' in df.columns:
    selected_year = st.sidebar.multiselect("Select Year", sorted(df['Year'].dropna().unique()))
else:
    selected_year = []

# Apply Filtering
filtered_df = df.copy()

if selected_city:
    filtered_df = filtered_df[filtered_df['City location'].isin(selected_city)]
if selected_industry:
    filtered_df = filtered_df[filtered_df['Industry Vertical'].isin(selected_industry)]
if selected_year:
    filtered_df = filtered_df[filtered_df['Year'].isin(selected_year)]

st.subheader("Filtered Data")
st.dataframe(filtered_df.head(20))

# ✅ Visual 1: Top Funded Startups
st.subheader("Top 10 Funded Startups")
if 'Startup Name' in filtered_df.columns and 'Amount in USD' in filtered_df.columns:
    top_funded = filtered_df.groupby('Startup Name')['Amount in USD'].sum().nlargest(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=top_funded.values, y=top_funded.index, ax=ax1)
    ax1.set_title("Top 10 Funded Startups")
    st.pyplot(fig1)
else:
    st.warning("Required columns missing for this chart.")

# ✅ Visual 2: Funding Over Years
st.subheader("Funding Over the Years")
if 'Year' in filtered_df.columns and 'Amount in USD' in filtered_df.columns:
    year_data = filtered_df.groupby('Year')['Amount in USD'].sum()
    fig2, ax2 = plt.subplots()
    sns.lineplot(x=year_data.index, y=year_data.values, marker="o", ax=ax2)
    ax2.set_title("Total Funding by Year")
    st.pyplot(fig2)
else:
    st.warning("Required columns missing for this chart.")

# ✅ Visual 3: Top Cities by Funding Count
st.subheader("Top Cities by Funding Count")
if 'City location' in filtered_df.columns:
    city_counts = filtered_df['City location'].value_counts().nlargest(10)
    fig3, ax3 = plt.subplots()
    sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax3)
    ax3.set_title("Top 10 Cities by Funding Count")
    st.pyplot(fig3)
else:
    st.warning("City location column not found.")

# ✅ Visual 4: Industry Wise Funding
st.subheader("Industry Wise Funding")
if 'Industry Vertical' in filtered_df.columns and 'Amount in USD' in filtered_df.columns:
    industry_funding = filtered_df.groupby('Industry Vertical')['Amount in USD'].sum().nlargest(10)
    fig4, ax4 = plt.subplots()
    sns.barplot(x=industry_funding.values, y=industry_funding.index, ax=ax4)
    ax4.set_title("Top 10 Funded Industries")
    st.pyplot(fig4)

st.markdown("---")
st.markdown("✅ Developed by Vi Jay | Startup Data Visualization")
