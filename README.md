# Adbrew Test — TODO app

A TODO app with a React frontend, a Django REST API and MongoDB, all running in Docker.

## Setup

```bash
export ADBREW_CODEBASE_PATH="{path_to_repository}/src"   # optional, defaults to ./src
docker compose build
docker compose up -d
```

| Container | URL |
|---|---|
| `app` (React dev server) | http://localhost:3000 |
| `api` (Django) | http://localhost:8000/todos |
| `mongo` | `localhost:27017` |

The `app` container runs `yarn install` on first start, so give it a minute.

### Tests

```bash
docker exec api python manage.py test todos
docker exec -e CI=true app yarn test --watchAll=false
```

## API

| Method | Path | Body | Response |
|---|---|---|---|
| `GET` | `/todos` | – | `200` list of todos, newest first |
| `POST` | `/todos` | `{"description": "..."}` | `201` created todo |

A todo looks like `{"id": "...", "description": "...", "created_at": "ISO-8601"}`.
Errors always return `{"error": "message"}`: `400` for invalid input, `503` when MongoDB is unreachable, `500` otherwise.

## Code structure

### Backend (`src/rest`)

```
rest/
  settings.py      config from env vars (Mongo URI, CORS origins), no SQLite
  mongo.py         single shared MongoClient
  errors.py        InvalidInputError + DRF exception handler (maps errors to status codes)
todos/
  repository.py    Todo dataclass + TodoRepository, the only code that talks to Mongo
  service.py       TodoService, validation rules (required, trimmed, max 500 chars)
  views.py         TodoListView, thin HTTP layer
  tests.py         service, repository and view tests (no DB needed)
```

Each layer has one job: the view handles HTTP, the service holds business rules, and the repository handles persistence.
The service depends on the repository through its constructor, so tests swap in an in-memory repository instead of a real database.

### Frontend (`src/app/src`)

```
api/todosApi.js           fetch wrapper, base URL from REACT_APP_API_URL, turns failures into Error messages
hooks/useTodos.js         todos, isLoading, error, addTodo (creates, then re-fetches the list)
components/TodoList.js    loading / empty / error / list states
components/TodoForm.js    controlled input, disabled while submitting, shows validation and API errors
App.js                    composes the hook and components
```

Only function components and hooks are used.

## Docker setup

`docker-compose.yml` starts three containers on a shared network. Containers reach each other by service name, which is why the API connects to `mongo:27017`.

- **mongo**: official `mongo:4.4` image. Data is stored in `src/db` on the host through a bind mount, so it survives restarts. A healthcheck pings the DB.
- **api**: built from `Dockerfile` (`python:3.8-slim` + `requirements.txt`). `src/` is bind-mounted to `/src`, so code changes reload without a rebuild. It waits for mongo to be healthy (`depends_on: condition: service_healthy`). Mongo connection details and allowed CORS origins come from environment variables.
- **app**: `node:16` image that runs `yarn install && yarn start`. `src/` is bind-mounted, and `node_modules` lives in a named volume so Linux-built dependencies don't mix with the host's.

Ports are published to the host, so the browser reaches React on `3000` and the API on `8000`. The browser calls the API directly, which is why CORS is allowed for `http://localhost:3000`.

### Issues fixed in the original setup

| Problem | Fix |
|---|---|
| `apt-get install mongodb-org` failed: no arm64 package for Debian buster (Apple Silicon) | Use the official `mongo:4.4` image |
| Debian's yarn package pulls a recent Node; `react-scripts 4` fails on Node 17+ (`ERR_OSSL_EVP_UNSUPPORTED`) | Use `node:16` for the app |
| `easy_install pip` doesn't exist in current Python images | Removed; pip is already installed |
| One heavy image (Mongo, Node, nginx, Jupyter, pandas, …) used for all three containers | One image per job, `requirements.txt` trimmed to what the API uses |
| API could start before Mongo was ready | Healthcheck + `depends_on` condition |
| `POST /todos` (no trailing slash) fails, since Django can't redirect a POST | Route accepts both `/todos` and `/todos/` |
| Mongo's `ObjectId` isn't JSON serializable | Repository maps documents to a `Todo` with a string `id` |
