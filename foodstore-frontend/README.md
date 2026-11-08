# Food Store — Frontend Web

Aplicación de administración del catálogo de productos para **Food Store**, construida con **React**, **TypeScript** y **Tailwind CSS 4** sobre **Vite** para el **Parcial 2 de Programación IV (UTN TUPAD)**.

---

## 🛠️ Tecnologías y Decisiones de Diseño

- **Framework / Runtime:** React 19 + TypeScript (compilación estricta con `"strict": true` y `"noImplicitAny": true`, sin uso de `any`).
- **Empaquetador:** Vite (arranque instantáneo y HMR).
- **Estilos:** Tailwind CSS 4 con enfoque *utility-first* (`@tailwindcss/vite`).
- **Consumo HTTP:** `fetch` nativo del navegador (cumpliendo con la prohibición explícita de librerías externas como Axios, TanStack Query o Zustand).
- **Manejo de Estado:** `useState` y `useEffect` centralizados en `App.tsx`.
- **Arquitectura de Componentes:** Componentes funcionales en `src/components/` con props tipadas mediante interfaces:
  - `Navbar.tsx`: Barra superior con branding, contador de activos y disparador del modal de alta.
  - `ProductList.tsx`: Contenedor en cuadrícula (*responsive grid*) que itera la lista con `.map()`.
  - `ProductCard.tsx`: Tarjeta de producto con precio y stock acompañados del símbolo de la unidad, badges de disponibilidad y existencias (`hay_stock`), y acciones (Editar, Pausar/Reanudar, Anular).
  - `ProductModal.tsx`: Modal para creación y edición con selector dinámico de unidades de medida y manejo de errores (409/422) dentro del modal sin cerrarlo.
  - `StatusFeedback.tsx`: Componentes para estados de carga (*LoadingSpinner*), error (*ErrorState* con reintento) y catálogo vacío (*EmptyState*).

---

## ⚙️ Instalación y Ejecución

### 1. Requisitos Previos
- Node.js v18 o superior (v22 recomendado).
- Backend de Food Store ejecutándose en `http://127.0.0.1:8000`.

### 2. Instalación de Dependencias
```bash
cd foodstore-frontend
npm install
```

### 3. Variables de Entorno (Opcional)
Por defecto, la aplicación se comunica con `http://127.0.0.1:8000/api/v1`.  
Si se requiere cambiar el endpoint, se puede crear un archivo `.env` en la raíz de `foodstore-frontend/`:
```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

### 4. Ejecución en Modo Desarrollo
```bash
npm run dev
```

La aplicación estará disponible en: **`http://localhost:5173`**

### 5. Compilación para Producción (Verificación TypeScript)
```bash
npm run build
```
Ejecuta `tsc -b` y genera los artefactos optimizados en `dist/` asegurando que no existan errores de tipos.

---

## 📋 Funcionalidades Implementadas en la Interfaz

1. **Gestión de Productos (CRUD Completo):**
   - **Alta:** Apertura de modal con formulario limpio y unidades de venta provistas dinámicamente por la API.
   - **Edición:** Apertura de modal con datos precargados del producto seleccionado.
   - **Baja Lógica:** Confirmación y eliminación del listado activo mediante `DELETE`.
   - **Cambio de Disponibilidad:** Alterna el estado `disponible` con un solo clic sin recargar la página.
2. **Formateo Específico del Negocio:**
   - Precios en formato moneda argentina (`$ 1.500,00 / kg`).
   - Stock expresado en la unidad de venta (`stock: 12,5 kg` o `stock: 24 u`).
   - Badges visuales para `Disponible / Pausado` y `En stock / Sin stock` (RN-11).
   - Visualización de categorías asignadas con distinción dorada (`★`) para la categoría principal (RN-09).
3. **Manejo Amigable de Errores (409 / 422):**
   - Si la API rechaza la petición por nombre duplicado (RN-02) o stock decimal en unidad contable (RN-10), el mensaje de error se muestra en una alerta dentro del modal sin cerrarlo, permitiendo al usuario corregir el dato inmediatamente.
4. **Búsqueda y Filtros:**
   - Buscador en tiempo real por nombre o descripción.
   - Selector de filtrado por estado de disponibilidad (Todos, Disponibles, Pausados).
