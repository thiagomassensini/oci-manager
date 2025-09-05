#!/bin/bash

# OCI Manager v4.0 - Script de Instalação Unificado
# Instala automaticamente o OCI Manager com todas as dependências
# Resolve todos os problemas de permissão e compatibilidade

set -e  # Para execução em caso de erro

INSTALL_DIR="$HOME/oci-manager-v4"
VENV_DIR="$INSTALL_DIR/venv"

echo "→ OCI Manager v4.0 - Instalação Unificada"
echo "→ Instalando em: $INSTALL_DIR"

# Função para limpeza segura de instalação anterior
safe_cleanup() {
    if [ -d "$INSTALL_DIR" ]; then
        echo "→ Removendo instalação anterior..."
        # Primeira tentativa: remoção normal
        rm -rf "$INSTALL_DIR" 2>/dev/null || {
            echo "→ Problemas de permissão detectados, corrigindo..."
            # Tentar com chmod recursivo
            chmod -R 755 "$INSTALL_DIR" 2>/dev/null || true
            find "$INSTALL_DIR" -type f -exec chmod 644 {} \; 2>/dev/null || true
            rm -rf "$INSTALL_DIR" 2>/dev/null || {
                # Última tentativa com sudo se disponível
                if command -v sudo >/dev/null 2>&1; then
                    echo "→ Usando sudo para limpeza..."
                    sudo rm -rf "$INSTALL_DIR" 2>/dev/null || true
                fi
                # Se ainda existir, avisa mas continua
                if [ -d "$INSTALL_DIR" ]; then
                    echo "⚠️  Aviso: Instalação anterior não removida completamente"
                    echo "   Continuando instalação..."
                fi
            }
        }
    fi
}

# Limpeza segura
safe_cleanup

# Criar diretório de instalação
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download do arquivo principal
echo "→ Baixando oci_manager.py..."
curl -sSL https://raw.githubusercontent.com/thiagomassensini/oci-manager/main/oci_manager.py -o oci_manager.py
echo "✓ Copiado: oci_manager.py"

# Criar ambiente virtual
echo "→ Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip e ferramentas essenciais
echo "→ Atualizando pip e ferramentas..."
pip install --upgrade pip wheel setuptools

# Instalar dependências
echo "→ Instalando dependências OCI..."
pip install oci

echo "→ Instalando Rich para interface..."
pip install rich

# Teste de instalação
echo "→ Testando instalação..."
python3 -c "import oci; import rich; print('✓ Dependências OK')" || {
    echo "❌ Erro na instalação das dependências"
    exit 1
}

# Criar script de execução robusto
cat > run.sh << 'EOF'
#!/bin/bash
# Script de execução do OCI Manager
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 oci_manager.py "$@"
EOF

chmod +x run.sh

# Criar alias nos shells
ALIAS_LINE="alias oci-manager='$INSTALL_DIR/run.sh'"

# Bashrc
if [ -f ~/.bashrc ]; then
    if ! grep -q "oci-manager" ~/.bashrc 2>/dev/null; then
        echo "$ALIAS_LINE" >> ~/.bashrc
        echo "✓ Alias adicionado ao ~/.bashrc"
    fi
fi

# Zshrc
if [ -f ~/.zshrc ]; then
    if ! grep -q "oci-manager" ~/.zshrc 2>/dev/null; then
        echo "$ALIAS_LINE" >> ~/.zshrc
        echo "✓ Alias adicionado ao ~/.zshrc"
    fi
fi

echo ""
echo "🎉 OCI Manager v4.0 instalado com sucesso!"
echo ""
echo "Para usar:"
echo "  1. Execute: source ~/.bashrc (ou ~/.zshrc)"
echo "  2. Depois: oci-manager"
echo "  3. Ou diretamente: $INSTALL_DIR/run.sh"
echo ""
echo "Primeira execução: configure seus perfis OCI com 'oci setup config'"
