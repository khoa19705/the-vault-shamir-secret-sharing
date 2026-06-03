"""
============================================================
  THE VAULT — CHẾ ĐỘ HACKER: DEMO TẤN CÔNG HỆ THỐNG
  hacker_attack.py
============================================================
  Mục đích: Chứng minh hệ thống an toàn trước 4 kịch bản
  tấn công thực tế. Script này phải được chạy SAU KHI đã
  chạy share_generator.py (để có database.enc và shares).

  Cách chạy:
      python hacker_attack.py

  Kết quả mong đợi: CẢ 4 ATTACK ĐỀU THẤT BẠI
============================================================
"""

import os
import sys
import json
import time

# ── Đường dẫn project ───────────────────────────────────────
THU_MUC_SCRIPT  = os.path.dirname(os.path.abspath(__file__))
THU_MUC_GOC     = os.path.dirname(THU_MUC_SCRIPT)

# Nếu chạy thẳng từ thư mục gốc project thì THU_MUC_GOC = THU_MUC_SCRIPT
if not os.path.isdir(os.path.join(THU_MUC_GOC, "database")):
    THU_MUC_GOC = THU_MUC_SCRIPT

THU_MUC_SHARES  = os.path.join(THU_MUC_GOC, "shares")
DUONG_DAN_ENC   = os.path.join(THU_MUC_GOC, "database", "database.enc")
DUONG_DAN_GIAI  = os.path.join(THU_MUC_GOC, "database", "database_decrypted.json")
THU_MUC_NODES   = os.path.join(THU_MUC_GOC, "nodes")

# ── Import các module mật mã từ project ─────────────────────
sys.path.insert(0, THU_MUC_SCRIPT)
try:
    from utils import recover_secret, PRIME
    from decrypt_database import decrypt_database
except ImportError:
    print("[LỖI] Không tìm thấy utils.py / decrypt_database.py.")
    print("      Hãy chạy script này từ thư mục src/ của project.")
    sys.exit(1)

# ── Màu terminal (ANSI) ──────────────────────────────────────
DO    = "\033[91m"
XANH  = "\033[92m"
VANG  = "\033[93m"
CYAN  = "\033[96m"
DAM   = "\033[1m"
RESET = "\033[0m"
MO    = "\033[2m"

# ── Hàm tiện ích ────────────────────────────────────────────

def tieu_de(noi_dung: str) -> None:
    do_rong = 60
    print()
    print(CYAN + "=" * do_rong + RESET)
    print(CYAN + f"  {noi_dung}" + RESET)
    print(CYAN + "=" * do_rong + RESET)

def ket_qua_chan(thong_bao: str) -> None:
    print(XANH + DAM + f"  [ĐÃ CHẶN]    " + RESET + thong_bao)

def ket_qua_thua(thong_bao: str) -> None:
    print(DO + DAM + f"  [BỊ XÂMNHẬP] " + RESET + thong_bao)

def thong_tin(thong_bao: str) -> None:
    print(MO + f"               {thong_bao}" + RESET)

def doc_share_tu_node(so_node: int):
    """Đọc share trực tiếp từ file JSON của node (không qua HTTP)."""
    duong_dan = os.path.join(THU_MUC_NODES, f"node{so_node}", "share.json")
    if not os.path.exists(duong_dan):
        return None
    with open(duong_dan, "r") as f:
        du_lieu = json.load(f)
    return (int(du_lieu["x"]), int(du_lieu["y"]))

def doc_khoa_goc() -> int | None:
    duong_dan = os.path.join(THU_MUC_SHARES, "original_key.txt")
    if not os.path.exists(duong_dan):
        return None
    with open(duong_dan, "r") as f:
        return int(f.read().strip())

def la_json_hop_le(duong_dan: str) -> bool:
    """Kiểm tra file có chứa JSON hợp lệ không."""
    if not os.path.exists(duong_dan):
        return False
    try:
        with open(duong_dan, "rb") as f:
            noi_dung = f.read()
        json.loads(noi_dung.decode("utf-8"))
        return True
    except Exception:
        return False

