# ChromaDB 远程服务器部署指南

本指南将帮助你在另一台服务器上部署 ChromaDB，并让你的应用连接到远程服务器。

## 🎯 方案优势

- ✅ **完全免费**：使用你自己的服务器，无需付费
- ✅ **数据集中**：多台开发机可以共享同一个向量数据库
- ✅ **性能优化**：数据服务器可以使用更好的硬件
- ✅ **数据安全**：数据集中管理和备份
- ✅ **灵活部署**：可以随时切换本地/远程模式

---

## 第一步：在数据服务器上部署 ChromaDB

### 方法 1：使用 Docker（最简单，推荐）

```bash
# 1. 安装 Docker（如果还没安装）
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# 2. 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 3. 创建数据目录
sudo mkdir -p /data/chromadb
sudo chmod 777 /data/chromadb

# 4. 运行 ChromaDB 容器
sudo docker run -d \
  --name chromadb-server \
  --restart always \
  -p 8000:8000 \
  -v /data/chromadb:/chroma/chroma \
  -e ALLOW_RESET=TRUE \
  -e ANONYMIZED_TELEMETRY=FALSE \
  chromadb/chroma:latest

# 5. 查看运行状态
sudo docker ps | grep chromadb
sudo docker logs chromadb-server

# 6. 测试服务
curl http://localhost:8000/api/v1/heartbeat
```

### 方法 2：使用 Python 直接运行

```bash
# 1. 安装 Python 和 pip（如果还没安装）
sudo apt update
sudo apt install python3 python3-pip

# 2. 安装 ChromaDB
pip3 install chromadb

# 3. 创建启动脚本
cat > /opt/chromadb/start_server.sh << 'EOF'
#!/bin/bash
export CHROMA_HOST="0.0.0.0"
export CHROMA_PORT=8000
export PERSIST_DIRECTORY="/data/chromadb"

chroma run --host $CHROMA_HOST --port $CHROMA_PORT --path $PERSIST_DIRECTORY
EOF

chmod +x /opt/chromadb/start_server.sh

# 4. 启动服务
/opt/chromadb/start_server.sh

# 或者使用 systemd 管理服务
sudo cat > /etc/systemd/system/chromadb.service << 'EOF'
[Unit]
Description=ChromaDB Vector Database
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/chromadb
ExecStart=/usr/local/bin/chroma run --host 0.0.0.0 --port 8000 --path /data/chromadb
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start chromadb
sudo systemctl enable chromadb
sudo systemctl status chromadb
```

### 方法 3：使用 Docker Compose（推荐用于生产环境）

