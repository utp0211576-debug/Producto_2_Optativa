# 🍔 FriendlyEats — Gestión de Restaurantes con FastAPI y Cloud Firestore

Aplicación web y API REST desarrollada en **Python** con **FastAPI**, **Jinja2** y **Google Cloud Firestore** que permite gestionar un catálogo de restaurantes mediante operaciones CRUD completas (Crear, Leer, Actualizar y Eliminar), filtrado dinámico por ciudad, categoría y rango de precios, además de visualización de reseñas.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.13, FastAPI, Uvicorn
* **Base de Datos:** Firebase / Google Cloud Firestore
* **Frontend (Vistas):** HTML5, CSS3, JavaScript y plantillas Jinja2
* **Validación de Datos:** Pydantic v2
* **Pruebas:** Pytest

---

## 📂 Estructura del Proyecto

```text
friendlyeats-fastapi/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── restaurants.py          # Endpoints REST (GET, POST, PATCH, DELETE)
│   ├── core/
│   │   ├── config.py                   # Configuración general de la aplicación
│   │   └── firebase.py                 # Inicialización del cliente de Firestore
│   ├── domain/
│   │   ├── models.py                   # Abstracciones de dominio
│   │   └── schemas.py                  # Esquemas Pydantic de validación
│   ├── repositories/
│   │   └── restaurant_repository.py    # Acceso a datos y consultas en Firestore
│   ├── services/
│   │   └── restaurant_service.py       # Lógica de negocio y manejo de excepciones
│   ├── templates/
│   │   ├── base.html                   # Plantilla base HTML
│   │   ├── restaurants.html            # Catálogo principal con filtros y acciones
│   │   ├── restaurant_detail.html      # Vista de detalle y reseñas del restaurante
│   │   ├── restaurant_form.html        # Formulario de registro de nuevo restaurante
│   │   └── restaurants_edit.html       # Formulario de edición de restaurante
│   └── main.py                         # Punto de entrada de la app y rutas web HTML
├── scripts/
│   └── seed.py                         # Script para poblar datos iniciales en Firestore
├── static/
│   ├── css/styles.css                  # Hojas de estilo personalizadas
│   ├── js/app.js                       # Lógica auxiliar en el cliente
│   └── img/                            # Recursos gráficos
├── tests/
│   └── test_restaurant.py              # Pruebas automatizadas con Pytest
├── firebase.json                       # Configuración de Firebase
├── firestore.rules                     # Reglas de seguridad de Firestore
├── firestore.indexes.json              # Índices compuestos de Firestore
├── requeriments.txt                    # Dependencias del proyecto
└── README.md                           # Documentación del proyecto