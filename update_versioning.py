#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script seguro para agregar versioning a archivos HTML
- Crea backup automático
- Valida cambios antes de guardar
- Solo modifica lo necesario
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import sys

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def backup_file(filepath):
    """Crea un backup del archivo antes de modificar"""
    backup_path = f"{filepath}.backup"
    shutil.copy2(filepath, backup_path)
    return backup_path

def add_versioning_safe(html_dir="backend/static", version=None):
    """
    Agrega versioning a archivos HTML de forma segura

    Args:
        html_dir: Directorio con archivos HTML
        version: Versión a usar (default: fecha actual YYYYMMDD)
    """

    if version is None:
        version = datetime.now().strftime("%Y%m%d")

    # Patrones seguros que evitan duplicar versioning
    patterns = [
        # CSS: href="css/archivo.css" → href="css/archivo.css?v=20260819"
        # NO reemplaza si ya tiene ?v=
        (r'href="(css/[^"]+?)(?!\?v=)"', f'href="\\1?v={version}"'),

        # JS: src="js/archivo.js" → src="js/archivo.js?v=20260819"
        # NO reemplaza si ya tiene ?v=
        (r'src="(js/[^"]+?)(?!\?v=)"', f'src="\\1?v={version}"'),
    ]

    # Validar que el directorio existe
    if not os.path.isdir(html_dir):
        print(f"[ERROR] Directorio '{html_dir}' no existe")
        return False

    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]

    if not html_files:
        print(f"[ERROR] No se encontraron archivos .html en '{html_dir}'")
        return False

    print(f"[INFO] Procesando {len(html_files)} archivos HTML...")
    print(f"[INFO] Version: {version}\n")

    success_count = 0
    error_count = 0

    for filename in sorted(html_files):
        filepath = os.path.join(html_dir, filename)

        try:
            # Leer archivo original
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Crear backup
            backup_path = backup_file(filepath)

            # Aplicar patrones
            modified_content = original_content
            changes_made = False

            for pattern, replacement in patterns:
                modified_content, count = re.subn(pattern, replacement, modified_content)
                if count > 0:
                    changes_made = True

            # Validar que el archivo no esté vacío
            if not modified_content or len(modified_content) < len(original_content) * 0.5:
                print(f"[WARN] {filename}: Archivo corrupto detectado, restaurando backup...")
                shutil.copy2(backup_path, filepath)
                os.remove(backup_path)
                error_count += 1
                continue

            # Guardar archivo modificado
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            # Verificar que se guardó correctamente
            with open(filepath, 'r', encoding='utf-8') as f:
                saved_content = f.read()

            if saved_content == modified_content:
                print(f"[OK] {filename}")
                os.remove(backup_path)  # Eliminar backup si todo está bien
                success_count += 1
            else:
                print(f"[ERROR] {filename}: Error al guardar, restaurando backup...")
                shutil.copy2(backup_path, filepath)
                error_count += 1

        except Exception as e:
            print(f"[ERROR] {filename}: Error - {str(e)}")
            error_count += 1

    # Resumen
    print(f"\n{'='*50}")
    print(f"[OK] Completado: {success_count} archivos actualizados")
    if error_count > 0:
        print(f"[ERROR] {error_count} archivos fallaron")
    print(f"{'='*50}\n")

    return error_count == 0

if __name__ == "__main__":
    # Cambiar a la carpeta del proyecto si es necesario
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("[START] Iniciando actualizacion de versioning...\n")

    success = add_versioning_safe()

    if success:
        print("[SUCCESS] Actualizacion completada exitosamente!")
        print("[INFO] Los backups estan disponibles como .backup si necesitas restaurar")
    else:
        print("[WARN] Algunos archivos tuvieron errores")