def la_du_lieu_rac(duong_dan: str) -> bool:
    """Kiểm tra file có phải dữ liệu rác (non-UTF8 hoặc không parse được JSON)."""
    return not la_json_hop_le(duong_dan)

# ════════════════════════════════════════════════════════════
#  KIỂM TRA MÔI TRƯỜNG trước khi bắt đầu tấn công
# ════════════════════════════════════════════════════════════

tieu_de("KIỂM TRA MÔI TRƯỜNG TRƯỚC KHI TẤN CÔNG")

if not os.path.exists(DUONG_DAN_ENC):
    print(f"{DO}[LỖI]{RESET} Không tìm thấy database.enc tại:")
    print(f"      {DUONG_DAN_ENC}")
    print(f"      → Hãy chạy share_generator.py trước.")
    sys.exit(1)

khoa_goc = doc_khoa_goc()
if khoa_goc is None:
    print(f"{VANG}[CẢNH BÁO]{RESET} Không tìm thấy original_key.txt — "
          "sẽ kiểm tra bằng tính hợp lệ của JSON thay vì so sánh từng byte.")

tat_ca_shares = []
for i in range(1, 6):
    s = doc_share_tu_node(i)
    if s:
        tat_ca_shares.append(s)
        thong_tin(f"Đã tải share từ node{i}: x={s[0]}, y={str(s[1])[:20]}...")

if len(tat_ca_shares) < 3:
    print(f"{DO}[LỖI]{RESET} Cần ít nhất 3 shares để chạy demo đầy đủ.")
    sys.exit(1)

print()
print(f"  {XANH}✓{RESET} Tìm thấy database.enc  ({os.path.getsize(DUONG_DAN_ENC)} bytes)")
print(f"  {XANH}✓{RESET} Đã tải {len(tat_ca_shares)} shares từ các node")
print(f"  {XANH}✓{RESET} Môi trường sẵn sàng — bắt đầu mô phỏng tấn công\n")
time.sleep(0.5)

ket_qua_attacks = []   # (ten_attack, bi_chan: bool, mo_ta: str)

# ════════════════════════════════════════════════════════════
#  TẤN CÔNG 1: Dùng chỉ 2 shares để tái tạo khóa
#  Mối đe dọa: Kẻ tấn công mua chuộc được 2 trong 5 admin
# ════════════════════════════════════════════════════════════

tieu_de("TẤN CÔNG 1 — 2 Admin Câu Kết (2 trên 5 shares)")
print("  Kịch bản: Kẻ tấn công mua chuộc 2 quản trị viên và")
print("  lấy được shares của họ. Thử dùng nội suy Lagrange với")
print("  chỉ 2 điểm để khôi phục khóa AES-256 chủ.\n")
time.sleep(0.3)

shares_bi_lay = tat_ca_shares[:2]
thong_tin(f"Share bị lấy 1: ({shares_bi_lay[0][0]}, {str(shares_bi_lay[0][1])[:30]}...)")
thong_tin(f"Share bị lấy 2: ({shares_bi_lay[1][0]}, {str(shares_bi_lay[1][1])[:30]}...)")
print()

khoa_gia = recover_secret(shares_bi_lay)
thong_tin(f"Giá trị nội suy được:  {str(khoa_gia)[:60]}...")

