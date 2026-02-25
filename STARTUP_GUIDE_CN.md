# StarLabs Tempo Bot - 启动指南 🚀

这份指南解释了改进的启动流程和运行机器人的所有可用选项。

## 📋 目录

- [快速开始（最简单的方式）](#快速开始最简单的方式)
- [详细设置指南](#详细设置指南)
- [命令行选项](#命令行选项)
- [配置文件](#配置文件)
- [常见问题](#常见问题)

## 🎯 快速开始（最简单的方式）

### 首次设置

**方式1：向导式设置（推荐新手使用）**

Linux/Mac:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
chmod +x setup.sh
./setup.sh
```

设置向导会：
- 检查Python安装
- 创建配置文件
- 引导你编辑私钥和代理
- 安装所有依赖
- 验证你的配置

**方式2：使用启动脚本自动设置**

Linux/Mac:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
./start.sh
```

Windows:
```cmd
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
start.bat
```

脚本会自动：
- 检测Python安装
- 创建虚拟环境
- 安装依赖
- 从示例文件设置配置
- 提示你编辑配置（如需要）
- 启动机器人

## 📖 详细设置指南

### 第一步：克隆仓库

```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
```

### 第二步：准备配置文件

脚本会自动从示例创建这些文件，但你需要填入你的数据：

**data/private_keys.txt**
```
0x你的私钥1
0x你的私钥2
0x你的私钥3
```

**data/proxies.txt**
```
http://用户名1:密码1@IP1:端口1
http://用户名2:密码2@IP2:端口2
http://用户名3:密码3@IP3:端口3
```

### 第三步：配置设置（可选）

编辑 `config.yaml` 来自定义：
- 并发线程数
- 重试次数
- 暂停间隔
- 代币发送设置
- DEX交换设置
- Telegram日志（可选）

### 第四步：运行机器人

**交互模式（显示菜单）：**
```bash
./start.sh              # Linux/Mac
start.bat               # Windows
```

**自动启动模式（直接开始farming）：**
```bash
./start.sh --auto       # Linux/Mac
start.bat --auto        # Windows
```

## ⚙️ 命令行选项

### 启动脚本选项

**Linux/Mac (start.sh):**

```bash
# 交互模式（显示菜单）
./start.sh

# 自动启动farming（跳过菜单）
./start.sh --auto
./start.sh --start
./start.sh -s

# 直接选择菜单选项
./start.sh --option 1    # 开始farming
./start.sh --option 2    # 编辑配置
./start.sh --option 3    # 数据库操作
./start.sh --option 4    # 退出
./start.sh -o 1          # 简写形式

# 显示帮助
./start.sh --help
./start.sh -h
```

**Windows (start.bat):**

```cmd
REM 交互模式（显示菜单）
start.bat

REM 自动启动farming
start.bat --auto

REM 直接选择菜单选项
start.bat --option 1
start.bat --option 2
```

### 直接Python执行

你也可以直接用Python运行机器人（在安装依赖后）：

```bash
# 交互模式
python main.py

# 自动启动farming
python main.py --auto
python main.py --start

# 直接菜单选择
python main.py --option 1
python main.py -o 2

# 跳过logo显示
python main.py --no-logo

# 显示帮助
python main.py --help
python main.py -h
```

## 📝 配置文件

### data/private_keys.txt

格式：每行一个私钥

```text
0x1234567890abcdef...
0xabcdef1234567890...
```

**安全提示：**
- 永远不要分享你的私钥
- 保护好这个文件
- 已添加到 `.gitignore`

### data/proxies.txt

格式：每行一个代理

支持的格式：
```text
http://用户名:密码@IP:端口
http://IP:端口
socks5://用户名:密码@IP:端口
```

**代理提示：**
- 使用住宅或数据中心代理
- 运行前确保代理正常工作
- 推荐每个钱包使用一个代理

### config.yaml

需要自定义的关键设置：

```yaml
SETTINGS:
  THREADS: 1                    # 并发账户数 (1-10)
  ATTEMPTS: 5                   # 重试次数
  SHUFFLE_WALLETS: true         # 随机顺序

TOKEN_SENDER:
  SEND_TOKENS_TO_MY_WALLETS: false
  PERCENT_OF_BALANCE_TO_SEND: [5, 10]

DEX_SWAPS:
  NUMBER_OF_SWAPS_TO_PERFORM: [1, 3]
  PERCENT_OF_BALANCE_TO_SWAP: [10, 30]
  SLIPPAGE_TOLERANCE: 1
```

## 🎮 使用示例

### 示例1：首次使用

```bash
# 克隆并运行设置向导
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
./setup.sh

# 设置完成后，开始farming
./start.sh --auto
```

### 示例2：每日快速运行

```bash
cd StarLabs-Tempo
./start.sh --auto
```

### 示例3：编辑配置

```bash
cd StarLabs-Tempo
./start.sh --option 2
```

### 示例4：检查数据库状态

```bash
cd StarLabs-Tempo
./start.sh --option 3
```

## 🐳 Docker使用

用于自动化、定时运行：

```bash
# 快速启动
./docker-start.sh

# 或手动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

详见 [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md) 获取Docker详细说明。

## 🔧 常见问题

### 问题："未安装Python"

**解决方案：**
- 从 https://www.python.org/downloads/ 安装Python 3.11+
- 确保Python在系统PATH中
- 尝试使用 `python3` 而不是 `python`

### 问题："依赖安装失败"

**解决方案：**
```bash
# 先更新pip
pip install --upgrade pip

# 手动安装
pip install -r requirements.txt

# 如果仍然失败，使用详细输出
pip install -v -r requirements.txt
```

### 问题："配置文件包含示例数据"

**解决方案：**
- 编辑 `data/private_keys.txt` 用真实私钥替换示例密钥
- 编辑 `data/proxies.txt` 用真实代理替换示例代理
- 再次运行启动脚本

### 问题："未找到代理"

**解决方案：**
- 确保 `data/proxies.txt` 存在且不为空
- 检查代理格式：`http://用户名:密码@IP:端口`
- 确认每行至少有一个代理

### 问题：Linux/Mac上"权限被拒绝"

**解决方案：**
```bash
chmod +x start.sh
chmod +x setup.sh
chmod +x docker-start.sh
```

### 问题：虚拟环境激活失败

**解决方案：**
```bash
# 删除并重新创建
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows
```

## 📊 各脚本功能说明

### start.sh / start.bat

**用途：** 一体化启动脚本

**功能：**
- 检查Python安装
- 自动创建虚拟环境
- 按需安装依赖
- 验证配置文件
- 使用选项启动机器人

**何时使用：** 每次想运行机器人时

### setup.sh

**用途：** 交互式首次设置向导

**功能：**
- 引导式配置文件创建
- 在编辑器中打开文件便于编辑
- 验证配置
- 安装依赖
- 提供下一步操作

**何时使用：** 首次设置，或需要引导帮助时

### docker-start.sh

**用途：** Docker容器启动

**功能：**
- 验证Docker安装
- 设置配置文件
- 构建Docker镜像
- 在前台或后台启动容器

**何时使用：** 用于自动化、定时或隔离运行

## 🎯 最佳实践

1. **首次使用：** 运行 `./setup.sh` 进行引导式设置
2. **日常使用：** 运行 `./start.sh --auto` 快速farming
3. **测试：** 运行 `./start.sh`（交互式）测试新配置
4. **自动化：** 使用Docker和 `./docker-start.sh` 进行定时运行
5. **维护：** 在配置文件中保持代理和私钥更新

## 💡 提示

1. **节省时间：** 使用 `--auto` 标志跳过菜单选择
2. **先测试：** 从1-2个钱包开始测试配置
3. **监控日志：** 检查 `logs/app.log` 获取详细信息
4. **代理轮换：** 为不同账户使用不同代理
5. **保持更新：** 定期使用 `git pull` 检查更新

## 🆘 需要帮助？

如果遇到问题：

1. 查看本指南的常见问题部分
2. 查看终端和日志中的错误消息
3. 确保所有配置文件正确
4. 加入我们的社区：
   - Telegram频道：[@StarLabsTech](https://t.me/StarLabsTech)
   - Telegram聊天：[@StarLabsChat](https://t.me/StarLabsChat)
   - GitHub问题：[报告bug](https://github.com/0xStarLabs/StarLabs-Tempo/issues)

---

**StarLabs团队用❤️制作**
