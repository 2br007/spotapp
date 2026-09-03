# SpotApp

SpotApp is a map-first community for finding places to skateboard, surf, and ride BMX. Riders can browse nearby spots, search a city or coastline, register, and publish their own discoveries.

## Run locally

```bash
source tests/set_unittest_settings.sh
PYTHONPATH=. ./venv/bin/uvicorn spotapp:app --reload
```

Open `http://127.0.0.1:8000/` for the map or `/docs` for the API.

## Seed Gijon spots

With the database available, create the starter dataset with:

```bash
source tests/set_unittest_settings.sh
PYTHONPATH=. ./venv/bin/python scripts/seed_gijon.py
```

The seed is safe to run repeatedly. It adds five public spots around Gijon covering surfing, skateboarding, and BMX. The coordinates are approximate map pins, so verify local access and conditions before riding.

## Docker deployment

Create a `.env` file next to `docker-compose.yml`:

```dotenv
POSTGRES_PASSWORD=replace-with-a-long-database-password
SECRET_KEY=replace-with-a-long-random-signing-key
```

Start the production-style app and PostgreSQL database:

```bash
docker compose up --build -d
```

Populate that PostgreSQL database with the Gijon starter spots:

```bash
docker compose --profile seed run --rm seed
```

The database is stored in the `postgres_data` Docker volume. The seed service is opt-in and uses the same database as the app; it is not connected to the test database.

## Location services

- Map tiles: OpenStreetMap, rendered with Leaflet.
- Place search: Nominatim, the OpenStreetMap geocoder.
- Device location: the browser Geolocation API.

Nominatim is a free community service with usage limits. Production should use a proper application User-Agent, cache searches, rate-limit requests, and consider a dedicated geocoder or tile provider as traffic grows.
