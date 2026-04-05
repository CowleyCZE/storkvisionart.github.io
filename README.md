
# StorkVision Art Manager

StorkVision Art Manager is a lightweight, secure application that helps Etsy sellers manage listings, synchronize inventory in real time, and analyze sales performance. This repository contains the public landing page used for Etsy App Review and developer documentation.

## Key Features

- OAuth 2.0 authentication (PKCE) for secure delegated access
- Listing synchronization across channels
- Real-time inventory and automated stock updates
- Sales performance analytics and reporting
- Secure data encryption in transit and at rest

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Node.js or Python (example implementations) |
| API | Etsy Open API v3 |
| Hosting / Dev | GitHub Pages (landing), GitHub Codespaces for development |
| Frontend | Static HTML + Tailwind CSS (CDN), Lucide icons |

## Prerequisites

- An Etsy Developer Account (https://www.etsy.com/developers)
- Registered Etsy application (App Key / API Key) in the Etsy Developer Portal
- Shared secret (if provided) and OAuth 2.0 redirect URI configured in Etsy app settings
- GitHub account for repository hosting and (optional) GitHub Codespaces

## Configuration

Create a `.env` file at the project root (or use your preferred secrets manager). Example `.env` variables:

```ini
ETSY_API_KEY=your_etsy_api_key_here
ETSY_SHARED_SECRET=your_etsy_shared_secret_here
ETSY_REDIRECT_URI=https://your-domain.example.com/auth/etsy/callback
# Optional: local development callback
# ETSY_REDIRECT_URI=http://localhost:8000/auth/etsy/callback
```

Important notes about the OAuth 2.0 callback / redirect URL:

- The `ETSY_REDIRECT_URI` must exactly match the redirect URI registered in your Etsy application settings.
- For production, use a secure `https://` URL (e.g. `https://storkvision.example.com/auth/etsy/callback`).
- For local testing, you can register a `http://localhost:<port>/auth/etsy/callback` redirect in the Etsy app, but Etsy may require a public URL for app review. When submitting the app for review, provide the public URL (GitHub Pages or other) where the OAuth flow can be tested.

## Installation (GitHub Codespaces)

1. Open this repository in GitHub Codespaces or clone it locally:

```bash
git clone https://github.com/CowleyCZE/storkvisionart.github.io.git
cd storkvisionart.github.io
```

2. Create and populate `.env` as described above.

3. Install dependencies (example commands):

Node.js (if project uses Node backend)
```bash
# from project root
npm install
npm run dev         # or npm start depending on implementation
```

Python (if project uses Python backend)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m your_app_module
```

4. Local preview of the landing page (static):

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Etsy App Review / How this site is used

- This landing page documents the app's purpose, privacy policy, and technical compliance to help Etsy reviewers understand how the app will access and process shop data.
- When submitting your app in the Etsy Developer Portal, include the public URL of this site as the app's homepage and provide the redirect URI used during OAuth testing.

## Privacy & Security

- We do not sell user data. Access is limited to authorized Etsy scopes only.
- All sensitive tokens and credentials must be stored securely (environment variables, secret managers).
- Authentication uses OAuth 2.0 (PKCE) to avoid exposing client secrets in public clients.

## Etsy Compliance Disclaimer

The term "Etsy" is a trademark of Etsy, Inc. This application uses the Etsy Open API v3 to access shop data but is not endorsed, certified, or affiliated with Etsy, Inc.

## Contact

For questions about app review, privacy, or technical details, contact: `hello@storkvision.art`



