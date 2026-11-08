# 🎓 Guía Completa de Preparación: Cuestionario Moodle y Defensa Oral
### Parcial 2 — Programación IV (UTN TUPAD) · Food Store
**Estudiante:** Brian Emanuel Rios

---

## 🎯 Estructura de la Evaluación
1. **Fase 2 — Cuestionario en Plataforma Moodle:** 10 preguntas teóricas y prácticas enfocadas exclusivamente en el código entregado.
2. **Fase 3 — Defensa Oral por Zoom:** 2 preguntas directas (una de Backend y una de Frontend) tomadas del banco oficial de preguntas.

---

# 🧠 BANCO DE PREGUNTAS Y RESPUESTAS MODELO (Para sacar un 10)

---

## 🟦 BLOQUE A: BACKEND (FastAPI, SQLModel, Pydantic, Arquitectura y Reglas)

### 1. ¿Por qué usamos `SQLModel` en lugar de SQLAlchemy puro o Peewee?
> **Respuesta de 10:**  
> SQLModel está diseñado por el creador de FastAPI (Sebastián Ramírez) y unifica la potencia de **SQLAlchemy 2.0** con la validación de tipos de **Pydantic v2**.  
> Esto elimina la duplicación de código (*DRY*): una misma clase con `table=True` define la tabla relacional para la base de datos y al mismo tiempo hereda las capacidades de tipado, serialización y validación automática de Pydantic, integrándose directamente con la documentación automática de OpenAPI (Swagger).

---

### 2. ¿Por qué separamos los Schemas DTOs (`ProductoCreate`, `ProductoUpdate`, `ProductoPublic`) del modelo de tabla `Producto`?
> **Respuesta de 10:**  
> Para respetar el patrón de diseño **DTO (Data Transfer Object)** y desacoplar la capa de persistencia de la capa de presentación:
> - **Entrada (`ProductoCreate` / `ProductoUpdate`):** Valida los datos que el cliente envía (`Annotated + Field` con `min_length=3`, `ge=0`), sin permitir que el usuario envíe campos internos como `id`, `activo` o `anulado_at`.
> - **Salida (`ProductoPublic`):** Devuelve únicamente los campos públicos e incorpora atributos calculados que no existen en la tabla física, como **`hay_stock`** (RN-11) y la unidad de medida anidada (`UnidadMedidaSimple`).  
> Si expusiéramos el modelo de tabla directamente, violaríamos el encapsulamiento y arriesgaríamos la integridad de la base de datos.

---

### 3. ¿Por qué el campo `hay_stock` (RN-11) NO se persiste en la tabla `productos`?
> **Respuesta de 10:**  
> Porque es un **dato derivado (calculado)**: `hay_stock = stock_cantidad > 0`.  
> Si lo persistiéramos como una columna booleana en la tabla, violaríamos las formas normales de bases de datos relacionales y crearíamos un grave riesgo de **inconsistencia**: si en el futuro se actualiza el stock a 0 pero alguien olvida actualizar el booleano `hay_stock` a false, la base de datos quedaría en un estado contradictorio. Al calcularse dinámicamente en el servicio al momento de la lectura (`to_public_dto`), garantizamos consistencia absoluta.

---

### 4. ¿Cómo y dónde se implementa la regla RN-10 (validación de stock entero en unidades contables)?
> **Respuesta de 10:**  
> Se implementa en la **capa de Servicio** (`ProductoService._validate_stock_contable`), **antes de persistir**.  
> **¿Por qué en el servicio y no en el schema de Pydantic?** Porque Pydantic solo conoce los datos que llegan en el cuerpo JSON (`stock_cantidad` y el ID `unidad_venta_id`), pero no tiene acceso a la base de datos para saber si esa unidad es de tipo `peso`, `volumen` o `contable`.  
> El servicio consulta la `UnidadMedida` en la base de datos y, si su tipo es `contable` y `stock_cantidad % 1 != 0` (o `not float(stock).is_integer()`), lanza una `HTTPException(status_code=422, detail="...")`. Se valida tanto en `POST` como en `PUT`.

