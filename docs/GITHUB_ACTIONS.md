# GitHub Actions CI/CD Documentation

This document describes the GitHub Actions workflows configured for the CDN Checker project.

## Workflows Overview

### 1. CI - Build and Test (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main` or `master` branches

**Jobs:**

#### `lint-and-test`
Tests the Python code quality and functionality:
- ✅ Lints code with `flake8` (catches syntax errors and undefined names)
- ✅ Checks code formatting with `black`
- ✅ Tests Python imports
- ✅ Runs basic functionality tests:
  - URL validation
  - CDN signatures loading
  - SiteGround CDN presence verification

#### `build-docker`
Builds and tests the Docker image:
- ✅ Builds Docker image with BuildKit cache
- ✅ Starts container and tests health endpoint
- ✅ Reports image size in GitHub Summary
- ✅ Analyzes and displays image layers
- ✅ Uses GitHub Actions cache for faster builds

**Expected Image Size:** ~100-150 MB (Alpine-based multi-stage build)

---

### 2. Docker Build and Deploy (`.github/workflows/docker-build-deploy.yml`)

**Triggers:**
- Push to `main` or `master` branches
- Pull requests to `main` or `master` branches
- Manual workflow dispatch

**Jobs:**

#### `build-and-push`
Builds and publishes Docker image to GitHub Container Registry:
- ✅ Builds multi-platform images (amd64, arm64)
- ✅ Pushes to `ghcr.io/[username]/cdn-checker`
- ✅ Generates multiple tags:
  - `latest` (for default branch)
  - Branch name (e.g., `main`)
  - Commit SHA (e.g., `main-abc1234`)
  - Semantic versions (if tagged)
- ✅ Uses layer caching for faster builds
- ✅ Only pushes on non-PR events

#### `test-image`
Tests the published Docker image:
- ✅ Pulls the latest image from registry
- ✅ Runs container on port 5000
- ✅ Tests application health endpoint
- ✅ Shows container logs
- ✅ Reports image size
- ✅ Cleans up after testing

#### `security-scan`
Scans for vulnerabilities:
- ✅ Runs Trivy security scanner
- ✅ Uploads results to GitHub Security tab
- ✅ Generates SARIF report
- ✅ Identifies CVEs in dependencies

---

## Docker Image Optimization

The `Dockerfile` uses a multi-stage build for minimal image size:

### Stage 1: Builder (Alpine-based)
```dockerfile
FROM python:3.11-alpine AS builder
```
- Uses Alpine Linux for small base image
- Installs build dependencies (gcc, musl-dev)
- Installs Python packages to `/root/.local`

### Stage 2: Runtime (Alpine-based)
```dockerfile
FROM python:3.11-alpine
```
- Clean Alpine base (~50 MB)
- Copies only Python packages from builder
- No build tools in final image
- Runs as non-root user

### Size Comparison

| Base Image | Final Size | Notes |
|------------|-----------|-------|
| `python:3.11` | ~900 MB | Debian-based, includes many tools |
| `python:3.11-slim` | ~150 MB | Minimal Debian |
| `python:3.11-alpine` (multi-stage) | ~100-120 MB | **Optimal** |

---

## Using the Docker Image

### Pull from GitHub Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull latest image
docker pull ghcr.io/USERNAME/cdn-checker:latest

# Run container
docker run -d -p 5000:5000 --name cdn-checker ghcr.io/USERNAME/cdn-checker:latest
```

### Environment Variables

```bash
# Custom worker count
docker run -d -p 5000:5000 -e WORKERS=8 ghcr.io/USERNAME/cdn-checker:latest
```

### Health Check

The image includes a built-in health check:
```bash
docker ps  # Shows health status
```

---

## GitHub Secrets Required

### For Docker Build and Deploy workflow:

- **`GITHUB_TOKEN`** - Automatically provided by GitHub Actions
  - Used for authenticating with GitHub Container Registry
  - Requires `packages: write` permission (configured in workflow)

### Optional Secrets:

- **`DOCKER_HUB_USERNAME`** - If also publishing to Docker Hub
- **`DOCKER_HUB_TOKEN`** - Docker Hub access token

---

## Workflow Permissions

Both workflows require specific permissions:

```yaml
permissions:
  contents: read      # Read repository contents
  packages: write     # Push to GitHub Container Registry
  security-events: write  # Upload security scan results
```

---

## Caching Strategy

### GitHub Actions Cache
- **Python pip packages** - Cached based on `requirements.txt` hash
- **Docker layers** - Cached using GitHub Actions cache backend
  - `cache-from: type=gha` - Restore layers from cache
  - `cache-to: type=gha,mode=max` - Save all layers to cache

### Benefits:
- ⚡ 50-80% faster builds on subsequent runs
- 💾 Reduces bandwidth usage
- 🚀 Faster CI feedback

---

## Manual Workflow Trigger

You can manually trigger the Docker build workflow:

1. Go to **Actions** tab in GitHub
2. Select **"Build and Deploy Docker Image"**
3. Click **"Run workflow"**
4. Select branch
5. Click **"Run workflow"** button

---

## Monitoring Builds

### View Build Results:
1. Go to **Actions** tab
2. Click on workflow run
3. View job logs and summaries

### Check Image Size:
- Displayed in GitHub Actions Summary after each build
- Compare across builds to track size changes

### Security Vulnerabilities:
1. Go to **Security** tab
2. Click **"Code scanning"**
3. View Trivy scan results

---

## Troubleshooting

### Build Fails with "disk quota exceeded"
- Clear GitHub Actions cache:
  ```
  Settings → Actions → Caches → Delete old caches
  ```

### Image too large
- Check Docker history:
  ```bash
  docker history ghcr.io/USERNAME/cdn-checker:latest
  ```
- Look for large layers and optimize

### Tests fail with connection error
- Increase sleep time in workflow
- Check container logs in workflow output

### Cannot push to registry
- Verify `GITHUB_TOKEN` has `packages: write` permission
- Check if workflow has correct permissions configured

---

## Best Practices

1. **Tag Releases** - Use semantic versioning (v1.0.0) for stable releases
2. **Review Security Scans** - Check Trivy results regularly
3. **Monitor Image Size** - Keep image under 150 MB
4. **Test Before Deploy** - Always run CI workflow on PRs
5. **Use Cache** - Let workflows use GitHub Actions cache for speed

---

## Future Enhancements

- [ ] Add integration tests with real CDN checks
- [ ] Deploy to staging environment automatically
- [ ] Add performance benchmarks
- [ ] Implement blue-green deployments
- [ ] Add Slack/Discord notifications
- [ ] Create release automation workflow
