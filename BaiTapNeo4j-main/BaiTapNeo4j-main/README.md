# GeometryNeo4j

Project nhỏ mô hình hóa **Tứ giác trong hình học phẳng bằng Neo4j kết hợp Streamlit và SVG Dynamic Simulation**.

## 🚀 Tính năng nổi bật

- **Hệ thống Tri thức (Knowledge Graph)**: Lưu trữ cấu trúc hình học dưới dạng đồ thị tri thức trên Neo4j.
- **Tra cứu thông tin**: Hiển thị tên gọi, định nghĩa, tính chất, dấu hiệu nhận biết, chu vi và diện tích chuẩn xác.
- **Truy vấn quan hệ & Suy luận**: 
  - Khám phá các hình được suy ra từ một hình.
  - Tìm đường suy luận logic (Step-by-step path) giữa hai hình bất kỳ thông qua các điều kiện trung gian.
- **Đồ thị trực quan (Pyvis)**: Trực quan hóa mạng lưới quan hệ bao hàm giữa các hình hình học.
- **Máy tính hình học & Mô phỏng SVG động**: Cung cấp các thanh trượt thông số (sliders) thay đổi theo thời gian thực, hình vẽ SVG tự động co giãn theo tỷ lệ thực tế cùng kết quả tính toán tức thì cho tất cả các loại tứ giác (Hình chữ nhật, Hình vuông, Hình bình hành, Hình thoi, Hình thang, Hình thang cân, Hình thang vuông, Hình tứ giác tổng quát).
- **Giao diện Demo trực quan**: Xây dựng bằng Streamlit và hỗ trợ Neo4j Browser để trực tiếp kiểm tra cấu trúc Graph.

## 📊 Mô hình Graph

Mỗi node (`TuGiac`) lưu trữ các thuộc tính:
```text
tenGoi
tinhChat
nhanBiet
chuVi
dienTich
