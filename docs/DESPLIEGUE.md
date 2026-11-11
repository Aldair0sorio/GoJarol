# Guía de Despliegue en Producción (Linux Debian) · Go Jarol

Esta guía describe cómo desplegar la plataforma **Go Jarol** en un servidor con **Debian** (versión 11 bullseye o 12 bookworm), cubriendo tanto la arquitectura con **Docker & Docker Compose** (opción recomendada) como la opción **Nativa con Nginx y Systemd**.

---

## 1. Arquitectura de Producción

El sistema se compone de 3 capas principales:
1. **Frontend (React + Vite + Tailwind)**: Empaquetado estático servido mediante **Nginx**.
2. **Backend (Django REST Framework + SymPy + ML)**: Servido a través de **Gunicorn** atendiendo la API en `/api/v1/`.
3. **Base de Datos**: **PostgreSQL**.

```
[ Cliente / Celular / Jurado ]
              │ (HTTP/HTTPS puerto 80 / 443)
              ▼
       [ Nginx (Reverse Proxy) ]
        ├── /              ──▶ Archivos estáticos de React (dist/)
        └── /api/v1/       ──▶ Gunicorn / Django WSGI (puerto 8000)
                                      │
                                      ▼
                                [ PostgreSQL ]
```

---

## Opción A: Despliegue con Docker y Docker Compose (Recomendada)

Permite levantar todo el stack con un solo comando, aislando versiones de Node, Python y PostgreSQL.

### Paso 1: Instalar Docker en Debian
Si el servidor Debian aún no tiene Docker:
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Añadir clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Añadir repositorio
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Permitir ejecutar docker sin sudo (opcional)
sudo usermod -aG docker $USER
newgrp docker
```

---

### Paso 2: Clonar el repositorio y configurar variables de entorno
```bash
cd /opt
sudo git clone https://github.com/Aldair0sorio/GoJarol.git
cd GoJarol

# Crear el archivo de variables a partir del ejemplo
cp .env.example .env
nano .env
```

Variables indispensables en `.env`:
```env
DEBUG=False
SECRET_KEY=tu_clave_secreta_segura_de_produccion
ALLOWED_HOSTS=ip_o_dominio_del_servidor,localhost,127.0.0.1
DATABASE_URL=postgres://jarol_user:jarol_pass@db:5432/gojarol_db
POSTGRES_DB=gojarol_db
POSTGRES_USER=jarol_user
POSTGRES_PASSWORD=jarol_pass
VITE_API_URL=/api/v1
```

---

### Paso 3: Estructura del `docker-compose.yml` (en la raíz)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: gojarol_db
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - gojarol_net

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: gojarol_backend
    restart: always
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
    env_file: .env
    depends_on:
      - db
    networks:
      - gojarol_net

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: gojarol_frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - gojarol_net

volumes:
  postgres_data:

networks:
  gojarol_net:
    driver: bridge
```

---

### Paso 4: Dockerfile del Frontend (`frontend/Dockerfile`)
Usa multi-stage build para que la imagen final sea de menos de 30 MB:
```dockerfile
# Etapa 1: Compilación
FROM node:20-alpine AS build
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Etapa 2: Servidor Web Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Y su archivo de configuración `frontend/nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;

    # Archivos estáticos del frontend React
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Redirección de peticiones al Backend Django
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Caché para assets estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        root /usr/share/nginx/html;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

### Paso 5: Levantar y migrar
```bash
# Construir y levantar contenedores en segundo plano
docker compose up -d --build

# Ejecutar migraciones de base de datos en Django
docker compose exec backend python manage.py migrate

# Cargar fixture de datos iniciales (materias y temas de fracciones)
docker compose exec backend python manage.py loaddata initial_data.json
```

---

## Opción B: Despliegue Nativo en Debian (Sin Docker)

Si el servidor de tu compañero se administra directamente con paquetes nativos:

### 1. Dependencias del sistema
```bash
sudo apt update
sudo apt install -y nginx git python3-venv python3-pip postgresql postgresql-contrib

# Instalar Node.js 20 LTS y pnpm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pnpm
```

### 2. Compilar el Frontend
```bash
cd /var/www/GoJarol/frontend
pnpm install
pnpm build
# Los archivos generados quedan en /var/www/GoJarol/frontend/dist
```

### 3. Configurar Nginx nativo en Debian
Crear el archivo en `/etc/nginx/sites-available/gojarol`:
```nginx
server {
    listen 80;
    server_name _; # O la IP pública / dominio del servidor

    # Frontend estático
    root /var/www/GoJarol/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy hacia Gunicorn (Backend en 127.0.0.1:8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Activar el sitio y reiniciar Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/gojarol /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 3. Verificación de Funcionamiento

Desde la terminal del servidor o un navegador externo:
```bash
# Verificar que Nginx y el backend responden
curl -I http://localhost/
curl http://localhost/api/v1/health/
```
Respuesta esperada: `{"status": "ok"}`.

---

## 4. Notas Clave para el Jurado
- **Cero dependencia externa**: Toda la app corre localmente en la máquina Debian sin requerir conexiones a APIs de OpenAI o servicios externos.
- **Sin pérdida de sesión**: La SPA maneja el enrutamiento con `try_files $uri /index.html` para que si el jurado refresca la pantalla en `/chat` o `/progreso`, no obtenga un error 404.
