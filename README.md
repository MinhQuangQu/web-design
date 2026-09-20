# Week 07 — FastAPI Routing & Request/Response

## Chạy ứng dụng

Từ thư mục gốc project:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Mở frontend: <http://127.0.0.1:8000/static/house_form.html>

Tài liệu API tự sinh: <http://127.0.0.1:8000/docs>

## Các chức năng đã thực hiện

- `GET /items`: lọc theo `min_price`, `max_price`, tìm tên bằng `q` (không phân biệt hoa thường), sắp xếp theo `sort_by=id|name|price` và `order=asc|desc`, rồi phân trang bằng `skip` và `limit`.
- Kết quả danh sách có dạng `{ "items": [...], "total": 0, "skip": 0, "limit": 10 }`. `total` là số item sau lọc, trước phân trang.
- `POST /items` và thao tác đổi tên qua `PUT`/`PATCH` trả `409` nếu trùng tên (không phân biệt hoa thường).
- `PATCH /items/{item_id}` chỉ cập nhật các trường có trong JSON body. Ví dụ:

  ```json
  { "price": 120000 }
  ```

- `POST /predict/house-price` nhận `area_sqm`, `bedrooms`, `distance_to_center_km` và trả giá dự đoán giả lập bằng VND. `area_sqm` phải lớn hơn 0 và `bedrooms` không được âm.

Frontend là HTML thuần, không dùng CSS. Trang hỗ trợ CRUD, lọc/tìm kiếm/sắp xếp/phân trang và gửi request dự đoán.
