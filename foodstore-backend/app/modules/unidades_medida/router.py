from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.modules.unidades_medida.model import UnidadMedida

# 1. Definición del Router modular
router = APIRouter(prefix="/unidades-medida", tags=["Unidades de Medida"])


# 2. Endpoint GET de solo lectura
@router.get(
    "",
    response_model=List[UnidadMedida],
    status_code=status.HTTP_200_OK,
    summary="Listar catálogo de unidades de medida (Solo lectura)"
)
def list_unidades_medida(
    session: Session = Depends(get_session)
) -> List[UnidadMedida]:
    """
    Retorna el listado completo de unidades de venta disponibles.
    Consumido por el frontend para poblar el selector de unidad de venta.
    """
    unidades = session.exec(select(UnidadMedida)).all()
    return list(unidades)

