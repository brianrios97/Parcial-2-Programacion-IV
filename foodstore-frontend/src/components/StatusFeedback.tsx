interface LoadingStateProps {
  message?: string;
}

export const LoadingState = ({ message = 'Cargando catálogo de productos...' }: LoadingStateProps) => {
  return (
    <div className="py-20 flex flex-col items-center justify-center space-y-4">
      <div className="w-10 h-10 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin" />
      <p className="text-slate-400 text-sm font-medium">{message}</p>
    </div>
  );
};

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export const ErrorState = ({ message, onRetry }: ErrorStateProps) => {
  return (
    <div className="my-8 p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-center max-w-lg mx-auto">
      <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 mx-auto flex items-center justify-center text-xl font-bold mb-3">
        !
      </div>
      <h3 className="text-base font-bold text-rose-300">Error al conectar con la API</h3>
      <p className="text-xs text-rose-200/80 mt-1 mb-4 leading-relaxed">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="px-4 py-2 bg-rose-500 hover:bg-rose-400 text-slate-950 font-semibold text-xs rounded-lg transition-colors cursor-pointer"
      >
        Reintentar conexión
      </button>
    </div>
  );
};

interface EmptyStateProps {
  onOpenCreate: () => void;
}

export const EmptyState = ({ onOpenCreate }: EmptyStateProps) => {
  return (
    <div className="py-20 text-center border-2 border-dashed border-slate-800 rounded-3xl p-8 max-w-xl mx-auto">
      <div className="w-16 h-16 rounded-2xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center mx-auto mb-4 text-3xl">
        📦
      </div>
      <h3 className="text-lg font-bold text-white">No hay productos registrados</h3>
      <p className="text-slate-400 text-xs mt-1 mb-6 max-w-md mx-auto leading-relaxed">
        El catálogo se encuentra vacío. Podés dar de alta tu primer producto haciendo clic en el botón de abajo.
      </p>
      <button
        type="button"
        onClick={onOpenCreate}
        className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm rounded-xl transition-colors cursor-pointer"
      >
        + Dar de alta el primer producto
      </button>
    </div>
  );
};

