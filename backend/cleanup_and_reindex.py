"""
Script para limpiar citas duplicadas y reconstruir el índice único.
Ejecutar esto si ya tienes citas duplicadas en la BD.
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def limpiar_duplicados():
    """Eliminar citas duplicadas y reconstruir índice"""

    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise ValueError("MONGO_URI no está configurada en .env")

    client = MongoClient(mongo_uri)
    db = client.get_database()
    citas_collection = db.citas

    print("=" * 60)
    print("LIMPIEZA DE CITAS DUPLICADAS Y REINDEXACIÓN")
    print("=" * 60)

    # 1. Contar citas antes de limpiar
    total_antes = citas_collection.count_documents({})
    print(f"\n1. Total de citas antes: {total_antes}")

    # 2. Buscar grupos de citas duplicadas (mismo día, hora, estado confirmada)
    pipeline = [
        {
            '$match': {'estado': 'confirmada'}
        },
        {
            '$group': {
                '_id': {'dia': '$dia', 'hora': '$hora'},
                'count': {'$sum': 1},
                'ids': {'$push': '$_id'}
            }
        },
        {
            '$match': {'count': {'$gt': 1}}
        }
    ]

    duplicados = list(citas_collection.aggregate(pipeline))

    if duplicados:
        print(f"\n2. Se encontraron {len(duplicados)} horarios duplicados:")
        for dup in duplicados:
            print(f"   - Día: {dup['_id']['dia']}, Hora: {dup['_id']['hora']}")
            print(f"     Cantidad: {dup['count']} citas")
            print(f"     IDs: {dup['ids']}")

        # 3. Eliminar citas duplicadas (mantener solo la primera)
        print(f"\n3. Eliminando duplicados (guardando solo la primera de cada)...")
        eliminadas = 0
        for dup in duplicados:
            ids_a_eliminar = dup['ids'][1:]  # Mantener el primero, eliminar el resto
            resultado = citas_collection.delete_many({'_id': {'$in': ids_a_eliminar}})
            eliminadas += resultado.deleted_count

        print(f"   ✅ Se eliminaron {eliminadas} citas duplicadas")
    else:
        print("\n2. ✅ No se encontraron citas duplicadas")

    # 4. Eliminar índice anterior (si existe)
    print("\n4. Eliminando índice anterior (si existe)...")
    try:
        citas_collection.drop_index('unique_confirmed_appointment')
        print("   ✅ Índice eliminado")
    except Exception as e:
        print(f"   ℹ️  No había índice anterior: {str(e)}")

    # 5. Asegurar que todas las citas tengan el campo 'barbero'
    print("\n5. Verificando campo 'barbero' en todas las citas...")
    sin_barbero = citas_collection.count_documents({'barbero': {'$exists': False}})
    if sin_barbero > 0:
        print(f"   - Se encontraron {sin_barbero} citas sin barbero")
        citas_collection.update_many(
            {'barbero': {'$exists': False}},
            {'$set': {'barbero': 'Rosbin'}}
        )
        print("   ✅ Se agregó 'barbero: Rosbin' a todas las citas")
    else:
        print("   ✅ Todas las citas tienen barbero")

    # 6. Crear nuevo índice único parcial
    print("\n6. Creando nuevo índice único parcial...")
    try:
        citas_collection.create_index(
            [
                ('dia', 1),
                ('hora', 1),
                ('barbero', 1)
            ],
            unique=True,
            partialFilterExpression={'estado': 'confirmada'},
            name='unique_confirmed_appointment'
        )
        print("   ✅ Índice único creado correctamente")
    except Exception as e:
        print(f"   ❌ Error al crear índice: {str(e)}")
        raise

    # 7. Verificar resultado final
    total_despues = citas_collection.count_documents({})
    print(f"\n7. Total de citas después: {total_despues}")
    print(f"   Citas eliminadas: {total_antes - total_despues}")

    print("\n" + "=" * 60)
    print("✅ LIMPIEZA Y REINDEXACIÓN COMPLETADA")
    print("=" * 60)

    client.close()

if __name__ == '__main__':
    try:
        limpiar_duplicados()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
