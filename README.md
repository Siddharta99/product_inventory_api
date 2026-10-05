# Product Inventory API
A small web service that keeps products in a SQLite file and lets any client add, view, change, and delete them over HTTP.
A complete CRUD REST API for managing a product inventory — built with Python, FastAPI, and SQLite.
Products are created, read, updated, and deleted over HTTP, with automatic validation and honest error codes.

## Features

- Full CRUD over HTTP: POST, GET, PUT, DELETE
- Automatic request validation with Pydantic — bad JSON dies with 422 and a detailed report
- Honest responses: unknown ids return 404, verified with rowcount before claiming success
- Auto-generated interactive documentation at `/docs` (Swagger UI)
- SQLite persistence — one file, zero setup

## Endpoints

| Method | Endpoint           | Purpose            | Success | On error        |
|--------|--------------------|--------------------|---------|-----------------|
| GET    | `/`                | Heartbeat check    | 200     | —               |
| GET    | `/products`        | List all products  | 200     | —               |
| POST   | `/products`        | Create a product   | 200     | 422 invalid body|
| PUT    | `/products/{id}`   | Update a product   | 200     | 404 unknown id  |
| DELETE | `/products/{id}`   | Delete a product   | 200     | 404 unknown id  |

## Tech Stack

Python 3.10 · FastAPI · Uvicorn · SQLModel (ORM) · SQLite

## How to Run
1. Clone this repository: `git clone https://github.com/Siddharta99/product_inventory_api.git`
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `.\venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install the exact dependencies from the recipe: `pip install -r requirements.txt`
4. Start the server: `uvicorn api:app --reload --port 9000`
5. Open the interactive docs: http://127.0.0.1:9000/docs

## Example

POST /products  →  body: {"name": "Keyboard", "price": 2000}
response:       →  {"message": "Product added!", "id": 1}

## War Stories — what this project taught me

- Quotes make text; no quotes make values. One pair of quotes turned every price into the literal string "row[2]".
- (5) is an int. (5,) is a tuple. The comma IS the tuple.
- Two files named products.db in two folders = split-brain confusion. Always verify which database the server actually talks to.
- When the UI lies, descend the layers: server logs, then curl, then the file itself.
- **The ORM Translator:** Migrated from raw SQL strings to SQLModel. The database still only speaks SQL, but the ORM translates my Python objects into SQL queries (and back) automatically. Types are now law: sending a string for an integer price triggers a 422 shield before it ever touches the database.

## Author

Siddharta99 — learning backend one bug at a time. This repo is proof the bugs were worth it.