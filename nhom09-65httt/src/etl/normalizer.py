from datetime import datetime
import pytz

def normalize_datetime(dt_input, input_timezone: str = "Asia/Ho_Chi_Minh"):
    """
    Chuẩn hóa thời gian về đồng thời UTC và giờ địa phương ICT (Asia/Ho_Chi_Minh).
    Trả về: (dt_utc, dt_ict) dạng ISO-8601 string hoặc datetime objects.
    """
    tz_ict = pytz.timezone("Asia/Ho_Chi_Minh")
    tz_utc = pytz.utc
    
    dt = None
    if isinstance(dt_input, str):
        # Hỗ trợ đa dạng format phổ biến tại báo chí Việt Nam
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_input.strip(), fmt)
                break
            except ValueError:
                continue
        if dt is None:
            # Fallback nếu không parse được
            dt = datetime.now()
    elif isinstance(dt_input, datetime):
        dt = dt_input
    else:
        dt = datetime.now()

    # Gán múi giờ gốc nếu chưa có (Naive datetime)
    if dt.tzinfo is None:
        if input_timezone == "Asia/Ho_Chi_Minh":
            dt_ict = tz_ict.localize(dt)
        else:
            dt_ict = tz_utc.localize(dt).astimezone(tz_ict)
    else:
        dt_ict = dt.astimezone(tz_ict)
        
    dt_utc = dt_ict.astimezone(tz_utc)
    
    return dt_utc, dt_ict
