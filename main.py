from decouple import config

from fastapi import FastAPI

# there seems to be a bug with FastAPI's middleware
# https://stackoverflow.com/questions/65191061/fastapi-cors-middleware-not-working-with-get-method/65994876#65994876
# https://nilsdebruin.medium.com/fastapi-how-to-add-basic-and-cookie-authentication-a45c85ef47d3
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# connect to mongodb
from motor.motor_asyncio import AsyncIOMotorClient

from routers.cars import router as cars_router
from routers.users import router as users_router


DB_URL = config("DB_URL", cast=str)
DB_NAME = config("DB_NAME", cast=str)

sample= {
    1: { "name": "John", "age": 30, "city": "New York"},
    2: { "name": "Peter", "age": 20, "city": "Berlin"},
    3: { "name": "Amy", "age": 20, "city": "Paris"},
    4: { "name": "Hannah", "age": 20, "city": "London"}}

# define origins
origins = [
    "*",
]

# instantiate the app
app = FastAPI(middleware=middleware)
@app.get("/")
def home():
    return {"Message": "Welcome to the Car API"}

@app.get("/get-item/{item_id}")
def get_item( item_id: int):
    return sample[item_id]

app.include_router(cars_router, prefix="/cars", tags=["cars"])
app.include_router(users_router, prefix="/users", tags=["users"])



@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.mongodb = app.mongodb_client[DB_NAME]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
