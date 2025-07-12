# Etapa 1: Build de la aplicación
FROM node:20-alpine AS builder

# Crear directorio de trabajo
WORKDIR /app

RUN ls

# Copiar package.json y lockfile
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias
RUN npm install

# Copiar el resto del proyecto
COPY . .

# Construir el proyecto
RUN npm run build

# Etapa 2: Servir con nginx
FROM nginx:alpine

# Eliminar la configuración por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*

# Copiar archivos estáticos del build anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx (opcional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Arrancar nginx
CMD ["nginx", "-g", "daemon off;"]