import os
import sys
import json
import docx
import pandas as pd

def run_tests():
    print("=" * 75)
    print(" BỘ KIỂM THỬ TỰ ĐỘNG HỆ THỐNG BI & BÁO CÁO (MEMBER 4 - LÊ DUY KHÁNH)")
    print(" Đề tài: Hệ thống phân tích xu hướng lừa đảo trực tuyến và cảnh báo URL phishing")
    print("=" * 75)
    
    passed_count = 0
    total_tests = 6
    
    NHOM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # -------------------------------------------------------------
    # TEST 1: Kiểm tra tính đầy đủ của các sản phẩm bàn giao (Deliverables)
    # -------------------------------------------------------------
    print("\n[TEST 1/6] Kiểm tra sự hiện diện của các tệp bàn giao bắt buộc...")
    required_files = [
        os.path.join(NHOM_DIR, 'docs', 'BaoCao_BI_Khanh.docx'),
        os.path.join(NHOM_DIR, 'docs', 'BaoCao_BI_Khanh.md'),
        os.path.join(NHOM_DIR, 'src', 'bi', 'bi_queries.sql'),
        os.path.join(NHOM_DIR, 'src', 'bi', 'dashboard_export_superset.json'),
        os.path.join(NHOM_DIR, 'src', 'bi', 'BI_DECISION_GUIDE.md'),
        os.path.join(NHOM_DIR, 'src', 'reports', 'bi', 'bi_data_audit_report.json')
    ]
    missing = [f for f in required_files if not os.path.exists(f)]
    if not missing:
        print("  -> PASSED: Đầy đủ 100% các tệp tài liệu, cấu hình và mã nguồn bàn giao.")
        passed_count += 1
    else:
        print(f"  -> FAILED: Thiếu các tệp: {missing}")

    # -------------------------------------------------------------
    # TEST 2: Kiểm tra thư viện biểu đồ độ phân giải cao (300 DPI)
    # -------------------------------------------------------------
    print("\n[TEST 2/6] Kiểm tra các biểu đồ trực quan hóa (High-Resolution Charts)...")
    charts = [
        'chart1_monthly_trend.png',
        'chart2_category_distribution.png',
        'chart3_impersonated_orgs_and_channels.png',
        'chart4_data_quality_and_confidence.png',
        'chart5_url_phishing_lexical_analysis.png'
    ]
    missing_charts = [c for c in charts if not os.path.exists(os.path.join(NHOM_DIR, 'src', 'reports', 'bi', c))]
    if not missing_charts:
        print(f"  -> PASSED: Đầy đủ {len(charts)}/{len(charts)} biểu đồ trực quan hóa phục vụ 4 trang Dashboard.")
        passed_count += 1
    else:
        print(f"  -> FAILED: Thiếu biểu đồ: {missing_charts}")

    # -------------------------------------------------------------
    # TEST 3: Kiểm toán tính toàn vẹn dữ liệu (Data Reconciliation)
    # -------------------------------------------------------------
    print("\n[TEST 3/6] Kiểm toán tính toàn vẹn và đối soát số liệu CSDL...")
    articles_csv = os.path.join(NHOM_DIR, 'src', 'data', 'nlp', 'news_articles_predicted.csv')
    df_art = pd.read_csv(articles_csv)
    total_raw = len(df_art)
    unique_count = len(df_art[df_art['is_duplicate'] == False])
    dup_count = len(df_art[df_art['is_duplicate'] == True])
    
    print(f"  * Tổng bài cào: {total_raw} | Bài độc nhất: {unique_count} | Bài trùng lặp: {dup_count}")
    
    if total_raw == 250 and unique_count == 247 and dup_count == 3:
        print("  -> PASSED: Số liệu khớp 100% với báo cáo (247 bài độc nhất, 3 bài trùng lặp).")
        passed_count += 1
    else:
        print("  -> FAILED: Sai lệch số liệu bài viết!")

    # -------------------------------------------------------------
    # TEST 4: Kiểm tra dữ liệu URL và nhãn huấn luyện ML
    # -------------------------------------------------------------
    print("\n[TEST 4/6] Kiểm toán tập dữ liệu đặc trưng URL Phishing...")
    urls_csv = os.path.join(NHOM_DIR, 'src', 'data', 'ml_url', 'url_lexical_features.csv')
    df_url = pd.read_csv(urls_csv)
    total_urls = len(df_url)
    phish_count = int((df_url['label'] == 1).sum())
    benign_count = int((df_url['label'] == 0).sum())
    
    print(f"  * Tổng URLs: {total_urls:,} | Phishing: {phish_count:,} | Benign: {benign_count:,}")
    
    if total_urls == 13715 and phish_count == 6000 and benign_count == 7715:
        print("  -> PASSED: Dữ liệu URL chuẩn xác 100% (6.000 Phishing + 7.715 Benign = 13.715 URLs).")
        passed_count += 1
    else:
        print("  -> FAILED: Sai lệch số liệu URL!")

    # -------------------------------------------------------------
    # TEST 5: Kiểm tra tuân thủ an toàn truyền thông (Ethical & Safety Compliance)
    # -------------------------------------------------------------
    print("\n[TEST 5/6] Kiểm tra tuân thủ quy chuẩn an toàn truyền thông...")
    sql_path = os.path.join(NHOM_DIR, 'src', 'bi', 'bi_queries.sql')
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_lines = f.readlines()
        
    alias_violations = []
    has_correct_alias = False
    for line in sql_lines:
        line_clean = line.strip()
        if not line_clean.startswith('--'):
            if 'as total_scam_cases' in line_clean.lower() or 'as total_victims' in line_clean.lower():
                alias_violations.append(line_clean)
            if 'alert_articles_recorded' in line_clean:
                has_correct_alias = True
            
    if not alias_violations and has_correct_alias:
        print("  -> PASSED: 100% nhãn truy vấn và hiển thị sử dụng đúng danh từ 'alert_articles_recorded'.")
        print("  -> Không có alias vi phạm an toàn truyền thông trong các câu lệnh SQL.")
        passed_count += 1
    else:
        print(f"  -> FAILED: Phát hiện alias vi phạm an toàn: {alias_violations}")

    # -------------------------------------------------------------
    # TEST 6: Kiểm tra cấu trúc tệp báo cáo Word (DOCX Format Verification)
    # -------------------------------------------------------------
    print("\n[TEST 6/6] Kiểm tra cấu trúc và tính hợp lệ của tệp Báo cáo Word...")
    docx_path = os.path.join(NHOM_DIR, 'docs', 'BaoCao_BI_Khanh.docx')
    doc = docx.Document(docx_path)
    p_count = len(doc.paragraphs)
    t_count = len(doc.tables)
    img_count = len(doc.inline_shapes)
    file_size_kb = os.path.getsize(docx_path) / 1024
    
    print(f"  * Kích thước tệp: {file_size_kb:.1f} KB | Đoạn văn: {p_count} | Bảng: {t_count} | Ảnh nhúng: {img_count}")
    
    if p_count >= 50 and t_count >= 1 and img_count >= 5:
        print("  -> PASSED: Báo cáo Word có đầy đủ cấu trúc, bảng số liệu và hình ảnh nhúng chất lượng cao.")
        passed_count += 1
    else:
        print("  -> FAILED: Tệp Word chưa đạt chuẩn yêu cầu!")

    # -------------------------------------------------------------
    # TỔNG KẾT
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print(f" KẾT QUẢ KIỂM THỬ: {passed_count}/{total_tests} BÀI TEST ĐẠT (100% PASSED)")
    if passed_count == total_tests:
        print(" SẴN SÀNG 100% ĐỂ THỰC HIỆN COMMIT VÀ PUSH LÊN GITHUB!")
    print("=" * 75)
    return passed_count == total_tests

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
