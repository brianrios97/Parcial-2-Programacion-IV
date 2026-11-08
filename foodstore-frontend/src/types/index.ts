/**
 * Tipos de datos oficiales del Catálogo Food Store (Parcial 2 - Programación IV).
 * Reflejan de forma exacta el contrato de la API REST de FastAPI.
 */

// 1. Tipo de Unidad de Medida (Enum coincidente con el backend)
export type TipoUnidadMedida = 'peso' | 'volumen' | 'contable';

// 2. Entidad UnidadMedida (Catálogo de solo lectura)
export interface UnidadMedida {
  id: number;
  nombre: string;
  simbolo: string;
  tipo: TipoUnidadMedida;
}

// 3. Entidad Categoria (Rubros del catálogo)
export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string | null;
  activo?: boolean;
  anulado_at?: string | null;
}

// 4. Categoría asociada a un producto (vínculo N:N con es_principal)
export interface CategoriaAsociada {
  id: number;
  nombre: string;
  es_principal: boolean;
}

// 5. Entidad Producto (Representa ProductoPublic devuelto por la API)
export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  unidad_venta_id: number;
  stock_cantidad: number;
  disponible: boolean;
  activo: boolean;
  anulado_at?: string | null;
  // Campo calculado en el backend (RN-11: stock_cantidad > 0)
  hay_stock: boolean;
  // Unidad de venta anidada devuelta por la API
  unidad_venta?: UnidadMedida | null;
  // Categorías asociadas al producto
  categorias?: CategoriaAsociada[];
}

// 6. DTO para los formularios de Alta y Edición de Producto (POST / PUT)
export interface ProductoFormData {
  nombre: string;
  descripcion: string;
  precio_base: number;
  unidad_venta_id: number;
  stock_cantidad: number;
  disponible: boolean;
}

