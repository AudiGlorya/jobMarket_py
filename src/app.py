import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Kenya Tech Job Market", page_icon="🇰🇪", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0F1724; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .search-container { text-align: center; padding: 25px 0 15px 0; }
    .search-title { font-size: 30px; font-weight: 700; color: #F8FAFC; margin-bottom: 5px; }
    .search-subtitle { font-size: 14px; color: #94A3B8; margin-bottom: 20px; }
    .dashboard-panel { background-color: #172236; border: 1px solid #23344D; border-radius: 8px; padding: 18px; margin-bottom: 15px; }
    .panel-header { font-size: 13px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #23344D; padding-bottom: 8px; margin-bottom: 12px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap:10px; }
    .kpi-card { text-align: center; padding: 14px 8px; background-color: #101B2D; border: 1px solid #23344D; border-radius: 6px; }
    .kpi-value { font-size: 22px; font-weight: 700; color: #D4AF37; }
    .kpi-label { font-size: 10px; color: #64748B; text-transform: uppercase; margin-top: 4px; }
    div[role="radiogroup"] { justify-content: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Cache removed to guarantee fresh data from the database
def load_data():
    db_path = os.path.join("data", "job_market.db")
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM job_postings", conn)
            if 'date_posted' in df.columns:
                df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce').fillna(pd.Timestamp.now())
            return df
    return pd.DataFrame()

df = load_data()
chart_theme = {'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)', 'font': {'color': '#94A3B8', 'size': 11}, 'margin': dict(t=10, b=20, l=10, r=10)}
colors = ['#D4AF37', '#38BDF8', '#10B981', '#F43F5E', '#A78BFA', '#F59E0B']

if df.empty:
    st.error("Database is empty. Please run data_collection.py, data_cleaning.py, feature_engineering.py, and load_to_sqlite.py")
else:
    # Top Hero Section
    st.markdown("""
        <div class="search-container">
            <div class="search-title">Kenya Tech Job Market Intelligence</div>
            <div class="search-subtitle">Real-time labor dynamics, technology stacks, and career insights across Kenya's Silicon Savannah and Global Remote spaces.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Dual-Source Filter Toggle
    scope_filter = st.radio("Market Scope", options=["All Jobs", "Kenya (Local)", "International (Remote)"], horizontal=True, label_visibility="collapsed")
    
    # Filter the Dataframe
    filtered_df = df.copy()
    if scope_filter == "Kenya (Local)":
        filtered_df = filtered_df[filtered_df.get('job_scope', '') == 'Local']
    elif scope_filter == "International (Remote)":
        filtered_df = filtered_df[filtered_df.get('job_scope', '') == 'International - Remote']
        
    st.markdown("<hr style='border: 1px solid #23344D; margin: 5px 0 20px 0;'>", unsafe_allow_html=True)

    # Row 1: KPIs
    st.markdown('<div class="dashboard-panel"><div class="panel-header">Macro Market Indicators</div>', unsafe_allow_html=True)
    total_jobs = len(filtered_df)
    unique_employers = filtered_df['company'].nunique() if 'company' in filtered_df.columns else 0
    entry_pct = (filtered_df['is_entry_level'].sum() / total_jobs * 100) if 'is_entry_level' in filtered_df.columns and total_jobs > 0 else 0
    remote_cnt = len(filtered_df[filtered_df['location'].str.contains('Remote', case=False, na=False)]) if 'location' in filtered_df.columns else 0
    
    st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-value">{total_jobs}</div><div class="kpi-label">Active Postings</div></div>
            <div class="kpi-card"><div class="kpi-value">{unique_employers}</div><div class="kpi-label">Hiring Companies</div></div>
            <div class="kpi-card"><div class="kpi-value">{entry_pct:.0f}%</div><div class="kpi-label">Entry/Junior Roles</div></div>
            <div class="kpi-card"><div class="kpi-value">{remote_cnt}</div><div class="kpi-label">Remote / Hybrid</div></div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Trends and Roles Distribution
    col_tr, col_rd = st.columns([2, 1.2])
    with col_tr:
        st.markdown('<div class="dashboard-panel"><div class="panel-header">Real-Time Demand Trends</div>', unsafe_allow_html=True)
        if 'job_title' in filtered_df.columns and 'date_posted' in filtered_df.columns and not filtered_df.empty:
            trend_df = filtered_df.groupby(filtered_df['date_posted'].dt.date).size().reset_index(name='Postings')
            fig_tr = px.line(trend_df, x='date_posted', y='Postings', markers=True, color_discrete_sequence=['#38BDF8'])
            fig_tr.update_layout(height=220, xaxis_title=None, yaxis_title=None, **chart_theme)
            st.plotly_chart(fig_tr, use_container_width=True)
        else:
            st.info("Insufficient timeline data to map trends.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_rd:
        st.markdown('<div class="dashboard-panel"><div class="panel-header">Top Job Categories</div>', unsafe_allow_html=True)
        if 'job_title' in filtered_df.columns and not filtered_df.empty:
            title_counts = filtered_df['job_title'].value_counts().head(5).reset_index()
            title_counts.columns = ['Role', 'Count']
            fig_exp = px.pie(title_counts, values='Count', names='Role', hole=0.6, color_discrete_sequence=colors)
            fig_exp.update_layout(height=220, showlegend=False, **chart_theme)
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.info("Insufficient role data.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 3: Skills, Top Employers, Geographic Distribution
    col_sk, col_emp, col_mp = st.columns([1, 1, 1.2])
    
    with col_sk:
        st.markdown('<div class="dashboard-panel"><div class="panel-header">Top Tech Stack Demand</div>', unsafe_allow_html=True)
        skill_cols = [c for c in filtered_df.columns if c.startswith('req_')]
        if skill_cols and not filtered_df[skill_cols].sum().sum() == 0:
            s_df = filtered_df[skill_cols].sum().reset_index()
            s_df.columns = ['Skill', 'Count']
            s_df['Skill'] = s_df['Skill'].str.replace('req_', '', regex=False).str.upper()
            s_df = s_df[s_df['Count'] > 0].sort_values('Count', ascending=True).tail(5) # Only show skills > 0
            if not s_df.empty:
                fig_s = px.bar(s_df, x='Count', y='Skill', orientation='h', color_discrete_sequence=['#38BDF8'])
                fig_s.update_layout(height=240, xaxis_title=None, yaxis_title=None, **chart_theme)
                st.plotly_chart(fig_s, use_container_width=True)
            else:
                st.info("No matching tech stack skills found in these jobs.")
        else:
            st.info("Tech stack engineering pending ETL update.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_emp:
        st.markdown('<div class="dashboard-panel"><div class="panel-header">Top Hiring Companies</div>', unsafe_allow_html=True)
        if 'company' in filtered_df.columns and not filtered_df.empty:
            c_df = filtered_df['company'].value_counts().head(5).reset_index()
            c_df.columns = ['Company', 'Postings']
            fig_c = px.bar(c_df, x='Postings', y='Company', orientation='h', color_discrete_sequence=['#D4AF37'])
            fig_c.update_layout(height=240, yaxis={'categoryorder':'total ascending'}, xaxis_title=None, yaxis_title=None, **chart_theme)
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.info("Insufficient company data.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_mp:
        st.markdown('<div class="dashboard-panel"><div class="panel-header">Geographic Distribution</div>', unsafe_allow_html=True)
        geo_map = {
            'Nairobi': {'lat': -1.2921, 'lon': 36.8219}, 
            'Mombasa':{'lat': -4.0435, 'lon': 39.6682}, 
            'Kenya': {'lat': -0.0236, 'lon': 37.9062},
            'Remote': {'lat': 25.0, 'lon': -40.0} 
        }
        
        if 'location' in filtered_df.columns and not filtered_df.empty:
            l_df = filtered_df['location'].value_counts().reset_index()
            l_df.columns = ['Location', 'Postings']
            l_df['lat'] = l_df['Location'].map(lambda x: geo_map.get(x, {}).get('lat', None))
            l_df['lon'] = l_df['Location'].map(lambda x: geo_map.get(x, {}).get('lon', None))
            m_df = l_df.dropna(subset=['lat', 'lon'])
            
            if not m_df.empty:
                map_zoom = 1 if scope_filter != "Kenya (Local)" else 5
                map_center = {"lat": 10.0, "lon": 0.0} if scope_filter != "Kenya (Local)" else {"lat": -0.0236, "lon": 37.9062}
                fig_m = px.scatter_map(m_df, lat="lat", lon="lon", size="Postings", hover_name="Location", color_discrete_sequence=["#10B981"], zoom=map_zoom, center=map_center)
                fig_m.update_layout(map_style="carto-darkmatter", height=240, margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("No recognizable map coordinates.")
        st.markdown('</div>', unsafe_allow_html=True)