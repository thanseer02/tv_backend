# TV Stream Backend API (Python / FastAPI)

A modern, fast, asynchronous REST API backend tailored for **TV Streaming Admin & TV Client Displays**.

It connects directly with:
- **`tv_admin` (Web & Flutter frontends)**: URL stream management, authorization, categorization, real-time status toggles.
- **TV Display Clients**: High-performance URL streaming feed resolution.

---

## Features
- **FastAPI + Pydantic v2**: High performance, strict data validation, automatic OpenAPI & Swagger documentation.
- **JWT Authentication**: Secure Bearer tokens (`/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me`).
- **Flexible Field Mapping**: Seamlessly supports both web admin payload attributes (`title`, `url`, `notes`, `category`, `refreshInterval`) and Flutter data models (`name`, `address`, `description`, `environment`, `status`).
- **CORS Configured**: Ready out-of-the-box for `localhost:3000`, `localhost:5000`, and Flutter web ports.
- **Persistent JSON Store**: Zero-setup storage with preloaded initial streaming feeds and demo admin accounts, with instant support for swapping to PostgreSQL / SQLite.
- **Automated Tests**: Included `pytest` suite testing all endpoints.

---

## Quick Start

### 1. Set Up Environment
```bash
cd tv_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Development Server
```bash
python run.py
```
Or with `uvicorn`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base:** `http://localhost:8000/api/v1`
- **Interactive Swagger Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Interactive ReDoc:** [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Log in with username/email & password. Returns JWT token & user. |
| `POST` | `/api/v1/auth/logout` | Invalidate current session. |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user info. |

**Default Admin Credentials:**
- **Username / Email:** `admin` or `admin@tvadmin.io` or `admin@linkdesk.io`
- **Password:** `admin` or `admin123`

---

### URL Management (`/api/v1/urls`)
All URL routes require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/urls` | Get list of URLs (supports `?search=`, `?category=`, `?status=`, `?environment=`). |
| `GET` | `/api/v1/urls/{id}` | Get single URL entry by ID. |
| `POST` | `/api/v1/urls` | Create new stream URL entry. |
| `PUT` | `/api/v1/urls/{id}` | Update existing stream URL entry. |
| `PATCH` | `/api/v1/urls/{id}/toggle-status` | Toggle status between `active` and `inactive`. |
| `DELETE` | `/api/v1/urls/{id}` | Delete stream URL entry. |

---

## Connecting with `tv_admin`

In [`/Users/tanseer/Documents/oopsss/tv_app/tv_admin/api.js`](file:///Users/tanseer/Documents/oopsss/tv_app/tv_admin/api.js):
```javascript
export const API_CONFIG = {
  USE_MOCK_API: false, // <-- Set to false
  BASE_URL: 'http://localhost:8000/api/v1',
  ENDPOINTS: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    GET_URLS: '/urls',
    ADD_URL: '/urls',
    UPDATE_URL: (id) => `/urls/${id}`,
    DELETE_URL: (id) => `/urls/${id}`,
  }
};
```

---

## Running Tests

```bash
PYTHONPATH=. ./venv/bin/pytest tests/
```

# tv_backend
