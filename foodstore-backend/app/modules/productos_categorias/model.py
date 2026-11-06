from sqlmodel import SQLModel, Field


class ProductoCategoria(SQLModel, table=True):
    """
    Tabla intermedia de la relación N:N entre Producto y Categoria.

    Decisión de diseño:
    - Clave primaria COMPUESTA (producto_id, categoria_id): garantiza por estructura
      que un producto no se clasifique dos veces en la misma categoría (RN-07).
    - Atributo propio 'es_principal': indica la categoría principal del producto.
      A lo sumo una fila por producto puede tener es_principal = True (RN-09).
    - Es un 'link model' en SQLModel: tiene table=True y campos propios,
      lo que permite navegar la relación desde ambos lados con Relationship.

    Pregunta de defensa: ¿Por qué no usar una tabla con id propio?
    → Porque la PK compuesta es suficiente para identificar el vínculo de forma única,
      y además impone la restricción de unicidad sin índices adicionales.
    """
    __tablename__ = "productos_categorias"

    # FK hacia Producto - parte de la clave primaria compuesta
    producto_id: int = Field(
        foreign_key="productos.id",
        primary_key=True,
        description="ID del producto clasificado"
    )
    # FK hacia Categoria - parte de la clave primaria compuesta
    categoria_id: int = Field(
        foreign_key="categorias.id",
        primary_key=True,
        description="ID de la categoría en la que se clasifica el producto"
    )
    # Atributo propio del vínculo
    es_principal: bool = Field(
        default=False,
        nullable=False,
        description="True si es la categoría principal del producto. Solo una por producto (RN-09)"
    )

