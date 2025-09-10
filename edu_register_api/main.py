from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from edu_register_api.core.config import settings


app = FastAPI(title=f"{settings.APP_ENV} Edu Register API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
