# The Vault - Shamir Secret Sharing

The Vault - Distributed Secret System một ứng dụng quản lý bí mật phân tán sử dụng thuật toán Chia sẻ bí mật của Shamir (Shamir's Secret Sharing - SSS) kết hợp với mã hóa đối xứng AES-256. Hệ thống cho phép chia nhỏ một khóa Master Key thành nhiều phần (shares) và lưu trữ phân tán trên các nút (nodes) độc lập.

Tính năng chính
    Phân tách bí mật (Threshold Scheme): Sử dụng sơ đồ ngưỡng (3, 5). Khóa bí mật được chia thành 5 phần, nhưng chỉ cần ít nhất 3 phần bất kỳ để khôi phục lại hoàn toàn.
    Mã hóa Cơ sở dữ liệu: Tự động tạo khóa AES-256 ngẫu nhiên để mã hóa tệp tin database.json.
    Quản lý Node tập trung: Giao diện GUI (Tkinter) cho phép khởi chạy, dừng và kiểm tra trạng thái của 5 Node lưu trữ riêng biệt.
    Khôi phục an toàn: Quá trình khôi phục sử dụng nội suy Lagrange trên trường hữu hạn (Finite Field) với số nguyên tố lớn ($2^{257} - 93).
    Báo cáo chi tiết: Tự động tạo báo cáo sau mỗi lần khôi phục khóa để kiểm tra tính toàn vẹn.

Kiến trúc hệ thống
Dự án bao gồm các thành phần chính:
    Frontend (Python Tkinter): Bảng điều khiển chính để điều phối hoạt động.
    Backend Nodes (Node.js/Express): (Giả lập) Các máy chủ lưu trữ từng phần khóa (Share) và cung cấp qua API.
    Cryptographic Core (Python): Xử lý toán học cho SSS và mã hóa AES. 

Cấu trúc thư mục
    app.py: Tệp chạy chính, chứa giao diện người dùng và quản lý tiến trình.
    share_generator.py: Tạo khóa Master, chia nhỏ khóa và phân phối tới các Node.
    recovery_secret.py: Thu thập các phần khóa từ các Node đang Online và khôi phục khóa.
    encrypt_database.py / decrypt_database.py: Xử lý mã hóa/giải mã tệp dữ liệu bằng AES.
    utils.py: Chứa các hàm toán học (nội suy Lagrange, nghịch đảo modulo, đa thức).
    nodes/: Thư mục chứa dữ liệu và mã nguồn cho từng Node lưu trữ.

Hướng dẫn sử dụng
    1. Yêu cầu hệ thống
    Python 3.x
    Node.js (để chạy các node server)
    Thư viện Python: pycryptodome, requests
    2. Khởi chạy ứng dụng
    Chạy tệp giao diện chính: python app.py
    3. Quy trình thực hiện
    Generate Shares: Nhấn nút này để tạo khóa mới. Hệ thống sẽ mã hóa database và chia khóa vào 5 thư mục node.
    Check Nodes: Kiểm tra xem các Node có đang Online hay không.
    Recover Secret: Hệ thống sẽ lấy ngẫu nhiên 3 phần khóa từ các Node đang Online để giải mã cơ sở dữ liệu.

Lưu ý bảo mật
Dự án này được thiết kế cho mục đích giáo dục và minh họa cơ chế.
Trong môi trường thực tế, các Node cần được triển khai trên các máy chủ vật lý khác nhau và kết nối qua HTTPS.
Trong dự án này, file original_key.txt được lưu để đối chiếu kết quả phục hồi khóa, trong thực tế nên được lưu bằng mã băm vì lý do bảo mật.