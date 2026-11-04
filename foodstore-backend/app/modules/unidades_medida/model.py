from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class TipoUnidadMedida(str, Enum):
    """
    Tipo de unidad de venta permitida en Food Store.
    Define cómo se interpreta y valida el stock (RN-10):
    - peso: permite decimales (ej. kg, g)
    - volumen: permite decimales (ej. L, mL)
    - contable: requiere cantidades enteras (ej. u, doc)
    """
    peso = "peso"
    volumen = "volumen"
    contable = "contable"


class UnidadMedida(SQLModel, table=True):
    """
    Entidad UnidadMedida: Catálogo de solo lectura con seed inicial.
    Todo producto tiene una única unidad de venta obligatoria.
    """
    __tablename__ = "unidades_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True, min_length=2, max_length=50)
    simbolo: str = Field(unique=True, min_length=1, max_length=10)
    tipo: TipoUnidadMedida = Field(index=True)

