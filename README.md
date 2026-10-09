# Product Inventory API
A small web service that keeps products in a SQLite file and lets clients add, view, change, and delete them over HTTP — now guarded by a full bouncer system: hashed passwords, JWT wristbands, and locked write-doors.

A complete CRUD REST API for managing a product inventory — built with Python, FastAPI, SQLModel, and SQLite, secured with salted PBKDF2 hashing and JWT authentication.
Products are created, read, updated, and deleted over HTTP, with automatic validation and honest error codes. Write operations require a valid Bearer wristband.

## Features

- Full CRUD over HTTP: POST, GET, PUT, DELETE
- Automatic request validation with Pydantic — bad JSON dies with 422 and a detailed report
- Honest responses: unknown ids return 404, verified with rowcount before claiming success
- Auto-generated interactive documentation at `/docs` (Swagger UI) — with an Authorize button
- SQLite persistence — one file, zero setup
- **Secure registration:** passwords are never stored — only per-user salted PBKDF2 fingerprints (100,000 rounds)
- **JWT authentication:** OAuth2 password flow issues 30-minute wristbands; a scanner checks every write-door
- **Honest refusals:** 409 for taken usernames, 401 for missing/fake/expired wristbands — identical messages so thieves cannot enumerate users

## Endpoints

| Method | Endpoint           | Purpose                        | Auth      | Success | On error                  |
|--------|--------------------|--------------------------------|-----------|---------|---------------------------|
| GET    | `/`                | Heartbeat check                | —         | 200     | —                         |
| GET    | `/products`        | List all products (public menu)| —         | 200     | —                         |
| POST   | `/users`           | Register a user                | —         | 200     | 409 taken · 422 bad shape |
| POST   | `/login`           | Login, receive JWT wristband   | —         | 200     | 401 wrong credentials     |
| POST   | `/products`        | Create a product               | 🔒 Bearer | 200     | 401 · 422 invalid body    |
| PUT    | `/products/{id}`   | Update a product               | 🔒 Bearer | 200     | 401 · 404 unknown id      |
| DELETE | `/products/{id}`   | Delete a product               | 🔒 Bearer | 200     | 401 · 404 unknown id      |

## Security Model (the club)

- **Door-law (422):** Pydantic checks the shape at the threshold; bad JSON dies before endpoint code wakes up.
- **Vault-law (409):** truth check before write; duplicate usernames are refused, never silently overwritten.
- **Fingerprint vault:** password + random per-user salt, ground 100,000 rounds (PBKDF2-HMAC-SHA256); only `salt:grind` is stored.
- **Wristbands (JWT):** HS256-signed tokens, 30-minute expiry; `Depends(get_current_user)` verifies the hologram at every locked door.
- **Menu vs kitchen:** `GET /products` stays public — customers must browse to buy. All write-doors are staff-only.

## Tech Stack

Python 3.10 · FastAPI · Uvicorn · SQLModel (ORM) · SQLite · PyJWT · python-multipart · stdlib hashlib/secrets

## How to Run
1. Clone this repository: `git clone https://github.com/Siddharta99/product_inventory_api.git`
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `.\venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install the exact dependencies from the recipe: `pip install -r requirements.txt`
4. Start the server: `uvicorn api:app --reload --port 9000`
5. Open the interactive docs: http://127.0.0.1:9000/docs
6. Register via `POST /users`, then click **Authorize** (top-right), log in with those credentials — the locked doors open.

## Example

POST /users   →  {"username": "sidd", "email": "s@x.com", "password": "hunter2"}  →  200
POST /login   →  (form: sidd / hunter2)  →  {"access_token": "eyJ...", "token_type": "bearer"}
POST /products  (header: Authorization: Bearer eyJ...)  →  {"message": "Product added!", "id": 1}

## War Stories — what this project taught me

- **Quotes make text:** no quotes make values. One pair of quotes turned every price into the literal string `"row[2]"`.
- **(5) is an int. (5,) is a tuple:** The comma IS the tuple.
- **Two files named products.db in two folders:** split-brain confusion. Always verify which database the server actually talks to.
- **When the UI lies, descend the layers:** server logs, then curl, then the file itself.
- **The ORM Translator:** Migrated from raw SQL strings to SQLModel. The database still only speaks SQL, but the ORM translates my Python objects into SQL queries (and back) automatically. Types are now law: sending a string for an integer price triggers a 422 shield before it ever touches the database.
- **The Ghost Table:** `create_all(engine)` ran *before* `class User` was defined, so the `users` table was never born; INSERT knocked on a ghost and the server died with a 500. *Lesson: Blueprints before construction, always.*
- **The Paper-Form Door:** Switching `/login` to the OAuth2 form flow crashed the server with a RuntimeError demanding a reading machine I didn't own. The traceback printed its own cure: `pip install python-multipart`. *Lesson: Read the last line of the traceback first.*
- **Two Guards, One Code:** `401 "Not authenticated"` is the rope (no wristband). `401 "Fake or expired wristband!"` is the hologram scanner (dead or forged band). Same status, different depths — defense in depth.



## Author

Siddharta99 — learning backend one bug at a time. This repo is proof the bugs were worth it.