# URL Shortener

A lightweight, full-stack URL shortening service built with **Python (Flask)** and **SQLite**. Clean server-rendered UI, click tracking, and a JSON API for programmatic use.

## Features

- Shorten any long URL into a compact 6-character code
- Automatic redirection from short link to original URL
- Click tracking per link (`/stats/<code>`)
- REST-style JSON API (`/api/shorten`)
- Zero external dependencies beyond Flask — SQLite requires no separate server

## Tech Stack

| Layer      | Technology            |
|------------|------------------------|
| Backend    | Python 3, Flask        |
| Database   | SQLite3                |
| Frontend   | HTML5, CSS3 (Jinja2)   |

## Project Structure

```
url-shortener/
├── app.py              # Application entry point & routes
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html       # Home page (shorten form)
│   ├── stats.html       # Click statistics page
│   └── 404.html         # Error page
├── static/
│   └── style.css        # Styling
└── README.md
```

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/url-shortener.git
cd url-shortener

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

## API Reference

**POST** `/api/shorten`

Request:
```json
{ "url": "https://www.example.com/some/long/path" }
```

Response:
```json
{
  "short_url": "http://127.0.0.1:5000/aB3xY9",
  "short_code": "aB3xY9",
  "original_url": "https://www.example.com/some/long/path"
}
```

## Roadmap

- Custom short code aliases
- Link expiration
- User authentication & personal dashboards
- Rate limiting

## License

MIT