---

### 5. ¿Por qué usamos Baja Lógica (Soft Delete) y cómo se implementa (RN-04 / RN-06)?
> **Respuesta de 10:**  
> En sistemas de comercio como *Food Store*, los datos históricos nunca deben borrarse físicamente (*Hard Delete*), porque romperíamos la integridad referencial de pedidos pasados, auditorías y estadísticas.  
> Se implementa en el endpoint `DELETE` mediante dos campos:
> 1. `activo: bool = False` (para excluirlo de las consultas activas por defecto).
> 2. `anulado_at: datetime = datetime.now(timezone.utc)` (para registrar la marca temporal exacta de cuándo se dio de baja).  
> Además, se valida que si un recurso ya está anulado y se intenta anular nuevamente o modificar vía `PUT`, se rechaza con **`409 Conflict`** (RN-04 y RN-05).

---

### 6. ¿Cómo se resuelve la relación N:N entre `Producto` y `Categoria` y por qué usamos una clave primaria compuesta en `ProductoCategoria`?
> **Respuesta de 10:**  
> Se resuelve mediante un **modelo intermedio (link model)** llamado `ProductoCategoria` con los campos `producto_id`, `categoria_id` y el atributo propio `es_principal: bool`.  
> Definir la clave primaria compuesta `(producto_id, categoria_id)` tiene dos grandes ventajas:
> 1. **Garantiza la RN-07 a nivel del motor relacional:** es imposible que un producto se vincule dos veces a la misma categoría, sin necesidad de agregar índices únicos adicionales.
> 2. Permite modelar el atributo `es_principal` que pertenece al vínculo y no a ninguna de las dos tablas por separado.

---

### 7. ¿Cómo se garantiza la regla RN-09 (a lo sumo una categoría principal por producto)?
> **Respuesta de 10:**  
> En `ProductoCategoriaService.clasificar`, cuando se clasifica un producto con `es_principal = True`:  
> Primero se busca en la base de datos si ya existe algún vínculo previo de ese producto con `es_principal == True`. Si existe, se le cambia el valor a `False` dentro de la misma transacción. Luego se inserta el nuevo vínculo con `es_principal = True` y se hace `session.commit()`.  
> Esto garantiza atomicidad: la categoría anterior deja de ser principal y la nueva pasa a serlo en una única operación.

---

### 8. ¿Para qué sirve el ciclo de vida `lifespan` en `app/main.py`?
> **Respuesta de 10:**  
> Es el estándar moderno de FastAPI (reemplaza a los viejos eventos `@app.on_event("startup")`).  
> Utiliza un `@asynccontextmanager`:
> 1. Al iniciar la aplicación (antes del `yield`): llama a `create_db_and_tables()` para crear las tablas de SQLModel en la base de datos y ejecuta `seed_unidades_medida(session)` de forma idempotente para asegurar que existan las 6 unidades base (`kg`, `g`, `L`, `mL`, `u`, `doc`).
> 2. Al apagar la aplicación (después del `yield`): permite cerrar pools de conexiones y liberar recursos de forma limpia.

---

### 9. ¿Qué es y cómo funciona la inyección de dependencias con `Depends(get_session)`?
> **Respuesta de 10:**  
> Es un patrón de diseño donde el framework suministra los recursos necesarios a cada endpoint.  
> La función generadora `get_session()` en `app/core/database.py` abre una sesión de base de datos con `with Session(engine) as session: yield session`.  
> Cuando un endpoint lo recibe mediante `service: ProductoService = Depends(get_producto_service)`, FastAPI garantiza que cada petición HTTP tenga su propia sesión aislada y que, al terminar la respuesta (o si ocurre un error), la sesión se cierre automáticamente, evitando fugas de conexiones en el pool.

