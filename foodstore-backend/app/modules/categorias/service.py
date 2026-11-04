from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.modules.categorias.model import Categoria
from app.modules.categorias.schema import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    """
    Servicio de dominio para Categorías.
    Concentra la lógica de negocio, validaciones y acceso a la base de datos.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: CategoriaCreate) -> Categoria:
        """
        RN-02: El nombre debe ser único entre las categorías activas.
        Si ya existe una activa con el mismo nombre, responde 409 Conflict.
        """
        existente = self.session.exec(
            select(Categoria)
            .where(Categoria.activo == True)
            .where(func.lower(Categoria.nombre) == data.nombre.strip().lower())
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoría activa con el nombre '{data.nombre.strip()}'"
            )

        categoria = Categoria(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion.strip() if data.descripcion else None,
            activo=True,
            anulado_at=None
        )
        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria)
        return categoria

    def list(
        self,
        activo: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Categoria]:
        """
        Listado con filtros opcionales:
        - activo: True (solo activas), False (solo anuladas), None (por defecto solo activas).
        - search: búsqueda parcial por nombre (case-insensitive).
        """
        query = select(Categoria)

        # Filtro de activo: si no se especifica o es True, devuelve solo activas
        if activo is None or activo is True:
            query = query.where(Categoria.activo == True)
        else:
            query = query.where(Categoria.activo == False)

        if search and search.strip():
            query = query.where(
                func.lower(Categoria.nombre).contains(search.strip().lower())
            )

        return list(self.session.exec(query).all())

    def get_by_id(self, categoria_id: int) -> Categoria:
        """Obtiene una categoría por su ID. Si no existe, responde 404."""
        categoria = self.session.get(Categoria, categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {categoria_id} no encontrada"
            )
        return categoria

    def update(self, categoria_id: int, data: CategoriaUpdate) -> Categoria:
        """
        Actualiza nombre y descripción.
        Si está anulada responde 409. Si el nuevo nombre colisiona con otra activa, 409.
        """
        categoria = self.get_by_id(categoria_id)

        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede modificar una categoría anulada"
            )

        nombre_limpio = data.nombre.strip()
        # Verificar que otra categoría activa distinta no tenga ya ese nombre
        if nombre_limpio.lower() != categoria.nombre.lower():
            duplicada = self.session.exec(
                select(Categoria)
                .where(Categoria.activo == True)
                .where(Categoria.id != categoria_id)
                .where(func.lower(Categoria.nombre) == nombre_limpio.lower())
            ).first()
            if duplicada:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otra categoría activa con el nombre '{nombre_limpio}'"
                )

        categoria.nombre = nombre_limpio
        categoria.descripcion = data.descripcion.strip() if data.descripcion else None

        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria)
        return categoria

    def delete(self, categoria_id: int) -> None:
        """
        RN-06: Baja lógica. Fija activo = False y registra anulado_at.
        Si ya está anulada responde 409. No elimina físicamente la fila.
        """
        categoria = self.get_by_id(categoria_id)

        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La categoría '{categoria.nombre}' ya se encuentra anulada"
            )

        categoria.activo = False
        categoria.anulado_at = datetime.now(timezone.utc)

        self.session.add(categoria)
        self.session.commit()

