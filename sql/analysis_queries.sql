-- Kenya Tech Job Market Analysis - Core Analytical Queries
-- These queries are designed to be run against the job_market.db SQLite database.

-- 1. Demand by Role (Which technology job titles appear most frequently?)
SELECT 
    job_title, 
    COUNT(*) as total_postings 
FROM job_postings 
GROUP BY job_title 
ORDER BY total_postings DESC;

-- 2. Entry-Level Accessibility (How many postings are suitable for juniors/interns?)
SELECT 
    is_entry_level, 
    COUNT(*) as total_postings,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM job_postings), 1) as percentage
FROM job_postings 
GROUP BY is_entry_level;

-- 3. Core Skill Demand (How frequently are key technologies requested?)
SELECT 
    SUM(req_python) as python_demand,
    SUM(req_sql) as sql_demand,
    SUM(req_javascript) as javascript_demand,
    SUM(req_cloud) as cloud_demand,
    COUNT(*) as total_analyzed_jobs
FROM job_postings;

-- 4. Geographical Distribution (Where are captured roles located?)
SELECT 
    location, 
    remote_status,
    COUNT(*) as total_postings 
FROM job_postings 
GROUP BY location, remote_status
ORDER BY total_postings DESC;