---

### 10. ¿Por qué usamos `func.lower()` al validar la unicidad de nombres (RN-02)?
> **Respuesta de 10:**  
> Porque las bases de datos como PostgreSQL diferencian mayúsculas de minúsculas (*case-sensitive*). Si comparáramos con un simple `==`, la base de datos permitiría crear `"Pizzas"` y `"pizzas"`.  
> Al usar `func.lower(Producto.nombre) == nombre.strip().lower()`, la comparación se ejecuta en minúsculas en el motor SQL, garantizando que el nombre sea realmente único para el negocio sin importar cómo lo escriba el usuario.

---

## 🟩 BLOQUE B: FRONTEND (React, TypeScript, Tailwind, Estado y Consumo)

### 11. ¿Por qué la aplicación usa `fetch` nativo y no librerías como Axios o React Query?
> **Respuesta de 10:**  
> Por estricta consigna pedagógica de la cátedra para evaluar el dominio de las APIs estándar de la web y de React puro.  
> `fetch` es una función nativa de JavaScript disponible en todos los navegadores modernos que devuelve Promesas. No requiere dependencias externas, reduciendo el tamaño del bundle. El manejo de errores se resuelve evaluando la propiedad `response.ok` y capturando las respuestas en formato JSON con `await response.json()`.

---

### 12. ¿Por qué el estado está centralizado en `App.tsx` en lugar de que cada componente consulte la API?
> **Respuesta de 10:**  
> Sigue el patrón arquitectónico de **Componentes Contenedores vs. Componentes Presentacionales (Dumb Components)**:
> - `App.tsx` actúa como contenedor inteligente: gestiona el estado global (`productos`, `unidades`, `isLoading`, `error`), define las funciones que interactúan con el backend y pasa los datos hacia abajo mediante `props`.
> - Los componentes hijos (`ProductList`, `ProductCard`, `ProductModal`, `Navbar`) son puramente presentacionales: reciben datos y callbacks por props y no tienen efectos secundarios ni acoplamiento a URLs de red. Esto los hace 100% reutilizables, predecibles y fáciles de testear.

---

### 13. ¿Para qué se usa `useCallback` en la función `cargarDatos` dentro de `App.tsx`?
> **Respuesta de 10:**  
> En React, cada vez que un componente se vuelve a renderizar, todas las funciones declaradas en su interior se recrean con una nueva referencia de memoria.  
> Si pasáramos `cargarDatos` a `useEffect` sin `useCallback`, en cada renderizado la referencia cambiaría, haciendo que `useEffect` crea que la dependencia cambió y se vuelva a ejecutar en un bucle infinito (*infinite loop*). `useCallback` memoriza la función y solo la recrea si cambian sus dependencias reales.

---

### 14. ¿Cómo se cumple la regla de no cerrar el modal cuando la API devuelve un error (ej. 409 o 422)?
> **Respuesta de 10:**  
> En `App.tsx`, la función `handleFormSubmit` realiza la petición `fetch`. Si la respuesta no es exitosa (`!response.ok`), parsea el cuerpo de error `{"detail": "..."}` y retorna un objeto `{ success: false, error: errorDetail }`.  
> En `ProductModal.tsx`, al recibir `result.success === false`, el modal **NO** llama a `onClose()`. En su lugar, guarda el mensaje en su estado local `errorMessage`, mostrándolo inmediatamente en un banner de alerta rojo dentro del modal. De esta forma, el usuario puede corregir el nombre repetido o el stock inválido sin perder los demás campos que ya había completado.

---

