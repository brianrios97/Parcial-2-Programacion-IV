from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.modules.productos.model import Producto
from app.modules.productos.schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoPublic,
    UnidadMedidaSimple,
    CategoriaSimple,
)
from app.modules.unidades_medida.model import UnidadMedida, TipoUnidadMedida
from app.modules.productos_categorias.model import ProductoCategoria
from app.modules.categorias.model import Categoria


class ProductoService:
    """
    Capa de servicio para el módulo de Productos.
    Encapsula toda la lógica de negocio y las validaciones de las reglas del parcial:
    - RN-01: Validaciones de campos (en schema y service).
    - RN-02: Nombre único entre productos activos.
    - RN-03: Validación de existencia de ID de producto y FK de unidad_venta_id (404).
    - RN-04: Baja lógica con activo=False y anulado_at. Rechazo de re-anulación (409).
    - RN-05: Modificación prohibida en productos anulados (409).
    - RN-10: Stock debe ser entero para unidades de tipo contable (422).
    - RN-11: Campo calculado hay_stock (stock_cantidad > 0), no persistido.
    - RN-12: Independencia de disponible, activo y stock_cantidad.
    """

    def __init__(self, session: Session):
        self.session = session

    # --- VALIDACIONES AUXILIARES DE NEGOCIO ---

    def _validate_unidad_venta(self, unidad_venta_id: int) -> UnidadMedida:
        """
        RN-03: Valida que la unidad de venta exista en la base de datos.
        Si no existe, devuelve 404 Not Found.
        """
        unidad = self.session.get(UnidadMedida, unidad_venta_id)
        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La unidad de medida con id {unidad_venta_id} no existe"
            )
        return unidad

    def _validate_stock_contable(self, unidad: UnidadMedida, stock_cantidad: float) -> None:
        """
        RN-10: Si la unidad de venta es de tipo contable, stock_cantidad
        debe ser un número entero (sin decimales). Si tiene decimales, devuelve 422.
        """
        if unidad.tipo == TipoUnidadMedida.contable:
            if not float(stock_cantidad).is_integer():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Para la unidad de venta contable '{unidad.nombre}', el stock debe ser un número entero (recibido: {stock_cantidad})"
                )

    def _validate_nombre_unico(self, nombre: str, exclude_id: Optional[int] = None) -> None:
        """
        RN-02: El nombre es único entre productos activos (case-insensitive).
        Un registro anulado libera su nombre.
        """
        stmt = select(Producto).where(
            func.lower(Producto.nombre) == nombre.strip().lower(),
            Producto.activo == True
        )
        if exclude_id is not None:
            stmt = stmt.where(Producto.id != exclude_id)

        existente = self.session.exec(stmt).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto activo con el nombre '{nombre.strip()}'"
            )

    def to_public_dto(self, producto: Producto) -> ProductoPublic:
        """
        Transforma una entidad de base de datos Producto en su DTO de salida ProductoPublic.
        - RN-11: Calcula hay_stock dinámicamente (stock_cantidad > 0).
        - Anida la unidad de venta (id, nombre, símbolo, tipo).
        - Inicializa la lista de categorías (completada en Issue #4).
        """
        # Obtener o construir UnidadMedidaSimple
        unidad_dto: Optional[UnidadMedidaSimple] = None
        if producto.unidad_venta:
            unidad_dto = UnidadMedidaSimple(
                id=producto.unidad_venta.id,  # type: ignore
                nombre=producto.unidad_venta.nombre,
                simbolo=producto.unidad_venta.simbolo,
                tipo=producto.unidad_venta.tipo,
            )
        elif producto.unidad_venta_id:
            unidad_db = self.session.get(UnidadMedida, producto.unidad_venta_id)
            if unidad_db:
                unidad_dto = UnidadMedidaSimple(
                    id=unidad_db.id,  # type: ignore
                    nombre=unidad_db.nombre,
                    simbolo=unidad_db.simbolo,
                    tipo=unidad_db.tipo,
                )

        # Categorías asignadas (consulta directa a ProductoCategoria)
        categorias_dto: List[CategoriaSimple] = []
        from app.modules.productos_categorias.model import ProductoCategoria
        from app.modules.categorias.model import Categoria
        stmt_cats = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto.id
        )
        links = self.session.exec(stmt_cats).all()
        for link in links:
            cat = self.session.get(Categoria, link.categoria_id)
            if cat:
                categorias_dto.append(CategoriaSimple(
                    id=cat.id,  # type: ignore
                    nombre=cat.nombre,
                    es_principal=link.es_principal,
                ))

        # RN-11: hay_stock calculado
        hay_stock = bool(producto.stock_cantidad > 0)

        return ProductoPublic(
            id=producto.id,  # type: ignore
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            unidad_venta_id=producto.unidad_venta_id,
            stock_cantidad=producto.stock_cantidad,
            disponible=producto.disponible,
            activo=producto.activo,
            anulado_at=producto.anulado_at,
            hay_stock=hay_stock,
            unidad_venta=unidad_dto,
            categorias=categorias_dto,
        )

    # --- OPERACIONES CRUD ---

    def create(self, data: ProductoCreate) -> ProductoPublic:
        """
        Crea un nuevo producto tras validar:
        - RN-03: Unidad de venta existente en BD.
        - RN-10: Stock entero si la unidad es contable.
        - RN-02: Nombre único entre activos.
        """
        unidad = self._validate_unidad_venta(data.unidad_venta_id)
        self._validate_stock_contable(unidad, data.stock_cantidad)
        self._validate_nombre_unico(data.nombre)

        db_product = Producto.model_validate(data)
        db_product.nombre = db_product.nombre.strip()
        db_product.activo = True
        db_product.anulado_at = None

        self.session.add(db_product)
        self.session.commit()
        self.session.refresh(db_product)

        return self.to_public_dto(db_product)

    def list(
        self,
        skip: int = 0,
        limit: int = 10,
        activo: Optional[bool] = None,
        disponible: Optional[bool] = None,
        categoria_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[ProductoPublic]:
        """
        Lista productos paginados con filtros:
        - skip / limit: paginación.
        - activo: omitido o True = solo activos; False = solo anulados.
        - disponible: filtro por pausa de venta (True / False).
        - search: coincidencia parcial case-insensitive en el nombre.
        - categoria_id: filtra por categoría clasificada (si existe el enlace N:N).
        """
        stmt = select(Producto)

        # Filtro de activo: por defecto (None o True) solo activos; False solo anulados
        if activo is None or activo is True:
            stmt = stmt.where(Producto.activo == True)
        else:
            stmt = stmt.where(Producto.activo == False)

        # Filtro disponible
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        # Filtro búsqueda por nombre
        if search:
            stmt = stmt.where(func.lower(Producto.nombre).contains(search.strip().lower()))

        # Filtro por categoría vía tabla intermedia ProductoCategoria (Issue #4)
        if categoria_id is not None:
            from app.modules.productos_categorias.model import ProductoCategoria
            stmt = stmt.join(
                ProductoCategoria,
                Producto.id == ProductoCategoria.producto_id
            ).where(ProductoCategoria.categoria_id == categoria_id)

        stmt = stmt.offset(skip).limit(limit)
        productos = self.session.exec(stmt).all()

        return [self.to_public_dto(p) for p in productos]

    def get_by_id(self, id: int) -> ProductoPublic:
        """
        RN-03: Detalle de un producto por ID.
        Si no existe, devuelve 404.
        """
        producto = self.session.get(Producto, id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {id} no encontrado"
            )
        return self.to_public_dto(producto)

    def update(self, id: int, data: ProductoUpdate) -> ProductoPublic:
        """
        Actualiza los campos propios del producto:
        - RN-03: Producto debe existir (404).
        - RN-05: Si está anulado, no admite modificación (409).
        - RN-03: unidad_venta_id debe existir (404).
        - RN-10: Si la unidad es contable, stock debe ser entero (422).
        - RN-02: Nombre único entre activos excluyendo este ID (409).
        """
        producto = self.session.get(Producto, id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {id} no encontrado"
            )

        if not producto.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto '{producto.nombre}' está anulado y no admite modificaciones"
            )

        unidad = self._validate_unidad_venta(data.unidad_venta_id)
        self._validate_stock_contable(unidad, data.stock_cantidad)
        self._validate_nombre_unico(data.nombre, exclude_id=id)

        # Actualización de campos propios (PUT reemplaza los campos propios)
        producto.nombre = data.nombre.strip()
        producto.descripcion = data.descripcion
        producto.precio_base = data.precio_base
        producto.unidad_venta_id = data.unidad_venta_id
        producto.stock_cantidad = data.stock_cantidad
        producto.disponible = data.disponible

        self.session.add(producto)
        self.session.commit()
        self.session.refresh(producto)

        return self.to_public_dto(producto)

    def delete(self, id: int) -> None:
        """
        RN-04: Baja lógica de producto.
        - Cambia activo = False y registra timestamp en anulado_at.
        - Si no existe: 404.
        - Si ya está anulado: 409.
        """
        producto = self.session.get(Producto, id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {id} no encontrado"
            )

        if not producto.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto '{producto.nombre}' ya se encuentra anulado"
            )

        producto.activo = False
        producto.anulado_at = datetime.now(timezone.utc)

        self.session.add(producto)
        self.session.commit()

