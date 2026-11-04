from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.core.database import create_db_and_tables, engine
from app.core.seed import seed_unidades_medida
from app.modules.unidades_medida.router import router as unidades_router


# 1. Ciclo de vida moderno de FastAPI (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta automáticamente al iniciar y apagar el servidor:
    - Al arrancar: crea las tablas de SQLModel y corre el seed idempotente.
    """
    create_db_and_tables()
    with Session(engine) as session:
        seed_unidades_medida(session)
    yield


# 2. Instancia principal de FastAPI
app = FastAPI(
    title="Food Store — API Catálogo de Productos",
    description="Sistema de gestión de catálogo, stock y relaciones (Parcial 2 - Programación IV)",
    version="1.0.0",
    lifespan=lifespan
)

# 3. Middleware de CORS (Cross-Origin Resource Sharing)
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [
    frontend_origin,
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Inclusión de los routers bajo el prefijo /api/v1
app.include_router(unidades_router, prefix="/api/v1")


# 5. Endpoint simple de salud de la API
@app.get("/", tags=["Health"])
def health_check():
    """Verificación de que el backend está encendido y accesible."""
    return {
        "status": "ok",
        "service": "Food Store API",
        "docs": "/docs"
    }

