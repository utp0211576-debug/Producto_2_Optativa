"""
Módulo principal de la aplicación web FriendlyEats (FastAPI + Jinja2 + Firestore).

Define la configuración inicial de FastAPI, la conexión directa a Cloud Firestore,
el montaje de archivos estáticos y todas las rutas web (HTML) para listar, crear,
ver detalles, editar y eliminar restaurantes.
"""

import json
import os
from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from google.cloud import firestore

from app.api.v1.restaurants import router as restaurants_api_router

# ==============================================================================
# 1. CONFIGURACIÓN DE CREDENCIALES Y CONEXIÓN A FIRESTORE
# ==============================================================================

# Limpiar variable de entorno del emulador local para forzar conexión a la nube
if "FIRESTORE_EMULATOR_HOST" in os.environ:
    del os.environ["FIRESTORE_EMULATOR_HOST"]

# Cargar credenciales de cuenta de servicio de Firebase si el archivo existe
CREDENTIALS_FILE = os.path.abspath("serviceAccountKey.json")
if os.path.exists(CREDENTIALS_FILE):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        key_data = json.load(f)
        project_id = key_data.get("project_id", "basedatos-97124")
else:
    project_id = "basedatos-97124"

# Inicializar cliente de Cloud Firestore
db = firestore.Client(project=project_id)

# ==============================================================================
# 2. INICIALIZACIÓN DE FASTAPI, ESTÁTICOS Y PLANTILLAS
# ==============================================================================

app = FastAPI(
    title="FriendlyEats API & Web",
    description="Aplicación web y API REST para gestión de restaurantes con FastAPI y Firebase Firestore.",
    version="1.0.0"
)

# Montar carpeta de recursos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar motor de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

# Registrar endpoints REST (v1) bajo el prefijo /api/v1
app.include_router(restaurants_api_router, prefix="/api/v1")

# URL de imagen por defecto cuando el usuario no proporciona fotografía
DEFAULT_PHOTO_URL = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600"


# ==============================================================================
# 3. RUTAS WEB (VISTAS HTML / CRUD DE RESTAURANTES)
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
def read_restaurants(
    request: Request,
    city: str = Query(None, description="Filtro opcional por ciudad"),
    category: str = Query(None, description="Filtro opcional por categoría gastronómica"),
    price: str = Query(None, description="Filtro opcional por rango de precio (1 a 4)")
):
    """Renderiza el catálogo principal de restaurantes con soporte para filtros.

    Args:
        request (Request): Objeto de petición HTTP requerido por Jinja2.
        city (str, optional): Nombre de la ciudad a filtrar.
        category (str, optional): Categoría de comida a filtrar.
        price (str, optional): Nivel de precio en formato cadena ('1' a '4').

    Returns:
        HTMLResponse: Página principal renderizada (`restaurants.html`).
    """
    query = db.collection("restaurants")

    # Aplicar filtros dinámicos si fueron enviados en la URL
    if city and city.strip():
        query = query.where("city", "==", city.strip())
    if category and category.strip():
        query = query.where("category", "==", category.strip())
    if price and price.strip() and price.isdigit():
        query = query.where("price", "==", int(price))

    docs = query.stream()
    restaurants = [dict(doc.to_dict(), id=doc.id) for doc in docs]

    return templates.TemplateResponse(
        request=request,
        name="restaurants.html",
        context={
            "restaurants": restaurants,
            "selected_city": city or "",
            "selected_category": category or "",
            "selected_price": price or ""
        }
    )


@app.get("/restaurants/new", response_class=HTMLResponse)
def show_create_form(request: Request):
    """Muestra el formulario HTML para registrar un nuevo restaurante.

    Args:
        request (Request): Objeto de petición HTTP.

    Returns:
        HTMLResponse: Vista del formulario de creación (`restaurant_form.html`).
    """
    return templates.TemplateResponse(
        request=request,
        name="restaurant_form.html",
        context={}
    )


@app.post("/restaurants/new")
def create_restaurant(
    name: str = Form(..., description="Nombre del restaurante"),
    category: str = Form(..., description="Categoría gastronómica"),
    city: str = Form(..., description="Ciudad donde se ubica"),
    price: int = Form(..., description="Nivel de precio (1 a 4)"),
    photo: str = Form(None, description="URL opcional de la fotografía")
):
    """Procesa el formulario de creación y guarda el nuevo restaurante en Firestore.

    Args:
        name (str): Nombre del establecimiento.
        category (str): Tipo de cocina o categoría.
        city (str): Ciudad del establecimiento.
        price (int): Escala de precio entre 1 y 4.
        photo (str, optional): Enlace a la imagen; usa una por defecto si está vacío.

    Returns:
        RedirectResponse: Redirección al inicio (código 303 See Other).
    """
    new_data = {
        "name": name.strip(),
        "category": category.strip(),
        "city": city.strip(),
        "price": int(price),
        "photo": photo.strip() if photo and photo.strip() else DEFAULT_PHOTO_URL,
        "numRatings": 0,
        "avgRating": 5.0
    }

    db.collection("restaurants").add(new_data)
    return RedirectResponse(url="/", status_code=303)


