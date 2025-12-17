# Docker Quick Reference 🚀

Quick command reference for StarLabs Tempo Bot Docker deployment.

## 🏁 Quick Start

```bash
# 1. Verify setup
./verify-docker-setup.sh

# 2. Start the bot (interactive)
./docker-start.sh

# 3. Or start directly
docker-compose up -d
```

## 📦 Setup Commands

```bash
# Copy configuration files from examples
cp data/private_keys.txt.example data/private_keys.txt
cp data/proxies.txt.example data/proxies.txt

# Edit configuration files
nano data/private_keys.txt  # Add your private keys
nano data/proxies.txt       # Add your proxies
nano config.yaml            # Adjust settings

# Verify setup before running
./verify-docker-setup.sh
```

## 🔨 Build Commands

```bash
# Build the Docker image
docker-compose build

# Build without cache (clean build)
docker-compose build --no-cache

# Build and pull latest base images
docker-compose build --pull
```

## ▶️ Run Commands

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start and rebuild if needed
docker-compose up -d --build

# Force recreate containers
docker-compose up -d --force-recreate
```

## 🔍 Monitor Commands

```bash
# View real-time logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail 100

# View logs for specific time
docker-compose logs --since 30m

# Check container status
docker-compose ps

# View resource usage
docker stats starlabs-tempo-bot
```

## 🛑 Stop Commands

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop containers gracefully
docker-compose stop

# Kill containers immediately
docker-compose kill
```

## 🔄 Restart Commands

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart tempo-bot

# Stop and start again
docker-compose down && docker-compose up -d
```

## 🐛 Debug Commands

```bash
# Enter container shell
docker-compose exec tempo-bot bash

# View container logs
docker-compose logs tempo-bot

# Inspect container configuration
docker inspect starlabs-tempo-bot

# View container processes
docker-compose top

# Check disk usage
docker system df
```

## 🗑️ Cleanup Commands

```bash
# Remove stopped containers
docker-compose rm

# Remove all unused containers, networks, images
docker system prune

# Remove all with volumes
docker system prune -a --volumes

# Remove specific image
docker rmi starlabs-tempo-bot

# Clean build cache
docker builder prune
```

## 📁 File Management

```bash
# Copy file from container to host
docker cp starlabs-tempo-bot:/app/logs/app.log ./local-logs/

# Copy file from host to container
docker cp ./local-file.txt starlabs-tempo-bot:/app/

# View file in container
docker-compose exec tempo-bot cat /app/config.yaml

# Edit file in container
docker-compose exec tempo-bot nano /app/config.yaml
```

## 🔐 Permissions

```bash
# Fix data directory permissions
chmod -R u+w data/
chown -R $(whoami):$(whoami) data/

# Fix logs directory permissions
chmod -R u+w logs/
chown -R $(whoami):$(whoami) logs/

# Make scripts executable
chmod +x *.sh
```

## 🌐 Network Commands

```bash
# List networks
docker network ls

# Create custom network
docker network create tempo-network

# Connect container to network
docker network connect tempo-network starlabs-tempo-bot

# Disconnect from network
docker network disconnect tempo-network starlabs-tempo-bot

# Inspect network
docker network inspect tempo-network
```

## 💾 Volume Commands

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect starlabs-tempo_data

# Remove volume
docker volume rm starlabs-tempo_data

# Backup volume
docker run --rm -v starlabs-tempo_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

## 🔧 Troubleshooting

### Container won't start
```bash
# Check logs for errors
docker-compose logs

# Validate docker-compose.yml
docker-compose config

# Remove and recreate
docker-compose down && docker-compose up -d --force-recreate
```

### Permission denied errors
```bash
# Fix permissions
sudo chown -R $(whoami):$(whoami) data/ logs/
chmod -R u+w data/ logs/
```

### Out of disk space
```bash
# Check usage
docker system df

# Clean up
docker system prune -a
docker volume prune
```

### Configuration not updating
```bash
# Restart after config change
docker-compose down
docker-compose up -d

# Or for code changes
docker-compose down
docker-compose up -d --build
```

## 📊 Common Workflows

### Update Configuration
```bash
# 1. Stop container
docker-compose down

# 2. Edit config.yaml
nano config.yaml

# 3. Restart
docker-compose up -d
```

### Update Code/Tasks
```bash
# 1. Stop container
docker-compose down

# 2. Edit tasks.py or other files
nano tasks.py

# 3. Rebuild and restart
docker-compose up -d --build
```

### View Progress
```bash
# Real-time logs
docker-compose logs -f

# Or check log file
tail -f logs/app.log

# Or enter container
docker-compose exec tempo-bot bash
```

### Backup Data
```bash
# Backup data directory
tar czf backup-$(date +%Y%m%d).tar.gz data/

# Backup logs
tar czf logs-$(date +%Y%m%d).tar.gz logs/
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi starlabs-tempo-bot

# Remove database
rm data/accounts.db

# Rebuild and start
docker-compose up -d --build
```

## 🔑 Environment Variables

You can override settings via environment variables in `docker-compose.yml`:

```yaml
environment:
  - TZ=America/New_York          # Timezone
  - PYTHONUNBUFFERED=1           # Unbuffered output
  - LOG_LEVEL=DEBUG              # Custom log level
```

## 📱 Multi-Instance Setup

```bash
# Create instance directories
mkdir -p instances/bot1 instances/bot2

# Copy configuration
cp -r data/ config.yaml docker-compose.yml instances/bot1/
cp -r data/ config.yaml docker-compose.yml instances/bot2/

# Edit container names in each docker-compose.yml
# Then start each instance
cd instances/bot1 && docker-compose up -d
cd instances/bot2 && docker-compose up -d
```

## ⏰ Scheduled Execution

### Using cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add entry (run daily at 2 AM)
0 2 * * * cd /path/to/StarLabs-Tempo && docker-compose up >> /var/log/tempo-bot.log 2>&1
```

### Using systemd (Linux)
Create `/etc/systemd/system/tempo-bot.service`:
```ini
[Unit]
Description=StarLabs Tempo Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/path/to/StarLabs-Tempo
ExecStart=/usr/local/bin/docker-compose up
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tempo-bot.timer
sudo systemctl start tempo-bot.timer
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Full deployment guide
- [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md) - 中文部署指南

## 💡 Tips

1. **Always verify setup first**: Run `./verify-docker-setup.sh`
2. **Use detached mode for production**: `docker-compose up -d`
3. **Monitor logs regularly**: `docker-compose logs -f`
4. **Backup your data**: Regular backups of `data/` directory
5. **Keep images updated**: Rebuild periodically with `--no-cache`
6. **Check disk space**: Run `docker system df` regularly
7. **Use the quick start script**: `./docker-start.sh` for easy setup
