-- schema.sql
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_reports (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    upload_filename VARCHAR(255),
    revenue DECIMAL(15, 2),
    expenses DECIMAL(15, 2),
    net_profit DECIMAL(15, 2),
    health_score INTEGER,
    ai_analysis_text TEXT,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
