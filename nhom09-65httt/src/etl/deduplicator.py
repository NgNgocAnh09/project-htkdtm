import re
import hashlib
from simhash import Simhash

class SimHashDeduplicator:
    """
    Thuật toán SimHash 64-bit và n-gram char/word khử trùng lặp văn bản báo chí
    """
    def __init__(self, f: int = 64):
        self.f = f

    def _get_features(self, text: str):
        text = text.lower()
        # Loại bỏ ký tự đặc biệt
        words = re.findall(r'[\w]+', text, re.UNICODE)
        # Sinh 2-grams để tăng độ phân giải ngữ cảnh
        shingles = []
        for i in range(len(words) - 1):
            shingles.append(f"{words[i]}_{words[i+1]}")
        return words + shingles

    def build_simhash(self, text: str) -> int:
        features = self._get_features(text)
        if not features:
            return 0
        return Simhash(features, f=self.f).value

    def hamming_distance(self, hash1: int, hash2: int) -> int:
        s1 = Simhash(hash1, f=self.f)
        s2 = Simhash(hash2, f=self.f)
        return s1.distance(s2)

    def is_duplicate(self, text1: str, text2: str, distance_threshold: int = 15) -> bool:
        """
        Nếu khoảng cách Hamming <= distance_threshold (mặc định 10-15 cho n-grams),
        hai văn bản được xác định trùng lặp/sao chép.
        """
        h1 = self.build_simhash(text1)
        h2 = self.build_simhash(text2)
        return self.hamming_distance(h1, h2) <= distance_threshold


