from sqlmodel import SQLModel


class ClasificarProductoRequest(SQLModel):
    """Body de la petición para clasificar un producto en una categoría."""
    categoria_id: int
    es_principal: bool = False


class ProductoCategoriaRead(SQLModel):
    """DTO de salida de un vínculo Producto-Categoría."""
    producto_id: int
    categoria_id: int
    es_principal: bool
    # Nombre de la categoría para facilitar la lectura en la respuesta
    categoria_nombre: str = ""

