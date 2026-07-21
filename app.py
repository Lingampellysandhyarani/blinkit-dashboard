import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Blinkit Dashboard", layout="wide")

st.title("🛒 Blinkit Dashboard")
st.markdown("---")

# ============================================
# LOAD DATA - SIMPLE VERSION
# ============================================
@st.cache_data
def load_data():
    # Load ONLY the main data file
    df = pd.read_csv('data/BlinkIT Grocery Data.csv')
    
    # Load dimension tables
    items = pd.read_csv('data/Items.csv')
    fat = pd.read_csv('data/Items Content.csv')
    outlets = pd.read_csv('data/Outlet Info.csv')
    location = pd.read_csv('data/Outlet Location.csv')
    
    # Simple merge - no complex joins
    df = df.merge(items, on='ItemKey', how='left')
    
    # Add Fat Content
    fat_map = {1: 'Regular', 2: 'Low Fat'}
    df['Fat Content'] = df['ItemContentKey'].map(fat_map)
    
    # Add Outlet Info
    df = df.merge(outlets, on='OutletKey', how='left')
    df = df.merge(location, on='OutletLocationKey', how='left')
    
    return df

df = load_data()

# ============================================
# SHOW DATA INFO (TO VERIFY)
# ============================================
st.write(f"✅ Total Rows: {len(df):,}")
st.write(f"✅ Total Sales: ${df['Sales'].sum():,.2f}")
st.write(f"✅ Unique Outlets: {df['OutletKey'].nunique()}")

st.markdown("---")

# ============================================
# KPI CARDS
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = df['Sales'].sum()
    st.metric("💰 Total Sales", f"${total_sales/1e6:.2f}M")

with col2:
    avg_rating = df['Rating'].mean()
    st.metric("⭐ Avg Rating", f"{avg_rating:.2f}")

with col3:
    total_items = len(df)
    st.metric("📦 Total Items", f"{total_items/1000:.0f}K")

with col4:
    unique_outlets = df['OutletKey'].nunique()
    avg_sales = total_sales / unique_outlets
    st.metric("🏪 Avg Sales/Outlet", f"${avg_sales/1000:.2f}K")

st.markdown("---")

# ============================================
# CHARTS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Fat Content")
    fat_data = df.groupby('Fat Content')['Sales'].sum().reset_index()
    fig = px.pie(fat_data, values='Sales', names='Fat Content', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Sales by Item Type")
    item_data = df.groupby('Item Type')['Sales'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(item_data.head(10), x='Sales', y='Item Type', orientation='h')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# OUTLET CHARTS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Outlet Size")
    size_data = df.groupby('Outlet Size')['Sales'].sum().reset_index()
    fig = px.bar(size_data, x='Outlet Size', y='Sales')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏙️ Outlet Location")
    loc_data = df.groupby('Outlet Location Type')['Sales'].sum().reset_index()
    fig = px.bar(loc_data, x='Outlet Location Type', y='Sales')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# TABLE
# ============================================
st.subheader("📋 Outlet Type Summary")
outlet_table = df.groupby('Outlet Type').agg({
    'Sales': 'sum',
    'Item Identifier': 'count',
    'Rating': 'mean'
}).reset_index()
outlet_table.columns = ['Outlet Type', 'Total Sales', 'Items', 'Avg Rating']
st.dataframe(outlet_table, use_container_width=True)