if khoa_goc is not None:
    tan_cong_1_thanh_cong = (khoa_gia == khoa_goc)
    if tan_cong_1_thanh_cong:
        ket_qua_thua("Giá trị tái tạo KHỚP với khóa gốc — tấn công thành công!")
        ket_qua_attacks.append(("2 admin câu kết", False,
                                 "Đã tái tạo đúng khóa bí mật — HỆ THỐNG CÓ LỖ HỔNG"))
    else:
        thong_tin(f"Khóa gốc thực sự:      {str(khoa_goc)[:60]}...")
        print()
        ket_qua_chan("Giá trị tái tạo KHÔNG khớp với khóa gốc.")
        thong_tin("Nội suy Lagrange qua 2 điểm trả về một giá trị tùy ý")
        thong_tin("trong GF(p) — mọi giá trị bí mật đều có xác suất bằng nhau.")
        thong_tin("Kẻ tấn công không thu được thêm thông tin gì. (Bảo mật hoàn hảo)")
        ket_qua_attacks.append(("2 admin câu kết", True,
                                 "Tái tạo sai khóa — kẻ tấn công không có gì"))
else:
    # Phương án dự phòng: thử giải mã và kiểm tra dữ liệu rác
    decrypt_database(khoa_gia)
    if la_du_lieu_rac(DUONG_DAN_GIAI):
        ket_qua_chan("Giải mã bằng khóa giả tạo ra dữ liệu hoàn toàn vô nghĩa.")
        thong_tin("Quá trình bỏ padding AES-CBC thất bại → lưu ra raw bytes, JSON không hợp lệ.")
        ket_qua_attacks.append(("2 admin câu kết", True,
                                 "Dữ liệu rác — cơ sở dữ liệu được bảo vệ"))
    else:
        ket_qua_thua("Giải mã tạo ra output đọc được — tấn công có thể thành công!")
        ket_qua_attacks.append(("2 admin câu kết", False,
                                 "JSON hợp lệ bất thường — cần điều tra ngay"))

# ════════════════════════════════════════════════════════════
#  TẤN CÔNG 2: Đọc trực tiếp database.enc từ ổ đĩa
#  Mối đe dọa: Kẻ tấn công truy cập vật lý vào máy chủ DB
# ════════════════════════════════════════════════════════════

tieu_de("TẤN CÔNG 2 — Đánh Cắp File Database Trực Tiếp")
print("  Kịch bản: Kẻ tấn công có quyền truy cập vật lý hoặc")
print("  cấp hệ điều hành vào máy chủ DB và sao chép trực tiếp")
print("  database.enc. Thử đọc như plaintext hoặc JSON.\n")
time.sleep(0.3)

thong_tin(f"File mục tiêu: {DUONG_DAN_ENC}")

with open(DUONG_DAN_ENC, "rb") as f:
    du_lieu_thu = f.read()

iv_hex        = du_lieu_thu[:16].hex()
mau_ma_hoa    = du_lieu_thu[16:48]

thong_tin(f"Kích thước file:          {len(du_lieu_thu)} bytes")
thong_tin(f"16 bytes đầu (IV):        {iv_hex}")
thong_tin(f"32 bytes tiếp (ciphertext): {mau_ma_hoa.hex()}")
print()

# Thử parse như JSON
try:
    du_lieu_thu.decode("utf-8")
    json.loads(du_lieu_thu)
    ket_qua_thua("File đọc được như plaintext — HỆ THỐNG CÓ LỖ HỔNG!")
    ket_qua_attacks.append(("đánh cắp file trực tiếp", False,
                             "Tìm thấy database không mã hóa trên ổ đĩa"))
except (UnicodeDecodeError, json.JSONDecodeError):
    ket_qua_chan("File là ciphertext nhị phân — hoàn toàn không đọc được nếu không có khóa.")
    thong_tin("Nếu không có khóa AES-256, file này về mặt tính toán")
    thong_tin(f"không thể phân biệt với nhiễu ngẫu nhiên (không gian brute-force: 2^256).")
    thong_tin("IV được công khai ở đầu file nhưng không cung cấp thông tin về khóa.")
    ket_qua_attacks.append(("đánh cắp file trực tiếp", True,
                             "Chỉ là ciphertext nhị phân — cần khóa để giải mã"))

