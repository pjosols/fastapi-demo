# mongo-datatables FastAPI Demo

A FastAPI app demonstrating server-side DataTables powered by
[mongo-datatables](https://github.com/pjosols/mongo-datatables), using the
[GeoNames](https://www.geonames.org/) dataset (~13M geographic place names).

## Quickstart

1. Clone and install:
   ```bash
   git clone https://github.com/pjosols/fastapi-demo.git
   cd fastapi-demo
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Download and seed the database:
   ```bash
   python seed_geonames.py --download
   ```
   If you already have `data/allCountries.txt`:
   ```bash
   python seed_geonames.py
   ```

3. Run:
   ```bash
   uvicorn app.main:app --reload
   ```

Open [http://localhost:8000](http://localhost:8000).

## Custom MongoDB connection

```bash
python seed_geonames.py --connection "mongodb://user:password@host:port/"
```

Set `MONGO_URI` in the environment to point the app at a different instance.

## Project structure

```
fastapi-demo/
├── app/
│   ├── main.py              # routes + API endpoint
│   ├── static/
│   │   ├── css/style.css    # dark theme
│   │   └── js/table.js      # DataTables init + header→field mapping
│   └── templates/index.html # page template
├── data/allCountries.txt    # GeoNames bulk data (downloaded separately)
├── seed_geonames.py         # downloads and loads data into MongoDB
└── requirements.txt
```

## How it works

`main.py` defines the data fields and passes the DataTables request to `mongo-datatables`:

```python
GEONAMES_FIELDS = [
    DataField("name",         "string"),   # substring search
    DataField("country_code", "keyword"),  # exact match, uses index
    DataField("feature_code", "keyword"),  # exact match, uses index
    DataField("admin1_code",  "keyword"),  # exact match, uses index
    DataField("population",   "number"),   # numeric comparison
    DataField("timezone",     "string"),   # substring search
    DataField("latitude",     "number"),
    DataField("longitude",    "number"),
]

@app.post("/api/places")
async def places_data(request: Request):
    data = await request.json()
    result = DataTables(get_db(), "places", data, data_fields=GEONAMES_FIELDS).get_rows()
    return JSONResponse(result)
```

`table.js` maps friendly column header names to MongoDB field names so users can
type `country:GB` instead of `country_code:GB`:

```javascript
const headerToKey = {
    'name':       'name',
    'country':    'country_code',
    'feature':    'feature_code',
    'region':     'admin1_code',
    'population': 'population',
    'timezone':   'timezone',
};
```

That mapping is applied in the `ajax.data` function before the request is sent to the server.

## Search examples

```
name:york                    →  all places containing "york"
country:GB                   →  exact match on country_code (indexed)
feature:PPL                  →  populated places
country:US feature:MT        →  mountains in the US
population:>1000000          →  cities over 1 million
timezone:America             →  all American timezones
```

## License

MIT
