from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


from api.core.config import settings
from api.routes import (
    ingredient_routes,
    planned_recipe_routes,
    recipe_routes,
    auth_routes,
    upload_routes,
)


app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc")

# Add CORS middleware for development environment
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_HOST],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


api_router = APIRouter()
api_router.include_router(recipe_routes.router)
api_router.include_router(recipe_routes.unauth_router)
api_router.include_router(auth_routes.router)
api_router.include_router(planned_recipe_routes.router)
api_router.include_router(ingredient_routes.router)
api_router.include_router(upload_routes.router)


app.include_router(api_router, prefix=settings.API_V1_STR)


# Add the static frontend files if not in development
if settings.ENVIRONMENT != "development":
    app.mount(
        "/", StaticFiles(directory=settings.VUE_STATIC_DIR, html=True), name="frontend"
    )

    # Add catch-all route for handling 404s
    @app.exception_handler(404)
    async def custom_404_handler(request, __):
        return FileResponse(f"{settings.VUE_STATIC_DIR}/index.html")
