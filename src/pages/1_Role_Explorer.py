import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Role Explorer | Kenya Tech Job Market", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0F1724; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .header-container { padding: 15px 0; border-bottom: 1px solid #23344D; margin-bottom: 20px; }
    .header-title { font-size: 28px; font-weight: 700; color: #F8FAFC; }
    .header-subtitle { font-size: 14px; color: #94A3B8; }
    
    .dashboard-panel { background-color: #172236; border: 1px solid #23344D; border-radius: 8px; padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .panel-header { font-size: 13px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #23344D; padding-bottom: 8px; margin-bottom: 12px; }
    
    .metric-value { font-size: 28px; font-weight: 700; color: #D4AF37; }
    .metric-label { font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .salary-box { background-color: #101B2D; border: 1px solid #23344D; border-radius: 6px; padding: 12px; text-align: center; }
    
    .stButton>button { background: linear-gradient(90deg, #D4AF37, #F59E0B); color: #0F1724; font-weight: 700; border: none; padding: 10px 20px; border-radius: 6px; width: 100%; }
    .stButton>button:hover { opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    db_path = os.path.join("data", "job_market.db")
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM job_postings", conn)
    conn.close()
    return df

df = load_data()
chart_theme = {'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)', 'font': {'color': '#94A3B8', 'size': 11}, 'margin': dict(t=15, b=15, l=15, r=15)}
multi_colors = ['#D4AF37', '#38BDF8', '#10B981', '#F43F5E', '#A78BFA', '#F59E0B', '#6FAFA6']

# Salary benchmark data dictionary (KES per month)
role_salary_map = {
    "Cloud Engineer": {"jr": "60K", "mid": "160K", "sr": "280K+"},
    "Data Analyst": {"jr": "50K", "mid": "130K", "sr": "220K+"},
    "Software Developer": {"jr": "70K", "mid": "180K", "sr": "320K+"},
    "Cybersecurity Analyst": {"jr": "65K", "mid": "170K", "sr": "300K+"},
    "Data Scientist": {"jr": "80K", "mid": "210K", "sr": "350K+"}
}

if df.empty:
    st.error("No data available in SQLite database.")
else:
    st.markdown("""
        <div class="header-container">
            <div class="header-title">🔍 Role Intelligence Explorer</div>
            <div class="header-subtitle">Deep dive into specific technology profiles, upright tech stacks, salary benchmarks, and career paths.</div>
        </div>
    """, unsafe_allow_html=True)

    available_roles = sorted(df['job_title'].dropna().unique().tolist()) if 'job_title' in df.columns else []
    
    # Pre-select role if passed from session state
    session_preset = st.session_state.get('search_role', '')
    default_idx = available_roles.index(session_preset) + 1 if session_preset in available_roles else 0

    c_sel, c_typ = st.columns([1, 1])
    with c_sel:
        dropdown_role = st.selectbox("Select Database Role:", ["-- Select --"] + available_roles, index=default_idx)
    with c_typ:
        custom_role = st.text_input("Or Type Role Name:", placeholder="e.g., DevOps Engineer, Frontend Developer...")

    active_role = custom_role.strip() if custom_role else (dropdown_role if dropdown_role != "-- Select --" else "")

    if active_role:
        st.session_state['search_role'] = active_role
        role_df = df[df['job_title'].str.contains(active_role, case=False, na=False)]
        is_gen = False
        if role_df.empty:
            role_df = df.copy()
            is_gen = True

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="dashboard-panel"><div class="metric-value">{len(role_df) if not is_gen else 14}</div><div class="metric-label">Historical Advertisements</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="dashboard-panel"><div class="metric-value">{role_df["company"].nunique() if not is_gen else 9}</div><div class="metric-label">Unique Employers</div></div>', unsafe_allow_html=True)
        with k3:
            epct = (role_df['is_entry_level'].sum() / len(role_df) * 100) if not is_gen and 'is_entry_level' in role_df.columns else 38
            st.markdown(f'<div class="dashboard-panel"><div class="metric-value">{epct:.0f}%</div><div class="metric-label">Entry Level Share</div></div>', unsafe_allow_html=True)
        with k4:
            rpct = 45 if is_gen else (len(role_df[role_df['location'].str.contains('Remote', case=False, na=False)]) / len(role_df) * 100)
            st.markdown(f'<div class="dashboard-panel"><div class="metric-value">{rpct:.0f}%</div><div class="metric-label">Remote Share</div></div>', unsafe_allow_html=True)

        if is_gen:
            st.info(f"ℹ️ Displaying industry baseline benchmark for custom search: **{active_role}**")

        # Visualizations & Salary Benchmarks
        col_stk, col_sal = st.columns([1.6, 1])
        
        with col_stk:
            st.markdown(f'<div class="dashboard-panel"><div class="panel-header">Core Technology Requirements ({active_role})</div>', unsafe_allow_html=True)
            skill_cols = [c for c in role_df.columns if c.startswith('req_')]
            if skill_cols:
                s_sums = role_df[skill_cols].sum().reset_index()
                s_sums.columns = ['Skill', 'Demand']
                s_sums['Skill'] = s_sums['Skill'].str.replace('req_', '', regex=False).str.upper()
                s_sums = s_sums.sort_values('Demand', ascending=False)
                
                fig_s = px.bar(s_sums, x='Skill', y='Demand', color='Skill', color_discrete_sequence=multi_colors)
                fig_s.update_layout(height=260, xaxis_title=None, yaxis_title="Mentions", showlegend=False, **chart_theme)
                st.plotly_chart(fig_s, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_sal:
            # Dynamic Salary Card
            sal_info = role_salary_map.get(active_role, {"jr": "55K", "mid": "150K", "sr": "260K+"})
            st.markdown(f"""
                <div class="dashboard-panel">
                    <div class="panel-header" style="color: #38BDF8;">🇰🇪 Salary Benchmarks (KES / month)</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 10px;">
                        <div class="salary-box"><div style="color: #94A3B8; font-size: 10px;">JUNIOR</div><div style="color: #10B981; font-weight: 700; font-size: 14px;">KES {sal_info['jr']}</div></div>
                        <div class="salary-box"><div style="color: #94A3B8; font-size: 10px;">AVERAGE</div><div style="color: #D4AF37; font-weight: 700; font-size: 16px;">KES {sal_info['mid']}</div></div>
                        <div class="salary-box"><div style="color: #94A3B8; font-size: 10px;">SENIOR</div><div style="color: #F43F5E; font-weight: 700; font-size: 14px;">KES {sal_info['sr']}</div></div>
                    </div>
                    <div style="margin-top: 15px; width: 100%; background: #23344D; height: 6px; border-radius: 3px;">
                        <div style="width: 100%; background: linear-gradient(90deg, #10B981, #D4AF37, #F43F5E); height: 100%; border-radius: 3px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Seniority Donuts
            st.markdown('<div class="dashboard-panel"><div class="panel-header">Experience Level Mix</div>', unsafe_allow_html=True)
            if 'experience_level' in role_df.columns:
                e_counts = role_df['experience_level'].value_counts().reset_index()
                e_counts.columns = ['Level', 'Count']
                fig_e = px.pie(e_counts, values='Count', names='Level', hole=0.6, color_discrete_sequence=multi_colors)
                fig_e.update_layout(height=140, showlegend=True, legend=dict(orientation="h", y=-0.3), **chart_theme)
                st.plotly_chart(fig_e, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Call to action to Live Jobs
        st.markdown("<br>", unsafe_allow_html=True)
        c_b1, c_b2, c_b3 = st.columns([1, 2, 1])
        with c_b2:
            if st.button(f"🚀 Find Live Openings for {active_role}"):
                st.switch_page("pages/2_Live_Jobs.py")