# ════════════════════════════════════════════════════════════
#  TẤN CÔNG 3: Brute-force với 1 share để đoán secret
#  Mối đe dọa: Kẻ tấn công lấy được 1 share, thử đoán ngẫu nhiên
# ════════════════════════════════════════════════════════════

tieu_de("TẤN CÔNG 3 — Brute-Force Với 1 Share")
print("  Kịch bản: Kẻ tấn công xâm nhập 1 node và lấy được")
print("  1 share. Thử thu hẹp không gian tìm kiếm bằng cách")
print("  thử ngẫu nhiên các ứng viên và kiểm tra tính nhất quán.\n")
time.sleep(0.3)

share_bi_chiem = tat_ca_shares[0]
thong_tin(f"Share bị chiếm: ({share_bi_chiem[0]}, {str(share_bi_chiem[1])[:40]}...)")
thong_tin(f"Kích thước trường GF(p): 2^257 - 93  ≈ 10^77 khả năng")
print()

SO_LAN_THU = 100_000
thong_tin(f"Đang mô phỏng {SO_LAN_THU:,} lần đoán ngẫu nhiên trên GF(p)...")

import random as _rnd
_rnd.seed(42)

so_lan_trung = 0
for _ in range(SO_LAN_THU):
    ung_vien = _rnd.randrange(0, PRIME)
    # Một share (1, y) nhất quán với MỌI secret vì với bất kỳ s nào
    # ta đều dựng được đa thức bậc 2 qua (0,s) và (1,y).
    # Không có cách nào lọc ra đúng s từ 1 điểm duy nhất.
    if khoa_goc is not None and ung_vien == khoa_goc:
        so_lan_trung += 1

thong_tin(f"Số lần đoán đúng trong {SO_LAN_THU:,} lần thử: {so_lan_trung}")
thong_tin(f"Xác suất lý thuyết: 1 / {PRIME} ≈ 10^-77")
print()

if so_lan_trung == 0:
    ket_qua_chan("Không có lần đoán nào đúng trong 100.000 lần thử.")
    thong_tin("Với 1 share, mọi ứng viên đều nhất quán với điểm dữ liệu quan sát.")
    thong_tin("Brute-force không mang lại lợi thế nào.")
    thong_tin("Thời gian ước tính để brute-force: lớn hơn tuổi của vũ trụ.")
    ket_qua_attacks.append(("brute-force 1 share", True,
                             "0/100.000 lần đoán đúng — trường quá lớn"))
else:
    ket_qua_thua(f"Đoán đúng {so_lan_trung} lần — kết quả bất ngờ!")
    ket_qua_attacks.append(("brute-force 1 share", False,
                             f"Đoán đúng bất ngờ {so_lan_trung} lần"))

# ════════════════════════════════════════════════════════════
#  TẤN CÔNG 4: Thử giải mã với khóa AES ngẫu nhiên (không có share)
#  Mối đe dọa: Kẻ tấn công có database.enc nhưng không có share nào
# ════════════════════════════════════════════════════════════

tieu_de("TẤN CÔNG 4 — Giải Mã Không Cần Share (Bonus)")
print("  Kịch bản: Kẻ tấn công có database.enc nhưng không có")
print("  share nào. Tự tạo khóa AES 256-bit ngẫu nhiên và thử giải mã.\n")
time.sleep(0.3)

import secrets as _sec
khoa_ngau_nhien = _sec.randbits(256)
thong_tin(f"Khóa AES ngẫu nhiên: {khoa_ngau_nhien.to_bytes(32,'big').hex()[:40]}...")

decrypt_database(khoa_ngau_nhien)

if la_du_lieu_rac(DUONG_DAN_GIAI):
    ket_qua_chan("Giải mã bằng khóa ngẫu nhiên tạo ra dữ liệu vô nghĩa.")
    thong_tin("Quá trình bỏ padding PKCS7 thất bại — xác nhận khóa sai.")
    thong_tin("File output chứa các byte thô không đọc được.")
    ket_qua_attacks.append(("giải mã không cần share", True,
                             "Dữ liệu rác — bỏ padding thất bại với khóa sai"))
