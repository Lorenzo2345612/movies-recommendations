# 🎬 Sistema de Recomendación de Películas basado en Embeddings

Este proyecto es un sistema de recomendación de películas que utiliza **embeddings** para ofrecer sugerencias personalizadas a los usuarios. El backend está construido con **Python**, usando **FastAPI** como framework principal, y almacena vectores en **Qdrant** y metadatos en **PostgreSQL**. El frontend está hecho en **React + Vite**. Todo el sistema está desplegado en la nube mediante **Railway**.

---

## 🚀 Tecnologías Utilizadas

- 🐍 **Python** + **FastAPI** - Backend de la API
- 🧠 **Qdrant** - Almacenamiento de vectores y búsqueda por similitud
- 🐘 **PostgreSQL** - Base de datos relacional para películas y usuarios
- ⚛️ **React + Vite** - Frontend moderno y rápido
- ☁️ **Railway** - Plataforma de despliegue

---

## 📦 Estructura del Proyecto

/backend → API en FastAPI + conexión con Qdrant y PostgreSQL
/frontend → Interfaz hecha en React (Vite)

## ⚙️ Despliegue

Este proyecto está diseñado para desplegarse fácilmente en Railway en **tres etapas**:

### 1️⃣ Levantar servicios en Railway

Primero debes levantar los siguientes servicios como proyectos independientes en Railway:

- **PostgreSQL Database**
- **Qdrant (vector database)**
- **Backend (FastAPI)**
- **Frontend (React + Vite)**

Puedes hacerlo importando directamente desde GitHub o conectando Railway con tu repositorio. Asegúrate de definir las siguientes variables de entorno:

#### Variables del backend (`.env`)

```env
DATABASE_URL=postgresql://<usuario>:<contraseña>@<host>:<puerto>/<nombre_db>
QDRANT_URL=http://<host_qdrant>:<puerto>
TMDB_API_KEY=<tu_api_key_tmdb>
```

#### Variables del frontend (`.env`)

```env
VITE_API_URL=http://<host_backend>:<puerto>
```

### 2️⃣ Cargar datos de películas

Para cargar los datos de películas se necesitan ejecutar los siguientes scripts en el backend:

```bash
python generate_json_movies.py
python upload_to_postgres.py
python upload_to_qdrant.py
```

## 🔧 Instalación y Ejecución Local

1.- Clona el repositorio:

```bash
git clone https://github.com/Lorenzo2345612/movies-recommendations
cd movies-recommendations
```

2.- Instala las dependencias del backend:

```bash
cd backend
pip install -r requirements.txt
```

3.- Instala las dependencias del frontend:

```bash
cd frontend
npm install
```

4.- Configura las variables de entorno en el backend:
Crea un archivo `.env` en la carpeta `backend` con las variables necesarias (ver sección de despliegue).

5.- Ejecuta el backend:

```bash
uvicorn main:app --reload
```

6.- Ejecuta el frontend:

```bash
npm run dev
```

7.- Ejecutar el script para cargar los datos de películas:

```bash
python generate_json_movies.py
python upload_to_postgres.py
python upload_to_qdrant.py
```

8.- Abre tu navegador y ve a `http://localhost:5173` para ver la aplicación en acción.

## 📝 TMDB

This product uses the TMDB API but is not endorsed or certified by TMDB.
