from datetime import datetime
from typing import Annotated, List, Optional
from sqlmodel import SQLModel, Field
from app.modules.unidades_medida.model import TipoUnidadMedida


# 1. Esquema simple de Unidad de Medida para anidar en ProductoPublic
class UnidadMedidaSimple(SQLModel):
    """Información básica de la unidad de venta anidada en ProductoPublic."""
    id: int
    nombre: str
    simbolo: str
    tipo: TipoUnidadMedida


# 2. Esquema simple de Categoría para anidar en ProductoPublic
class CategoriaSimple(SQLModel):
    """Información de la categoría asociada al producto con indicador de principal."""
    id: int
    nombre: str
    es_principal: bool = False


# 3. Esquema Base con validaciones obligatorias (RN-01)
class ProductoBase(SQLModel):
    """
    Campos base compartidos de Producto.
    Validaciones declaradas con Annotated + Field según consigna:
    - nombre: min_length=3
    - precio_base: ge=0
    - stock_cantidad: ge=0
    - unidad_venta_id: obligatorio (ge=1)
    """
    nombre: Annotated[
        str,
        Field(min_length=3, max_length=150, description="Nombre del producto (mín. 3 caracteres)")
    ]
    descripcion: Annotated[
        Optional[str],
        Field(default=None, max_length=500, description="Descripción opcional del producto")
    ] = None
    precio_base: Annotated[
        float,
        Field(ge=0, description="Precio unitario base (>= 0)")
    ]
    unidad_venta_id: Annotated[
        int,
        Field(ge=1, description="ID de la unidad de venta obligatoria")
    ]
    stock_cantidad: Annotated[
        float,
        Field(default=0.0, ge=0, description="Cantidad de stock en unidad de venta (>= 0)")
    ] = 0.0
    disponible: Annotated[
        bool,
        Field(default=True, description="Pausa manual de venta (True: habilitado, False: pausado)")
    ] = True


# 4. Esquema de Entrada para Creación (POST)
class ProductoCreate(ProductoBase):
    """Cuerpo de la petición para crear un producto."""
    pass


# 5. Esquema de Entrada para Actualización Completa (PUT)
class ProductoUpdate(ProductoBase):
    """Cuerpo de la petición para actualizar campos propios del producto."""
    pass


# 6. Esquema de Salida Público (GET, POST response, PUT response)
class ProductoPublic(ProductoBase):
    """
    DTO de salida pública del producto.
    Incluye:
    - id: Identificador único autogenerado.
    - activo: Indicador de baja lógica (RN-04).
    - anulado_at: Fecha y hora de baja lógica.
    - hay_stock: Campo calculado (stock_cantidad > 0, RN-11). No persistido.
    - unidad_venta: Unidad de medida anidada con nombre, símbolo y tipo.
    - categorias: Lista de categorías en las que está clasificado el producto.
    """
    id: int
    activo: bool
    anulado_at: Optional[datetime] = None
    hay_stock: bool
    unidad_venta: Optional[UnidadMedidaSimple] = None
    categorias: List[CategoriaSimple] = []

