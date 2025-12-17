# Docker Deployment Guide 🐳

This guide explains how to deploy and run StarLabs Tempo Bot using Docker for automatic execution.

## Prerequisites

- Docker installed on your system ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Your Ethereum wallet private keys
- Valid proxy addresses

## Quick Start

### 1. Prepare Configuration Files

Before running the bot in Docker, you need to set up your configuration:

#### a. Private Keys
Copy the example file and add your private keys:
```bash
cp data/private_keys.txt.example data/private_keys.txt
```

Edit `data/private_keys.txt` and add your private keys (one per line):
```
0x1234567890abcdef...
0xabcdef1234567890...
```

#### b. Proxies
Copy the example file and add your proxies:
```bash
cp data/proxies.txt.example data/proxies.txt
```

Edit `data/proxies.txt` and add your proxies (one per line):
```
http://user:pass@ip:port
http://user2:pass2@ip2:port2
```

#### c. Configuration
Edit `config.yaml` to customize bot behavior:
- Number of threads
- Task selection
- Pause settings
- Token sender configuration
- etc.

### 2. Build Docker Image

Build the Docker image:
```bash
docker-compose build
```

### 3. Run the Bot

#### Option A: Run with Docker Compose (Recommended)
```bash
docker-compose up
```

To run in detached mode (background):
```bash
docker-compose up -d
```

#### Option B: Run with Docker directly
```bash
docker build -t starlabs-tempo-bot .
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs -v $(pwd)/config.yaml:/app/config.yaml:ro starlabs-tempo-bot
```

### 4. View Logs

If running in detached mode:
```bash
docker-compose logs -f
```

Or check the logs directory:
```bash
tail -f logs/app.log
```

## Stopping the Bot

If running in detached mode:
```bash
docker-compose down
```

If running in foreground, press `Ctrl+C`.

## Automatic Execution

The Docker container is configured for automatic execution:
- The entrypoint script automatically validates configuration files
- The bot automatically starts farming (option 1) without manual input
- All tasks defined in `tasks.py` will be executed automatically

## Volume Mounts

The Docker container uses the following volume mounts:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./data` | `/app/data` | Persistent data (keys, proxies, database) |
| `./logs` | `/app/logs` | Application logs |
| `./config.yaml` | `/app/config.yaml` | Configuration file (read-only) |

This ensures:
- Your private keys and proxies are not embedded in the image
- Logs persist after container restart
- Database state is maintained
- Configuration can be updated without rebuilding

## Configuration Management

### Updating Configuration

1. Stop the container:
```bash
docker-compose down
```

2. Edit `config.yaml` with your changes

3. Restart the container:
```bash
docker-compose up -d
```

### Updating Tasks

1. Stop the container
2. Edit `tasks.py` to modify task configuration
3. Rebuild and restart:
```bash
docker-compose up -d --build
```

## Troubleshooting

### Container exits immediately

Check logs for errors:
```bash
docker-compose logs
```

Common issues:
- Missing or empty `data/private_keys.txt`
- Missing or empty `data/proxies.txt`
- Invalid `config.yaml` syntax

### Permission issues

If you encounter permission issues with mounted volumes:
```bash
sudo chown -R $(whoami):$(whoami) data/ logs/
```

### Database issues

If you need to reset the database:
```bash
rm data/accounts.db
docker-compose restart
```

## Advanced Usage

### Running specific tasks

Edit `tasks.py` before building to select which tasks to run:
```python
TASKS = ["FAUCET"]  # Only run faucet
# or
TASKS = ["FAUCET", "TOKEN_SENDER"]  # Run both
```

### Multiple instances

To run multiple instances with different configurations:

1. Create separate directories:
```bash
mkdir instance1 instance2
```

2. Copy files to each directory:
```bash
cp -r data/ config.yaml docker-compose.yml instance1/
cp -r data/ config.yaml docker-compose.yml instance2/
```

3. Edit each `docker-compose.yml` to use different container names:
```yaml
services:
  tempo-bot:
    container_name: starlabs-tempo-bot-1  # Change for each instance
```

4. Run each instance:
```bash
cd instance1 && docker-compose up -d
cd instance2 && docker-compose up -d
```

### Custom Docker network

To isolate the bot in a custom network:
```bash
docker network create tempo-network
```

Update `docker-compose.yml`:
```yaml
networks:
  default:
    external:
      name: tempo-network
```

## Security Best Practices

1. **Never commit sensitive data**:
   - Add `data/private_keys.txt` to `.gitignore`
   - Add `data/proxies.txt` to `.gitignore`

2. **Use secure file permissions**:
```bash
chmod 600 data/private_keys.txt
chmod 600 data/proxies.txt
```

3. **Regularly update dependencies**:
```bash
docker-compose build --no-cache
```

4. **Monitor logs for suspicious activity**:
```bash
tail -f logs/app.log
```

## Environment Variables

You can override settings using environment variables in `docker-compose.yml`:

```yaml
environment:
  - TZ=America/New_York  # Set timezone
  - PYTHONUNBUFFERED=1   # Real-time log output
```

## Scheduled Execution

To run the bot on a schedule, use cron (Linux/Mac) or Task Scheduler (Windows).

Example cron job (run daily at 2 AM):
```bash
0 2 * * * cd /path/to/StarLabs-Tempo && docker-compose up >> /var/log/tempo-bot.log 2>&1
```

## Support

For issues and questions:
- Telegram Channel: [@StarLabsTech](https://t.me/StarLabsTech)
- Telegram Chat: [@StarLabsChat](https://t.me/StarLabsChat)
- GitHub: [0xStarLabs](https://github.com/0xStarLabs)
