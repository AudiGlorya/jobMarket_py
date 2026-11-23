import streamlit as st
import requests
import html

st.set_page_config(page_title="Live Jobs | Kenya Tech Job Market", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0F1724; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #172236; border-right: 1px solid #23344D; }
    
    .header-container { padding: 15px 0; border-bottom: 1px solid #23344D; margin-bottom: 20px; }
    .header-title { font-size: 28px; font-weight: 700; color: #F8FAFC; }
    .header-subtitle { font-size: 14px; color: #94A3B8; }
    
    .job-card { background-color: #172236; border: 1px solid #23344D; border-left: 4px solid #D4AF37; border-radius: 8px; padding: 18px; margin-bottom: 12px; }
    .job-title { font-size: 17px; font-weight: 700; color: #F8FAFC; }
    .job-meta { font-size: 13px; color: #94A3B8; margin: 6px 0 10px 0; }
    .job-badge { background-color: #101B2D; color: #38BDF8; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid #23344D; display: inline-block; margin-right: 5px; }
    .apply-btn { background: linear-gradient(90deg, #D4AF37, #F59E0B); color: #0F1724 !important; font-weight: 700; padding: 6px 16px; border-radius: 6px; text-decoration: none; display: inline-block; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
        <div class="header-title">🌍 Live Online Opportunity Engine</div>
        <div class="header-subtitle">Real-time remote software opportunities fetched via live public API channels.</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='color: #D4AF37; font-size: 16px;'>🔍 Search Parameters</h3>", unsafe_allow_html=True)

# Pre-populate search input if passed from earlier pages
preset_query = st.session_state.get('search_role', 'Python')
search_keyword = st.sidebar.text_input("Role / Tech Stack:", value=preset_query)
job_category = st.sidebar.selectbox("Job Category:", ["All", "Software Development", "Data", "DevOps / SysAdmin", "Customer Support"])
result_limit = st.sidebar.slider("Max Job Cards:", min_value=5, max_value=30, value=12)

st.sidebar.markdown("---")
st.sidebar.caption("Data Source: Remotive API Pipeline")

if search_keyword:
    with st.spinner(f"Retrieving active positions for '{search_keyword}'..."):
        try:
            url = f"https://remotive.com/api/remote-jobs?search={search_keyword}&limit={result_limit}"
            res = requests.get(url, timeout=10)
            
            if res.status_code == 200:
                jobs = res.json().get('jobs', [])
                if job_category != "All":
                    jobs = [j for j in jobs if job_category.lower() in j.get('category', '').lower()]
                
                st.markdown(f"**Showing {len(jobs)} active opportunities matching '{search_keyword}'**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not jobs:
                    st.warning("No active listings found for this search. Try broadening your keywords in the sidebar.")
                else:
                    for job in jobs:
                        title = html.unescape(job.get('title', 'Software Role'))
                        comp = job.get('company_name', 'Employer')
                        jtype = job.get('job_type', 'Full-time').capitalize()
                        loc = job.get('candidate_required_location', 'Worldwide / Remote')
                        jurl = job.get('url', '#')
                        pdate = job.get('publication_date', '')[:10]
                        
                        st.markdown(f"""
                            <div class="job-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div>
                                        <div class="job-title">{title}</div>
                                        <div class="job-meta"><b>{comp}</b> &nbsp;•&nbsp; 📍 {loc} &nbsp;•&nbsp; 📅 {pdate}</div>
                                        <div>
                                            <span class="job-badge">💼 {jtype}</span>
                                            <span class="job-badge">⚡ Verified API Feed</span>
                                        </div>
                                    </div>
                                    <div>
                                        <a href="{jurl}" target="_blank" class="apply-btn">Apply Direct ↗</a>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Could not fetch remote jobs. Check network connectivity.")
        except Exception as e:
            st.error(f"API Error: {e}")