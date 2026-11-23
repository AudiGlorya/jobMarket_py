import streamlit as st

st.set_page_config(page_title="About & Methodology | Kenya Tech Job Market", page_icon="ℹ️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0F1724; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .header-container { padding: 15px 0; border-bottom: 1px solid #23344D; margin-bottom: 20px; }
    .header-title { font-size: 28px; font-weight: 700; color: #F8FAFC; }
    .header-subtitle { font-size: 14px; color: #94A3B8; }
    .about-panel { background-color: #172236; border: 1px solid #23344D; border-radius: 8px; padding: 22px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .panel-title { font-size: 17px; font-weight: 700; color: #D4AF37; margin-bottom: 10px; }
    .tech-pill { background-color: #101B2D; color: #38BDF8; padding: 5px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid #23344D; display: inline-block; margin-right: 6px; margin-bottom: 6px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
        <div class="header-title">ℹ️ Technical Methodology & Governance</div>
        <div class="header-subtitle">In-depth overview of sample collection, architecture, data ethics, and engineering standards.</div>
    </div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
        <div class="about-panel">
            <div class="panel-title">🎯 Vision & Objective</div>
            <p style="color: #94A3B8; font-size: 13px; line-height: 1.6;">
                The <b>Kenya Tech Job Market Intelligence Platform</b> synthesizes complex labor-market indicators into accessible career analytics. It tracks emerging technology requirements, regional tech hub concentrations (such as Nairobi's Silicon Savannah), and compensation patterns across East Africa.
            </p>
        </div>
        
        <div class="about-panel">
            <div class="panel-title">🔄 Dual Engine Architecture</div>
            <p style="color: #94A3B8; font-size: 13px; line-height: 1.6;">
                The platform relies on two completely distinct data flows:
            </p>
            <ul style="color: #94A3B8; font-size: 13px; line-height: 1.6;">
                <li><b>Flow A (Historical Market Analytics):</b> Data pipeline storing listings into an SQLite database (<code>job_market.db</code>) to power cross-role trendlines, geographic mapping, and tech stack histograms.</li>
                <li><b>Flow B (Live Job Search):</b> Real-time external queries targeting approved public REST APIs (Remotive API) for direct candidate application links.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="about-panel">
            <div class="panel-title">🛡️ Data Ethics & Boundaries</div>
            <ul style="color: #94A3B8; font-size: 13px; line-height: 1.6;">
                <li><b>Bounded Sampling:</b> Figures represent analyzed job post samples across Kenya rather than an exhaustive national census.</li>
                <li><b>Skill Mention Analysis:</b> High frequency counts reflect employer text phrasing patterns. Lack of a skill tag does not imply it is unnecessary for the role.</li>
                <li><b>API Compliance:</b> All external query procedures operate strictly within public API parameters without automated scraping.</li>
            </ul>
        </div>
        
        <div class="about-panel">
            <div class="panel-title">🛠️ Software Tech Stack</div>
            <div style="margin-top: 10px;">
                <span class="tech-pill">Python 3.12</span>
                <span class="tech-pill">Streamlit Multi-Page</span>
                <span class="tech-pill">Plotly 7.1 Express</span>
                <span class="tech-pill">SQLite 3 Engine</span>
                <span class="tech-pill">Pandas Dataframes</span>
                <span class="tech-pill">Remotive REST API</span>
            </div>
        </div>
    """, unsafe_allow_html=True)