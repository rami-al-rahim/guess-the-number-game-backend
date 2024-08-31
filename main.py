from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import geoip2.database
from supabase import create_client, Client
import random
app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

supabase: Client = create_client("https://vgvqjwynmklmvhoidvjz.supabase.co",
                                 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZndnFqd3lubWtsbXZob2lkdmp6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNDkzODQwMCwiZXhwIjoyMDQwNTE0NDAwfQ.2dXJm9egVRUYMxtS4RPzLXwCG6ML9JRAzOYKmNJTXZs")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.get("/dev")
async def leaderboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="developing.html"
    )


@app.post("/database/increase/{number}")
def increase(request: Request, number: int):
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        print(x_forwarded_for.split(',')[0])
    # Generate a random number between 1 and 10
    random_number = random.randint(1, 10)
    print(random_number)
    if random_number != number:
        return JSONResponse("no", status_code=201)
    # get user country
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    ip_address = None
    if x_forwarded_for:

        ip_address = x_forwarded_for.split(',')[0]
        print(ip_address)
    else:
        # Fall back to the client IP address
        ip_address = "176.28.251.255"
    reader = geoip2.database.Reader('IP2LOCATION-LITE-DB1.MMDB')

    response = reader.country(ip_address)

    # Extract information
    country = response.country.name
    reader.close()
    supabase.postgrest.rpc("increase_country", {
                           "country_name": country}).execute()
    return JSONResponse("", status_code=200)
