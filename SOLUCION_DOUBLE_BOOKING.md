# Solución: Prevención de Double Booking (Reservas Duplicadas)

## Problema Identificado

Cuando dos usuarios intentaban reservar la **misma hora del mismo día** de forma simultánea, ambas reservas se creaban en lugar de rechazar la segunda.

### Causa Raíz: Race Condition

```
Usuario A                          Usuario B
    │                                │
    ├─ Consulta: ¿Existe cita?       │
    │  Respuesta: NO ✓               │
    │                                ├─ Consulta: ¿Existe cita? (simultáneamente)
    │                                │  Respuesta: NO ✓ (aún no se inserta la de A)
    │                                │
    ├─ Inserta cita (OK) ✓           │
    │                                ├─ Inserta cita (OK) ✗ ← PROBLEMA
    │                                │
    └─ RESULTADO: Dos citas confirmadas para la misma hora
```

**El problema:** La validación (`find_one`) y la inserción (`insert_one`) NO son operaciones atómicas. Hay un pequeño lapso de tiempo donde dos usuarios pueden pasar la validación antes de que ninguno se inserte.

---

## Solución Implementada

### 1. **Índice Único Parcial en MongoDB** 
Se agregó un índice único que previene inserciones duplicadas:

```javascript
db.citas.createIndex(
  { dia: 1, hora: 1, barbero: 1 },
  { 
    unique: true, 
    partialFilterExpression: { estado: 'confirmada' }
  }
)
```

**¿Qué hace?**
- Garantiza que no pueden existir dos documentos con el mismo `(día, hora, barbero)` cuando `estado = 'confirmada'`
- La segunda inserción falla automáticamente con `DuplicateKeyError`
- Esto es **atómico y thread-safe** a nivel de BD

### 2. **Captura de DuplicateKeyError**
Se reemplazó la lógica de validación + inserción con una más segura:

**Antes (INSEGURO):**
```python
# Paso 1: Validar
cita_existe = db.citas.find_one({...})  # Race condition aquí
if cita_existe:
    return error_409

# Paso 2: Insertar (otro usuario podría haber insertado entre paso 1 y 2)
resultado = db.citas.insert_one(cita.to_dict())
```

**Después (SEGURO):**
```python
# Ambos pasos son atómicos - no hay brecha
try:
    resultado = db.citas.insert_one(cita.to_dict())
except DuplicateKeyError:
    return error_409  # El índice único previno la inserción
```

### 3. **Inicialización Automática del Índice**
- En `database.py`: Se crea automáticamente al iniciar la aplicación
- En `init_indexes.py`: Script manual opcional para crear el índice

---

## Cambios Realizados

### Backend Files Modificados:

1. **`backend/routes/citas.py`**
   - Línea 8: Agregó importación de `OperationFailure`
   - Líneas 44-98: Reemplazó lógica de `crear_cita()` con validación atómica
   - Línea 373: Cambió `'confirmed'` → `'confirmada'` para consistencia

2. **`backend/database.py`**
   - Línea 24: Agregó llamada a `_crear_indice_unico()`
   - Líneas 30-50: Nuevo método que crea el índice único parcial

3. **`backend/init_indexes.py`** (nuevo archivo)
   - Script para crear manualmente el índice si es necesario

---

## Flujo Después de la Solución

```
Usuario A                          Usuario B
    │                                │
    ├─ Intenta insertar cita         │
    │  (pasa por índice único) ✓     │
    │                                ├─ Intenta insertar cita (simultáneamente)
    │                                │  MongoDB: DuplicateKeyError ✗
    │                                │
    ├─ Reserva exitosa               │
    │  Estado: 201 Created            ├─ Reserva rechazada
    │                                │  Estado: 409 Conflict
    │                                │  Mensaje: "Ese horario ya está reservado"
    │
    └─ RESULTADO: Solo una cita confirmada
```

---

## Testing

Para verificar que funciona:

1. **Abrir dos navegadores** (o dos pestañas en incógnito)
2. **Ambos usuarios seleccionan:**
   - Mismo día
   - Misma hora
3. **Ambos dan click en "Reservar"** exactamente al mismo tiempo
4. **Resultado esperado:**
   - ✅ Primer usuario: Reserva exitosa
   - ❌ Segundo usuario: Mensaje de error "Ese horario ya está reservado"
   - Frontend ya tiene manejo para este error 409 (ver línea 206 en `app.js`)

---

## Consideraciones de Producción

✅ **Thread-safe**: Funciona con múltiples servidores simultáneamente  
✅ **Escalable**: El índice está a nivel de base de datos  
✅ **Compatible**: Funciona con MongoDB 3.2+  
✅ **Sin cambios de esquema**: Solo agrega un índice  
✅ **Transacciones automáticas**: No requiere código de transacciones complejas  

---

## Resumen

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Race Condition** | ❌ Vulnerable | ✅ Prevenida |
| **Double Booking** | ❌ Posible | ✅ Imposible |
| **Performance** | ✓ Normal | ✓ Normal (+índice) |
| **Complejidad** | ✓ Simple | ✓ Simple |
| **Mantenibilidad** | ✓ Fácil | ✓ Fácil |
