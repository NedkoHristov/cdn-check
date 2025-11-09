# Watchtower Auto-Deployment Setup

This guide explains how Watchtower automatically deploys new versions of your CDN Checker application when GitHub Actions builds and pushes new images.

## What is Watchtower?

Watchtower is a container-based solution that automatically updates running Docker containers whenever a new image is pushed to the registry. It monitors your containers and pulls new images when available.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions Pipeline                                     │
│ ├─ Code push to main branch                                │
│ ├─ Build Docker image                                       │
│ ├─ Push to ghcr.io/nedkohristov/cdn-check:latest          │
│ └─ Image pushed successfully                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Watchtower (on VPS)                                         │
│ ├─ Polls registry every 5 minutes                          │
│ ├─ Detects new image digest                                │
│ ├─ Pulls new image from ghcr.io                            │
│ ├─ Stops old cdn-checker container                         │
│ ├─ Starts new container with new image                     │
│ ├─ Removes old image (cleanup)                             │
│ └─ Application running with latest code                     │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Docker Compose Setup

The `docker-compose.yml` includes two services:

#### 1. CDN Checker Service
```yaml
cdn-checker:
  image: ghcr.io/nedkohristov/cdn-check:latest
  labels:
    - "com.centurylinklabs.watchtower.enable=true"
```

**Key points:**
- Uses `image:` instead of `build:` to pull from registry
- Label enables Watchtower monitoring for this container
- Watchtower will only update containers with this label

#### 2. Watchtower Service
```yaml
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  environment:
    - WATCHTOWER_POLL_INTERVAL=300       # Check every 5 minutes
    - WATCHTOWER_LABEL_ENABLE=true       # Only monitor labeled containers
    - WATCHTOWER_CLEANUP=true            # Remove old images
```

## Setup Instructions

### Step 1: Update Docker Compose File

Your `docker-compose.yml` is already configured! It includes:
- CDN Checker using registry image
- Watchtower service for auto-updates
- Proper labels and configuration

### Step 2: Make Image Public (One-time setup)

For Watchtower to pull images without authentication, make your package public:

1. Go to GitHub: https://github.com/users/NedkoHristov/packages
2. Find `cdn-check` package
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

**Alternative:** Configure Watchtower with GitHub token (see Authentication section below)

### Step 3: Deploy on VPS

```bash
# SSH into your VPS
ssh nedko@nedko.info

# Navigate to project directory
cd /usr/share/nginx/html/nedko.info/cdn-check

# Stop existing containers
docker-compose down

# Pull the latest configuration
git pull

# Start services (this will pull the image and start Watchtower)
docker-compose up -d

# Verify both containers are running
docker-compose ps
```

Expected output:
```
NAME           IMAGE                                    STATUS
cdn-checker    ghcr.io/nedkohristov/cdn-check:latest   Up 10 seconds (healthy)
watchtower     containrrr/watchtower                    Up 10 seconds
```

### Step 4: Verify Watchtower is Working

```bash
# Check Watchtower logs
docker logs watchtower

# You should see:
# - Watchtower starting
# - Monitoring containers
# - Checking for updates every 5 minutes
```

## How Auto-Deployment Works

### Normal Flow

1. **You push code to GitHub**
   ```bash
   git add .
   git commit -m "Fix bug"
   git push origin main
   ```

2. **GitHub Actions runs automatically**
   - Builds Docker image
   - Pushes to `ghcr.io/nedkohristov/cdn-check:latest`
   - Takes ~5-10 minutes

3. **Watchtower detects the update** (within 5 minutes)
   - Checks registry for new image digest
   - Finds new version available
   - Automatically pulls and deploys

4. **Your VPS is updated automatically!**
   - Zero manual intervention needed
   - Application updated with zero downtime (brief restart)
   - Old image cleaned up automatically

### Timeline Example

```
10:00 AM - You push code to GitHub
10:01 AM - GitHub Actions starts building
10:08 AM - GitHub Actions pushes new image to registry
10:10 AM - Watchtower checks for updates (on schedule)
10:10 AM - Watchtower detects new image
10:10 AM - Watchtower pulls new image
10:11 AM - Watchtower restarts container with new image
10:11 AM - Your app is live with the new code!
```

