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

DATA_FIELDS = [
    DataField("name",          "string"),
    DataField("birth_country", "string"),
    DataField("year",          "number"),
    DataField("category",      "string"),
    DataField("motivation",    "string"),
    DataField("share",         "number"),
]


def get_db():
    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
    client.db = client["nobel_demo"]
    return client


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/laureates")
async def laureates_data(request: Request):
    try:
        data = await request.json()
        result = DataTables(get_db(), "laureates", data, data_fields=DATA_FIELDS).get_rows()
        return JSONResponse(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e), "data": [],
            "draw": 1, "recordsTotal": 0, "recordsFiltered": 0
        }, status_code=500)
