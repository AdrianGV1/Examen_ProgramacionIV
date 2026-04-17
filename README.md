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

## Endpoints de auth
- `GET /auth/login` inicia el flujo de Google.
- `GET /auth/callback` procesa la respuesta y genera JWT.
- `GET /auth/me` devuelve el usuario autenticado (requiere JWT).

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
Abrir la URL configurada por Flask OpenAPI (por defecto en `/openapi/swagger`).

## Notas de seguridad
- Cambiar `SECRET_KEY` y `JWT_SECRET_KEY` en produccion.
- No usar `OAUTHLIB_INSECURE_TRANSPORT=1` en produccion.
