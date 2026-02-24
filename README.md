# Bookly

Bookly is a FastAPI-based library management service with PostgreSQL, pgAdmin, and Docker Compose.

## 1. How To Start (Docker)

### Prerequisites
- Docker
- Docker Compose plugin (`docker compose`)

### Start sequence
1. Go to project root:
   ```bash
   cd /var/www/html/bookly
   ```
2. Start all services:
   ```bash
   docker compose up -d --build
   ```
3. Verify containers:
   ```bash
   docker compose ps
   ```
4. Open API docs:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Stop services
```bash
docker compose down
```

## 2. pgAdmin Access

### URL
- `http://localhost:5050`

### Login credentials
- Email: `admin@bookly.com`
- Password: `admin8404`

### Register PostgreSQL server in pgAdmin
1. Open pgAdmin and click `Add New Server`.
2. In `General` tab:
   - Name: `bookly-db`
3. In `Connection` tab:
   - Host name/address: `db`
   - Port: `5432`
   - Maintenance database: `booklydb`
   - Username: `booklyuser`
   - Password: `booklypass`

## 3. API Reference

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 4. Design Documents

All design assets are in `app/design`.

- Software Design Document (PDF): [`app/design/Software Design Document.pdf`](app/design/Software%20Design%20Document.pdf)
- High-Level Design (PlantUML): [`app/design/bookly_hld.puml`](app/design/bookly_hld.puml)
- Class Schema (PlantUML): [`app/design/bookly_schema.puml`](app/design/bookly_schema.puml)
- DB Schema (DBML): [`app/design/schema.dbml`](app/design/schema.dbml)
- Generated Diagram (PNG): [`app/design/bookly.png`](app/design/bookly.png)

## 5. Runtime Validation

Run the validation script:

```bash
./scripts/validate_runtime.sh
```

What it validates:
- Builds and starts `db` and `app` with Docker Compose.
- Waits for API startup (`/docs`).
- Verifies FastAPI app import and route registration inside the app container.
- Verifies `/openapi.json` is reachable.

Optional environment variables:
- `APP_PORT` (default: `8000`)
- `MAX_WAIT_SECONDS` (default: `120`)
