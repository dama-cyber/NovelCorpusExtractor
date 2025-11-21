# 后端部署指南

本文档介绍如何部署 NovelCorpusExtractor 后端API服务。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml` 文件，设置：
- API密钥（OpenAI、Gemini等）
- 拓扑模式
- 输出目录等

### 3. 启动服务器

**Windows:**
```bash
start_api.bat
```

**Linux/Mac:**
```bash
chmod +x start_api.sh
./start_api.sh
```

**或直接使用Python:**
```bash
python api_server.py
```

服务器默认运行在 `http://localhost:8000`

## 环境变量

可以通过环境变量配置服务器：

- `CONFIG_PATH`: 配置文件路径（默认: `config.yaml`）
- `PORT`: 服务器端口（默认: `8000`）
- `HOST`: 服务器主机（默认: `0.0.0.0`）

示例：
```bash
export PORT=8080
export CONFIG_PATH=production_config.yaml
python api_server.py
```

## API接口

### 健康检查
```
GET /api/health
```

### 处理小说
```
POST /api/process
Content-Type: multipart/form-data

参数:
- file: 小说文件（可选）
- novel_type: 小说类型（如：玄幻、都市、言情）
- topology_mode: 拓扑模式（auto/linear/triangular/swarm）
- api_pool_mode: API池模式（auto/single/triple/swarm）
- sample_text: 示例文本（可选，当没有文件时使用）
- workflow_targets: 工作流目标列表（JSON字符串）
- run_creative_flow: 是否运行创作流程（true/false）
```

### 获取配置
```
GET /api/config
```

## 生产环境部署

### 使用 Gunicorn (推荐)

```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py"]
```

构建和运行：
```bash
docker build -t novel-extractor-api .
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml novel-extractor-api
```

### 使用 systemd (Linux)

创建 `/etc/systemd/system/novel-extractor.service`:

```ini
[Unit]
Description=NovelCorpusExtractor API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/NovelCorpusExtractor
Environment="CONFIG_PATH=/path/to/config.yaml"
Environment="PORT=8000"
ExecStart=/usr/bin/python3 api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable novel-extractor
sudo systemctl start novel-extractor
```

## 反向代理 (Nginx)

示例 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 文件上传大小限制
        client_max_body_size 100M;
    }
}
```

## 安全建议

1. **CORS配置**: 生产环境应限制 `allow_origins` 为特定域名
2. **API密钥**: 使用环境变量存储API密钥，不要提交到代码仓库
3. **HTTPS**: 使用反向代理（如Nginx）配置HTTPS
4. **速率限制**: 考虑添加速率限制中间件
5. **认证**: 如需保护API，添加认证机制

## 故障排查

### 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# 使用其他端口
export PORT=8080
python api_server.py
```

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 单独安装问题依赖
pip install fastapi uvicorn python-multipart
```

### 配置文件错误
确保 `config.yaml` 文件存在且格式正确，检查API密钥是否设置。

## 监控和日志

日志文件默认保存在 `novel_extractor.log`，可以通过修改日志配置调整日志级别和输出位置。


