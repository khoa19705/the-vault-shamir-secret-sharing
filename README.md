# The Vault — Shamir's Secret Sharing for DB Credentials

> **Project #103** | Môn học: Cơ Sở Dữ Liệu Phân Tán  
> Học viện Công nghệ Bưu chính Viễn thông (PTIT)  
> Sinh viên: Bùi Kiếm Khoa — N23DCCN029 — D23CQCN01-N  
> Giảng viên: Lê Hà Thanh

---

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cơ sở lý thuyết](#3-cơ-sở-lý-thuyết)
4. [Cấu trúc thư mục](#4-cấu-trúc-thư-mục)
5. [Yêu cầu cài đặt](#5-yêu-cầu-cài-đặt)
6. [Hướng dẫn chạy](#6-hướng-dẫn-chạy)
7. [Chế độ Hacker Mode](#7-chế-độ-hacker-mode)
8. [Bảng kịch bản lỗi](#8-bảng-kịch-bản-lỗi)
9. [Thiết kế mật mã học](#9-thiết-kế-mật-mã-học)
10. [Tham chiếu lý thuyết](#10-tham-chiếu-lý-thuyết)

---

## 1. Giới thiệu

**The Vault** triển khai cơ chế **Shamir's (t, n) Secret Sharing** để bảo vệ khóa mã hóa chủ (master key) của một cơ sở dữ liệu phân tán.

### Vấn đề cần giải quyết

Trong bất kỳ hệ thống cơ sở dữ liệu phân tán nào, nếu khóa AES được lưu tại một máy chủ duy nhất thì máy chủ đó trở thành cả **điểm lỗi đơn** (single point of failure) lẫn **mục tiêu tấn công duy nhất** (single point of attack). Một admin bị mua chuộc hoặc một node bị xâm nhập là đủ để lộ toàn bộ dữ liệu.

### Giải pháp

Khóa AES-256-bit được phân rã thành **5 mảnh (shares)** và phân phối trên 5 node HTTP Node.js độc lập theo mô hình ngưỡng **(t=3, n=5)**:

- Bất kỳ **3 shares trở lên** → khôi phục được khóa gốc chính xác tuyệt đối.
- Chỉ **1 hoặc 2 shares** → không thu được bất kỳ thông tin nào về khóa (Perfect Secrecy theo Shannon).
- **0 shares** → hệ thống từ chối hoàn toàn.

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────┐
│              GUI / Control Layer                │
│         app.py  (Python Tkinter)                │
│  Generate Shares │ Recover Secret │ Check Nodes │
└────────┬─────────────────────────┬──────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Crypto Core    │     │    Node Layer (×5)   │
│                 │     │                      │
│ share_generator │     │  node1  :3001        │
│ recover_secret  │◄───►│  node2  :3002        │
│ encrypt_db      │     │  node3  :3003        │
│ decrypt_db      │     │  node4  :3004        │
│ utils (GF math) │     │  node5  :3005        │
└────────┬────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────┐
│    Storage      │
│  database.enc   │  ← Database mã hóa AES-256-CBC
│  shares/        │  ← original_key.txt (demo only)
│  nodes/nodeX/   │  ← share.json (mỗi node 1 file)
└─────────────────┘
```

| Layer | Module | Trách nhiệm |
|---|---|---|
| GUI / Control | `app.py` | Giao diện người dùng, quản lý node, hiển thị tiến trình |
| Crypto Core | `share_generator.py`, `utils.py`, `encrypt_database.py`, `decrypt_database.py` | Sinh khóa, tính đa thức, nội suy Lagrange, mã hóa/giải mã AES-256-CBC |
| Node Layer | `node1–node5 / server.js` | HTTP REST endpoints: `/share`, `/health`, `/shutdown` |
| Storage | `shares/`, `nodes/`, `database/` | JSON shares, binary `.enc`, kết quả giải mã, báo cáo |

---

## 3. Cơ sở lý thuyết

### 3.1 Xây dựng đa thức và sinh shares

Cho khóa bí mật `s` là khóa AES-256 được sinh bởi OS CSPRNG (`secrets.randbits(256)`), hệ thống xây dựng đa thức bậc 2 trên trường hữu hạn GF(p):

```
f(x) = s + a₁x + a₂x²  (mod p)
```

Trong đó:
- `s = f(0)` là khóa bí mật cần bảo vệ
- `a₁, a₂` là các hệ số ngẫu nhiên trong GF(p)
- `p = 2²⁵⁷ − 93` là số nguyên tố lớn hơn mọi giá trị 256-bit

5 shares được tạo dưới dạng: `(i, f(i) mod p)` với `i ∈ {1, 2, 3, 4, 5}`

### 3.2 Khôi phục khóa — Nội suy Lagrange

Khi có ít nhất 3 shares hợp lệ, khóa được khôi phục bằng:

```
s = Σ yⱼ · Lⱼ(0)  (mod p)

với  Lⱼ(0) = ∏ (−xₘ) / (xⱼ − xₘ)  (mod p),  m ≠ j
```

Mọi phép toán thực hiện trong GF(p) nên kết quả chính xác tuyệt đối ở mức bit.

### 3.3 Tại sao 2 shares không tiết lộ gì

Với 2 điểm bất kỳ, tồn tại **vô số** đa thức bậc 2 đi qua 2 điểm đó, mỗi đa thức cho một giá trị `f(0)` khác nhau. Theo lý thuyết Entropy của Shannon, xác suất hậu nghiệm của mọi giá trị bí mật bằng đúng xác suất tiên nghiệm `1/p`. Kẻ tấn công **không thu được thêm bất kỳ thông tin nào**.

### 3.4 Trường hữu hạn GF(2²⁵⁷ − 93)

`p = 2²⁵⁷ − 93` được chọn vì:
- Lớn hơn `2²⁵⁶` → khóa AES 256-bit nằm trọn trong trường, không bị wraparound.
- Là số nguyên tố → mọi phần tử đều có nghịch đảo nhân (cần cho Lagrange).
- Đảm bảo Tính đầy đủ (Completeness) của phân mảnh theo Özsu & Valduriez Ch.2 §2.1.

---

## 4. Cấu trúc thư mục

```
the-vault/
│
├── src/                         ← Python Crypto Core + GUI
│   ├── app.py                   ← Giao diện điều khiển Tkinter
│   ├── share_generator.py       ← Sinh khóa, đa thức, phân phối shares
│   ├── recovery_secret.py       ← Thu thập shares từ nodes, khôi phục khóa
│   ├── encrypt_database.py      ← Mã hóa database bằng AES-256-CBC
│   ├── decrypt_database.py      ← Giải mã database
│   ├── utils.py                 ← GF(p) arithmetic, Lagrange interpolation
│   └── hacker_attack.py         ← Demo tấn công (Hacker Mode)
│
├── nodes/
│   ├── node1/
│   │   ├── server.js            ← HTTP server Node.js (port 3001)
│   │   └── share.json           ← Share của node 1 (tạo tự động)
│   ├── node2/ ... node5/        ← Tương tự, ports 3002–3005
│
├── database/
│   ├── database.json            ← Dữ liệu gốc (username/password)
│   ├── database.enc             ← Database đã mã hóa AES-CBC (tạo tự động)
│   └── database_decrypted.json  ← Kết quả giải mã (tạo tự động)
│
├── shares/
│   ├── original_key.txt         ← Khóa gốc lưu để kiểm tra demo
│   ├── recovered_key.txt        ← Khóa đã khôi phục
│   ├── recovery_report.txt      ← Báo cáo quá trình khôi phục
│   └── bao_cao_tan_cong.txt     ← Báo cáo Hacker Mode
│
└── README.md
```

> **Lưu ý:** `original_key.txt` chỉ tồn tại phục vụ mục đích demo và kiểm thử tự động. Trong hệ thống thực tế, khóa gốc **không bao giờ** được ghi ra đĩa sau khi đã phân chia.

---

## 5. Yêu cầu cài đặt

### Python (>= 3.10)

```bash
pip install pycryptodome requests
```

### Node.js (>= 16)

```bash
cd nodes/node1 && npm install
# Lặp lại cho node2 → node5
```

### Kiểm tra

```bash
python --version    # >= 3.10
node --version      # >= 16
```

---

## 6. Hướng dẫn chạy

### Bước 1 — Khởi động GUI

```bash
cd src
python app.py
```

### Bước 2 — Sinh shares và mã hóa database

Nhấn nút **"Generate Shares"** trong GUI. Hệ thống sẽ:

1. Sinh khóa AES-256 ngẫu nhiên bằng CSPRNG.
2. Xây dựng đa thức bậc 2 trên GF(2²⁵⁷ − 93).
3. Tính 5 shares và ghi vào `nodes/nodeX/share.json`.
4. Mã hóa `database.json` thành `database.enc` bằng AES-256-CBC.
5. Khởi động lại 5 HTTP node servers.

### Bước 3 — Kiểm tra trạng thái node

Nhấn **"Check Nodes"** để xem node nào đang ONLINE / OFFLINE.

### Bước 4 — Khôi phục khóa và giải mã database

Nhấn **"Recover Secret"**. Hệ thống sẽ:

1. Gửi GET request đến `/share` của từng node (timeout 3s).
2. Thu thập các shares từ node đang ONLINE.
3. Thực hiện nội suy Lagrange để khôi phục khóa.
4. Giải mã `database.enc` → `database_decrypted.json`.
5. Xuất báo cáo `recovery_report.txt`.

### Bước 5 — Điều khiển từng node riêng lẻ

Dùng các nút **START / STOP** bên cạnh mỗi node để mô phỏng node bị lỗi, sau đó nhấn **"Recover Secret"** để kiểm chứng tính chịu lỗi.

---

## 7. Chế độ Hacker Mode

Script `hacker_attack.py` mô phỏng 4 kịch bản tấn công thực tế và chứng minh hệ thống chặn tất cả.

### Cách chạy

```bash
# Phải chạy SAU khi đã Generate Shares
cd src
python hacker_attack.py
```

### 4 kịch bản tấn công

| # | Tên tấn công | Mô tả | Kết quả mong đợi |
|---|---|---|---|
| 1 | **2 Admin câu kết** | Lấy 2 shares, thực hiện nội suy Lagrange | `[ĐÃ CHẶN]` — Giá trị tái tạo sai, không khớp khóa gốc |
| 2 | **Đánh cắp file trực tiếp** | Đọc `database.enc` từ ổ đĩa, thử parse như JSON | `[ĐÃ CHẶN]` — Binary ciphertext, không đọc được |
| 3 | **Brute-force với 1 share** | 100.000 lần đoán ngẫu nhiên trên GF(p) | `[ĐÃ CHẶN]` — 0/100.000 lần đúng |
| 4 | **Giải mã không có share** | Sinh khóa AES ngẫu nhiên, thử giải mã | `[ĐÃ CHẶN]` — PKCS7 unpadding thất bại, dữ liệu rác |

### Output mong đợi khi chạy thành công

```
============================================================
  BÁO CÁO TỔNG KẾT CÁC CUỘC TẤN CÔNG
============================================================

  Kịch bản tấn công                      Kết quả
  ──────────────────────────────────────────────────────
  2 admin câu kết                         ĐÃ CHẶN
  đánh cắp file trực tiếp                ĐÃ CHẶN
  brute-force 1 share                     ĐÃ CHẶN
  giải mã không cần share                ĐÃ CHẶN

  Số cuộc tấn công bị chặn: 4 / 4

  ✓ TẤT CẢ TẤN CÔNG THẤT BẠI — THE VAULT AN TOÀN
```

Báo cáo chi tiết được lưu tự động tại `shares/bao_cao_tan_cong.txt`.

---

## 8. Bảng kịch bản lỗi

Bảng này chứng minh tính chất ngưỡng (threshold property) của hệ thống:

| Nodes online | Shares thu được | Kết quả khôi phục | Database output |
|:---:|:---:|:---:|---|
| 5 / 5 | 5 | **ĐÚNG** | JSON hợp lệ, đọc được |
| 4 / 5 | 4 | **ĐÚNG** | JSON hợp lệ, đọc được |
| 3 / 5 | 3 (đúng ngưỡng) | **ĐÚNG** | JSON hợp lệ, đọc được |
| 2 / 5 | 2 (dưới ngưỡng) | **SAI** | Dữ liệu rác — unpadding lỗi |
| 1 / 5 | 1 (dưới ngưỡng) | **SAI** | Dữ liệu rác — unpadding lỗi |
| 0 / 5 | 0 | **THẤT BẠI** | Không thực hiện giải mã |

---

## 9. Thiết kế mật mã học

### Mã hóa AES-256-CBC

```
[IV ngẫu nhiên 16 bytes] + [Ciphertext (PKCS7 padded)]
          ↓
     database.enc
```

- Khóa `s` được serialize thành 32 bytes big-endian làm khóa AES.
- IV mới được sinh ngẫu nhiên mỗi lần mã hóa, prepend vào đầu file.
- Khi giải mã: đọc 16 bytes đầu làm IV, phần còn lại là ciphertext.
- Nếu PKCS7 unpadding thất bại → tín hiệu mật mã xác nhận khóa sai.

### Ma trận quyết định thiết kế

| Quyết định | Lựa chọn | Lý do kỹ thuật | Đánh đổi chấp nhận |
|---|---|---|---|
| Trường số | GF(2²⁵⁷ − 93) | Lớn hơn 2²⁵⁶, bí mật 256-bit không bị wraparound | Chi phí tính toán số nguyên lớn tăng nhẹ |
| Ngưỡng | (3, 5) | Chịu lỗi tối đa 2 node, nguyên lý Quorum đa số | Tăng độ phức tạp quản lý shares |
| Giao thức | HTTP REST stateless | Bảo toàn Site Autonomy (Ö&V §1.6.1.1) | Giao tiếp localhost không TLS (demo only) |
| Chế độ AES | AES-256-CBC + random IV | Ciphertext indistinguishability, chống known-plaintext | — |
| `original_key.txt` | Lưu để demo | Hỗ trợ kiểm tra tự động byte-by-byte | Không dùng trong production |

---

## 10. Tham chiếu lý thuyết

Toàn bộ thiết kế hệ thống được xây dựng dựa trên:

> Özsu, M. T., & Valduriez, P. (2020). *Principles of Distributed Database Systems* (4th ed.).

| Quyết định thiết kế | Tham chiếu |
|---|---|
| Tính minh bạch phân tán | Ch.1 §1.4.1 |
| Tính tin cậy và sẵn sàng | Ch.1 §1.4.2 |
| Tính tự trị của vị trí | Ch.1 §1.6.1.1 |
| Chiến lược phân mảnh (Completeness, Reconstruction, Disjointness) | Ch.2 §2.1 |
| Xử lý truy vấn phân tán, Semi-join | Ch.4 §4.1.1, §4.3.3 |
| Độ tin cậy và phục hồi lỗi | Ch.5 §5.4, §5.4.3 |
| Nhân bản Write-once, Primary-site protocol | Ch.6 §6.2.1, §6.3.1 |
| Nguyên lý Quorum đa số | Ch.6 §6.5.2 |

---

*The Vault — TP.HCM, tháng 05/2026*
