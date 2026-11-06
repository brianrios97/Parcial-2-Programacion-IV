from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.modules.productos_categorias.model import ProductoCategoria
from app.modules.productos.model import Producto
from app.modules.categorias.model import Categoria


class ProductoCategoriaService:
    """
    Servicio de la relación N:N Producto-Categoría.
    Implementa las reglas de negocio RN-07, RN-08 y RN-09.
    """

    def __init__(self, session: Session):
        self.session = session

    # --- VALIDACIONES AUXILIARES ---

    def _get_producto_activo(self, producto_id: int) -> Producto:
        """
        Obtiene el producto. Si no existe: 404. Si está anulado: 409 (RN-08).
        Un producto anulado no puede clasificarse en ninguna categoría.
        """
        producto = self.session.get(Producto, producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {producto_id} no encontrado"
            )
        if not producto.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto '{producto.nombre}' está anulado. No se puede clasificar un producto anulado (RN-08)"
            )
        return producto

    def _get_categoria_activa(self, categoria_id: int) -> Categoria:
        """
        Obtiene la categoría. Si no existe: 404. Si está anulada: 409 (RN-08).
        Un producto no puede clasificarse en una categoría anulada.
        """
        categoria = self.session.get(Categoria, categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id {categoria_id} no encontrada"
            )
        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La categoría '{categoria.nombre}' está anulada. No se puede clasificar en una categoría anulada (RN-08)"
            )
        return categoria

    # --- OPERACIONES ---

    def clasificar(
        self, producto_id: int, categoria_id: int, es_principal: bool
    ) -> List[ProductoCategoria]:
        """
        Clasifica un producto en una categoría:
        - RN-08: Producto y categoría deben estar activos (409 si alguno está anulado).
        - RN-07: No se puede clasificar dos veces en la misma categoría (409).
        - RN-09: Si es_principal=True, se quita la bandera del vínculo que la tenía antes.
        Responde con la lista actualizada de vínculos del producto.
        """
        # Validar que ambos existen y están activos (RN-08)
        self._get_producto_activo(producto_id)
        self._get_categoria_activa(categoria_id)

        # RN-07: Verificar que el vínculo no existe ya
        existente = self.session.get(ProductoCategoria, (producto_id, categoria_id))
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto {producto_id} ya está clasificado en la categoría {categoria_id} (RN-07)"
            )

        # RN-09: Si la nueva categoría es principal, desactivar la anterior principal
        if es_principal:
            stmt = select(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id,
                ProductoCategoria.es_principal == True
            )
            anterior_principal = self.session.exec(stmt).first()
            if anterior_principal:
                anterior_principal.es_principal = False
                self.session.add(anterior_principal)

        # Crear el nuevo vínculo
        nuevo = ProductoCategoria(
            producto_id=producto_id,
            categoria_id=categoria_id,
            es_principal=es_principal
        )
        self.session.add(nuevo)
        self.session.commit()

        # Retornar todos los vínculos actualizados del producto
        return self.listar(producto_id)

    def listar(self, producto_id: int) -> List[ProductoCategoria]:
        """
        Lista todos los vínculos Producto-Categoría de un producto.
        Verifica que el producto existe (404 si no).
        """
        # Verificar que el producto existe (no importa si está anulado para listar)
        producto = self.session.get(Producto, producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {producto_id} no encontrado"
            )

        stmt = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id
        )
        return list(self.session.exec(stmt).all())

