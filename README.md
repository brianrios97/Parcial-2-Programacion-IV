# Food Store — Catálogo de Productos (Parcial 2)
### Programación IV — Tecnicatura Universitaria en Programación a Distancia (UTN)

Sistema de administración de catálogo de productos para negocio de comidas con:
- **Backend:** FastAPI + SQLModel + Pydantic sobre PostgreSQL / SQLite. Arquitectura modular por dominio.
- **Frontend:** React + TypeScript + Tailwind CSS 4 sobre Vite con consumo nativo (`fetch`) y estado centralizado.

---

## 🏗️ Estructura del Proyecto

```text
foodstore-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── seed.py
│   └── modules/
│       ├── unidades_medida/    # __init__ · model · router
│       ├── categorias/         # __init__ · router · model · schema · service
│       └── productos/          # ídem · más ProductoCategoria
├── tests/                      # productos.http · relaciones.http
├── requirements.txt
└── README.md

foodstore-frontend/
├── src/
│   ├── components/
│   ├── types/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
└── tsconfig.json
```

---

## 🎯 Requerimientos y Puntos de Evaluación
- **Requerimiento 1 (15 pts):** Backend: estructura, persistencia y modelo de datos.
- **Requerimiento 2 (30 pts):** Módulo Productos: CRUD, stock, validaciones y consultas.
- **Requerimiento 3 (25 pts):** Relaciones 1:N y N:N con modelo intermedio `ProductoCategoria`.
- **Requerimiento 4 (30 pts):** Frontend React + TypeScript + Tailwind CSS 4.
