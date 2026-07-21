import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Blinkit Dashboard", layout="wide")

st.title("🛒 Blinkit Dashboard")
st.markdown("---")

# ============================================
# LOAD DATA FROM GITHUB RAW URLs
# ============================================
@st.cache_data
def load_data():
    # GitHub raw base URL (change username if different)
    base = "https://raw.githubusercontent.com/Lingampellysandhyarani/blinkit-dashboard/main/data/"
    
    # Load all CSV files from GitHub
    df = pd.read_csv(base + "BlinkIT%20Grocery%20Data.csv")
    items = pd.read_csv(base + "Items.csv")
    items_content = pd.read_csv(base + "Items%20Content.csv")
    outlet_info = pd.read_csv(base + "Outlet%20Info.csv")
    outlet_location = pd.read_csv(base + "Outlet%20Location.csv")
    
    # Map fat content
    fat_map = {1: 'Regular', 2: 'Low Fat'}
    df['Fat Content'] = df['ItemContentKey'].map(fat_map)
    
    # Merge tables
    df = df.merge(items, on='ItemKey', how='left')
    df = df.merge(outlet_info, on='OutletKey', how='left')
    df = df.merge(outlet_location, on='OutletLocationKey', how='left')
    
    # Create calculated columns
    df['Years of Operation'] = 2026 - df['Outlet Establishment Year']
    
    return df

# Load data
df = load_data()

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
    avg_sales = total_sales / unique_outlets if unique_outlets > 0 else 0
    st.metric("🏪 Avg Sales/Outlet", f"${avg_sales/1000:.2f}K")

st.markdown("---")

# ============================================
# CHARTS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Fat Content Distribution")
    fat_dist = df.groupby('Fat Content')['Sales'].sum().reset_index()
    if not fat_dist.empty:
        fig = px.pie(fat_dist, values='Sales', names='Fat Content', hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Sales by Item Type")
    item_sales = df.groupby('Item Type')['Sales'].sum().sort_values(ascending=False).reset_index()
    if not item_sales.empty:
        fig = px.bar(item_sales.head(10), x='Sales', y='Item Type', orientation='h')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# OUTLET CHARTS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Outlet Size")
    size_sales = df.groupby('Outlet Size')['Sales'].sum().reset_index()
    if not size_sales.empty:
        fig = px.bar(size_sales, x='Outlet Size', y='Sales')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏙️ Outlet Location")
    loc_sales = df.groupby('Outlet Location Type')['Sales'].sum().reset_index()
    if not loc_sales.empty:
        fig = px.bar(loc_sales, x='Outlet Location Type', y='Sales')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# OUTLET TYPE TABLE
# ============================================
st.subheader("📋 Outlet Type Summary")
outlet_table = df.groupby('Outlet Type').agg({
    'Sales': 'sum',
    'Item Identifier': 'count',
    'Rating': 'mean'
}).reset_index()
outlet_table.columns = ['Outlet Type', 'Total Sales', 'Items', 'Avg Rating']

if not outlet_table.empty:
    outlet_table['Total Sales'] = outlet_table['Total Sales'].apply(lambda x: f"${x:,.0f}")
    outlet_table['Avg Rating'] = outlet_table['Avg Rating'].apply(lambda x: f"{x:.2f}")
    st.dataframe(outlet_table, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>🛒 Blinkit Dashboard | Data Analytics Project | Built with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