### 15. ¿Cómo se actualiza la interfaz al alternar la disponibilidad de un producto sin recargar la página?
> **Respuesta de 10:**  
> Al presionar el botón "Pausar" o "Reanudar", se envía un `PUT` a la API con `disponible = !producto.disponible`.  
> Cuando el backend responde exitosamente con el `ProductoPublic` actualizado, ejecutamos:
> ```ts
> setProductos((prev) => prev.map((p) => (p.id === actualizado.id ? actualizado : p)));
> ```
> Usamos la función de actualización de estado (`prev => ...`) que reemplaza únicamente el elemento que coincide con el ID, manteniendo el orden de la lista. React detecta el cambio en ese objeto y re-renderiza solo esa fila o tarjeta de forma atómica y sin recargar la ventana.

---

### 16. ¿Qué ventaja ofrece el enfoque *utility-first* de Tailwind CSS 4 en este proyecto?
> **Respuesta de 10:**  
> Permite construir interfaces modernas y adaptables (*responsive*) componiendo clases utilitarias directamente sobre los elementos JSX (`flex`, `grid`, `bg-slate-900`, `text-amber-400`, `rounded-2xl`, etc.).  
> Con Tailwind 4, el motor de compilación detecta en tiempo real las clases utilizadas e inyecta solo el CSS necesario a través del plugin de Vite, logrando un bundle mínimo, diseño consistente sin inventar nombres arbitrarios de clases CSS y eliminando conflictos de especificidad.

---

### 17. ¿Por qué usamos TypeScript con `"strict": true` y qué significa no usar `any`?
> **Respuesta de 10:**  
> Con `"strict": true` y `"noImplicitAny": true`, el compilador de TypeScript activa todas las verificaciones rigurosas de tipo (como control estricto de nulos `null` y `undefined`).  
> Usar `any` desactiva completamente el sistema de tipos de TypeScript y convierte el código en JavaScript plano sin seguridad. Al tipar todo con interfaces (`Producto`, `UnidadMedida`, etc.), cualquier error de tipeo en un campo (ej. escribir `stock` en vez de `stock_cantidad`) es detectado en tiempo de compilación antes de llegar a producción.

---

### 18. ¿Por qué usamos `import type` para importar las interfaces en los componentes?
> **Respuesta de 10:**  
> En TypeScript moderno con la bandera `verbatimModuleSyntax: true`, `import type` le indica explícitamente al transpilador que esa importación es únicamente para verificación estática de tipos.  
> Al compilar a JavaScript para el navegador, el empaquetador (Vite / Rollup) elimina por completo esa línea (*type erasure*), garantizando que no queden referencias vacías en el código final y optimizando el tiempo de carga.

---

### 19. ¿Cómo se contemplan los tres estados de la interfaz (carga, error y lista vacía)?
> **Respuesta de 10:**  
> Mediante renderizado condicional en `App.tsx`:
> 1. **Carga (`isLoading === true`):** Muestra el componente `LoadingState` con un spinner animado mientras se resuelven las promesas de `fetch`.
> 2. **Error (`error !== null`):** Si el servidor está apagado o falla la red, muestra `ErrorState` con un botón "Reintentar conexión" que vuelve a invocar `cargarDatos()`.
> 3. **Vacío (`productos.length === 0`):** Si no hay error ni carga pero el catálogo no tiene ítems, muestra `EmptyState` invitando al usuario a crear el primer producto.

---

### 20. ¿Qué demuestra la prueba de independencia de estados entre `disponible`, `activo` y `stock_cantidad` (RN-12)?
> **Respuesta de 10:**  
> Demuestra que son tres atributos ortogonales con propósitos totalmente distintos en el modelo del negocio:
> - `activo`: define si el registro existe en el sistema o si fue dado de baja lógica (`DELETE`).
> - `disponible`: es una pausa manual y comercial de la venta que el administrador activa o desactiva a voluntad sin borrar el producto.
> - `stock_cantidad`: es la cantidad física real de existencias en el depósito.  
> Un producto puede estar activo, pero no disponible (pausado comercialmente); o puede estar activo y disponible pero con stock 0 (`hay_stock = false`, agotado temporalmente); o puede estar anulado conservando su última configuración histórica. Ninguna operación sobre uno modifica los otros.

