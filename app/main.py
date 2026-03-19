from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from mongo_datatables import DataTables, DataField
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

GEONAMES_FIELDS = [
    DataField("name",         "string"),
    DataField("country_code", "keyword"),
    DataField("feature_code", "keyword"),
    DataField("admin1_code",  "keyword"),
    DataField("population",   "number"),
    DataField("timezone",     "string"),
    DataField("latitude",     "number"),
    DataField("longitude",    "number"),
]


_client = None


def get_db():
    global _client
    if _client is None:
        _client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
    return _client["geonames_demo"]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/places")
async def places_data(request: Request):
    try:
        data = await request.json()
        result = DataTables(get_db(), "places", data, data_fields=GEONAMES_FIELDS).get_rows()
        return JSONResponse(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e), "data": [],
            "draw": 1, "recordsTotal": 0, "recordsFiltered": 0
        }, status_code=500)
