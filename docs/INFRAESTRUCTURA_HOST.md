# Contexto Maestro de Infraestructura del Servidor Host (VPS Debian)

Este documento define la arquitectura y reglas obligatorias de despliegue para todos los servicios de **Go Jarol** en el servidor de producción.

---

## 1. Arquitectura Base
* **Servidor Host**: VPS con Linux Debian (multi-tenant con usuarios de sistema aislados).
* **Reverse Proxy Principal**: **Nginx nativo en el Host** (puertos públicos 80 y 443). Gestiona dominios y certificados SSL automatizados con **Certbot**.
* **SSL**: Termina en el Nginx nativo del host. Los contenedores de Docker solo sirven tráfico HTTP interno.

---

## 2. Reglas de Puertos y Aislamiento de Red
1. **CERO puertos públicos directos en Docker**: Prohibido usar `ports: - "80:80"` o `ports: - "443:443"` en cualquier archivo compose.
2. **Binding exclusivo al Loopback (`127.0.0.1`)**:
   - Todo servicio que requiera tráfico web debe mapearse únicamente a `127.0.0.1:<puerto_libre>:80`.
   - **Puerto asignado a Go Jarol Frontend**: **`3000`** (`127.0.0.1:3000:80`).
3. **Mapa de Puertos Ocupados en el Host (NO USAR)**:
   - `8000`: API Tonalkab (FastAPI)
   - `8080`: Admin Tonalkab (React)
   - `3000`: **Go Jarol Frontend** (React / Nginx interno)
4. **Aislamiento de Backend y Base de Datos**:
   - Backend Django y PostgreSQL **NUNCA** usan la directiva `ports`.
   - Se comunican exclusivamente a través de la red interna de Docker (`gojarol_net` con driver `bridge`) o mediante `expose: - "8000"` para comunicación inter-contenedor.

---

## 3. Configuración del Virtual Host en el Nginx Nativo del Host
Archivo: `/etc/nginx/sites-available/gojarol` (en el host Debian):
```nginx
server {
    listen 80;
    server_name jarol.tudominio.com; # o subdominio asignado

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activación y certificado SSL en el host:
```bash
sudo ln -s /etc/nginx/sites-available/gojarol /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d jarol.tudominio.com
```

---

## 4. Seguridad de Usuarios y Variables de Entorno
* Sin permisos de root asumidos.
* Volúmenes con nombres gestionados por Docker (`postgres_data`) o rutas relativas (`./data`).
* Cero secretos en Git: todas las credenciales se cargan desde `.env`.
