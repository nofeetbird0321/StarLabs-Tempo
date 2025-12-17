# Docker 部署指南 🐳

本指南说明如何使用 Docker 部署并自动运行 StarLabs Tempo Bot。

## 前置要求

- 系统已安装 Docker ([安装 Docker](https://docs.docker.com/get-docker/))
- 系统已安装 Docker Compose ([安装 Docker Compose](https://docs.docker.com/compose/install/))
- 您的以太坊钱包私钥
- 有效的代理地址

## 快速开始

### 1. 准备配置文件

在使用 Docker 运行机器人之前，需要设置配置：

#### a. 私钥
复制示例文件并添加您的私钥：
```bash
cp data/private_keys.txt.example data/private_keys.txt
```

编辑 `data/private_keys.txt` 并添加您的私钥（每行一个）：
```
0x1234567890abcdef...
0xabcdef1234567890...
```

#### b. 代理
复制示例文件并添加您的代理：
```bash
cp data/proxies.txt.example data/proxies.txt
```

编辑 `data/proxies.txt` 并添加您的代理（每行一个）：
```
http://user:pass@ip:port
http://user2:pass2@ip2:port2
```

#### c. 配置
编辑 `config.yaml` 自定义机器人行为：
- 线程数量
- 任务选择
- 暂停设置
- 代币发送配置
- 等等

### 2. 构建 Docker 镜像

构建 Docker 镜像：
```bash
docker-compose build
```

### 3. 运行机器人

#### 方式 A: 使用 Docker Compose（推荐）
```bash
docker-compose up
```

后台运行（分离模式）：
```bash
docker-compose up -d
```

#### 方式 B: 直接使用 Docker
```bash
docker build -t starlabs-tempo-bot .
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs -v $(pwd)/config.yaml:/app/config.yaml:ro starlabs-tempo-bot
```

#### 方式 C: 使用快速启动脚本
```bash
./docker-start.sh
```

### 4. 查看日志

如果以分离模式运行：
```bash
docker-compose logs -f
```

或查看日志目录：
```bash
tail -f logs/app.log
```

## 停止机器人

如果以分离模式运行：
```bash
docker-compose down
```

如果在前台运行，按 `Ctrl+C`。

## 自动执行

Docker 容器配置为自动执行：
- 入口脚本自动验证配置文件
- 机器人自动开始挖矿（选项 1），无需手动输入
- `tasks.py` 中定义的所有任务将自动执行

## 卷挂载

Docker 容器使用以下卷挂载：

| 主机路径 | 容器路径 | 用途 |
|---------|---------|------|
| `./data` | `/app/data` | 持久化数据（密钥、代理、数据库）|
| `./logs` | `/app/logs` | 应用程序日志 |
| `./config.yaml` | `/app/config.yaml` | 配置文件（只读）|

这确保了：
- 您的私钥和代理不会嵌入镜像中
- 日志在容器重启后保持
- 数据库状态被维护
- 可以在不重建的情况下更新配置

## 配置管理

### 更新配置

1. 停止容器：
```bash
docker-compose down
```

2. 编辑 `config.yaml` 进行更改

3. 重启容器：
```bash
docker-compose up -d
```

### 更新任务

1. 停止容器
2. 编辑 `tasks.py` 修改任务配置
3. 重建并重启：
```bash
docker-compose up -d --build
```

## 故障排除

### 容器立即退出

查看日志以获取错误：
```bash
docker-compose logs
```

常见问题：
- `data/private_keys.txt` 缺失或为空
- `data/proxies.txt` 缺失或为空
- `config.yaml` 语法无效

### 权限问题

如果遇到挂载卷的权限问题：
```bash
sudo chown -R $(whoami):$(whoami) data/ logs/
```

### 数据库问题

如果需要重置数据库：
```bash
rm data/accounts.db
docker-compose restart
```

## 高级用法

### 运行特定任务

在构建前编辑 `tasks.py` 选择要运行的任务：
```python
TASKS = ["FAUCET"]  # 只运行水龙头
# 或
TASKS = ["FAUCET", "TOKEN_SENDER"]  # 运行两者
```

### 多个实例

使用不同配置运行多个实例：

1. 创建单独的目录：
```bash
mkdir instance1 instance2
```

2. 复制文件到每个目录：
```bash
cp -r data/ config.yaml docker-compose.yml instance1/
cp -r data/ config.yaml docker-compose.yml instance2/
```

3. 编辑每个 `docker-compose.yml` 使用不同的容器名称：
```yaml
services:
  tempo-bot:
    container_name: starlabs-tempo-bot-1  # 为每个实例更改
```

4. 运行每个实例：
```bash
cd instance1 && docker-compose up -d
cd instance2 && docker-compose up -d
```

### 自定义 Docker 网络

将机器人隔离在自定义网络中：
```bash
docker network create tempo-network
```

更新 `docker-compose.yml`：
```yaml
networks:
  default:
    external:
      name: tempo-network
```

## 安全最佳实践

1. **永远不要提交敏感数据**：
   - 将 `data/private_keys.txt` 添加到 `.gitignore`
   - 将 `data/proxies.txt` 添加到 `.gitignore`

2. **使用安全的文件权限**：
```bash
chmod 600 data/private_keys.txt
chmod 600 data/proxies.txt
```

3. **定期更新依赖项**：
```bash
docker-compose build --no-cache
```

4. **监控日志以发现可疑活动**：
```bash
tail -f logs/app.log
```

## 环境变量

您可以在 `docker-compose.yml` 中使用环境变量覆盖设置：

```yaml
environment:
  - TZ=Asia/Shanghai  # 设置时区
  - PYTHONUNBUFFERED=1   # 实时日志输出
```

## 定时执行

要按计划运行机器人，使用 cron（Linux/Mac）或任务计划程序（Windows）。

cron 作业示例（每天凌晨 2 点运行）：
```bash
0 2 * * * cd /path/to/StarLabs-Tempo && docker-compose up >> /var/log/tempo-bot.log 2>&1
```

## 支持

如有问题和疑问：
- Telegram 频道：[@StarLabsTech](https://t.me/StarLabsTech)
- Telegram 聊天：[@StarLabsChat](https://t.me/StarLabsChat)
- GitHub: [0xStarLabs](https://github.com/0xStarLabs)

## 快速命令参考

```bash
# 构建镜像
docker-compose build

# 启动（前台）
docker-compose up

# 启动（后台）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down

# 重启
docker-compose restart

# 重建并启动
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 进入容器
docker-compose exec tempo-bot bash
```
