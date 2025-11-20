from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_routes


def create_app():
    app = FastAPI(title="Bookstation - Content-Based Recommender")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_routes)
    return app
