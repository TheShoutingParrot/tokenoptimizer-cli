#!/bin/bash
#
# Token Optimizer Installation Script
# ------------------------------------
# This script installs tokenoptimizer and optionally sets up authentication.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/TheShoutingParrot/tokenoptimizer-cli/main/install.sh | bash
#   ./install.sh
#   ./install.sh --user        # Install for current user only
#   ./install.sh --no-auth     # Skip authentication setup
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
USER_INSTALL=false
SKIP_AUTH=false
VENV_INSTALL=false
VENV_PATH=""
BREAK_SYSTEM_PACKAGES=false

print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║       Token Optimizer Installer       ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        error "Python 3 is required but not found. Please install Python 3.8 or later."
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        error "Python 3.8+ is required. Found Python $PYTHON_VERSION"
    fi

    success "Found Python $PYTHON_VERSION"
}

check_pip() {
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        PIP_CMD="$PYTHON_CMD -m pip"
        success "Found pip"
    else
        error "pip is required but not found. Please install pip."
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --user)
                USER_INSTALL=true
                shift
                ;;
            --no-auth)
                SKIP_AUTH=true
                shift
                ;;
            --venv)
                VENV_INSTALL=true
                VENV_PATH="${2:-./venv}"
                shift 2 2>/dev/null || shift
                ;;
            --break-system-packages)
                BREAK_SYSTEM_PACKAGES=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --user       Install for current user only (no sudo)"
                echo "  --no-auth    Skip API key setup"
                echo "  --venv PATH  Install into a virtual environment"
                echo "  --break-system-packages  Pass --break-system-packages to pip"
                echo "  -h, --help   Show this help message"
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                shift
                ;;
        esac
    done
}

install_package() {
    info "Installing tokenoptimizer..."

    INSTALL_FLAGS=""
    if [ "$USER_INSTALL" = true ]; then
        INSTALL_FLAGS="--user"
    fi
    if [ "$BREAK_SYSTEM_PACKAGES" = true ]; then
        INSTALL_FLAGS="$INSTALL_FLAGS --break-system-packages"
    fi

    # Check if we're in the project directory or need to install from PyPI
    if [ -f "pyproject.toml" ]; then
        info "Installing from local directory..."
        $PIP_CMD install $INSTALL_FLAGS -e . || $PIP_CMD install $INSTALL_FLAGS .
    else
        info "Installing from PyPI..."
        $PIP_CMD install $INSTALL_FLAGS tokenoptimizer
    fi

    success "tokenoptimizer installed successfully"
}

setup_venv() {
    if [ "$VENV_INSTALL" = true ]; then
        info "Creating virtual environment at $VENV_PATH..."
        $PYTHON_CMD -m venv "$VENV_PATH"

        # Activate venv and update pip/python commands
        source "$VENV_PATH/bin/activate"
        PYTHON_CMD="python"
        PIP_CMD="pip"

        success "Virtual environment created and activated"
    fi
}

setup_auth() {
    if [ "$SKIP_AUTH" = true ]; then
        info "Skipping authentication setup"
        return
    fi

    echo ""
    echo -e "${BLUE}Authentication Setup${NC}"
    echo "─────────────────────"

    # Check if already configured
    if tokenoptimizer auth show 2>/dev/null | grep -q "API key:"; then
        info "API key already configured"
        read -p "Do you want to update it? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    echo ""
    echo "Get your API key from: https://thetokencompany.com"
    echo ""
    read -p "Enter your API key (or press Enter to skip): " -r API_KEY

    if [ -n "$API_KEY" ]; then
        tokenoptimizer auth set --key "$API_KEY"
        success "API key configured"
    else
        info "Skipped. You can set it later with: tokenoptimizer auth set"
    fi
}

verify_installation() {
    info "Verifying installation..."

    if command -v tokenoptimizer &> /dev/null; then
        VERSION=$(tokenoptimizer --version 2>&1)
        success "Installation verified: $VERSION"
    elif $PYTHON_CMD -m tokenoptimizer --version &> /dev/null; then
        VERSION=$($PYTHON_CMD -m tokenoptimizer --version 2>&1)
        success "Installation verified: $VERSION"
        warn "tokenoptimizer is not in PATH. You may need to add ~/.local/bin to your PATH"
        echo ""
        echo "Add this to your ~/.bashrc or ~/.zshrc:"
        echo '  export PATH="$HOME/.local/bin:$PATH"'
    else
        error "Installation verification failed"
    fi
}

print_usage() {
    echo ""
    echo -e "${GREEN}Installation complete!${NC}"
    echo ""
    echo "Quick start:"
    echo "  tokenoptimizer auth set                 # Configure API key"
    echo "  tokenoptimizer \"Your prompt here\"       # Optimize a prompt"
    echo "  echo \"Prompt\" | tokenoptimizer          # Pipe input"
    echo "  tokenoptimizer --aggressive \"Prompt\"   # Maximum compression"
    echo "  tokenoptimizer --help                   # Show all options"
    echo ""
}

main() {
    print_banner
    parse_args "$@"
    check_python
    check_pip
    setup_venv
    install_package
    verify_installation
    setup_auth
    print_usage
}

main "$@"
