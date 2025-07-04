---
trigger: always_on
---

├── app.py                      # Điểm khởi đầu của ứng dụng Chainlit.
├── .env                        # Biến môi trường (không commit vào Git).
├── documents/                  # Chứa các tài liệu dự án đầu vào.
│   ├── requirements/           # Tài liệu yêu cầu nghiệp vụ.
│   ├── design_docs/            # Tài liệu thiết kế kỹ thuật.
│   └── user_manuals/           # Hướng dẫn sử dụng.
├── knowledge_graph/            # Lưu trữ knowledge graph và schema.
│   └── schema/                 # Định nghĩa schema cho knowledge graph.
│       └── kg_schema.py        # Định nghĩa cấu trúc KG.
│   └── generated_kgs/          # Nơi lưu trữ các knowledge graph đã tạo.
│       └── project_kg_v1.json  # Ví dụ về KG đã tạo.
├── agents/                     # Định nghĩa và logic cho các agent.
│   └── ba_agent.py             # Định nghĩa chính của agent BA Assistant.
│   └── tools/                  # Các công cụ tùy chỉnh cho agent.
│       └── kg_query_tool.py    # Công cụ truy vấn knowledge graph.
├── ui/                         # Chứa code Python tùy chỉnh cho giao diện Chainlit.
│   └── custom_ui_logic.py      # Ví dụ về code Python tùy chỉnh UI.
├── utils/                      # Các hàm tiện ích dùng chung.
│   ├── document_processor.py   # Xử lý tài liệu sang markdown.
│   ├── kg_generator.py         # Chuyển tài liệu markdown thành knowledge graph.
│   └── graphiti_client.py      # Client kết nối Graphiti.
│   └── data_quality_checks.py  # Kiểm tra chất lượng Knowledge Graph.
├── database/                   # Logic tương tác với Supabase.
│   └── supabase_client.py      # Client kết nối Supabase.
│   └── models.py               # Định nghĩa các mô hình dữ liệu.
├── config/                     # Các tệp cấu hình ứng dụng.
│   └── settings.py             # Cài đặt cấu hình ứng dụng.
│   └── .env.example            # Mẫu tệp môi trường.
├── tests/                      # Chứa các tệp kiểm thử.
│   ├── unit/                   # Unit tests.
│   └── integration/            # Integration tests.
├── logs/                       # Thư mục lưu trữ file log.
├── requirements.txt            # Danh sách thư viện Python.
├── Dockerfile                  # Tệp Dockerfile đóng gói ứng dụng.
└── README.md                   # Mô tả dự án và hướng dẫn sử dụng.