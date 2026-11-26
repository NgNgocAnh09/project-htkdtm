-- ====================================================================
-- CÁC VIEWS NGHIỆP VỤ HỖ TRỢ THÀNH VIÊN 4 (APACHE SUPERSET BI) & TV3 (ML)
-- TÁC GIẢ: THÀNH VIÊN 1 - DATA ENGINEER & ETL LEADER (NGỌC ÁNH)
-- ====================================================================

-- 1. TRANG 1 BI: XU HƯỚNG BẢN TIN CẢNH BÁO THEO THỜI GIAN
-- Lưu ý quy chuẩn: Đặt tên số lượng ghi nhận là 'alert_articles_recorded', tuyệt đối không dùng 'total_scam_cases'
CREATE OR REPLACE VIEW v_bi_monthly_article_trend AS
SELECT 
    TO_CHAR(publish_date_ict, 'YYYY-MM') AS month_year,
    publisher,
    COUNT(article_id) AS alert_articles_recorded
FROM news_articles
WHERE is_duplicate = FALSE
GROUP BY TO_CHAR(publish_date_ict, 'YYYY-MM'), publisher
ORDER BY month_year DESC, alert_articles_recorded DESC;

-- 2. TRANG 2 BI: PHÂN TÍCH NHÓM THỦ ĐOẠN VÀ ĐỐI TƯỢNG BỊ MẠO DANH
CREATE OR REPLACE VIEW v_bi_scam_category_distribution AS
SELECT 
    sc.category_code,
    sc.category_name,
    COUNT(DISTINCT na.article_id) AS total_alert_articles,
    COUNT(DISTINCT aom.org_id) AS distinct_impersonated_orgs
FROM scam_categories sc
JOIN article_scam_mapping asm ON sc.category_id = asm.category_id
JOIN news_articles na ON asm.article_id = na.article_id
LEFT JOIN article_org_mapping aom ON na.article_id = aom.article_id
WHERE na.is_duplicate = FALSE
GROUP BY sc.category_code, sc.category_name
ORDER BY total_alert_articles DESC;

-- 3. TRANG 3 BI: GIÁM SÁT CHẤT LƯỢNG VÀ NGUỒN GỐC DỮ LIỆU (GOVERNANCE & COVERAGE)
CREATE OR REPLACE VIEW v_bi_data_governance_metrics AS
SELECT 
    pl.source_name,
    pl.source_type,
    pl.fetch_timestamp,
    pl.total_records_ingested,
    pl.status,
    (SELECT COUNT(*) FROM news_articles WHERE is_duplicate = TRUE) AS total_duplicate_articles_flagged,
    (SELECT COUNT(*) FROM news_articles WHERE is_duplicate = FALSE) AS total_unique_articles,
    (SELECT COUNT(*) FROM url_dataset WHERE ground_truth_label = 1) AS total_phishing_urls_ingested,
    (SELECT COUNT(*) FROM url_dataset WHERE ground_truth_label = 0) AS total_benign_urls_ingested
FROM provenance_logs pl
ORDER BY pl.fetch_timestamp DESC;

-- 4. VIEW PHỤC VỤ THÀNH VIÊN 3 (ML URL ENGINEER) TRÍCH XUẤT TRAINING MATRIX
CREATE OR REPLACE VIEW v_url_lexical_ml_dataset AS
SELECT 
    u.url_id,
    u.raw_url_defanged,
    u.domain,
    u.tld,
    u.split_set,
    u.ground_truth_label,
    lf.url_length,
    lf.domain_length,
    lf.subdomain_count,
    lf.special_char_ratio,
    lf.entropy_score,
    lf.has_ip_address,
    lf.is_shortened,
    lf.suspicious_keyword_count
FROM url_dataset u
JOIN lexical_features lf ON u.url_id = lf.url_id;
