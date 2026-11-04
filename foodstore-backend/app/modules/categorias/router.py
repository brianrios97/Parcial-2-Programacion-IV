from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Response, status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.categorias.schema import CategoriaCreate, CategoriaUpdate, CategoriaRead
from app.modules.categorias.service import CategoriaService

# 1. Definición del Router modular
router = APIRouter(prefix="/categorias", tags=["Categorías"])


# 2. Función auxiliar para inyectar el servicio
def get_categoria_service(session: Session = Depends(get_session)) -> CategoriaService:
    """Inyecta la sesión de BD dentro del servicio de Categorías."""
    return CategoriaService(session)


# --- LOS 5 ENDPOINTS DEL CRUD ---

@router.post(
    "",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría"
)
def create_categoria(
    data: CategoriaCreate,
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaRead:
    """Crea una nueva categoría. Aplica RN-02 (nombre único entre activas con 409)."""
    return service.create(data)


@router.get(
    "",
    response_model=List[CategoriaRead],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías con filtros"
)
def list_categorias(
    activo: Optional[bool] = Query(default=None, description="True: activas, False: anuladas"),
    search: Optional[str] = Query(default=None, description="Búsqueda parcial por nombre"),
    service: CategoriaService = Depends(get_categoria_service)
) -> List[CategoriaRead]:
    """Lista las categorías con soporte para filtros de activo y búsqueda por texto."""
    return service.list(activo=activo, search=search)


@router.get(
    "/{id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Detalle de una categoría"
)
def get_categoria(
    id: int = Path(..., ge=1, description="ID de la categoría"),
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaRead:
    """Retorna los datos de una categoría. Si no existe, devuelve 404."""
    return service.get_by_id(id)


@router.put(
    "/{id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una categoría"
)
def update_categoria(
    id: int = Path(..., ge=1, description="ID de la categoría"),
    data: CategoriaUpdate = ...,
    service: CategoriaService = Depends(get_categoria_service)
) -> CategoriaRead:
    """Actualiza nombre y descripción. Si está anulada o el nombre colisiona, devuelve 409."""
    return service.update(id, data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Anular una categoría (Baja lógica)"
)
def delete_categoria(
    id: int = Path(..., ge=1, description="ID de la categoría"),
    service: CategoriaService = Depends(get_categoria_service)
) -> Response:
    """
    RN-06: Baja lógica. Pone activo=False y registra fecha en anulado_at.
    Responde 204 No Content sin cuerpo.
    """
    service.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