else:
    ket_qua_thua("Khóa ngẫu nhiên tạo ra output đọc được — xác suất cực thấp!")
    ket_qua_attacks.append(("giải mã không cần share", False,
                             "JSON hợp lệ từ khóa ngẫu nhiên — cần điều tra"))

# ════════════════════════════════════════════════════════════
#  BÁO CÁO TỔNG KẾT
# ════════════════════════════════════════════════════════════

tieu_de("BÁO CÁO TỔNG KẾT CÁC CUỘC TẤN CÔNG")

tat_ca_bi_chan = all(bi_chan for _, bi_chan, _ in ket_qua_attacks)
so_lan_chan    = sum(1 for _, b, _ in ket_qua_attacks if b)

print(f"  {'Kịch bản tấn công':<38} {'Kết quả':<14} {'Chi tiết'}")
print("  " + "─" * 58)
for ten, bi_chan, mo_ta in ket_qua_attacks:
    trang_thai = f"{XANH}ĐÃ CHẶN{RESET}  " if bi_chan else f"{DO}BỊ XÂM NHẬP{RESET}"
    print(f"  {ten:<38} {trang_thai}  {MO}{mo_ta}{RESET}")

print()
print("  " + "─" * 58)
print(f"  Số cuộc tấn công bị chặn: {XANH}{so_lan_chan}{RESET} / {len(ket_qua_attacks)}")
print()

if tat_ca_bi_chan:
    print(DAM + XANH +
          "  ✓ TẤT CẢ TẤN CÔNG THẤT BẠI — THE VAULT AN TOÀN" + RESET)
    print()
    print(MO + "  Các đảm bảo an toàn đã được chứng minh:" + RESET)
    print(MO + "  • Bảo mật hoàn hảo: t-1 shares không tiết lộ thông tin nào" + RESET)
    print(MO + "  • Mã hóa AES-256: database không đọc được nếu thiếu khóa" + RESET)
    print(MO + "  • Trường GF(2^257-93): brute-force không khả thi về mặt tính toán" + RESET)
    print(MO + "  • Cơ chế ngưỡng: không node đơn lẻ nào có thể tái tạo bí mật" + RESET)
else:
    print(DAM + DO +
          "  ✗ MỘT HOẶC NHIỀU CUỘC TẤN CÔNG THÀNH CÔNG — XEM XÉT LẠI BẢO MẬT" + RESET)

print()
print(CYAN + "=" * 60 + RESET)
print()

# ── Ghi báo cáo ra file ──────────────────────────────────────
duong_dan_bao_cao = os.path.join(THU_MUC_SHARES, "bao_cao_tan_cong.txt")
os.makedirs(THU_MUC_SHARES, exist_ok=True)
with open(duong_dan_bao_cao, "w", encoding="utf-8") as bao_cao:
    bao_cao.write("THE VAULT — BÁO CÁO TẤN CÔNG HACKER MODE\n")
    bao_cao.write("=" * 50 + "\n\n")
    for ten, bi_chan, mo_ta in ket_qua_attacks:
        trang_thai = "ĐÃ CHẶN" if bi_chan else "BỊ XÂM NHẬP"
        bao_cao.write(f"[{trang_thai}] {ten}\n")
        bao_cao.write(f"           {mo_ta}\n\n")
    bao_cao.write("=" * 50 + "\n")
    bao_cao.write(f"Kết quả: {so_lan_chan}/{len(ket_qua_attacks)} cuộc tấn công bị chặn\n")
    trang_thai_chung = "AN TOÀN" if tat_ca_bi_chan else "CÓ LỖ HỔNG"
    bao_cao.write(f"Trạng thái hệ thống: {trang_thai_chung}\n")

print(MO + f"  Báo cáo đã lưu tại: {duong_dan_bao_cao}" + RESET)
print()