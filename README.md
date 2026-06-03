The Vault — Hệ Thống Chia Sẻ Bí Mật Phân Tán

Ứng dụng desktop triển khai thuật toán **Shamir's Secret Sharing** để phân phối và phục hồi khóa mã hóa AES-256 trên nhiều node độc lập.

Mục Lục

- [Tổng Quan](#tổng-quan)
- [Cách Hoạt Động](#cách-hoạt-động)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
- [Lưu Ý Bảo Mật](#lưu-ý-bảo-mật)

Tổng Quan

**The Vault** chia một khóa AES 256-bit thành **5 phần (shares)** và phân phối đến 5 server Node.js độc lập. Chỉ cần **bất kỳ 3 trong 5 shares** (ngưỡng `T=3`) là đủ để tái tạo lại bí mật gốc và giải mã cơ sở dữ liệu. Điều này đảm bảo:

- Không node nào đơn lẻ có đủ thông tin để xâm phạm hệ thống.
- Hệ thống vẫn hoạt động bình thường khi có tối đa 2 node bị lỗi hoặc ngoại tuyến.
- Cơ sở dữ liệu được mã hóa vẫn an toàn ngay cả khi một số node bị tấn công.

---

## Cách Hoạt Động

### Tạo & Phân Phối Khóa

1. Một bí mật ngẫu nhiên 256-bit được tạo bằng phương pháp mật mã học an toàn.
2. Một đa thức bậc `T-1 = 2` được xây dựng với bí mật là hệ số tự do.
3. 5 điểm `(x, y)` được tính từ đa thức để tạo ra 5 shares.
4. Mỗi share được phân phối đến một server Node.js riêng biệt (`node1`–`node5`).
5. Cơ sở dữ liệu được mã hóa AES-256 bằng bí mật vừa tạo.

### Phục Hồi Bí Mật

1. Ứng dụng gửi yêu cầu đến tất cả các node đang hoạt động để lấy shares.
2. Nội suy Lagrange được thực hiện trên các shares thu được trong trường số nguyên tố.
3. Bí mật được tái tạo và dùng để giải mã cơ sở dữ liệu.
4. Kết quả được xác minh bằng cách so sánh với khóa gốc đã lưu.

### Thông Số Mật Mã

| Thông số | Giá trị |
|----------|---------|
| Kích thước bí mật | 256 bit |
| Tổng số shares (N) | 5 |
| Ngưỡng phục hồi (T) | 3 |
| Số nguyên tố modulus | `2²⁵⁷ - 93` |
| Thuật toán mã hóa | AES-256-CBC |

---

## Cấu Trúc Dự Án

```
project-root/
│
├── gui/
│   └── app.py                  # Giao diện đồ họa Tkinter
│
├── scripts/
│   ├── share_generator.py      # Tạo shares và mã hóa cơ sở dữ liệu
│   ├── recovery_secret.py      # Phục hồi bí mật từ các node
│   ├── encrypt_db.py           # Mã hóa cơ sở dữ liệu AES-256
│   ├── decrypt_db.py           # Giải mã cơ sở dữ liệu AES-256
│   └── utils.py                # Toán học đa thức & nội suy Lagrange
│
├── nodes/
│   ├── node1/
│   │   ├── server.js           # Server Node.js giữ share (cổng 3001)
│   │   └── share.json          # Dữ liệu share của node 1
│   ├── node2/                  # (cổng 3002)
│   ├── node3/                  # (cổng 3003)
│   ├── node4/                  # (cổng 3004)
│   └── node5/                  # (cổng 3005)
│
├── database/
│   ├── database.json           # Cơ sở dữ liệu gốc (plaintext)
│   └── database.enc            # Cơ sở dữ liệu đã mã hóa AES-256
│
└── shares/
    ├── original_key.txt        # Bí mật gốc (cần bảo vệ cẩn thận!)
    ├── recovered_key.txt       # Bí mật phục hồi lần cuối
    └── recovery_report.txt     # Nhật ký kiểm tra phục hồi
```

---

## Yêu Cầu Hệ Thống

### Python

- Python 3.8 trở lên
- `pycryptodome`
- `requests`
- `tkinter` (thường đã có sẵn trong Python)

### Node.js

- Node.js 14 trở lên
- Mỗi node server cần cài đặt dependencies riêng

---

## Cài Đặt

**1. Clone repository:**

```bash
git clone https://github.com/ten-cua-ban/the-vault.git
cd the-vault
```

**2. Cài đặt thư viện Python:**

```bash
pip install pycryptodome requests
```

**3. Cài đặt dependencies Node.js cho từng node:**

```bash
for i in 1 2 3 4 5; do
  cd nodes/node$i && npm install && cd ../..
done
```

**4. Chuẩn bị cơ sở dữ liệu:**

Đảm bảo file `database/database.json` tồn tại trước khi chạy ứng dụng.

---

## Hướng Dẫn Sử Dụng

### Khởi Chạy Ứng Dụng

```bash
python gui/app.py
```

### Các Nút Điều Khiển

| Nút | Chức năng |
|-----|-----------|
| **Generate Shares** | Tạo bí mật mới, phân phối shares đến tất cả các node và mã hóa cơ sở dữ liệu |
| **Recover Secret** | Truy vấn các node, tái tạo bí mật bằng nội suy Lagrange và giải mã cơ sở dữ liệu |
| **Check Nodes** | Kiểm tra trạng thái hoạt động của tất cả 5 node |
| **START ALL NODES** | Khởi động toàn bộ 5 server Node.js |
| **STOP ALL NODES** | Dừng toàn bộ 5 server Node.js một cách an toàn |
| **Node N → START/STOP** | Điều khiển từng node riêng lẻ |

### Quy Trình Sử Dụng Thông Thường

```
1. Nhấn "START ALL NODES"    → Khởi động tất cả các server
2. Nhấn "Generate Shares"    → Tạo bí mật mới và phân phối shares
3. Nhấn "Check Nodes"        → Xác nhận tất cả node đang hoạt động
4. Nhấn "Recover Secret"     → Phục hồi bí mật và giải mã cơ sở dữ liệu
```

---

## Kiến Trúc Hệ Thống

### Server Các Node

Mỗi server Node.js lắng nghe tại cổng `3000 + N` và cung cấp các endpoint:

| Endpoint | Phương thức | Mô tả |
|----------|-------------|-------|
| `/share` | GET | Trả về share `(x, y)` của node dưới dạng JSON |
| `/health` | GET | Trả về HTTP 200 nếu node đang hoạt động |
| `/shutdown` | GET | Dừng server node một cách an toàn |

### Các Hàm Toán Học (`utils.py`)

| Hàm | Mô tả |
|-----|-------|
| `polynomial(x, coefficients)` | Tính giá trị đa thức tại điểm `x` trên trường số nguyên tố |
| `recover_secret(shares)` | Thực hiện nội suy Lagrange để tái tạo bí mật từ danh sách shares `(x, y)` |
| `mod_inverse(a)` | Tính nghịch đảo modular sử dụng định lý nhỏ Fermat |

---

## Lưu Ý Bảo Mật

>  **Dự án này được xây dựng cho mục đích học tập và minh họa.**

- File `shares/original_key.txt` lưu bí mật gốc dưới dạng plaintext để kiểm tra. **Xóa hoặc bảo vệ file này trong môi trường thực tế.**
- Trong triển khai thực tế, mỗi node nên chạy trên một máy chủ hoặc mạng riêng biệt và cách ly.
- Khóa AES hiện được lấy trực tiếp từ số nguyên phục hồi. Nên sử dụng KDF (ví dụ: HKDF) trong môi trường production.
- Giao tiếp giữa các node hiện chưa được mã hóa (HTTP thuần). Cần dùng HTTPS với TLS lẫn nhau trong môi trường thực tế.

---

## Giấy Phép

MIT License — xem file [LICENSE](LICENSE) để biết thêm chi tiết.
