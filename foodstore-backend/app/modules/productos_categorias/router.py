from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlmodel import Session
from app.core.database import get_session
from app.modules.productos_categorias.schema import ClasificarProductoRequest, ProductoCategoriaRead
from app.modules.productos_categorias.service import ProductoCategoriaService
from app.modules.categorias.model import Categoria

router = APIRouter(prefix="/productos", tags=["Relación Producto-Categoría"])


def get_service(session: Session = Depends(get_session)) -> ProductoCategoriaService:
    return ProductoCategoriaService(session)


def _enrich(links, session: Session) -> List[ProductoCategoriaRead]:
    """Enriquece los vínculos con el nombre de la categoría."""
    result = []
    for lnk in links:
        cat = session.get(Categoria, lnk.categoria_id)
        result.append(ProductoCategoriaRead(
            producto_id=lnk.producto_id,
            categoria_id=lnk.categoria_id,
            es_principal=lnk.es_principal,
            categoria_nombre=cat.nombre if cat else "",
        ))
    return result


@router.post(
    "/{id}/categorias",
    response_model=List[ProductoCategoriaRead],
    status_code=status.HTTP_201_CREATED,
    summary="Clasificar un producto en una categoría"
)
def clasificar_producto(
    id: int = Path(..., ge=1, description="ID del producto"),
    data: ClasificarProductoRequest = ...,
    service: ProductoCategoriaService = Depends(get_service),
    session: Session = Depends(get_session)
) -> List[ProductoCategoriaRead]:
    """
    Clasifica un producto en una categoría:
    - RN-07: Rechaza si ya existe el vínculo (409).
    - RN-08: Rechaza si el producto o la categoría están anulados (409).
    - RN-09: Si es_principal=True, la categoría principal anterior pierde esa bandera.
    Retorna la lista actualizada de vínculos del producto.
    """
    links = service.clasificar(id, data.categoria_id, data.es_principal)
    return _enrich(links, session)


@router.get(
    "/{id}/categorias",
    response_model=List[ProductoCategoriaRead],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías de un producto"
)
def listar_categorias_producto(
    id: int = Path(..., ge=1, description="ID del producto"),
    service: ProductoCategoriaService = Depends(get_service),
    session: Session = Depends(get_session)
) -> List[ProductoCategoriaRead]:
    """Lista todas las categorías en las que está clasificado un producto."""
    links = service.listar(id)
    return _enrich(links, session)