**Total time from push to live: ~11 minutes** (fully automated!)

## Watchtower Configuration Options

### Poll Interval

Control how often Watchtower checks for updates:

```yaml
environment:
  - WATCHTOWER_POLL_INTERVAL=300  # 5 minutes (default)
  # - WATCHTOWER_POLL_INTERVAL=60   # 1 minute (frequent)
  # - WATCHTOWER_POLL_INTERVAL=3600 # 1 hour (less frequent)
```

**Recommended:** 300 seconds (5 minutes) balances responsiveness with API rate limits

### Update Schedule (Alternative to Poll Interval)

Instead of polling, run updates on a schedule:

```yaml
environment:
  - WATCHTOWER_SCHEDULE=0 0 4 * * *  # Daily at 4 AM
  # - WATCHTOWER_SCHEDULE=0 */30 * * * *  # Every 30 minutes
```

**Cron format:** `seconds minutes hours day month weekday`

### Cleanup Old Images

```yaml
environment:
  - WATCHTOWER_CLEANUP=true   # Remove old images (recommended)
```

**Benefit:** Saves disk space by removing old images after update

### Label-based Filtering

```yaml
environment:
  - WATCHTOWER_LABEL_ENABLE=true  # Only update labeled containers
```

**Benefit:** Prevents Watchtower from updating other containers on your server

### Run Once (No Monitoring)

```yaml
command: --run-once
```

**Use case:** Manually trigger updates without continuous monitoring

## Authentication (Private Packages)

If your package is private, configure Watchtower with GitHub credentials:

### Method 1: Environment Variables

```yaml
watchtower:
  environment:
    - REPO_USER=nedkohristov
    - REPO_PASS=ghp_your_github_personal_access_token
```

### Method 2: Config File

```bash
# Create config file
mkdir -p ~/.docker
cat > ~/.docker/config.json << 'EOF'
{
  "auths": {
    "ghcr.io": {
      "auth": "base64_encoded_username:token"
    }
  }
}
EOF

# Mount in docker-compose.yml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - ~/.docker/config.json:/config.json:ro
environment:
  - DOCKER_CONFIG=/
```

### Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `read:packages` - Download packages from GitHub Container Registry
4. Copy the token (starts with `ghp_`)
5. Use in Watchtower configuration

## Notifications

Get notified when Watchtower updates your containers!

### Telegram Notifications

```yaml
watchtower:
  environment:
    - WATCHTOWER_NOTIFICATIONS=shoutrrr
    - WATCHTOWER_NOTIFICATION_URL=telegram://token@telegram?channels=channel-1
```

### Email Notifications

```yaml
watchtower:
  environment:
    - WATCHTOWER_NOTIFICATIONS=shoutrrr
    - WATCHTOWER_NOTIFICATION_URL=smtp://username:password@host:port/?from=sender@example.com&to=recipient@example.com
```

### Slack Notifications

```yaml
watchtower:
  environment:
    - WATCHTOWER_NOTIFICATIONS=shoutrrr
    - WATCHTOWER_NOTIFICATION_URL=slack://token@channel
```

## Monitoring and Logs

### Check Watchtower Status

```bash
# View logs
docker logs watchtower

# Follow logs in real-time
docker logs -f watchtower

# Check last 50 lines
docker logs --tail=50 watchtower
```

### Check for Updates Manually

```bash
# Force Watchtower to check now
docker exec watchtower watchtower --run-once
```

### View Update History

```bash
# Show all Watchtower updates
docker logs watchtower | grep "Found new"

# Show today's updates
docker logs watchtower --since $(date -u +%Y-%m-%d)
```

## Troubleshooting

### Watchtower Not Pulling Updates

**Check 1: Verify new image exists**
```bash
# Check image digest on registry
docker manifest inspect ghcr.io/nedkohristov/cdn-check:latest

# Compare with running container
docker inspect cdn-checker | grep Image
```

**Check 2: Verify labels**
```bash
# Check if container has the watchtower label
docker inspect cdn-checker | grep watchtower
```

**Check 3: Check Watchtower logs**
```bash
docker logs watchtower
```

### Authentication Errors

```
Error response from daemon: unauthorized: authentication required
```

