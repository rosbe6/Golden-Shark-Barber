# 🔧 Instrucciones para Reparar el Sistema de Reservas

## Problemas Solucionados

### 1. ✅ Desfase de Zona Horaria (Timezone)
**Problema**: Al reservar para el 27, se guardaba el 26 en la confirmación.

**Solución**: Cambié cómo se envía la fecha desde el frontend para usar la zona horaria local.

**Archivo modificado**: `backend/static/js/app.js` (línea 71)

---

### 2. ✅ Race Condition en Reservas Simultáneas
**Problema**: Dos usuarios podían reservar el mismo horario al mismo tiempo.

**Solución**: Agregué índice único en MongoDB para prevenir duplicados.

**Archivos modificados**:
- `backend/routes/citas.py`
- `backend/database.py`
- `backend/models/cita.py`

---

## 🚀 Pasos para Aplicar la Reparación

### Paso 1: Parar la Aplicación
```bash
# Detener el servidor Flask (Ctrl+C si está corriendo)
```

### Paso 2: Ejecutar Limpieza y Reindexación
Este script eliminará citas duplicadas y creará el índice:

```bash
cd backend
python cleanup_and_reindex.py
```

**¿Qué hace?**
- ✅ Busca citas duplicadas (mismo día/hora)
- ✅ Elimina las duplicadas (mantiene solo la primera)
- ✅ Crea el índice único para prevenir futuros duplicados
- ✅ Asegura que todas las citas tengan el campo 'barbero'

**Output esperado:**
```
============================================================
LIMPIEZA DE CITAS DUPLICADAS Y REINDEXACIÓN
============================================================

1. Total de citas antes: 12
2. Se encontraron 2 horarios duplicados:
   - Día: 2026-06-27, Hora: 13:20
     Cantidad: 2 citas
   ...
3. Eliminando duplicados (guardando solo la primera de cada)...
   ✅ Se eliminaron 2 citas duplicadas
4. Eliminando índice anterior (si existe)...
   ✅ Índice eliminado
5. Verificando campo 'barbero' en todas las citas...
   ✅ Todas las citas tienen barbero
6. Creando nuevo índice único parcial...
   ✅ Índice único creado correctamente
7. Total de citas después: 10

============================================================
✅ LIMPIEZA Y REINDEXACIÓN COMPLETADA
============================================================
```

### Paso 3: Reiniciar la Aplicación
```bash
python app.py
```

La aplicación verificará/creará automáticamente el índice al iniciar.

---

## ✅ Verificar que Funciona

### Test 1: Fecha Correcta
1. Abre la app de reservas
2. Selecciona una fecha (ej: 27 de Junio)
3. Reserva y verifica que la confirmación muestre la fecha correcta

**Esperado**: Debe mostrar el 27, no el 26 ❌

### Test 2: Prevención de Duplicados
1. Abre **dos navegadores** (o dos pestañas en incógnito)
2. En ambos, selecciona **el mismo día y hora**
3. En ambos, completa los datos y haz click en "Reservar" **exactamente al mismo tiempo**

**Esperado**:
- ✅ Usuario 1: Reserva exitosa → Ve confirmación
- ❌ Usuario 2: Error 409 → Mensaje "Ese horario ya está reservado"

---

## ⚠️ Si Algo Sale Mal

### Error: "Database connection failed"
- Verifica que MongoDB esté corriendo
- Verifica que `MONGO_URI` está en el archivo `.env`

### Error: "E11000 duplicate key error"
- Significa que el índice no se creó correctamente
- Ejecuta nuevamente: `python cleanup_and_reindex.py`

### Aún Puedo Reservar el Mismo Horario
- Verifica que el script se ejecutó sin errores
- Comprueba que el índice existe en MongoDB:
  ```bash
  # En MongoDB shell:
  db.citas.getIndexes()
  ```
  Deberías ver un índice llamado `unique_confirmed_appointment`

---

## 📋 Resumen de Cambios

| Archivo | Cambio | Razón |
|---------|--------|-------|
| `app.js` | Usar zona horaria local para fechas | Arreglar desfase de 1 día |
| `citas.py` | Capturar `DuplicateKeyError` | Prevenir race condition |
| `database.py` | Crear índice único al iniciar | Garantizar atomicidad |
| `models/cita.py` | Agregar campo 'barbero' | Requerido por el índice |
| `cleanup_and_reindex.py` | Script nuevo | Limpiar duplicados existentes |

---

## 🎯 Resultado Final

✅ **Fechas correctas** - Sin desfase de zona horaria  
✅ **Sin duplicados** - Imposible reservar el mismo horario dos veces  
✅ **Thread-safe** - Funciona con múltiples usuarios simultáneamente  
✅ **Escalable** - El índice está a nivel de base de datos  

---

## ¿Necesitas Ayuda?

Si después de ejecutar `cleanup_and_reindex.py` sigue sin funcionar:

1. Verifica en MongoDB que el índice exista:
   ```javascript
   db.citas.getIndexes()
   ```

2. Comprueba que todas las citas nuevas tengan estos campos:
   ```javascript
   db.citas.findOne()
   ```
   Debe tener: `_id`, `dia`, `hora`, `barbero`, `estado: "confirmada"`

3. Prueba crear una cita manualmente desde la app y verifica que se guarde correctamente
