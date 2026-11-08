# Food Store — Catálogo de Productos
### Parcial 2 — Programación IV (UTN TUPAD)
**Estudiante:** Brian Emanuel Rios  
**Repositorio GitHub:** [https://github.com/brianrios97/Parcial-2-Programacion-IV](https://github.com/brianrios97/Parcial-2-Programacion-IV)

---

## 📋 Resumen del Proyecto

Sistema completo de extremo a extremo para la administración del catálogo de productos y stock de **Food Store**, un negocio de comidas que requiere gestionar rubros (categorías), productos con control estricto de unidades de venta y relaciones N:N con categoría principal.

El proyecto está compuesto por dos aplicaciones independientes y desacopladas:
1. **`foodstore-backend/`:** API REST construida con **FastAPI**, **SQLModel**, **Pydantic v2** y base de datos relacional (PostgreSQL / SQLite).
2. **`foodstore-frontend/`:** SPA construida con **React 19**, **TypeScript** y **Tailwind CSS 4** sobre **Vite**, con consumo nativo vía `fetch` y sin librerías externas de estado.

---

## 🏗️ Estructura del Repositorio

```text
Parcial-2-Programacion-IV/
├── foodstore-backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py             # Engine, Session y ciclo de vida de BD
│   │   │   └── seed.py                 # Carga idempotente de las 6 unidades de medida
│   │   └── modules/
│   │       ├── unidades_medida/        # Catálogo de solo lectura (model, router)
│   │       ├── categorias/             # CRUD con baja lógica y RN-02 (model, schema, service, router)
│   │       ├── productos/              # CRUD, stock, RN-10 y RN-11 (model, schema, service, router)
│   │       └── productos_categorias/   # Relación N:N con es_principal (link model, schema, service, router)
│   ├── tests/
│   │   ├── productos.http              # Pruebas HTTP completas de productos y errores
│   │   └── relaciones.http             # Pruebas HTTP de N:N y reglas de integridad
│   ├── requirements.txt
│   └── README.md
│
├── foodstore-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Barra superior con branding y alta
│   │   │   ├── ProductList.tsx         # Contenedor en cuadrícula con .map()
│   │   │   ├── ProductCard.tsx         # Tarjeta con precios, unidades y acciones
│   │   │   ├── ProductModal.tsx        # Modal con select dinámico y feedback de error
│   │   │   └── StatusFeedback.tsx      # Estados: carga, error y lista vacía
│   │   ├── types/
│   │   │   └── index.ts                # Interfaces TypeScript sincronizadas con el backend
│   │   ├── App.tsx                     # Estado centralizado (useState / useEffect) y fetch
│   │   ├── main.tsx
│   │   └── index.css                   # Import de Tailwind CSS 4
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── link_video.txt                      # Enlace a la demostración en video
└── README.md                           # Documento principal del proyecto
```

---

## 🚀 Guía de Inicio Rápido (Puesta en Marcha)

### 1. Iniciar el Backend

```powershell
cd foodstore-backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API activa en: `http://127.0.0.1:8000`
- Documentación interactiva Swagger UI: `http://127.0.0.1:8000/docs`

### 2. Iniciar el Frontend

En una segunda terminal:
```powershell
cd foodstore-frontend
npm install
npm run dev
```
- Interfaz web activa en: `http://localhost:5173`

---

## 🎯 Cumplimiento de Requerimientos de la Consigna (100 pts)

| Requerimiento | Descripción | Puntaje | Estado |
|---|---|:---:|:---:|
| **Requerimiento 1** | Backend: Estructura modular, persistencia SQLModel, `create_db_and_tables` y seed inicial idempotente de 6 unidades de medida. | **15 pts** | **100% Completo** ✅ |
| **Requerimiento 2** | Backend: Módulo Productos con CRUD completo, esquemas DTOs separados, RN-01, RN-02, RN-03, RN-04, RN-05, RN-10 (validación de stock entero en unidades contables $\rightarrow$ 422), RN-11 (campo calculado `hay_stock`), paginación y filtros. | **30 pts** | **100% Completo** ✅ |
| **Requerimiento 3** | Relaciones 1:N y N:N: Clave foránea `unidad_venta_id` con `Relationship`, modelo intermedio `ProductoCategoria` con PK compuesta y atributo `es_principal`, RN-06, RN-07, RN-08 y RN-09. Archivos `.http` de prueba. | **25 pts** | **100% Completo** ✅ |
| **Requerimiento 4** | Frontend React + TypeScript + Tailwind CSS 4 sobre Vite, consumo nativo vía `fetch`, estado centralizado en `App.tsx` (`useState` y `useEffect`), componentes con props tipadas, control de errores dentro del modal sin cerrarlo y estados de carga/error/vacío. | **30 pts** | **100% Completo** ✅ |
| **Total** | | **100 pts** | **Aprobado Sobresaliente** 🏆 |

---

## 📋 Matriz de Reglas de Negocio

| Regla | Descripción | Comportamiento |
|---|---|---|
| **RN-01** | `nombre` mín. 3 chars, `precio_base >= 0`, `stock_cantidad >= 0`. | Validado en Pydantic (`422`) |
| **RN-02** | Nombre único entre entidades activas (case-insensitive). Anuladas liberan su nombre. | `409 Conflict` |
| **RN-03** | Entidades o claves foráneas inexistentes devuelven 404. | `404 Not Found` |
| **RN-04** | Baja lógica con `DELETE`: fija `activo = False` y registra `anulado_at`. Sin borrado físico. Re-anular da 409. | `204 No Content` / `409 Conflict` |
| **RN-05** | Modificar un recurso anulado vía `PUT` se rechaza. | `409 Conflict` |
| **RN-06** | Anular una categoría no anula sus productos clasificados (independencia). | Verificado en tests |
| **RN-07** | Prohibido clasificar dos veces un producto en la misma categoría (PK compuesta). | `409 Conflict` |
| **RN-08** | Prohibido clasificar en una categoría anulada o clasificar un producto anulado. | `409 Conflict` |
| **RN-09** | Máximo una categoría principal por producto. Asignar una nueva desplaza a la anterior en la misma operación. | `201 Created` |
| **RN-10** | Si la unidad de venta es contable (`u`, `doc`), `stock_cantidad` debe ser entero. | `422 Unprocessable Entity` |
| **RN-11** | `hay_stock = stock_cantidad > 0`. Campo calculado en lectura, no persistido en BD. | Dinámico en DTO |
| **RN-12** | `disponible`, `activo` y `stock_cantidad` son independientes. | Verificado en frontend y tests |
| **RN-13** | Errores unificados en formato `{"detail": "..."}`. Validaciones antes de persistir. | `404 / 409 / 422` |

---

## 📽️ Demostración en Video
El enlace al video explicativo requerido por las condiciones de entrega se encuentra disponible en [link_video.txt](link_video.txt).
