from sqlmodel import Session, select
from app.modules.unidades_medida.model import UnidadMedida, TipoUnidadMedida

# Diccionarios de configuración para no disparar la inicialización de mappers de SQLAlchemy durante el import
UNIDADES_INICIALES = [
    # Tipo Peso
    {"nombre": "kilogramo", "simbolo": "kg", "tipo": TipoUnidadMedida.peso},
    {"nombre": "gramo", "simbolo": "g", "tipo": TipoUnidadMedida.peso},
    # Tipo Volumen
    {"nombre": "litro", "simbolo": "L", "tipo": TipoUnidadMedida.volumen},
    {"nombre": "mililitro", "simbolo": "mL", "tipo": TipoUnidadMedida.volumen},
    # Tipo Contable
    {"nombre": "pieza", "simbolo": "u", "tipo": TipoUnidadMedida.contable},
    {"nombre": "docena", "simbolo": "doc", "tipo": TipoUnidadMedida.contable},
]


def seed_unidades_medida(session: Session) -> None:
    """
    Carga inicial idempotente de Unidades de Medida.
    Solo inserta si la tabla está vacía: no duplica registros al reiniciar la aplicación.
    """
    existentes = session.exec(select(UnidadMedida)).first()
    if existentes is None:
        for data in UNIDADES_INICIALES:
            session.add(UnidadMedida(**data))
        session.commit()
