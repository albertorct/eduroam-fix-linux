#!/usr/bin/env python3
# ==============================================================================
# Script: configura_eduroam.py
# Autor: Alberto Tomaz
#
# ORIENTAÇÃO DE USO:
# Para rodar este script, abra o terminal na pasta onde o arquivo foi salvo
# e digite o seguinte comando:
#
# sudo python3 configura_eduroam.py
#
# (O 'sudo' é necessário porque o script ajusta configurações de rede e 
#  segurança do sistema).
# ==============================================================================

import os
import time
import subprocess
import getpass

def verifica_root():
    if os.geteuid() != 0:
        print("Erro: Este script precisa de permissões de administrador.")
        print("Por favor, execute usando: sudo python3 configura_eduroam.py")
        exit(1)

def corrige_openssl():
    print("[*] Verificando e corrigindo as regras do OpenSSL (Nível de Segurança 1)...")
    caminho_cnf = "/etc/ssl/openssl.cnf"
    
    with open(caminho_cnf, "r") as f:
        conteudo = f.read()

    alterado = False

    # Ativa a seção ssl_conf na inicialização se não estiver ativa
    if "ssl_conf = ssl_sect" not in conteudo:
        conteudo = conteudo.replace("[openssl_init]", "[openssl_init]\nssl_conf = ssl_sect")
        alterado = True

    # Adiciona a exceção de conexões legadas no final do arquivo
    config_legada = """
[ssl_sect]
system_default = system_default_sect

[system_default_sect]
Options = UnsafeLegacyServerConnect
CipherString = DEFAULT:@SECLEVEL=1
"""
    if "UnsafeLegacyServerConnect" not in conteudo:
        conteudo += "\n" + config_legada
        alterado = True

    if alterado:
        with open(caminho_cnf, "w") as f:
            f.write(conteudo)
        print("[+] Configuração do OpenSSL atualizada com sucesso.")
    else:
        print("[-] As regras do OpenSSL já estavam configuradas corretamente.")

def configura_rede(usuario, senha):
    print("[*] Limpando configurações antigas da eduroam...")
    subprocess.run(["nmcli", "connection", "delete", "eduroam"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    print("[*] Criando o novo perfil de rede...")
    comando_add = [
        "nmcli", "connection", "add", "type", "wifi", "con-name", "eduroam", "ssid", "eduroam",
        "wifi-sec.key-mgmt", "wpa-eap", "802-1x.eap", "peap", "802-1x.phase2-auth", "mschapv2",
        "802-1x.identity", usuario, "802-1x.password", senha,
        "802-1x.anonymous-identity", "anonymous@ufg.br",
        "802-1x.system-ca-certs", "no", "802-1x.ca-cert", "", "802-1x.domain-suffix-match", "",
        "wifi-sec.pmf", "disable"
    ]
    subprocess.run(comando_add, stdout=subprocess.DEVNULL)

def reinicia_e_conecta():
    print("[*] Reiniciando o NetworkManager para aplicar as mudanças...")
    subprocess.run(["systemctl", "restart", "NetworkManager"])
    time.sleep(5) # Aguarda a placa de rede voltar
    
    print("[*] Tentando conectar na eduroam...")
    resultado = subprocess.run(["nmcli", "connection", "up", "eduroam"], capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("\n[+++] SUCESSO! Conectado à eduroam. [+++]")
    else:
        print("\n[!] A tentativa de conexão falhou. Verifique se a senha está correta ou rode journalctl para investigar.")

def main():
    print("=== Assistente de Conexão Eduroam ===")
    verifica_root()
    
    usuario = input("Digite seu email de acesso (ex: seu.nome@ufg.br): ").strip()
    
    # Tratamento específico para evitar o bloqueio do servidor RADIUS da UFG
    if "@discente.ufg.br" in usuario:
        print("[!] Corrigindo domínio: removendo '@discente.ufg.br' e aplicando '@ufg.br'...")
        usuario = usuario.replace("@discente.ufg.br", "@ufg.br")
    elif "@" not in usuario:
        usuario += "@ufg.br"
        
    senha = getpass.getpass("Digite sua senha (ela ficará oculta enquanto você digita): ")

    corrige_openssl()
    configura_rede(usuario, senha)
    reinicia_e_conecta()

if __name__ == "__main__":
    main()
