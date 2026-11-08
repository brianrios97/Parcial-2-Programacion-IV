# Food Store — Backend API

Backend del sistema de gestión de catálogo de productos para **Food Store**, desarrollado con **FastAPI**, **SQLModel** y **Pydantic v2** para el **Parcial 2 de Programación IV (UTN TUPAD)**.

---

## 🛠️ Tecnologías y Arquitectura

- **Framework:** FastAPI 0.115+
- **ORM / Modelado:** SQLModel 0.0.22+ (basado en SQLAlchemy 2.0 y Pydantic v2)
- **Persistencia:** PostgreSQL 15+ (con fallback local transparente a SQLite)
- **Servidor ASGI:** Uvicorn
- **Arquitectura:** Modular por feature (`unidades_medida/`, `categorias/`, `productos/`, `productos_categorias/`) organizada en capas:
  - `model.py`: Definición relacional con `table=True` y `Relationship`.
  - `schema.py`: DTOs de entrada y salida con validaciones declarativas `Annotated + Field`.
  - `service.py`: Lógica pura del negocio y validación de reglas antes de persistir.
  - `router.py`: Endpoints HTTP con inyección de dependencias (`Depends(get_session)`).

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Requisitos Previos
- Python 3.12 o superior instalado.

### 2. Creación y Activación del Entorno Virtual

En Windows (PowerShell):
```powershell
cd foodstore-backend
python -m venv .venv
.\.venv\Scripts\activate
```

En Linux / macOS:
```bash
cd foodstore-backend
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Base de Datos (`DATABASE_URL`)

La conexión se administra en `app/core/database.py` leyendo la variable de entorno `DATABASE_URL`.

- **Opción A — SQLite local (por defecto, no requiere configuración):**
  Si no se define variable de entorno, el backend utiliza automáticamente:
  ```text
  sqlite:///./foodstore_p2.db
  ```

- **Opción B — PostgreSQL (exigido para entrega final):**
  Crear un archivo `.env` en `foodstore-backend/` (o configurar la variable en el sistema):
  ```env
  DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/foodstore_db
  FRONTEND_ORIGIN=http://localhost:5173
  ```

> **Nota sobre el arranque:** El ciclo de vida moderno de FastAPI (`@asynccontextmanager lifespan`) crea automáticamente todas las tablas relacionales y ejecuta el seed inicial idempotente de las 6 unidades de medida oficiales sin duplicar registros.

### 5. Ejecución del Servidor de Desarrollo

```bash
uvicorn app.main:app --reload --port 8000
```

- **Health Check:** `http://localhost:8000/`
- **Swagger UI interactivo:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🧪 Pruebas HTTP con REST Client

Los archivos de prueba se ubican en `tests/` y son ejecutables con la extensión **REST Client** de VS Code:

1. **`tests/productos.http`:**
   - Demuestra los 5 endpoints del CRUD de Productos.
   - Demuestra los filtros de paginación (`skip`, `limit`), estado (`activo`, `disponible`), texto (`search`) y categoría (`categoria_id`).
   - Demuestra los códigos de error HTTP: `404 Not Found`, `409 Conflict` y `422 Unprocessable Entity` (incluyendo stock negativo y stock con decimales sobre unidades contables).
   - Demuestra el campo calculado dinámico **`hay_stock`** antes y después de agotar existencias.

2. **`tests/relaciones.http`:**
   - Demuestra el alta de categorías y la validación de nombre único activo (409).
   - Demuestra la anulación de una categoría y la verificación de que sus productos asociados conservan su estado activo (RN-06).
   - Demuestra la clasificación N:N de productos en categorías con asignación de categoría principal (RN-09).
   - Demuestra el rechazo de clasificación duplicada (409, RN-07) y sobre recursos anulados (409, RN-08).

---

## 📋 Reglas de Negocio Implementadas

| Regla | Descripción | Código HTTP |
|---|---|---|
| **RN-01** | `nombre` mín. 3 caracteres, `precio_base >= 0`, `stock_cantidad >= 0`. Validados en schema con `Field`. | `422` |
| **RN-02** | Nombre único entre entidades activas (case-insensitive). Un recurso anulado libera su nombre. | `409` |
| **RN-03** | No se puede operar sobre IDs inexistentes ni referenciar FKs inválidas (`unidad_venta_id`, `categoria_id`). | `404` |
| **RN-04** | Baja lógica con `DELETE`: fija `activo = False` y registra `anulado_at`. No existe borrado físico. Re-anular da error. | `204` / `409` |
| **RN-05** | Un recurso anulado no admite modificaciones (`PUT`). | `409` |
| **RN-06** | Anular una categoría no anula los productos clasificados en ella. Estados independientes. | Verificable |
| **RN-07** | Un producto no puede clasificarse dos veces en la misma categoría (PK compuesta). | `409` |
| **RN-08** | Prohibido clasificar en una categoría anulada o clasificar un producto anulado. | `409` |
| **RN-09** | A lo sumo una categoría principal (`es_principal = True`) por producto. Una nueva desplaza a la anterior. | `201` |
| **RN-10** | Si la unidad de venta es contable (`u`, `doc`), `stock_cantidad` debe ser entero. | `422` |
| **RN-11** | `hay_stock` es un campo calculado (`stock_cantidad > 0`). No se persiste en la BD. | Calculado |
| **RN-12** | `disponible`, `activo` y `stock_cantidad` son completamente independientes entre sí. | Verificable |
| **RN-13** | Errores devueltos en formato consistente `{"detail": "..."}` mediante `HTTPException`. | `404/409/422` |

