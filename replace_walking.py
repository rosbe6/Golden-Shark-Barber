#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reemplaza "Walking" por "WALK-INS" en todos los archivos HTML
"""

import os
import shutil
from pathlib import Path

def replace_walking(html_dir="backend/static"):
    """Reemplaza Walking por WALK-INS"""

    # Validar que el directorio existe
    if not os.path.isdir(html_dir):
        print(f"[ERROR] Directorio '{html_dir}' no existe")
        return False

    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]

    if not html_files:
        print(f"[ERROR] No se encontraron archivos .html en '{html_dir}'")
        return False

    print(f"[INFO] Procesando {len(html_files)} archivos HTML...\n")

    success_count = 0
    changes_count = 0

    for filename in sorted(html_files):
        filepath = os.path.join(html_dir, filename)

        try:
            # Leer archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Guardar copia de seguridad
            backup_path = f"{filepath}.backup"
            shutil.copy2(filepath, backup_path)

            # Contar cambios
            count = content.count('Walking')

            if count > 0:
                # Reemplazar Walking por WALK-INS
                modified_content = content.replace('Walking', 'WALK-INS')

                # Guardar archivo
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_content)

                # Verificar
                with open(filepath, 'r', encoding='utf-8') as f:
                    saved = f.read()

                if saved == modified_content:
                    print(f"[OK] {filename} - {count} cambio(s)")
                    os.remove(backup_path)
                    success_count += 1
                    changes_count += count
                else:
                    print(f"[ERROR] {filename} - Error al guardar, restaurando...")
                    shutil.copy2(backup_path, filepath)
                    os.remove(backup_path)
            else:
                print(f"[SKIP] {filename} - Sin cambios")
                os.remove(backup_path)

        except Exception as e:
            print(f"[ERROR] {filename}: {str(e)}")

    print(f"\n{'='*50}")
    print(f"[OK] Completado: {success_count} archivos actualizados")
    print(f"[OK] Total cambios: {changes_count}")
    print(f"{'='*50}\n")

    return True

if __name__ == "__main__":
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("[START] Reemplazando 'Walking' por 'WALK-INS'...\n")
    replace_walking()
    print("[SUCCESS] Reemplazo completado!")
