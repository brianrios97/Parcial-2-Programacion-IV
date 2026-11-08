interface NavbarProps {
  onOpenCreateModal: () => void;
  totalProductos: number;
}

/**
 * Componente Navbar: Barra superior de navegación de Food Store.
 * Cumple con el requerimiento de props tipadas mediante interfaces.
 */
export const Navbar = ({ onOpenCreateModal, totalProductos }: NavbarProps) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logotipo y Título del Sistema */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500 flex items-center justify-center font-black text-slate-950 text-xl shadow-inner">
            FS
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-white tracking-tight">
                Food Store
              </h1>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Catálogo
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Gestión de productos, stock y relaciones
            </p>
          </div>
        </div>

        {/* Acciones principales: Contador y Botón Nuevo Producto */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center px-3 py-1 rounded-lg bg-slate-800 border border-slate-700/60 text-xs text-slate-300">
            <span className="text-slate-400 mr-1.5">Activos:</span>
            <span className="font-bold text-amber-400">{totalProductos}</span>
          </div>

          <button
            type="button"
            onClick={onOpenCreateModal}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 active:bg-amber-600 text-slate-950 font-semibold text-sm rounded-lg shadow-sm hover:shadow transition-colors duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500/50"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M12 4v16m8-8H4"
              />
            </svg>
            <span>Nuevo Producto</span>
          </button>
        </div>
      </div>
    </header>
  );
};

