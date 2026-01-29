# ☁️ How to Deploy Yuna Backend to Render (Free)

This guide will move your "Brain" to the cloud so Yuna works 24/7.

## Step 1: Put Code on GitHub
You need a GitHub account.
1.  Open your terminal in `c:\aribot\backend`.
2.  Run these commands:
    ```bash
    git init
    git add .
    git commit -m "Initial backend commit"
    ```
3.  Go to [GitHub.com](https://github.com/new) and create a **New Repository** named `yuna-backend`.
4.  Copy the commands GitHub gives you (similar to these) and run them:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/yuna-backend.git
    git branch -M main
    git push -u origin main
    ```

## Step 2: Deploy to Render.com
1.  Sign up/Login to [Render.com](https://render.com).
2.  Click **"New +"** -> **"Web Service"**.
3.  Select **"Build and deploy from a Git repository"**.
4.  Connect your `yuna-backend` repo.

## Step 3: Configure Render
Fill in these details:
-   **Name**: `yuna-brain`
-   **Region**: Closest to you (e.g., Singapore/Frankfurt).
-   **Branch**: `main`
-   **Runtime**: `Python 3`
-   **Build Command**: `pip install -r requirements.txt`
-   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
-   **Instance Type**: **Free**

## Step 4: Environment Variables (Crucial!)
Scroll down to **"Advanced"** or **"Environment Variables"** and click **"Add Environment Variable"**:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.11.6` |
| `LLM_PROVIDER` | `gemini` |
| `GOOGLE_API_KEY` | *(Paste your actual AI Studio key here)* |

## Step 5: Finish
Click **"Create Web Service"**.
Wait ~5 minutes. Render will give you a URL like:
`https://yuna-brain.onrender.com`

---

## Step 6: Connect App
1.  Copy that URL.
2.  Open `frontend/lib/services/chat_api.dart`.
3.  Update the `_baseUrl` code to use your new Cloud URL.