```bash
# 1. 创建项目目录
mkdir -p /opt/chromadb
cd /opt/chromadb

# 2. 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb-server
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./data:/chroma/chroma
    environment:
      - ALLOW_RESET=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
      - CHROMA_SERVER_AUTHN_CREDENTIALS=admin:your-password-here  # 可选：添加认证
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.basic.BasicAuthServerProvider  # 可选
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

---

## 第二步：配置防火墙和网络

### Linux 防火墙配置

```bash
# Ubuntu/Debian (使用 ufw)
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS/RHEL (使用 firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 检查端口是否监听
sudo netstat -tlnp | grep 8000
```

### 云服务器安全组配置

如果使用阿里云、腾讯云、AWS 等，需要在控制台配置安全组：

1. 登录云服务器控制台
2. 找到你的服务器实例
3. 配置安全组规则
4. 添加入站规则：
   - 协议：TCP
   - 端口：8000
   - 源地址：你的开发机 IP（或 0.0.0.0/0 允许所有）

---

## 第三步：在你的应用中配置远程连接

### 配置示例 1：连接到局域网服务器

打开 `core/config.py`，修改：

```python
@dataclass
class Config:
    # ... 其他配置 ...
    
    # 向量存储配置
    vector_store_type: str = "chromadb"  # 使用 ChromaDB
    chromadb_collection_name: str = "rag_documents"
    
    # ChromaDB 远程服务器配置
    chromadb_remote_host: str = "192.168.1.100"  # 👈 你的数据服务器 IP
    chromadb_remote_port: int = 8000
    chromadb_use_ssl: bool = False
    chromadb_api_token: str = None  # 如果服务器需要认证，填写 token
```

### 配置示例 2：连接到公网服务器

```python
@dataclass
class Config:
    # ... 其他配置 ...
    
    vector_store_type: str = "chromadb"
    chromadb_collection_name: str = "rag_documents"
    
    # ChromaDB 远程服务器配置
    chromadb_remote_host: str = "chromadb.example.com"  # 👈 你的域名或公网 IP
    chromadb_remote_port: int = 8000
    chromadb_use_ssl: bool = False  # 如果配置了 HTTPS，改为 True
    chromadb_api_token: str = None
```

### 配置示例 3：使用本地模式（默认）

```python
@dataclass
class Config:
    # ... 其他配置 ...
    
    vector_store_type: str = "chromadb"
    chromadb_collection_name: str = "rag_documents"
    
    # ChromaDB 远程服务器配置
    chromadb_remote_host: str = None  # 👈 None 表示使用本地模式
    chromadb_remote_port: int = 8000
```

---

## 第四步：测试连接

### 1. 测试服务器是否可访问

在你的开发机上运行：

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "http://192.168.1.100:8000/api/v1/heartbeat"

# 或使用 curl（如果安装了）
curl http://192.168.1.100:8000/api/v1/heartbeat
```

**预期响应：**
```json
{"nanosecond heartbeat": 1234567890}
```

### 2. 测试 Python 连接

```powershell
python
```

```python
import chromadb

# 连接到远程服务器
client = chromadb.HttpClient(host="192.168.1.100", port=8000)

# 测试连接
print(client.heartbeat())  # 应该返回时间戳

# 查看集合
collections = client.list_collections()
print(f"集合数量: {len(collections)}")

exit()
```

### 3. 启动你的应用

```powershell
python launcher.py --https
```

**查看日志，应该看到：**
```
✅ ChromaDB 可用（远程模式: http://192.168.1.100:8000）
SUCCESS: RAG服务初始化完成，使用: ChromaDB
🌐 连接到远程ChromaDB服务器 192.168.1.100:8000...
✅ 连接远程ChromaDB成功，包含 0 个文档
```

---

## 第五步：性能优化建议

### 1. 网络优化

```bash
# 在数据服务器上调整网络参数
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8192
```

### 2. 使用 Nginx 反向代理（可选）

```nginx
# /etc/nginx/sites-available/chromadb
server {
    listen 80;
    server_name chromadb.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 增加超时时间（向量搜索可能需要较长时间）
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

### 3. 配置 HTTPS（推荐）

```bash
# 使用 Let's Encrypt 申请免费证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d chromadb.example.com
```

然后在你的配置中启用 SSL：
```python
chromadb_use_ssl: bool = True
```

---

## 🔒 安全建议

### 1. 启用认证（推荐）

在服务器上配置基本认证：

```bash
# docker-compose.yml
environment:
  - CHROMA_SERVER_AUTHN_CREDENTIALS=admin:your-strong-password
  - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.basic.BasicAuthServerProvider
```

在应用配置中添加：
```python
chromadb_api_token: str = "admin:your-strong-password"
```

### 2. 限制访问 IP

```bash
# 使用防火墙只允许特定 IP 访问
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw deny 8000
```

### 3. 使用 VPN 或 SSH 隧道

```bash
# 在开发机上创建 SSH 隧道
ssh -L 8000:localhost:8000 user@your-server-ip

# 然后在配置中使用 localhost
chromadb_remote_host: str = "localhost"
```

---

## 📊 监控和维护

### 查看服务状态

```bash
# Docker 方式
docker ps
docker logs chromadb-server
docker stats chromadb-server

# Systemd 方式
sudo systemctl status chromadb
sudo journalctl -u chromadb -f

# 磁盘使用
du -sh /data/chromadb
```

### 备份数据

```bash
# 停止服务
docker stop chromadb-server

# 备份数据
tar -czf chromadb_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data/chromadb

# 启动服务
docker start chromadb-server

# 或者使用 rsync 增量备份
rsync -avz /data/chromadb/ /backup/chromadb/
```

---

## 🚀 完整部署脚本

保存为 `deploy_chromadb.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 开始部署 ChromaDB 服务器..."

# 1. 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "📦 安装 Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 2. 创建数据目录
echo "📁 创建数据目录..."
sudo mkdir -p /data/chromadb
sudo chmod 777 /data/chromadb

# 3. 拉取镜像
echo "🐳 拉取 ChromaDB 镜像..."
sudo docker pull chromadb/chroma:latest

# 4. 停止旧容器（如果存在）
if [ "$(sudo docker ps -aq -f name=chromadb-server)" ]; then
    echo "🛑 停止旧容器..."
    sudo docker stop chromadb-server
    sudo docker rm chromadb-server
fi

# 5. 启动新容器
echo "▶️  启动 ChromaDB 服务..."
sudo docker run -d \
  --name chromadb-server \
  --restart always \
  -p 8000:8000 \
  -v /data/chromadb:/chroma/chroma \
  -e ALLOW_RESET=TRUE \
  -e ANONYMIZED_TELEMETRY=FALSE \
  chromadb/chroma:latest

# 6. 配置防火墙
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8000/tcp
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
fi

# 7. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 8. 测试服务
echo "🧪 测试服务..."
if curl -f http://localhost:8000/api/v1/heartbeat; then
    echo ""
    echo "✅ ChromaDB 部署成功！"
    echo "📍 服务地址: http://$(hostname -I | awk '{print $1}'):8000"
    echo "📊 查看日志: sudo docker logs -f chromadb-server"
    echo "🛑 停止服务: sudo docker stop chromadb-server"
else
    echo "❌ 服务测试失败，请检查日志"
    sudo docker logs chromadb-server
fi
```

运行部署脚本：
```bash
chmod +x deploy_chromadb.sh
sudo ./deploy_chromadb.sh
```

---

## 💡 使用场景

### 场景 1：多台开发机共享数据
- 办公室有多台电脑
- 在数据服务器上部署 ChromaDB
- 所有开发机连接到同一个服务器
- 数据共享，协同工作

### 场景 2：笔记本 + 台式机
- 笔记本外出使用（本地模式）
- 在家/办公室连接台式机（远程模式）
- 灵活切换

### 场景 3：生产环境部署
- 专用服务器运行 ChromaDB
- 应用服务器连接向量数据库
- 数据集中管理和备份

---

## ❓ 常见问题

### Q: 远程连接速度慢怎么办？
**A**: 
1. 检查网络带宽
2. 使用局域网连接
3. 调整 chunk_size 减少请求次数
4. 考虑在服务器上部署整个应用

### Q: 如何在本地和远程模式之间切换？
**A**: 只需修改配置文件：
```python
# 本地模式
chromadb_remote_host: str = None

# 远程模式
chromadb_remote_host: str = "192.168.1.100"
```

### Q: 数据如何从本地迁移到远程？
**A**: 
```bash
# 1. 备份本地数据
tar -czf local_chromadb.tar.gz data/vector_store

# 2. 传输到服务器
scp local_chromadb.tar.gz user@server:/tmp/

# 3. 在服务器上解压
ssh user@server
cd /data
tar -xzf /tmp/local_chromadb.tar.gz
```

### Q: 服务器重启后数据会丢失吗？
**A**: 不会！使用 `-v` 挂载了数据卷，数据持久化在 `/data/chromadb`

---

**🎉 恭喜！你已经成功部署了 ChromaDB 远程服务器！**
