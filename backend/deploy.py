#!/usr/bin/env python3
import subprocess
import sys
import getpass
from pathlib import Path

# Configuración
VPS_IP = "108.181.184.168"
VPS_USER = "administrator"
VPS_PATH = "/var/www/Golden-Shark-Barber"

def run_command(cmd, description):
    """Ejecuta comando y reporta"""
    print(f"\n📌 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {description}")
    if result.stdout:
        print(result.stdout)
    return True

def deploy():
    """Deploy automático"""
    
    # 1. Pedir contraseña VPS
    print("🔐 Contraseña VPS requerida")
    vps_password = getpass.getpass("Contraseña: ")
    
    # 2. Git commit
    commit_msg = input("\n📝 Commit message: ").strip()
    if not commit_msg:
        print("❌ Mensaje vacío")
        return
    
    if not run_command(f'git add -A', 'Git add'):
        return
    
    if not run_command(f'git commit -m "{commit_msg}"', 'Git commit'):
        return
    
    if not run_command(f'git push origin main', 'Git push'):
        return
    
    # 3. SSH a VPS con contraseña
    print(f"\n🚀 Conectando a VPS...")
    
    commands = f"""
    cd {VPS_PATH}
    git pull origin main
    systemctl restart goldenshark
    systemctl status goldenshark
    """
    
    # Usar sshpass
    ssh_cmd = f'sshpass -p "{vps_password}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_IP} "{commands}"'
    
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"⚠️ {result.stderr}")
    
    if result.returncode == 0:
        print("\n✅ DEPLOY COMPLETADO!")
    else:
        print(f"\n❌ Error en deploy")

if __name__ == "__main__":
    deploy()