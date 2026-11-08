import type { Producto } from '../types';
import { ProductCard } from './ProductCard';

interface ProductListProps {
  productos: Producto[];
  onEdit: (producto: Producto) => void;
  onToggleDisponibilidad: (producto: Producto) => void;
  onAnular: (id: number) => void;
}

/**
 * Componente ProductList: Recibe la lista de productos por props
 * y la renderiza mediante .map(), pasando cada producto al componente ProductCard.
 */
export const ProductList = ({
  productos,
  onEdit,
  onToggleDisponibilidad,
  onAnular,
}: ProductListProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {productos.map((producto) => (
        <ProductCard
          key={producto.id}
          producto={producto}
          onEdit={onEdit}
          onToggleDisponibilidad={onToggleDisponibilidad}
          onAnular={onAnular}
        />
      ))}
    </div>
  );
};
