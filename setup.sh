#!/usr/bin/env bash
set -euo pipefail

### ───────────────────────────────────────────────────────────
###  OCI Manager v4.0 — setup.sh
###  - Cria venv e instala deps (oci, rich)
###  - Copia o oci_manager.py para ~/oci-manager-v4
###  - Gera run_oci_manager.sh
###  - Cria atalho "oci-manager" no PATH
### ───────────────────────────────────────────────────────────

# 1) Detecta diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/oci-manager-v4"
VENV_DIR="$APP_DIR/venv"
LAUNCHER="$APP_DIR/run_oci_manager.sh"

echo "→ Instalando OCI Manager v4.0 em: $APP_DIR"

# 2) Garante Python3 e venv
if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠️  python3 não encontrado. Tentando instalar..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update -y && sudo apt install -y python3 python3-venv python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3 python3-pip python3-virtualenv || true
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3 python3-pip python3-virtualenv || true
  else
    echo "❌ Não consegui instalar Python automaticamente. Instale python3/venv e rode novamente."
    exit 1
  fi
fi

# 3) Prepara estrutura
mkdir -p "$APP_DIR/reports"

# 4) Copia o último oci_manager.py (o seu v4.0)
if [[ -f "$SCRIPT_DIR/oci_manager.py" ]]; then
  cp -f "$SCRIPT_DIR/oci_manager.py" "$APP_DIR/oci_manager.py"
  echo "✓ Copiado: $SCRIPT_DIR/oci_manager.py → $APP_DIR/oci_manager.py"
else
  echo "⚠️  oci_manager.py não encontrado ao lado do setup.sh."
  echo "    Coloque o seu oci_manager.py v4.0 no mesmo diretório do setup.sh e rode de novo."
  exit 1
fi

# 5) Cria venv e instala dependências
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip wheel
# OCI SDK + Rich (UI)
pip install "oci>=2.130.0" "rich>=13.0.0"

# 6) Gera launcher
cat > "$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ativa venv do app
if [[ -d "$SCRIPT_DIR/venv" ]]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/venv/bin/activate"
fi

# Executa
exec python3 "$SCRIPT_DIR/oci_manager.py" "$@"
EOF
chmod +x "$LAUNCHER"
echo "✓ Gerado launcher: $LAUNCHER"

# 7) Cria atalho no PATH (preferência: /usr/local/bin, fallback: ~/.local/bin)
TARGET_BIN="/usr/local/bin/oci-manager"
if [[ -w "/usr/local/bin" ]]; then
  ln -sf "$LAUNCHER" "$TARGET_BIN"
  echo "✓ Atalho criado: $TARGET_BIN"
else
  mkdir -p "$HOME/.local/bin"
  ln -sf "$LAUNCHER" "$HOME/.local/bin/oci-manager"
  echo "✓ Atalho criado: $HOME/.local/bin/oci-manager"
  if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo '⚠️  Adicione ao PATH (bash/zsh): export PATH="$HOME/.local/bin:$PATH"'
  fi
fi

# 8) Checagem opcional do arquivo ~/.oci/config
if [[ ! -f "$HOME/.oci/config" ]]; then
  echo "⚠️  Não encontrei ~/.oci/config. Crie/perfil( DEFAULT/INANNA/HERICKASF ) antes de usar."
fi

echo
echo "✅ OCI Manager v4.0 instalado."
echo "→ Rode:  oci-manager"
echo "   ou:   $LAUNCHER"
