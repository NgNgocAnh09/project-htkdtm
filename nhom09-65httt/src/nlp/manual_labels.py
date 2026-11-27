# Nhãn gán thủ công cho 247 bài trong sample_articles_for_nlp_tv2.csv
# Khóa = số thứ tự dòng (0..246) theo đúng thứ tự file gốc. Xem ANNOTATION_GUIDELINE.md
LABELS_BY_ROW = {
    0: "K", 1: "G", 2: "A", 3: "I", 4: "D", 5: "E", 6: "C", 7: "I", 8: "I", 9: "A",
    10: "I", 11: "H", 12: "K", 13: "I", 14: "B", 15: "F", 16: "C", 17: "D", 18: "G", 19: "I",
    20: "D", 21: "I", 22: "C", 23: "E", 24: "C", 25: "I", 26: "I", 27: "A", 28: "I", 29: "I",
    30: "C", 31: "C", 32: "G", 33: "B", 34: "H", 35: "I", 36: "K", 37: "I", 38: "K", 39: "B",
    40: "B", 41: "F", 42: "I", 43: "B", 44: "B", 45: "I", 46: "I", 47: "C", 48: "I", 49: "C",
    50: "C", 51: "H", 52: "I", 53: "K", 54: "I", 55: "B", 56: "B", 57: "F", 58: "C", 59: "D",
    60: "I", 61: "I", 62: "I", 63: "C", 64: "I", 65: "I", 66: "B", 67: "D", 68: "B", 69: "B",
    70: "B", 71: "C", 72: "I", 73: "E", 74: "I", 75: "I", 76: "I", 77: "I", 78: "K", 79: "I",
    80: "I", 81: "E", 82: "I", 83: "I", 84: "K", 85: "I", 86: "D", 87: "E", 88: "I", 89: "K",
    90: "B", 91: "I", 92: "B", 93: "K", 94: "B", 95: "B", 96: "K", 97: "I", 98: "C", 99: "I",
    100: "E", 101: "B", 102: "B", 103: "B", 104: "B", 105: "B", 106: "I", 107: "K", 108: "I", 109: "D",
    110: "B", 111: "A", 112: "B", 113: "C", 114: "K", 115: "B", 116: "K", 117: "K", 118: "C", 119: "B",
    120: "B", 121: "B", 122: "I", 123: "B", 124: "K", 125: "E", 126: "B", 127: "I", 128: "I", 129: "I",
    130: "I", 131: "K", 132: "K", 133: "I", 134: "E", 135: "I", 136: "G", 137: "F", 138: "K", 139: "I",
    140: "I", 141: "B", 142: "D", 143: "B", 144: "D", 145: "K", 146: "A", 147: "I", 148: "I", 149: "B",
    150: "E", 151: "D", 152: "I", 153: "D", 154: "D", 155: "B", 156: "I", 157: "I", 158: "I", 159: "A",
    160: "B", 161: "I", 162: "I", 163: "I", 164: "I", 165: "K", 166: "E", 167: "F", 168: "D", 169: "I",
    170: "H", 171: "H", 172: "F", 173: "D", 174: "F", 175: "E", 176: "K", 177: "B", 178: "A", 179: "K",
    180: "K", 181: "K", 182: "I", 183: "E", 184: "K", 185: "C", 186: "B", 187: "B", 188: "A", 189: "B",
    190: "B", 191: "I", 192: "C", 193: "B", 194: "B", 195: "I", 196: "B", 197: "I", 198: "K", 199: "I",
    200: "I", 201: "G", 202: "G", 203: "I", 204: "K", 205: "I", 206: "A", 207: "H", 208: "C", 209: "I",
    210: "K", 211: "H", 212: "B", 213: "I", 214: "I", 215: "F", 216: "I", 217: "I", 218: "E", 219: "H",
    220: "G", 221: "A", 222: "I", 223: "I", 224: "K", 225: "D", 226: "H", 227: "H", 228: "I", 229: "K",
    230: "K", 231: "H", 232: "I", 233: "H", 234: "K", 235: "B", 236: "I", 237: "E", 238: "I", 239: "K",
    240: "E", 241: "D", 242: "H", 243: "D", 244: "K", 245: "B", 246: "B",
}

# Mã nhóm -> tên nhóm thủ đoạn và các mã SCAM_xx tương ứng trong bảng scam_categories (TV1)
GROUPS = {
    "A": ("GIA_DANH_CO_QUAN", "Giả danh công an, cơ quan nhà nước, quân đội; bắt cóc online", "SCAM_02, SCAM_08, SCAM_12, SCAM_16, SCAM_18, SCAM_20"),
    "B": ("DAU_TU_HUY_DONG_VON", "Lừa đầu tư tài chính, sàn ảo, tiền số, đa cấp, huy động vốn", "SCAM_05"),
    "C": ("BAT_DONG_SAN_NHA_O", "Lừa mua bán đất, nhà ở xã hội, giấy tờ nhà đất giả", "(mới)"),
    "D": ("VAY_TIEN_NGAN_HANG_HUI", "Lừa vay đáo hạn, giả nhân viên/dịch vụ ngân hàng, cho vay online, hụi", "SCAM_03, SCAM_13"),
    "E": ("LUA_DAO_QUA_MANG_XA_HOI", "Lừa qua mạng xã hội: bán hàng/vé, tình cảm, việc nhẹ lương cao, livestream, quyên góp", "SCAM_04, SCAM_09, SCAM_10, SCAM_11, SCAM_15, SCAM_22, SCAM_25"),
    "F": ("GIA_BAC_SI_Y_TE", "Giả bác sĩ, thẩm mỹ chui, thuốc/thực phẩm chức năng", "SCAM_21"),
    "G": ("NHAN_CHAY_VIEC_CHAY_AN", "Nổ quan hệ để nhận tiền chạy việc, chạy án, chạy thủ tục, dự án", "SCAM_19"),
    "H": ("TAI_KHOAN_DU_LIEU_MA_DOC", "Mua bán tài khoản ngân hàng, dữ liệu cá nhân, mã độc, rửa tiền qua tài khoản", "SCAM_06, SCAM_07, SCAM_23"),
    "K": ("LUA_DAO_KHAC", "Lừa đảo chiếm đoạt tài sản khác (doanh nghiệp, ngân hàng, mua bán trực tiếp)", "-"),
    "I": ("KHONG_PHAI_LUA_DAO", "Không phải bài về thủ đoạn lừa đảo (bạo lực, tin giả, thuế, tham ô…)", "-"),
}
