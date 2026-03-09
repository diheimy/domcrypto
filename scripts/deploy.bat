@echo off
REM Script de Deploy - DomCrypto (Windows)
REM Uso: scripts\deploy.bat [build^|up^|down^|restart^|status^|logs^|health]

setlocal enabledelayedexpansion

set "GREEN=[INFO]"
set "RED=[ERRO]"
set "YELLOW=[AVISO]"

echo.
echo ====================================
echo   DomCrypto - Deploy Script
echo ====================================
echo.

REM Verificar Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% Docker nao encontrado. Instale Docker Desktop primeiro.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% Docker Compose nao encontrado. Instale Docker Desktop.
    exit /b 1
)

echo %GREEN% Docker: instalado
echo %GREEN% Docker Compose: instalado
echo.

REM Verificar .env
if not exist ".env" (
    echo %YELLOW% .env nao encontrado. Copiando .env.example...
    copy .env.example .env
    echo %YELLOW% Edite .env com suas configuracoes antes de continuar.
    echo.
    pause
    exit /b 1
)

echo %GREEN% .env: encontrado
echo.

REM Comandos
if "%1"=="build" goto :build
if "%1"=="up" goto :up
if "%1"=="down" goto :down
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="health" goto :health

:default
echo Comandos disponiveis:
echo   build   - Constroi containers
echo   up      - Build + up + health check
echo   down    - Para serviços
echo   restart - Reinicia serviços
echo   status  - Mostra status
echo   logs    - Mostra logs
echo   health  - Verifica health checks
echo.
goto :end

:build
echo %GREEN% Construindo containers...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo %RED% Falha no build!
    exit /b 1
)
echo %GREEN% Build concluído!
goto :end

:up
echo %GREEN% Subindo serviços...
call :build
docker-compose up -d
timeout /t 10 /nobreak >nul
echo.
echo %GREEN% Verificando saúde dos serviços...
call :health
echo.
echo %GREEN% Deploy concluído!
echo %GREEN% Acesse: http://localhost:3000
goto :end

:down
echo %GREEN% Parando serviços...
docker-compose down
echo %GREEN% Serviços parados!
goto :end

:restart
echo %GREEN% Reiniciando serviços...
docker-compose restart
echo %GREEN% Serviços reiniciados!
goto :end

:status
echo %GREEN% Status dos serviços:
docker-compose ps
goto :end

:logs
echo %GREEN% Logs (Ctrl+C para sair):
docker-compose logs -f
goto :end

:health
echo %GREEN% Health checks:
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   Backend: OK
) else (
    echo   Backend: Aguardando...
)
curl -s http://localhost:3000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   Frontend: OK
) else (
    echo   Frontend: Aguardando...
)
goto :end

:end
endlocal
