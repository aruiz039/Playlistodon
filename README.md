# Playlistodon

Overview
--------
This repository is a small Python web application that creates a YouTube playlist from YouTube links found in Mastodon posts matching a supplied hashtag. The application pulls Mastodon posts on a configured instance and extracts YouTube URLs, then assembles them into a playlist on YouTube using the configured Google API credentials. The entry point is `app.py`. Frontend assets live in `static/` and server-rendered HTML templates live in `templates/`.

Project layout (important files)
- `app.py` - application entry point (runs the web server / handles routes).
- `templates/` - HTML templates used by the app.
- `static/` - JavaScript and CSS used by the frontend.
- `config.json` - application configuration. **I would not commit because i want my URL private but up to you.**
- `config.example.json` - example configuration you can rename to `config.json`.
- `youtube_credentials.json` - Google API client credentials (downloaded from Google Cloud). **DO NOT commit this file.**
- `token.json` - persisted OAuth tokens (access/refresh tokens). **DO NOT commit this file.**
- `token.secret` - local secret you would obtain from mastodon server for access  **DO NOT commit this file.**

Why some files must stay out of git
----------------------------------
- `youtube_credentials.json` contains private client credentials from Google Cloud. If leaked, others could use your API quota or impersonate your app.
- `token.json` contains OAuth access and refresh tokens that grant access to user accounts.
- `token.secret` may store encryption keys or other sensitive values used to protect tokens or sign requests.

Recommended local files / placeholders
------------------------------------
Create these files locally (do not commit them). Example minimal contents:

- `youtube_credentials.json` (example placeholder — real file is obtained from Google Cloud):

```json
{
  "installed": {
    "client_id": "REPLACE_WITH_CLIENT_ID",
    "project_id": "REPLACE_WITH_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "REPLACE_WITH_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
  }
}
```

- `token.json` (created/updated at runtime after OAuth flow):

- `token.secret` (single-line secret or key):

```
REPLACE_WITH_MASTODON_SECRET_API_VALUE
```

Git ignore recommendations
-------------------------
Add the following entries to your `.gitignore` to ensure secrets are not committed:

```
token.json
token.secret
youtube_credentials.json
```
<img width="2840" height="1574" alt="image" src="https://github.com/user-attachments/assets/386ca3be-6b69-4d0c-b01e-0dd54f9fb8b2" />

