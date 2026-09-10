# 🛜 Eduroam Fix para Linux (OpenSSL 3 / NetworkManager)

Um script em Python para automatizar e corrigir definitivamente os problemas de conexão com a rede Wi-Fi **eduroam** em distribuições Linux modernas, com foco nas configurações exigidas pelos servidores RADIUS de universidades federais (testado no ambiente da Universidade Federal de Goiás - UFG).

## ⚠️ O Problema

Estudantes que utilizam distribuições Linux recentes (como Ubuntu 22.04+, Fedora, Arch Linux, Pop!_OS) frequentemente enfrentam um erro silencioso ao tentar conectar na eduroam: a rede conecta e desconecta em loop, entra em *timeout* de "no-secrets", ou a interface gráfica fica pedindo a senha repetidamente como se estivesse errada.

Isso não é um erro de driver ou de senha, mas sim um **bloqueio de segurança arquitetural**:
1. **OpenSSL 3 e Criptografia Legada:** As distros modernas utilizam o OpenSSL 3 com Nível de Segurança 2 (SECLEVEL=2) por padrão. Isso bloqueia ativamente conexões com servidores que utilizam algoritmos de *hash* antigos (como SHA-1) ou que não suportam *Secure Renegotiation*. Muitos servidores universitários ainda não foram atualizados para os padrões mais novos.
2. **Exigência Estrita de Certificados:** O NetworkManager do Linux exige a validação do certificado CA da instituição, que muitas vezes conflita com as cadeias da RNP (Rede Nacional de Ensino e Pesquisa).
3. **Validação de Domínio:** Alguns servidores RADIUS rejeitam subdomínios de alunos (como `@discente.instituicao.br`), aceitando apenas o domínio base.

## 🛠️ O Que o Script Faz?

O `configura_eduroam.py` atua diretamente na raiz do problema sem comprometer a estabilidade do sistema operacional. O script executa as seguintes etapas:

- **Modificação do OpenSSL:** Injeta de forma segura as diretivas `UnsafeLegacyServerConnect` e `CipherString = DEFAULT:@SECLEVEL=1` no arquivo `/etc/ssl/openssl.cnf`, permitindo o *handshake* com servidores legados.
- **Saneamento de Perfis:** Remove perfis antigos e corrompidos da eduroam no NetworkManager.
- **Configuração via `nmcli`:** Cria um perfil de conexão à prova de falhas com os protocolos exatos (WPA-Enterprise, PEAP, MSCHAPv2) e desativa a verificação de certificados problemáticos (`802-1x.system-ca-certs no`).
- **Tratamento de Identidade:** Converte e-mails acadêmicos complexos automaticamente para o domínio raiz aceito pelo servidor.
- **Desativação do PMF:** Desativa o *Protected Management Frames* (PMF), que costuma causar incompatibilidade com placas de rede da Intel (ex: chipsets AX201/AX211).

## 🚀 Como Usar

### Pré-requisitos
- Uma distribuição Linux rodando o `NetworkManager`.
- Python 3 instalado.
- Permissões de superusuário (root/sudo).

### Instalação e Execução

1. Clone o repositório ou baixe o arquivo `configura_eduroam.py`:
   ```bash
   git clone [https://github.com/albertorct/eduroam-fix-linux.git](https://github.com/albertorct/eduroam-fix-linux.git)
   cd eduroam-fix-linux 