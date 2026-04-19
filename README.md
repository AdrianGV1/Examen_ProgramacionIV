# Examen_ProgramacionIV - Modulo de Autenticacion

Documentacion del modulo de autenticacion y seguridad (Google SSO + JWT).

## Requisitos
- Python 3.11+
- SQLite
- Credenciales de Google OAuth

## Instalacion
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracion (.env)
Ejemplo minimo:
```
DATABASE_URL=sqlite:///app.db
SECRET_KEY=dev_secret_key

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

JWT_SECRET_KEY=cambiar-esto-despues

# Solo desarrollo local
OAUTHLIB_INSECURE_TRANSPORT=1
OAUTHLIB_RELAX_TOKEN_SCOPE=1

```

## Ejecucion
```bash
python run.py
```
Servidor: http://127.0.0.1:5000

## Documentación Swagger 
```bash
python run.py
```
Servidor: http://127.0.0.1:5000/openapi/

## Endpoints

## Auth
- `GET /auth/login` inicia el flujo de Google.
- `GET /auth/callback` procesa la respuesta y genera JWT.
- `GET /auth/me` devuelve el usuario autenticado (requiere JWT).

### Radiographs
- `GET /api/v1/records` lista las placas radiográficas(JWT)
- `POST /api/v1/records` crear una nueva placa radiográfica(JWT)
- `DELETE /api/v1/records/{record_id}` elimina una placa radiográfica(JWT)
- `GET /api/v1/records/{record_id}` obtiene una placa por ID (JWT)
- `PUT /api/v1/records/{record_id}` actualiza una placa(JWT)
  
### Uploads
- `POST /api/v1/uploads`  sube una imagen a Cloudinary (JWT)
- `DELETE /api/v1/uploads/{public_id}` elimina una imagen de Cloudinary(JWT)
- `GET /api/v1/uploads/{record_id}/signed` obtiene la URL para la imagen protegida (JWT)

### Users
- `GET /api/v1/users` lista los usuarios (JWT)
- `POST /api/v1/users` crea un usuario (JWT)
- `DELETE /api/v1/users/{record_id}` elimina un usuario (JWT)
- `GET /api/v1/users/{record_id}` obtiene un usuario por ID (JWT)
- `PUT /api/v1/users/{record_id}` actualiza un usuario (JWT)


## Migraciones (SQLite + Alembic)
```bash
flask db upgrade
```

## Flujo de autenticacion (Google SSO + JWT)
1) El usuario inicia sesion en `GET /auth/login`.
2) Google autoriza y redirige a `GET /auth/callback`.
3) La API crea/actualiza el usuario y devuelve un JWT:
```json
{
	"access_token": "<token>",
	"token_type": "Bearer",
	"expires_in": 3600
}
```
4) El JWT se usa en endpoints protegidos con el header:
`Authorization: Bearer <token>`


## Flujo de acceso a imágenes protegidas

Cada día a las 11:59 PM las imágenes pasan a ser privadas en Cloudinary.
Para acceder a una imagen ya ocultada:

1. Llamar a `GET /api/v1/uploads/{record_id}/signed` con JWT.
2. El sistema verifica que la imagen existe y está en estado privado.
3. Se genera una URL firmada de Cloudinary con expiración configurable.
4. Se genera un token extra que identifica al usuario solicitante.
5. La URL es válida solo durante algunos minutos. 

Respuesta:
```json
{
  "record_id": 12,
  "signed_url": "https://api.cloudinary.com/...",
  "access_token": "eyJhbGci...",
  "expires_at": "2026-04-19T21:10:00Z",
  "expires_in_seconds": 600
}
```
## Pruebas rapidas
### Login y token
1) Abrir `GET http://localhost:5000/auth/login`.
2) Completar Google SSO.
3) Copiar `access_token` del JSON.

### Usar token en ruta protegida
```
GET http://localhost:5000/auth/me
Authorization: Bearer <token>
```

### Validacion sin token (debe fallar)
```
GET http://localhost:5000/auth/me
```
Respuesta esperada: `401 Unauthorized`.

## Swagger
La API expone documentacion Swagger via `flask_openapi3`.
Abrir la URL configurada por Flask OpenAPI (por defecto en `http://127.0.0.1:5000/openapi/`).

## Notas de seguridad
- Cambiar `SECRET_KEY` y `JWT_SECRET_KEY` en produccion.
- No usar `OAUTHLIB_INSECURE_TRANSPORT=1` en produccion.
