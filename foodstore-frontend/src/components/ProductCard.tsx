import type { Producto } from '../types';

interface ProductCardProps {
  producto: Producto;
  onEdit: (producto: Producto) => void;
  onToggleDisponibilidad: (producto: Producto) => void;
  onAnular: (id: number) => void;
}

/**
 * Componente ProductCard: Representa la tarjeta individual de un producto.
 * Muestra precio, stock formateado con símbolo de unidad, badges de estado y acciones.
 */
export const ProductCard = ({
  producto,
  onEdit,
  onToggleDisponibilidad,
  onAnular,
}: ProductCardProps) => {
  // Símbolo de la unidad de medida (ej. "kg", "u", "L")
  const simboloUnidad = producto.unidad_venta?.simbolo || '';

  // Formato de moneda en pesos argentinos (ARS)
  const precioFormateado = new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(producto.precio_base);

  // Formato del stock numérico
  const stockFormateado = new Intl.NumberFormat('es-AR', {
    maximumFractionDigits: 3,
  }).format(producto.stock_cantidad);

  return (
    <article className="bg-slate-900/80 rounded-2xl border border-slate-800 hover:border-slate-700 p-5 flex flex-col justify-between transition-all duration-200 shadow-sm hover:shadow-md">
      {/* 1. Encabezado de la Tarjeta: Categorías y Badges de Estado */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          {/* Categorías asignadas */}
          <div className="flex flex-wrap gap-1.5">
            {producto.categorias && producto.categorias.length > 0 ? (
              producto.categorias.map((cat) => (
                <span
                  key={cat.id}
                  className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${cat.es_principal
                      ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  title={cat.es_principal ? 'Categoría Principal' : 'Categoría Secundaria'}
                >
                  {cat.es_principal && '★ '}
                  {cat.nombre}
                </span>
              ))
            ) : (
              <span className="text-[11px] text-slate-500 italic">Sin categorizar</span>
            )}
          </div>

          {/* Badges de Disponibilidad y Stock (RN-11 / RN-12) */}
          <div className="flex items-center gap-1.5">
            {/* Indicador de Disponibilidad (Pausado manual) */}
            <span
              className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${producto.disponible
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
            >
              {producto.disponible ? 'Disponible' : 'Pausado'}
            </span>

            {/* Indicador de Stock Calculado (RN-11: hay_stock) */}
            <span
              className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${producto.hay_stock
                  ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}
            >
              {producto.hay_stock ? 'En stock' : 'Sin stock'}
            </span>
          </div>
        </div>

        {/* Nombre y Descripción */}
        <h2 className="text-lg font-bold text-white tracking-tight leading-snug">
          {producto.nombre}
        </h2>
        {producto.descripcion ? (
          <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
            {producto.descripcion}
          </p>
        ) : (
          <p className="text-xs text-slate-600 mt-1 italic">Sin descripción</p>
        )}
      </div>

      {/* 2. Cuerpo: Precio y Stock con Símbolo de Unidad */}
      <div className="mt-4 pt-4 border-t border-slate-800/80">
        <div className="flex items-baseline justify-between">
          {/* Precio Base por Unidad */}
          <div>
            <span className="text-xs text-slate-400 block font-medium">Precio</span>
            <div className="text-xl font-extrabold text-white">
              {precioFormateado}
              {simboloUnidad && (
                <span className="text-xs font-normal text-slate-400 ml-1">
                  / {simboloUnidad}
                </span>
              )}
            </div>
          </div>

          {/* Stock con Símbolo de Unidad */}
          <div className="text-right">
            <span className="text-xs text-slate-400 block font-medium">Stock</span>
            <div
              className={`text-sm font-bold ${producto.hay_stock ? 'text-slate-200' : 'text-rose-400'
                }`}
            >
              stock: {stockFormateado} {simboloUnidad}
            </div>
          </div>
        </div>

        {/* 3. Botones de Acción: Editar, Disponibilidad y Anular */}
        <div className="mt-4 grid grid-cols-3 gap-2">
          {/* Botón Editar */}
          <button
            type="button"
            onClick={() => onEdit(producto)}
            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer text-center"
          >
            Editar
          </button>

          {/* Botón Alternar Disponibilidad */}
          <button
            type="button"
            onClick={() => onToggleDisponibilidad(producto)}
            className={`px-2.5 py-1.5 text-xs font-medium rounded-lg border transition-colors cursor-pointer text-center ${producto.disponible
                ? 'bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20'
                : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20'
              }`}
            title={producto.disponible ? 'Pausar venta del producto' : 'Reanudar venta del producto'}
          >
            {producto.disponible ? 'Pausar' : 'Reanudar'}
          </button>

          {/* Botón Anular (Baja Lógica RN-04) */}
          <button
            type="button"
            onClick={() => onAnular(producto.id)}
            className="px-2.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/20 hover:border-rose-500/40 text-xs font-medium rounded-lg transition-colors cursor-pointer text-center"
            title="Dar de baja lógica al producto"
          >
            Anular
          </button>
        </div>
      </div>
    </article>
  );
};
