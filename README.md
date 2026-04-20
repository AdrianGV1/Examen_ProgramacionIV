# Examen_ProgramacionIV - API de placas radiograficas

## Requisitos
- Python 3.11+
- SQLite
- Credenciales de Google OAuth
- Cuenta Cloudinary

## Arquitectura
El proyecto esta organizado por capas:
- Routers: endpoints HTTP
- Services: logica de negocio
- Repositories: acceso a base de datos
- Schemas: validacion y respuestas con Pydantic

## Instalacion local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracion de entorno
Variables minimas para ejecutar:

```
DATABASE_URL=sqlite:///app.db
SECRET_KEY=dev_secret_key
JWT_SECRET_KEY=dev_jwt_secret

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

UPLOAD_FOLDER=radiografias
UPLOAD_MAX_FILE_SIZE_MB=5
UPLOAD_ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

SIGNED_IMAGE_URL_EXPIRES_MINUTES=10
IMAGE_HIDE_TIMEZONE=America/Costa_Rica
ENABLE_DAILY_HIDE_SCHEDULER=true
```

Solo para desarrollo local:
```
OAUTHLIB_INSECURE_TRANSPORT=1
OAUTHLIB_RELAX_TOKEN_SCOPE=1
DEBUG=true
```

## Ejecucion
```bash
python run.py
```
Servidor local: http://127.0.0.1:5000

## Swagger
Documentacion: http://127.0.0.1:5000/openapi/

## Endpoints principales

### Auth
- `GET /auth/login` inicia el flujo de Google SSO.
- `GET /auth/callback` retorna el JWT.
- `GET /auth/me` retorna el usuario autenticado (requiere JWT).

### Radiographs
- `GET /api/v1/records` lista registros con filtros y paginacion (JWT).
- `POST /api/v1/records` crea un registro (JWT).
- `GET /api/v1/records/{record_id}` obtiene un registro (JWT).
- `PUT /api/v1/records/{record_id}` actualiza un registro (JWT).
- `DELETE /api/v1/records/{record_id}` elimina un registro (JWT).
- `GET /api/v1/records/{record_id}/signed-image-url` obtiene URL firmada (JWT).

### Uploads
- `POST /api/v1/uploads` sube una imagen a Cloudinary (JWT).
- `DELETE /api/v1/uploads/{public_id}` elimina una imagen en Cloudinary (JWT).
- `GET /api/v1/uploads/{record_id}/signed` genera URL firmada alternativa (JWT).

### Users
- `GET /api/v1/users` lista usuarios (JWT).
- `POST /api/v1/users` crea un usuario (JWT).
- `GET /api/v1/users/{record_id}` obtiene un usuario (JWT).
- `PUT /api/v1/users/{record_id}` actualiza un usuario (JWT).
- `DELETE /api/v1/users/{record_id}` elimina un usuario (JWT).

## Migraciones
```bash
flask --app run.py db upgrade
```

## Flujo de autenticacion (Google SSO + JWT)
1) Ingresar a `GET /auth/login`.
2) Google autoriza y redirige al callback.
3) La API crea o actualiza el usuario y retorna:
```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```
4) Usar el token en el header:
```
Authorization: Bearer <token>
```

## Registro de pacientes (campos minimos)
Cada placa radiografica se guarda como un registro con datos del paciente. Campos minimos:
- `patient_name`
- `patient_id_number`
- `clinical_reference`
- `study_date`
- `image_public_id`
- `image_url`

Ejemplo de creacion:
```json
{
  "patient_name": "Juan Perez",
  "patient_id_number": "1-1234-5678",
  "clinical_reference": "Dolor toracico",
  "study_date": "2026-04-19",
  "image_public_id": "radiografias/abc123",
  "image_url": "https://res.cloudinary.com/.../image/upload/v1/radiografias/abc123.jpg"
}
```

## Ejemplos rapidos (POSTMAN o cURL)

### 1) Subir imagen
```
POST /api/v1/uploads
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <archivo.jpg>
```

Respuesta ejemplo:
```json
{
  "url": "https://res.cloudinary.com/.../image/upload/v1/radiografias/abc123.jpg",
  "public_id": "radiografias/abc123"
}
```

### 2) Crear registro
```
POST /api/v1/records
Authorization: Bearer <token>
Content-Type: application/json
```
Body:
```json
{
  "patient_name": "Juan Perez",
  "patient_id_number": "1-1234-5678",
  "clinical_reference": "Dolor toracico",
  "study_date": "2026-04-19",
  "image_public_id": "radiografias/abc123",
  "image_url": "https://res.cloudinary.com/.../image/upload/v1/radiografias/abc123.jpg"
}
```

### 3) Listar registros
```
GET /api/v1/records?page=1&page_size=10
Authorization: Bearer <token>
```

### 4) Actualizar registro
```
PUT /api/v1/records/{record_id}
Authorization: Bearer <token>
Content-Type: application/json
```
Body:
```json
{
  "clinical_reference": "Control anual",
  "study_date": "2026-04-20"
}
```

### 5) Eliminar registro
```
DELETE /api/v1/records/{record_id}
Authorization: Bearer <token>
```

### 6) Obtener URL firmada
```
GET /api/v1/records/{record_id}/signed-image-url?expires_minutes=10
Authorization: Bearer <token>
```

## Flujo de imagenes protegidas 
Cada dia a las 23:59, el scheduler marca las imagenes como privadas en Cloudinary. Para acceder a una imagen oculta:

1) `GET /api/v1/records/{record_id}/signed-image-url?expires_minutes=10`
2) La API genera un token extra por usuario y una URL firmada temporal.
3) La URL expira en el tiempo configurado.

Respuesta ejemplo:
```json
{
  "record_id": 12,
  "signed_url": "https://res.cloudinary.com/...",
  "access_token": "eyJhbGci...",
  "expires_at": "2026-04-19T21:10:00Z",
  "expires_in_seconds": 600
}
```

## Probar el sistema (pasos para probar)
1) Login: https://examen-programacioniv.onrender.com/auth/login
2) Copiar `access_token` del JSON.
3) Usar header `Authorization: Bearer <token>`.
4) Subir imagen: `POST /api/v1/uploads` (form-data, key `file`).
5) Crear registro: `POST /api/v1/records` con `image_public_id` y `image_url`.
6) Listar: `GET /api/v1/records`.
7) Detalle: `GET /api/v1/records/{id}`.
8) URL firmada: `GET /api/v1/records/{id}/signed-image-url?expires_minutes=10`.

Nota: la raiz `/` devuelve 404 porque es solo API. El ingreso se hace por los endpoints.

## Despliegue en Render
Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
flask --app run.py db upgrade && gunicorn -w 2 -b 0.0.0.0:$PORT run:app
```

Redirect URI de Google OAuth:
```
https://examen-programacioniv.onrender.com/auth/google/authorized
```
 
