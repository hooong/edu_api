from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from edu_register_api.api.payment import router as payment_router
from edu_register_api.core.config import settings
from edu_register_api.api.auth import router as auth_router
from edu_register_api.api.course import router as course_router
from edu_register_api.api.test import router as test_router


app = FastAPI(title=f"{settings.APP_ENV} Edu Register API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(course_router)
app.include_router(test_router)
app.include_router(payment_router)
