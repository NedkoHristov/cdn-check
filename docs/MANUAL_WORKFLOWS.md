# Running Pipelines Manually

This guide shows you how to manually trigger the GitHub Actions workflows.

## Manual Workflow Triggers

Both workflows now support manual execution with customizable options!

---

## 🚀 How to Run Manually

### Step 1: Go to GitHub Actions
1. Navigate to your repository on GitHub
2. Click the **"Actions"** tab at the top
3. You'll see a list of workflows on the left sidebar

### Step 2: Select a Workflow
Choose which workflow you want to run:
- **"CI - Build and Test"** - For testing code changes
- **"Build and Deploy Docker Image"** - For building and deploying Docker images

### Step 3: Click "Run workflow"
1. Click on the workflow name
2. Click the **"Run workflow"** button (top right)
3. A dropdown will appear with options

### Step 4: Configure Options
Select your options and click **"Run workflow"** to start!

---

## 📋 Workflow Options

### CI - Build and Test

**Options:**
- **Branch/Tag**: Select which branch to run on
- **Run security scan**: Enable/disable security scanning (default: off)

**What it does:**
- ✅ Lints and tests your Python code
- ✅ Builds Docker image
- ✅ Tests the built image
- ⚠️ Does NOT push to registry

**Use when:**
- Testing code changes before merging
- Verifying builds work correctly
- Quick validation without deployment

---

### Build and Deploy Docker Image

**Options:**

#### 1. **Branch/Tag**
Select which branch to build from
- Default: Your current branch

#### 2. **Push image to registry** (checkbox)
Whether to push the built image to ghcr.io
- ✅ Checked (default): Image is pushed to registry
- ⬜ Unchecked: Image is built but not pushed

#### 3. **Run image tests** (checkbox)
Whether to test the built image
- ✅ Checked (default): Runs container tests
- ⬜ Unchecked: Skips testing

#### 4. **Run security scan** (checkbox)
Whether to run Trivy vulnerability scan
- ✅ Checked (default): Scans for vulnerabilities
- ⬜ Unchecked: Skips security scan

#### 5. **Custom image tag** (text)
Optional custom tag for the image
- Default: `manual`
- Examples: `dev`, `test`, `v1.0.0-beta`

**What it does:**
- ✅ Builds multi-platform Docker image
- ✅ Pushes to ghcr.io (if enabled)
- ✅ Tests container (if enabled)
- ✅ Runs security scan (if enabled)

**Use when:**
- Creating a custom build
- Testing with specific configurations
- Deploying to staging/production
- Creating tagged releases

---

## 🎯 Common Scenarios

### Scenario 1: Quick Test Build (No Push)
**Workflow:** Build and Deploy Docker Image

**Settings:**
- Branch: `develop` or your feature branch
- Push to registry: ⬜ **Unchecked**
- Run tests: ✅ Checked
- Security scan: ⬜ Unchecked
- Custom tag: `test`

**Result:** Builds and tests image locally, doesn't push

---

### Scenario 2: Production Deployment
**Workflow:** Build and Deploy Docker Image

**Settings:**
- Branch: `main`
- Push to registry: ✅ **Checked**
- Run tests: ✅ Checked
- Security scan: ✅ Checked
- Custom tag: `v1.0.0` or `production`

**Result:** Full build, test, push, and security scan

---

### Scenario 3: Development Build with Custom Tag
**Workflow:** Build and Deploy Docker Image

**Settings:**
- Branch: `develop`
- Push to registry: ✅ **Checked**
- Run tests: ✅ Checked
- Security scan: ⬜ Unchecked
- Custom tag: `dev-2024-11-09`

**Result:** Builds, tests, and pushes with custom tag

---

### Scenario 4: Quick Code Check
**Workflow:** CI - Build and Test

**Settings:**
- Branch: Your feature branch
- Run security scan: ⬜ Unchecked

**Result:** Fast code quality check without deployment

---

## 🖼️ Visual Guide

### Finding the "Run workflow" Button

```
GitHub Repository
  └─ Actions Tab
      └─ Workflow Name (left sidebar)
          └─ "Run workflow" button (top right, blue button)
              └─ Dropdown with options appears
                  └─ Configure options
                      └─ Click "Run workflow" to start
```

