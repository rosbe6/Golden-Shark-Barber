#!/usr/bin/env python3
import subprocess
import sys
import getpass
import paramiko

# Configuración
VPS_IP = "108.181.184.168"
VPS_USER = "administrator"
VPS_PATH = "/var/www/Golden-Shark-Barber"

def run_command(cmd, description):
    """Ejecuta comando local"""
    print(f"\n📌 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {description}")
    if result.stdout:
        print(result.stdout)
    return True

def ssh_exec(ssh, command):
    """Ejecuta comando en VPS via SSH"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode()

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
    
    # 3. SSH a VPS
    print(f"\n🚀 Conectando a VPS...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, username=VPS_USER, password=vps_password, timeout=10)
        
        print("✅ Conectado a VPS")
        
        # Commands
        output = ssh_exec(ssh, f"cd {VPS_PATH} && git pull origin main")
        print(output)
        
        output = ssh_exec(ssh, "systemctl restart goldenshark")
        print(output)
        
        output = ssh_exec(ssh, "systemctl status goldenshark")
        print(output)
        
        ssh.close()
        print("\n✅ DEPLOY COMPLETADO!")
        
    except Exception as e:
        print(f"❌ Error SSH: {e}")

if __name__ == "__main__":
    deploy()