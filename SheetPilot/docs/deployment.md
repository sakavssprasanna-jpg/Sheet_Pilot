# Production Deployment Guide — SheetPilot AI

This guide details the step-by-step instructions for deploying SheetPilot AI to Streamlit Community Cloud and managing credentials securely.

---

## ☁️ Streamlit Community Cloud Deployment

Streamlit Community Cloud is a free hosting platform designed for Streamlit apps. Since SheetPilot AI does not require system-level audio driver binaries (e.g. FFmpeg, PortAudio), it is fully compatible out-of-the-box.

### Step 1: Push Repository to GitHub
Ensure your repository is clean, `.env` is ignored, and all files are pushed to GitHub:
```powershell
git status
git add .
git commit -m "docs: finalize phase 8 readiness and checklists"
git push origin main
```

### Step 2: Set Up Streamlit Account
1. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
2. Log in using your GitHub credentials.

### Step 3: Deploy New App
1. Click the **New app** button.
2. Select your repository: `your-username/SheetPilot-AI`.
3. Select your branch: `main`.
4. Specify the Main file path: `app.py`.
5. Specify a custom App URL (optional).

### Step 4: Configure Advanced Secrets
1. Click **Advanced settings** (located at the bottom of the deployment setup box).
2. Under the **Secrets** text box, paste your Google Gemini API Key in TOML format:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   ```
3. Click **Save**.

### Step 5: Start Deployment
1. Click **Deploy**.
2. Streamlit Cloud will automatically provision a container, install dependencies from `requirements.txt`, configure the environment secrets, and start the app.
3. Once built, copy the public deployment link and add it to your `README.md`.

---

## 🛠️ Local Development Secrets Config

For local environments, configuration is managed using a `.env` file located in the project root:

1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Add your key inside `.env`:
   ```env
   GEMINI_API_KEY=AIzaSyD...
   ```
3. Run the application:
   ```powershell
   streamlit run app.py
   ```

*Note: The `.env` file is whitelisted in `.gitignore` and will never be committed to Git.*
