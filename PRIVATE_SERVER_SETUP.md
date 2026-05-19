# Configuración de Servidor Privado Local

## Inicio Rápido

### Opción 1: Servidor Python (Recomendado)

```bash
# 1. Ir al directorio del proyecto
cd "bulk ISRC finder"

# 2. Crear un entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el servidor
python3 server.py
```

El servidor estará disponible en: **http://localhost:3000**

### Opción 2: Servidor Node.js

```bash
# 1. Ir al directorio del proyecto
cd "bulk ISRC finder"

# 2. Instalar dependencias
npm install

# 3. Ejecutar el servidor
npm start
```

El servidor estará disponible en: **http://localhost:3000**

## Configuración

### Variables de Entorno (.env.local)

El archivo `.env.local` contiene:
- `PORT`: Puerto del servidor (por defecto 3000)
- `SPOTIFY_CLIENT_ID`: Tu ID de cliente de Spotify
- `SPOTIFY_CLIENT_SECRET`: Tu secreto de cliente de Spotify
- `NODE_ENV`: development (para desarrollo local)

### Acceso Local Seguro

- ✅ El servidor solo es accesible desde tu máquina local (127.0.0.1:3000)
- ✅ No es accesible desde internet
- ✅ Perfecto para desarrollo y pruebas

## Pruebas

### Verificar el servidor

```bash
curl http://localhost:3000/api/health
```

Deberías recibir:
```json
{"status": "ok", "api": "deezer+spotify"}
```

### Probar búsqueda

```bash
curl -X POST http://localhost:3000/api/search-single \
  -H "Content-Type: application/json" \
  -d '{"song": {"title": "Bohemian Rhapsody", "artist": "Queen"}}'
```

## Solución de Problemas

### Puerto 3000 ya en uso

Cambia el puerto en el comando:

**Python:**
```bash
PORT=3001 python3 server.py
```

**Node.js:**
```bash
PORT=3001 npm start
```

### Credenciales de API

Si ves errores de API, verifica:
1. Las credenciales de Spotify en `.env.local`
2. Que tu cliente de Spotify esté activo
3. Tu conexión a internet

## Seguridad

⚠️ Importante:
- Nunca compartas `.env.local` públicamente
- Las credenciales de API solo son para desarrollo
- Este servidor local es solo para pruebas

## Detener el Servidor

Presiona `Ctrl + C` en la terminal para detener el servidor.
