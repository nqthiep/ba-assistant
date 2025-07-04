# BA Assistant

BA Assistant là trợ lý phân tích nghiệp vụ (Business Analyst Assistant) hỗ trợ các nhóm phát triển phần mềm trong việc xử lý tài liệu, tạo knowledge graph, truy vấn thông tin và tương tác tự động hóa với các công cụ hiện đại như LLM, LangChain, Chainlit, Supabase, v.v.

## 1. Tạo Conda Environment

Khuyến nghị sử dụng Python 3.11 để đảm bảo tương thích với các thư viện.

```bash
# Tạo environment mới tên là BAAssistant với Python 3.10
conda create -n BAAssistant python=3.11 -y

# Kích hoạt environment
conda activate BAAssistant
```

## 2. Cài đặt Poetry

Poetry là công cụ quản lý dependencies hiện đại cho Python.

```bash
# Cài đặt Poetry (nếu chưa có)
pip install poetry
```

## 3. Cài đặt Dependencies

Sau khi đã kích hoạt conda environment và cài Poetry:

```bash
# Cài đặt toàn bộ dependencies từ pyproject.toml
poetry install --no-root
```

Nếu bạn muốn sử dụng đúng environment Python đã tạo với conda:

```bash
# Poetry sử dụng Python của conda environment hiện tại
poetry env use $(which python)
```

## 4. Chạy Ứng Dụng BA Assistant

Ứng dụng sử dụng Chainlit làm front-end. Đảm bảo bạn đang ở đúng thư mục dự án:

```bash
# Chạy ứng dụng ở chế độ phát triển (hot reload)
chainlit run app.py -w
```

Truy cập vào [http://localhost:8000](http://localhost:8000) trên trình duyệt để bắt đầu sử dụng BA Assistant.

---

### Thông tin thêm
- Cấu trúc mã nguồn tuân thủ Clean Code & SOLID.
- Các file cấu hình quan trọng: `.env`, `pyproject.toml`, `config/settings.py`, ...
- Để đóng góp hoặc báo lỗi, vui lòng tạo issue trên repository.