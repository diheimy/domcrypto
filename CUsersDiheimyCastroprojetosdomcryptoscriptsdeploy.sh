#!/bin/bash
# Script de Deploy - DomCrypto
# Uso: ./scripts/deploy.sh

set -e

echo "🚀 Deploy DomCrypto"
echo "=================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_dependencies() {
    log_info "Verificando dependências..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker não encontrado."
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não encontrado."
        exit 1
    fi
    log_info "Docker e Docker Compose OK"
}

check_env() {
    if [ ! -f ".env" ]; then
        log_warn ".env não encontrado. Copiando .env.example..."
        cp .env.example .env
        log_warn "Edite .env com suas configurações."
        exit 1
    fi
    log_info ".env encontrado."
}

build() {
    log_info "Construindo containers..."
    docker-compose build --no-cache
    log_info "Build realizado!"
}

up() {
    log_info "Subindo serviços..."
    docker-compose up -d
    sleep 5
    log_info "Serviços subidos!"
}

health_check() {
    log_info "Verificando health checks..."
    sleep 10
    curl -s http://localhost:8000/health > /dev/null && log_info "Backend: OK" || log_warn "Backend: Aguardando..."
    curl -s http://localhost:3000/health > /dev/null && log_info "Frontend: OK" || log_warn "Frontend: Aguardando..."
}

down() {
    log_info "Parando serviços..."
    docker-compose down
    log_info "Serviços parados!"
}

status() {
    log_info "Status dos serviços:"
    docker-compose ps
}

case "${1:-up}" in
    build) check_dependencies && check_env && build ;;
    up) check_dependencies && check_env && build && up && health_check && log_info "✅ Acesse: http://localhost:3000" ;;
    down) down ;;
    restart) docker-compose restart && log_info "Reiniciado!" ;;
    status) status ;;
    logs) docker-compose logs -f ;;
    *) echo "Uso: $0 {build|up|down|restart|status|logs}" && exit 1 ;;
esac
