import { useState, useEffect, useCallback } from 'react';
import type { Producto, UnidadMedida, ProductoFormData } from './types';
import { Navbar } from './components/Navbar';
import { ProductList } from './components/ProductList';
import { ProductModal } from './components/ProductModal';
import { LoadingState, ErrorState, EmptyState } from './components/StatusFeedback';

// URL base de la API REST de FastAPI
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

/**
 * Componente Principal App:
 * Centraliza todo el estado de la aplicación mediante useState y useEffect
 * y consume la API usando la función nativa fetch (sin librerías externas).
 */
export function App() {
  // 1. Estados obligatorios exigidos por la consigna
  const [productos, setProductos] = useState<Producto[]>([]);
  const [unidades, setUnidades] = useState<UnidadMedida[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtro de búsqueda local en cliente
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDisponible, setFilterDisponible] = useState<'all' | 'true' | 'false'>('all');

  // 2. Carga inicial del catálogo y unidades de medida (useEffect al montar)
  const cargarDatos = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Peticiones paralelas nativas con fetch
      const [resProductos, resUnidades] = await Promise.all([
        fetch(`${API_BASE_URL}/productos?limit=50`),
        fetch(`${API_BASE_URL}/unidades-medida`),
      ]);

      if (!resProductos.ok) {
        throw new Error(`Error al cargar productos (HTTP ${resProductos.status})`);
      }
      if (!resUnidades.ok) {
        throw new Error(`Error al cargar unidades de medida (HTTP ${resUnidades.status})`);
      }

      const dataProductos: Producto[] = await resProductos.json();
      const dataUnidades: UnidadMedida[] = await resUnidades.json();

      setProductos(dataProductos);
      setUnidades(dataUnidades);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error desconocido al conectar con el servidor';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  // 3. Abrir modal para creación
  const handleOpenCreateModal = () => {
    setProductoSeleccionado(null);
    setIsModalOpen(true);
  };

  // 4. Abrir modal para edición
  const handleOpenEditModal = (producto: Producto) => {
    setProductoSeleccionado(producto);
    setIsModalOpen(true);
  };

  // 5. Cerrar modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setProductoSeleccionado(null);
  };

  // 6. Enviar formulario (Crear o Actualizar)
  const handleFormSubmit = async (
    formData: ProductoFormData
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const isEditing = Boolean(productoSeleccionado);
      const url = isEditing
        ? `${API_BASE_URL}/productos/${productoSeleccionado!.id}`
        : `${API_BASE_URL}/productos`;
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        // Intentar parsear el error {"detail": "..."} del backend
        let errorDetail = 'Ocurrió un error al procesar la solicitud';
        try {
          const errJson = await response.json();
          if (errJson && errJson.detail) {
            errorDetail = typeof errJson.detail === 'string'
              ? errJson.detail
              : JSON.stringify(errJson.detail);
          }
        } catch {
          errorDetail = `Error del servidor (HTTP ${response.status})`;
        }
        return { success: false, error: errorDetail };
      }

      const productoGuardado: Producto = await response.json();

      if (isEditing) {
        // Actualizar en el estado local sin recargar la página
        setProductos((prev) =>
          prev.map((p) => (p.id === productoGuardado.id ? productoGuardado : p))
        );
      } else {
        // Agregar al inicio de la lista
        setProductos((prev) => [productoGuardado, ...prev]);
      }

      return { success: true };
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error de conexión al guardar';
      return { success: false, error: msg };
    }
  };

  // 7. Alternar disponibilidad (PUT sobre disponible sin modificar stock ni activo, RN-12)
  const handleToggleDisponibilidad = async (producto: Producto) => {
    const nuevaDisponibilidad = !producto.disponible;

    try {
      const response = await fetch(`${API_BASE_URL}/productos/${producto.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          nombre: producto.nombre,
          descripcion: producto.descripcion || '',
          precio_base: producto.precio_base,
          unidad_venta_id: producto.unidad_venta_id,
          stock_cantidad: producto.stock_cantidad,
          disponible: nuevaDisponibilidad,
        }),
      });

      if (!response.ok) {
        const errJson = await response.json();
        alert(`No se pudo cambiar la disponibilidad: ${errJson.detail || response.statusText}`);
        return;
      }

      const actualizado: Producto = await response.json();

      // Reflejar cambio en la fila correspondiente sin recargar página
      setProductos((prev) =>
        prev.map((p) => (p.id === actualizado.id ? actualizado : p))
      );
    } catch {
      alert('Error de red al actualizar disponibilidad');
    }
  };

  // 8. Anular producto (DELETE baja lógica RN-04: lo quita del listado de activos)
  const handleAnular = async (id: number) => {
    const confirmar = window.confirm(
      '¿Estás seguro de que deseas anular este producto del catálogo? (Baja lógica, conservará su historial)'
    );
    if (!confirmar) return;

    try {
      const response = await fetch(`${API_BASE_URL}/productos/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok && response.status !== 204) {
        const errJson = await response.json();
        alert(`No se pudo anular: ${errJson.detail || response.statusText}`);
        return;
      }

      // Quitar del listado local de activos
      setProductos((prev) => prev.filter((p) => p.id !== id));
    } catch {
      alert('Error de conexión al anular el producto');
    }
  };

  // 9. Filtrado de productos para la vista
  const productosFiltrados = productos.filter((p) => {
    const matchSearch =
      p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      Boolean(p.descripcion && p.descripcion.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchSearch) return false;

    if (filterDisponible === 'true') return p.disponible;
    if (filterDisponible === 'false') return !p.disponible;
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-amber-500 selection:text-slate-950">
      {/* 1. Barra de Navegación */}
      <Navbar
        onOpenCreateModal={handleOpenCreateModal}
        totalProductos={productos.length}
      />

      {/* 2. Contenedor Principal */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Barra de Filtros y Búsqueda */}
        {!isLoading && !error && productos.length > 0 && (
          <section className="mb-6 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
            {/* Buscador */}
            <div className="relative flex-1">
              <span className="absolute inset-y-0 left-3 flex items-center text-slate-500 text-sm">
                🔍
              </span>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nombre o descripción..."
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
              />
            </div>

            {/* Selector de Disponibilidad */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-medium">Estado:</span>
              <select
                value={filterDisponible}
                onChange={(e) => setFilterDisponible(e.target.value as 'all' | 'true' | 'false')}
                className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500 cursor-pointer"
              >
                <option value="all">Todos los estados</option>
                <option value="true">Solo disponibles</option>
                <option value="false">Solo pausados</option>
              </select>
            </div>
          </section>
        )}

        {/* 3. Renderizado Condicional de Estados de la UI */}
        {isLoading && <LoadingState />}

        {!isLoading && error && (
          <ErrorState message={error} onRetry={cargarDatos} />
        )}

        {!isLoading && !error && productos.length === 0 && (
          <EmptyState onOpenCreate={handleOpenCreateModal} />
        )}

        {!isLoading && !error && productos.length > 0 && productosFiltrados.length === 0 && (
          <div className="py-16 text-center text-slate-400 text-sm">
            No se encontraron productos que coincidan con la búsqueda.
          </div>
        )}

        {!isLoading && !error && productosFiltrados.length > 0 && (
          <ProductList
            productos={productosFiltrados}
            onEdit={handleOpenEditModal}
            onToggleDisponibilidad={handleToggleDisponibilidad}
            onAnular={handleAnular}
          />
        )}
      </main>

      {/* 4. Modal de Alta y Edición */}
      <ProductModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleFormSubmit}
        unidades={unidades}
        productoToEdit={productoSeleccionado}
      />

      {/* 5. Pie de página informativo */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        Parcial 2 — Programación IV (UTN TUPAD) · Food Store Catálogo
      </footer>
    </div>
  );
}

export default App;