### What You'll See

```
┌─────────────────────────────────────────┐
│  Use workflow from                      │
│  Branch: main ▼                         │
│                                         │
│  ☑ Push image to registry              │
│  ☑ Run image tests                     │
│  ☑ Run security scan                   │
│                                         │
│  Custom image tag (optional)           │
│  [manual                            ]  │
│                                         │
│  [ Run workflow ]                      │
└─────────────────────────────────────────┘
```

---

## 📊 Monitoring Manual Runs

### Check Status
1. After clicking "Run workflow", you'll see it appear in the runs list
2. Status indicators:
   - 🟡 Yellow dot: Running
   - ✅ Green check: Success
   - ❌ Red X: Failed

### View Logs
1. Click on the workflow run
2. Click on job names to expand
3. Click on step names to see detailed logs

### Check Outputs
Look for:
- **Job summaries** - Shows image size, tags, test results
- **Artifacts** - Downloaded files (if any)
- **Annotations** - Warnings or errors

---

## 🔐 Pulling Your Manual Build

After a successful manual run with push enabled:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull with custom tag
docker pull ghcr.io/USERNAME/cdn-check:manual

# Or with your custom tag
docker pull ghcr.io/USERNAME/cdn-check:YOUR_CUSTOM_TAG

# Run it
docker run -d -p 5000:5000 ghcr.io/USERNAME/cdn-check:manual
```

---

## 🔄 Re-running Failed Workflows

If a workflow fails:

1. Go to the failed workflow run
2. Click **"Re-run jobs"** dropdown (top right)
3. Options:
   - **Re-run all jobs** - Runs everything again
   - **Re-run failed jobs** - Only re-runs what failed

---

## ⚙️ Advanced: Using GitHub CLI

Run workflows from command line:

```bash
# Install GitHub CLI (if not installed)
# See: https://cli.github.com/

# CI workflow
gh workflow run ci.yml

# Docker deploy workflow with options
gh workflow run docker-build-deploy.yml \
  -f push_to_registry=true \
  -f run_tests=true \
  -f run_security_scan=true \
  -f image_tag=custom-tag

# Check status
gh run list

# Watch a running workflow
gh run watch
```

---

## ❓ FAQ

### Q: Can I cancel a running workflow?
**A:** Yes! Click on the running workflow, then click "Cancel workflow" (top right)

### Q: How long do workflows take?
**A:** 
- CI: ~3-5 minutes
- Docker deploy: ~5-10 minutes (depending on options)

### Q: Can I run workflows on any branch?
**A:** Yes! Select the branch in the dropdown when running manually

### Q: What if I don't want to push to registry?
**A:** Uncheck "Push image to registry" when running manually

### Q: How do I create a tagged release?
**A:** 
1. Run Docker deploy workflow manually
2. Set custom tag to your version (e.g., `v1.0.0`)
3. Enable push to registry
4. The image will be tagged and pushed

---

## 🛠️ Troubleshooting

### "Run workflow" button is grayed out
- Make sure you're signed in to GitHub
- Check you have write access to the repository

### Workflow fails immediately
- Check branch exists
- Verify workflow file syntax is correct

### Can't pull image after manual run
- Ensure "Push to registry" was checked
- Verify you have correct permissions
- Check the image tag you're using

---

## 📝 Best Practices

1. **Test first** - Run CI workflow before deploying
2. **Use custom tags** - For tracking specific builds
3. **Enable tests** - Don't skip testing in production builds
4. **Security scans** - Always scan before deploying
5. **Meaningful tags** - Use descriptive names (e.g., `hotfix-auth`, `v2.1.0`)

---

## 🎉 Summary

Manual workflow execution gives you full control over:
- ✅ When to build
- ✅ What to build
- ✅ Where to deploy
- ✅ How to test
- ✅ Custom versioning

Perfect for:
- Testing features
- Creating releases
- Hotfix deployments
- Staging environments
- Custom builds

**Try it now!** Go to Actions → Select workflow → Run workflow 🚀
