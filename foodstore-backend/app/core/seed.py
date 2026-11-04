from sqlmodel import Session, select
from app.modules.unidades_medida.model import UnidadMedida, TipoUnidadMedida

# Las seis unidades oficiales exigidas por el Requerimiento 1
UNIDADES_INICIALES = [
    # Tipo Peso
    UnidadMedida(nombre="kilogramo", simbolo="kg", tipo=TipoUnidadMedida.peso),
    UnidadMedida(nombre="gramo", simbolo="g", tipo=TipoUnidadMedida.peso),
    # Tipo Volumen
    UnidadMedida(nombre="litro", simbolo="L", tipo=TipoUnidadMedida.volumen),
    UnidadMedida(nombre="mililitro", simbolo="mL", tipo=TipoUnidadMedida.volumen),
    # Tipo Contable
    UnidadMedida(nombre="pieza", simbolo="u", tipo=TipoUnidadMedida.contable),
    UnidadMedida(nombre="docena", simbolo="doc", tipo=TipoUnidadMedida.contable),
]


def seed_unidades_medida(session: Session) -> None:
    """
    Carga inicial idempotente de Unidades de Medida.
    Solo inserta si la tabla está vacía: no duplica registros al reiniciar la aplicación.
    """
    existentes = session.exec(select(UnidadMedida)).first()
    if existentes is None:
        for unidad in UNIDADES_INICIALES:
            session.add(unidad)
        session.commit()

