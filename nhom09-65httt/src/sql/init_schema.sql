-- ====================================================================
-- HỆ THỐNG CƠ SỞ DỮ LIỆU POSTGRESQL CHUẨN HÓA 3NF
-- DỰ ÁN: PHÂN TÍCH XU HƯỚNG LỪA ĐẢO VÀ PHÁT HIỆN URL PHISHING
-- TÁC GIẢ: THÀNH VIÊN 1 - DATA ENGINEER & ETL LEADER (NGỌC ÁNH)
-- ====================================================================

-- 1. KÍCH HOẠT EXTENSION UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. DỌN DẸP SCHEMA CŨ NẾU CẦN TÁI LẬP (DROP CÓ THỨ TỰ TRÁNH CONFLICT FK)
DROP VIEW IF EXISTS v_bi_monthly_article_trend CASCADE;
DROP VIEW IF EXISTS v_bi_scam_category_distribution CASCADE;
DROP VIEW IF EXISTS v_bi_data_governance_metrics CASCADE;
DROP VIEW IF EXISTS v_url_lexical_ml_dataset CASCADE;

DROP TABLE IF EXISTS lexical_features CASCADE;
DROP TABLE IF EXISTS label_versions CASCADE;
DROP TABLE IF EXISTS url_dataset CASCADE;
DROP TABLE IF EXISTS article_scam_mapping CASCADE;
DROP TABLE IF EXISTS article_org_mapping CASCADE;
DROP TABLE IF EXISTS news_articles CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS scam_categories CASCADE;
DROP TABLE IF EXISTS provenance_logs CASCADE;

-- ====================================================================
-- 3. BẢNG NHẬT KÝ XUẤT XỨ (DATA PROVENANCE)
-- ====================================================================
CREATE TABLE provenance_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(150) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'CSV_STATIC_DATASET', 'WEB_SCRAPING', 'API_FEED'
    fetch_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    raw_payload_checksum_sha256 VARCHAR(64) NOT NULL,
    total_records_ingested INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    notes TEXT
);

-- ====================================================================
-- 4. LUỒNG A: QUẢN LÝ BẢN TIN CẢNH BÁO LỪA ĐẢO (NLP & BI)
-- ====================================================================
CREATE TABLE scam_categories (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE organizations (
    org_id SERIAL PRIMARY KEY,
    org_name VARCHAR(255) UNIQUE NOT NULL,
    org_type VARCHAR(50) NOT NULL -- 'BANK', 'GOVERNMENT', 'ECOMMERCE', 'TELECOM', 'OTHER'
);

CREATE TABLE news_articles (
    article_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    clean_content TEXT NOT NULL,
    publisher VARCHAR(100) NOT NULL,
    publish_date_utc TIMESTAMPTZ NOT NULL,
    publish_date_ict TIMESTAMPTZ NOT NULL,
    original_url TEXT,
    simhash_fingerprint VARCHAR(64),
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_id UUID REFERENCES news_articles(article_id),
    provenance_id UUID REFERENCES provenance_logs(log_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE article_scam_mapping (
    article_id UUID REFERENCES news_articles(article_id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES scam_categories(category_id) ON DELETE CASCADE,
    is_ground_truth BOOLEAN DEFAULT FALSE,
    confidence_score NUMERIC(5, 4) DEFAULT 1.0000,
    PRIMARY KEY (article_id, category_id)
);

CREATE TABLE article_org_mapping (
    article_id UUID REFERENCES news_articles(article_id) ON DELETE CASCADE,
    org_id INTEGER REFERENCES organizations(org_id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, org_id)
);

-- ====================================================================
-- 5. LUỒNG B: BỘ DỮ LIỆU URL PHISHING (PHISHTANK & BENIGN CHO ML)
-- ====================================================================
CREATE TABLE url_dataset (
    url_id BIGSERIAL PRIMARY KEY,
    raw_url_defanged TEXT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    tld VARCHAR(50),
    ground_truth_label SMALLINT NOT NULL CHECK (ground_truth_label IN (0, 1)), -- 0: Benign, 1: Phishing
    split_set VARCHAR(10) DEFAULT 'TRAIN' CHECK (split_set IN ('TRAIN', 'TEST', 'VAL')),
    source_dataset VARCHAR(50) DEFAULT 'PhishTank',
    provenance_id UUID REFERENCES provenance_logs(log_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lexical_features (
    url_id BIGINT PRIMARY KEY REFERENCES url_dataset(url_id) ON DELETE CASCADE,
    url_length INTEGER CHECK (url_length >= 0),
    domain_length INTEGER CHECK (domain_length >= 0),
    subdomain_count INTEGER CHECK (subdomain_count >= 0),
    special_char_ratio NUMERIC(6, 4) CHECK (special_char_ratio BETWEEN 0 AND 1),
    entropy_score NUMERIC(6, 4) CHECK (entropy_score >= 0),
    has_ip_address BOOLEAN DEFAULT FALSE,
    is_shortened BOOLEAN DEFAULT FALSE,
    suspicious_keyword_count INTEGER DEFAULT 0
);

CREATE TABLE label_versions (
    version_id SERIAL PRIMARY KEY,
    version_tag VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 6. INDEXING CHIẾN LƯỢC TỐI ƯU HÓA TRUY VẤN BI VÀ MACHINE LEARNING
-- ====================================================================
-- Luồng A
CREATE INDEX idx_news_publish_date_ict ON news_articles (publish_date_ict);
CREATE INDEX idx_news_publisher ON news_articles (publisher);
CREATE INDEX idx_news_simhash ON news_articles (simhash_fingerprint);
CREATE INDEX idx_news_is_duplicate ON news_articles (is_duplicate);

-- Luồng B
CREATE INDEX idx_url_ground_truth ON url_dataset (ground_truth_label);
CREATE INDEX idx_url_domain ON url_dataset (domain);
CREATE INDEX idx_url_split_set ON url_dataset (split_set);
CREATE INDEX idx_lexical_features_length ON lexical_features (url_length);