**Solution:** Make package public OR add authentication (see Authentication section)

### Container Not Restarting

**Check health status:**
```bash
docker inspect cdn-checker | grep -A 10 Health
```

**Manually restart:**
```bash
docker-compose restart cdn-checker
```

### Old Images Not Being Cleaned

**Check cleanup setting:**
```bash
docker inspect watchtower | grep CLEANUP
```

**Manually clean:**
```bash
docker image prune -a
```

### Watchtower Consuming Too Much CPU/Memory

**Solution:** Increase poll interval
```yaml
environment:
  - WATCHTOWER_POLL_INTERVAL=600  # 10 minutes instead of 5
```

## Best Practices

### 1. Monitor First Deploy
Watch the logs during first automatic deployment:
```bash
docker logs -f watchtower
```

### 2. Test in Staging First
- Use a separate tag for staging: `ghcr.io/nedkohristov/cdn-check:staging`
- Test auto-deployment in staging before production
- Promote to `latest` tag after testing

### 3. Set Up Notifications
- Get alerted when deployments happen
- Know immediately if something fails

### 4. Keep Poll Interval Reasonable
- 5 minutes (300 seconds) is a good default
- Don't set too low (increases API calls)
- Don't set too high (delays deployments)

### 5. Label Only Production Containers
- Only add watchtower label to containers you want auto-updated
- Prevents accidental updates to other services

### 6. Monitor Disk Space
- Watchtower cleans up old images
- Still check periodically: `docker system df`

### 7. Use Health Checks
- Ensure your container has proper health checks
- Watchtower respects health status

## Rollback Strategy

### If Auto-Update Breaks Something

**Option 1: Rollback via Docker Compose**
```bash
# Stop current version
docker-compose down

# Use specific older version
docker run -d -p 127.0.0.1:5000:5000 \
  --name cdn-checker \
  ghcr.io/nedkohristov/cdn-check:main-abc123def
```

**Option 2: Temporarily Disable Watchtower**
```bash
# Pause Watchtower
docker pause watchtower

# Fix the issue
# Push corrected code
# Wait for new build

# Resume Watchtower
docker unpause watchtower
```

**Option 3: Remove Label Temporarily**
```yaml
cdn-checker:
  labels:
    # - "com.centurylinklabs.watchtower.enable=true"  # Commented out
```

## Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View Watchtower logs
docker logs watchtower

# View CDN Checker logs
docker logs cdn-checker

# Check running containers
docker-compose ps

# Force check for updates
docker exec watchtower watchtower --run-once

# Pause auto-updates
docker pause watchtower

# Resume auto-updates
docker unpause watchtower

# Restart Watchtower
docker-compose restart watchtower

# View Watchtower configuration
docker inspect watchtower

# Check for new images manually
docker pull ghcr.io/nedkohristov/cdn-check:latest
```

## Complete Workflow Example

### Day 1: Setup

```bash
# On VPS
cd /usr/share/nginx/html/nedko.info/cdn-check
git pull
docker-compose up -d

# Verify
docker-compose ps
docker logs watchtower
```

### Day 2: Make Code Changes

```bash
# On local machine
vim app.py  # Make changes
git add .
git commit -m "Add new feature"
git push origin main

# Wait ~11 minutes
# Check VPS - app is automatically updated!
```

### Day 3: Verify Auto-Update

```bash
# On VPS - check Watchtower logs
docker logs watchtower | grep "Found new"

# Output shows:
# Found new image for cdn-checker (ghcr.io/nedkohristov/cdn-check:latest)
# Stopping /cdn-checker (...)
# Removing container cdn-checker
# Starting container cdn-checker
```

## Summary

✅ **Fully Automated Deployment:**
- Push code → GitHub Actions builds → Watchtower deploys
- Zero manual intervention
- Updates within ~11 minutes

✅ **Safe and Reliable:**
- Health checks ensure app is working
- Old images cleaned automatically
- Can rollback if needed

✅ **Customizable:**
- Adjust poll interval
- Enable notifications
- Control which containers update

✅ **Production Ready:**
- Battle-tested solution
- Used by thousands of projects
- Minimal resource usage

**Your deployment is now fully automated! 🚀**
