import { useState, useEffect } from 'react';
import type { Producto, UnidadMedida, ProductoFormData } from '../types';

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: ProductoFormData) => Promise<{ success: boolean; error?: string }>;
  unidades: UnidadMedida[];
  productoToEdit: Producto | null;
}

/**
 * Componente ProductModal: Formulario de Alta y Edición de Productos.
 * 
 * Reglas implementadas:
 * - El selector de unidad se carga desde las unidades provistas por la API.
 * - Si la API responde con error (409 nombre repetido o 422 stock inválido),
 *   el mensaje se muestra dentro del modal sin cerrarlo.
 * - Al guardar exitosamente o cancelar, el modal se cierra.
 */
export const ProductModal = ({
  isOpen,
  onClose,
  onSubmit,
  unidades,
  productoToEdit,
}: ProductModalProps) => {
  // Estado local del formulario
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [precioBase, setPrecioBase] = useState<number | ''>('');
  const [unidadVentaId, setUnidadVentaId] = useState<number | ''>('');
  const [stockCantidad, setStockCantidad] = useState<number | ''>(0);
  const [disponible, setDisponible] = useState(true);

  // Estados de control de envío y error interno
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Efecto: Cuando cambia el modal o el producto a editar, inicializamos los valores
  useEffect(() => {
    if (productoToEdit) {
      setNombre(productoToEdit.nombre);
      setDescripcion(productoToEdit.descripcion || '');
      setPrecioBase(productoToEdit.precio_base);
      setUnidadVentaId(productoToEdit.unidad_venta_id);
      setStockCantidad(productoToEdit.stock_cantidad);
      setDisponible(productoToEdit.disponible);
    } else {
      // Modo Creación: Valores por defecto
      setNombre('');
      setDescripcion('');
      setPrecioBase('');
      setStockCantidad(0);
      setDisponible(true);
      // Seleccionar por defecto la primera unidad disponible si existe
      if (unidades.length > 0) {
        setUnidadVentaId(unidades[0].id);
      } else {
        setUnidadVentaId('');
      }
    }
    // Limpiar mensaje de error previo
    setErrorMessage(null);
  }, [productoToEdit, isOpen, unidades]);

  if (!isOpen) return null;

  // Manejo del envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Validación básica en cliente
    if (!nombre.trim() || nombre.trim().length < 3) {
      setErrorMessage('El nombre debe tener al menos 3 caracteres.');
      return;
    }
    if (precioBase === '' || Number(precioBase) < 0) {
      setErrorMessage('El precio base debe ser mayor o igual a 0.');
      return;
    }
    if (unidadVentaId === '') {
      setErrorMessage('Debe seleccionar una unidad de venta.');
      return;
    }
    if (stockCantidad === '' || Number(stockCantidad) < 0) {
      setErrorMessage('El stock debe ser mayor o igual a 0.');
      return;
    }

    setIsSubmitting(true);

    const payload: ProductoFormData = {
      nombre: nombre.trim(),
      descripcion: descripcion.trim() || '',
      precio_base: Number(precioBase),
      unidad_venta_id: Number(unidadVentaId),
      stock_cantidad: Number(stockCantidad),
      disponible,
    };

    const result = await onSubmit(payload);
    setIsSubmitting(false);

    if (result.success) {
      onClose();
    } else if (result.error) {
      // Muestra el error de la API dentro del modal sin cerrarlo (ej. 409 o 422)
      setErrorMessage(result.error);
    }
  };

  // Encontrar la unidad seleccionada para dar feedback sobre si es contable
  const unidadSeleccionada = unidades.find((u) => u.id === Number(unidadVentaId));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Cabecera del Modal */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">
            {productoToEdit ? 'Editar Producto' : 'Nuevo Producto'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Mensaje de Error dentro del Modal (409 / 422) */}
          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2">
              <span className="font-bold text-sm">⚠</span>
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Campo: Nombre */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Nombre <span className="text-amber-400">*</span>
            </label>
            <input
              type="text"
              required
              minLength={3}
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej: Medialuna de manteca"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
            />
          </div>

          {/* Campo: Descripción */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Descripción
            </label>
            <textarea
              rows={2}
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              placeholder="Detalles sobre el producto..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
            />
          </div>

          {/* Fila: Precio Base y Unidad de Venta */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Precio Base ($) <span className="text-amber-400">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                required
                value={precioBase}
                onChange={(e) => setPrecioBase(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="0.00"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Unidad de Venta <span className="text-amber-400">*</span>
              </label>
              <select
                required
                value={unidadVentaId}
                onChange={(e) => setUnidadVentaId(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 cursor-pointer"
              >
                {unidades.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.nombre} ({u.simbolo}) — {u.tipo}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Fila: Stock y Disponibilidad */}
          <div className="grid grid-cols-2 gap-4 items-center">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Stock Cantidad <span className="text-amber-400">*</span>
              </label>
              <input
                type="number"
                step={unidadSeleccionada?.tipo === 'contable' ? '1' : '0.001'}
                min="0"
                required
                value={stockCantidad}
                onChange={(e) => setStockCantidad(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="0"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
              />
              {unidadSeleccionada?.tipo === 'contable' && (
                <span className="text-[11px] text-amber-400/80 mt-1 block">
                  Unidad contable: solo números enteros (RN-10)
                </span>
              )}
            </div>

            <div className="pt-5">
              <label className="inline-flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={disponible}
                  onChange={(e) => setDisponible(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-950 border-slate-700 text-amber-500 focus:ring-amber-500/40 cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-200">
                  Disponible para la venta
                </span>
              </label>
            </div>
          </div>

          {/* Botones de Acción */}
          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-lg transition-colors cursor-pointer"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 active:bg-amber-600 disabled:opacity-50 text-slate-950 text-sm font-bold rounded-lg shadow transition-colors cursor-pointer"
            >
              {isSubmitting ? 'Guardando...' : productoToEdit ? 'Actualizar' : 'Crear Producto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
