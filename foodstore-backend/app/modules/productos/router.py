from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Response, status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.productos.schema import ProductoCreate, ProductoUpdate, ProductoPublic
from app.modules.productos.service import ProductoService

# 1. Definición del router modular
router = APIRouter(prefix="/productos", tags=["Productos"])


# 2. Inyección del servicio
def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    """Inyecta la sesión de BD en el servicio de Productos."""
    return ProductoService(session)


# --- LOS 5 ENDPOINTS DEL CRUD DE PRODUCTOS ---

@router.post(
    "",
    response_model=ProductoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un producto"
)
def create_producto(
    data: ProductoCreate,
    service: ProductoService = Depends(get_producto_service)
) -> ProductoPublic:
    """
    Crea un producto nuevo en el catálogo:
    - Valida nombre (mín. 3 caracteres), precio_base >= 0, stock_cantidad >= 0 (RN-01).
    - Valida que la unidad de venta exista en la base (RN-03).
    - Valida que si la unidad es contable, el stock sea un número entero (RN-10).
    - Valida nombre único entre productos activos (RN-02).
    - Retorna el producto creado con la unidad anidada y el campo calculado hay_stock (RN-11).
    """
    return service.create(data)


@router.get(
    "",
    response_model=List[ProductoPublic],
    status_code=status.HTTP_200_OK,
    summary="Listar productos con paginación y filtros"
)
def list_productos(
    skip: int = Query(0, ge=0, description="Offset de paginación (>= 0)"),
    limit: int = Query(10, ge=1, le=50, description="Límite por página (1..50)"),
    activo: Optional[bool] = Query(None, description="Omitido o true devuelve activos; false devuelve anulados"),
    disponible: Optional[bool] = Query(None, description="Filtrar por pausa manual de venta"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría clasificada"),
    search: Optional[str] = Query(None, description="Búsqueda por coincidencia parcial en el nombre"),
    service: ProductoService = Depends(get_producto_service)
) -> List[ProductoPublic]:
    """Retorna el listado paginado y filtrado de productos del catálogo."""
    return service.list(
        skip=skip,
        limit=limit,
        activo=activo,
        disponible=disponible,
        categoria_id=categoria_id,
        search=search,
    )


@router.get(
    "/{id}",
    response_model=ProductoPublic,
    status_code=status.HTTP_200_OK,
    summary="Detalle de un producto por ID"
)
def get_producto(
    id: int = Path(..., ge=1, description="ID del producto"),
    service: ProductoService = Depends(get_producto_service)
) -> ProductoPublic:
    """Retorna el detalle completo de un producto. Si no existe, devuelve 404 (RN-03)."""
    return service.get_by_id(id)


@router.put(
    "/{id}",
    response_model=ProductoPublic,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un producto"
)
def update_producto(
    id: int = Path(..., ge=1, description="ID del producto"),
    data: ProductoUpdate = ...,
    service: ProductoService = Depends(get_producto_service)
) -> ProductoPublic:
    """
    Actualiza todos los campos propios del producto:
    - Si el id no existe: 404 (RN-03).
    - Si el producto está anulado: 409 (RN-05).
    - Si la unidad_venta_id no existe: 404 (RN-03).
    - Si la unidad es contable y el stock tiene decimales: 422 (RN-10).
    - Si el nombre colisiona con otro producto activo: 409 (RN-02).
    """
    return service.update(id, data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Anular un producto (Baja lógica)"
)
def delete_producto(
    id: int = Path(..., ge=1, description="ID del producto"),
    service: ProductoService = Depends(get_producto_service)
) -> Response:
    """
    RN-04: Baja lógica del producto.
    - Fija activo = False y registra fecha y hora en anulado_at.
    - Nunca elimina la fila de la base de datos.
    - Si ya está anulado, devuelve 409 Conflict.
    - Responde 204 No Content sin cuerpo.
    """
    service.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