@app.get("/restaurants/{restaurant_id}", response_class=HTMLResponse)
def show_restaurant_detail(request: Request, restaurant_id: str):
    """Muestra la ficha detallada de un restaurante junto con sus reseñas.

    Args:
        request (Request): Objeto de petición HTTP.
        restaurant_id (str): Identificador único del documento en Firestore.

    Returns:
        HTMLResponse | RedirectResponse: Vista de detalle (`restaurant_detail.html`)
        o redirección al inicio si el restaurante no existe.
    """
    doc_ref = db.collection("restaurants").document(restaurant_id)
    doc = doc_ref.get()

    if not doc.exists:
        return RedirectResponse(url="/", status_code=303)

    restaurant_data = doc.to_dict()
    restaurant_data["id"] = doc.id

    # Obtener reseñas de la subcolección 'ratings'
    ratings_docs = doc_ref.collection("ratings").stream()
    ratings = [r.to_dict() for r in ratings_docs]

    return templates.TemplateResponse(
        request=request,
        name="restaurant_detail.html",
        context={
            "restaurant": restaurant_data,
            "ratings": ratings
        }
    )


@app.get("/restaurants/{restaurant_id}/edit", response_class=HTMLResponse)
def show_edit_form(request: Request, restaurant_id: str):
    """Muestra el formulario de edición precargado con los datos actuales del restaurante.

    Args:
        request (Request): Objeto de petición HTTP.
        restaurant_id (str): Identificador único del documento en Firestore.

    Returns:
        HTMLResponse | RedirectResponse: Vista de edición (`restaurants_edit.html`)
        o redirección al inicio si el restaurante no existe.
    """
    doc_ref = db.collection("restaurants").document(restaurant_id)
    doc = doc_ref.get()

    if not doc.exists:
        return RedirectResponse(url="/", status_code=303)

    restaurant_data = doc.to_dict()
    restaurant_data["id"] = doc.id

    # CORREGIDO: El archivo en app/templates/ se llama 'restaurants_edit.html' (plural)
    return templates.TemplateResponse(
        request=request,
        name="restaurants_edit.html",
        context={"restaurant": restaurant_data}
    )


@app.post("/restaurants/{restaurant_id}/edit")
def update_restaurant(
    restaurant_id: str,
    name: str = Form(..., description="Nombre actualizado"),
    category: str = Form(..., description="Categoría actualizada"),
    city: str = Form(..., description="Ciudad actualizada"),
    price: int = Form(..., description="Nivel de precio actualizado (1 a 4)"),
    photo: str = Form(None, description="URL de foto actualizada")
):
    """Guarda los cambios editados de un restaurante existente en Firestore.

    Args:
        restaurant_id (str): ID del restaurante a modificar.
        name (str): Nuevo nombre.
        category (str): Nueva categoría.
        city (str): Nueva ciudad.
        price (int): Nuevo nivel de precio.
        photo (str, optional): Nueva URL de fotografía.

    Returns:
        RedirectResponse: Redirección al inicio con parámetro `?updated=true`.
    """
    doc_ref = db.collection("restaurants").document(restaurant_id)
    if not doc_ref.get().exists:
        return RedirectResponse(url="/", status_code=303)

    updated_data = {
        "name": name.strip(),
        "category": category.strip(),
        "city": city.strip(),
        "price": int(price),
        "photo": photo.strip() if photo and photo.strip() else DEFAULT_PHOTO_URL
    }

    doc_ref.update(updated_data)
    return RedirectResponse(url="/?updated=true", status_code=303)


@app.post("/restaurants/{restaurant_id}/delete")
def delete_restaurant(restaurant_id: str):
    """Elimina un restaurante (y sus reseñas asociadas) de Firestore.

    Nota: Se utiliza el método POST porque los formularios HTML nativos solo
    soportan GET y POST.

    Args:
        restaurant_id (str): ID del restaurante a eliminar.

    Returns:
        RedirectResponse: Redirección al inicio con parámetro `?deleted=true`.
    """
    doc_ref = db.collection("restaurants").document(restaurant_id)
    doc = doc_ref.get()

    if doc.exists:
        # Eliminar primero documentos de la subcolección 'ratings' para evitar huérfanos
        for rating in doc_ref.collection("ratings").stream():
            rating.reference.delete()

        # Eliminar el documento principal del restaurante
        doc_ref.delete()

    return RedirectResponse(url="/?deleted=true", status_code=303)