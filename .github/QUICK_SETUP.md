# GitHub Actions Quick Setup

## ⚡ Quick Start

1. **Push your code to GitHub**
2. **Enable GitHub Actions** (if not already enabled)
3. **Workflows will run automatically** on push/PR

## 🔧 Initial Setup

### Enable GitHub Container Registry

No additional setup required! The workflows use `GITHUB_TOKEN` which is automatically provided.

### First Build

When you push to `main` or `master`:
1. CI workflow tests your code
2. Docker Build workflow creates image
3. Image pushed to `ghcr.io/[your-username]/cdn-checker`

## 📦 Using Your Built Image

### Pull and Run

```bash
# Login (use Personal Access Token with read:packages scope)
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull image
docker pull ghcr.io/YOUR_USERNAME/cdn-checker:latest

# Run
docker run -d -p 5000:5000 ghcr.io/YOUR_USERNAME/cdn-checker:latest
```

### Make Image Public (Optional)

1. Go to package: `https://github.com/users/YOUR_USERNAME/packages/container/cdn-checker`
2. Click **"Package settings"**
3. Change visibility to **"Public"**
4. Now anyone can pull without authentication

## 🏃 Workflow Triggers

| Event | CI Workflow | Docker Build |
|-------|------------|--------------|
| Push to `main`/`master` | ✅ | ✅ |
| Push to `develop` | ✅ | ❌ |
| Pull Request | ✅ | ✅ (no push) |
| Manual trigger | ❌ | ✅ |

## 📊 Monitoring Builds

### View Workflow Runs
```
Your Repo → Actions Tab → Select Workflow
```

### Check Image Size
- Shown in **Actions Summary** after each build
- Expected: ~100-120 MB (Alpine-based)

### Security Scan Results
```
Your Repo → Security Tab → Code Scanning
```

## 🐛 Common Issues

### "Permission denied" when pushing image
**Solution:** Workflow needs `packages: write` permission (already configured)

### Build fails on first run
**Solution:** Normal - no cache available yet. Second run will be faster.

### Image size too large (>200 MB)
**Solution:** Check `Dockerfile` - should use multi-stage Alpine build

### Tests fail with connection timeout
**Solution:** Increase `sleep` duration in workflow (line ~93 of ci.yml)

## 🔐 Security Best Practices

✅ **Enabled by default:**
- Non-root user in container
- Security scanning with Trivy
- Minimal Alpine base image
- No unnecessary packages

❌ **Not included (you should add):**
- Private registry authentication
- Production deployment secrets
- Custom SSL certificates

## 📝 Customization

### Change Worker Count

Edit `.github/workflows/docker-build-deploy.yml`:
```yaml
env:
  WORKERS: 8  # Add this line
```

### Add Environment Variables

In workflow file:
```yaml
- name: Test Docker image
  run: |
    docker run -d -p 5000:5000 \
      -e WORKERS=8 \
      -e YOUR_VAR=value \
      --name cdn-checker-test cdn-checker:test
```

### Deploy to Different Registry

Add Docker Hub login step:
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

## 🚀 Next Steps

1. ✅ **Push code to GitHub** - Workflows will run automatically
2. ✅ **Check Actions tab** - Monitor build progress
3. ✅ **Pull your image** - Test the built image locally
4. ⬜ **Add deployment** - Set up automatic deployment to your server
5. ⬜ **Configure notifications** - Get build status in Slack/Discord

## 📚 Full Documentation

See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for complete details.

---

**Need help?** Check workflow logs in the Actions tab for detailed error messages.
