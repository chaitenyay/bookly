# bookly

## Full runtime validation

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
