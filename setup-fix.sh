#!/usr/bin/env bash
# OCI Manager v4.0 - Setup Robusto para Ambientes Problemáticos

set -e  # Sair em caso de erro, mas sem strict mode

echo "→ OCI Manager v4.0 - Instalação Robusta"

# Detectar diretórios de forma segura
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(pwd)"
fi

APP_DIR="$HOME/oci-manager-v4"
VENV_DIR="$APP_DIR/venv"
LAUNCHER="$APP_DIR/run_oci_manager.sh"

echo "→ Instalando em: $APP_DIR"

# Verificar Python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠️  Python3 não encontrado. Tentando instalar..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update -y && sudo apt install -y python3 python3-venv python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3 python3-pip python3-virtualenv || true
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3 python3-pip python3-virtualenv || true
  else
    echo "❌ Instale Python3 manualmente e rode novamente."
    exit 1
  fi
fi

# Criar estrutura
mkdir -p "$APP_DIR/reports"

# Copiar ou baixar oci_manager.py
if [[ -f "$SCRIPT_DIR/oci_manager.py" ]]; then
  cp -f "$SCRIPT_DIR/oci_manager.py" "$APP_DIR/oci_manager.py"
  echo "✓ Copiado: oci_manager.py"
else
  echo "→ Baixando oci_manager.py do GitHub..."
  if command -v curl >/dev/null 2>&1; then
    curl -sSL https://raw.githubusercontent.com/thiagomassensini/oci-manager/main/oci_manager.py -o "$APP_DIR/oci_manager.py"
  elif command -v wget >/dev/null 2>&1; then
    wget -q https://raw.githubusercontent.com/thiagomassensini/oci-manager/main/oci_manager.py -O "$APP_DIR/oci_manager.py"
  else
    echo "❌ Instale curl ou wget para baixar o arquivo."
    exit 1
  fi
  echo "✓ Baixado: oci_manager.py"
fi

# Remover venv antigo se existir e tiver problemas
if [[ -d "$VENV_DIR" ]]; then
  echo "→ Removendo ambiente virtual antigo..."
  rm -rf "$VENV_DIR"
fi

# Criar novo ambiente virtual
echo "→ Criando ambiente virtual..."
python3 -m venv "$VENV_DIR"

# Ativar ambiente virtual
source "$VENV_DIR/bin/activate"

# Verificar se ativou corretamente
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "❌ Falha ao ativar ambiente virtual."
  exit 1
fi

# Atualizar pip de forma segura
echo "→ Atualizando pip..."
python -m pip install --upgrade pip || {
  echo "⚠️  Erro ao atualizar pip, continuando..."
}

# Instalar dependências com fallbacks
echo "→ Instalando OCI SDK..."
python -m pip install "oci>=2.130.0" || {
  echo "⚠️  Tentando instalação alternativa do OCI SDK..."
  python -m pip install oci || {
    echo "❌ Falha ao instalar OCI SDK."
    exit 1
  }
}

echo "→ Instalando Rich..."
python -m pip install "rich>=13.0.0" || {
  echo "⚠️  Tentando instalação alternativa do Rich..."
  python -m pip install rich || {
    echo "❌ Falha ao instalar Rich."
    exit 1
  }
}

# Criar launcher
echo "→ Criando launcher..."
cat > "$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
set -e

# Detectar diretório do script
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

# Ativar venv
if [[ -d "$SCRIPT_DIR/venv" ]]; then
  source "$SCRIPT_DIR/venv/bin/activate"
fi

# Executar
exec python3 "$SCRIPT_DIR/oci_manager.py" "$@"
EOF

chmod +x "$LAUNCHER"
chmod +x "$APP_DIR/oci_manager.py"

# Criar atalho
mkdir -p "$HOME/.local/bin"
ln -sf "$LAUNCHER" "$HOME/.local/bin/oci-manager" 2>/dev/null || true

# Adicionar ao PATH se necessário
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc 2>/dev/null || true
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

echo ""
echo "✅ OCI Manager v4.0 instalado com sucesso!"
echo ""
echo "Para executar:"
echo "  $LAUNCHER"
echo "  ou: oci-manager (após relogar ou source ~/.bashrc)"
echo ""

# Verificar configuração OCI
if [[ ! -f "$HOME/.oci/config" ]]; then
  echo "⚠️  Configure o OCI CLI antes de usar:"
  echo "   oci setup config"
fi
