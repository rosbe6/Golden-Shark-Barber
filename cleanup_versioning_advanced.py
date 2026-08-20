#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpia versioning multiple duplicado
Reemplaza ?v=20260819?v=20260819... por ?v=20260819
"""

import os
import re
from pathlib import Path

def cleanup_advanced(html_dir="backend/static"):
    """Limpia versioning duplicado avanzado"""

    if not os.path.isdir(html_dir):
        print(f"[ERROR] Directorio '{html_dir}' no existe")
        return False

    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]

    if not html_files:
        print(f"[ERROR] No se encontraron archivos .html en '{html_dir}'")
        return False

    print(f"[INFO] Limpiando {len(html_files)} archivos HTML...\n")

    success_count = 0

    for filename in sorted(html_files):
        filepath = os.path.join(html_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Patrón: ?v=20260819?v=20260819?v=20260819... (cualquier cantidad de duplicados)
            # Reemplazar por un solo ?v=20260819
            modified = re.sub(r'(\?v=20260819)+', '?v=20260819', content)

            if modified != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)

                print(f"[OK] {filename} - Limpiado")
                success_count += 1
            else:
                print(f"[SKIP] {filename}")

        except Exception as e:
            print(f"[ERROR] {filename}: {str(e)}")

    print(f"\n{'='*50}")
    print(f"[OK] Completado: {success_count} archivos")
    print(f"{'='*50}\n")

    return True

if __name__ == "__main__":
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("[START] Limpiando versioning avanzado...\n")
    cleanup_advanced()
    print("[SUCCESS] Limpieza completada!")
