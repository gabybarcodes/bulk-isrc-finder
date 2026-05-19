#!/bin/bash

# Script para iniciar el servidor privado local

echo "🚀 Iniciando servidor privado ISRC Finder..."
echo ""

# Verificar si Python está disponible
if command -v python3 &> /dev/null; then
    echo "✅ Python3 detectado"
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        echo "📦 Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Instalar dependencias
    echo "📥 Instalando dependencias..."
    pip install -q -r requirements.txt
    
    echo ""
    echo "✨ Servidor iniciado en: http://localhost:3000"
    echo "🛑 Para detener: Ctrl + C"
    echo ""
    
    # Ejecutar servidor
    python3 server.py
else
    echo "❌ Python3 no encontrado"
    echo "Por favor instala Python3"
    exit 1
fi
