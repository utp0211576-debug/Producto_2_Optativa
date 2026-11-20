"""
Controlador de endpoints REST (API v1) para el recurso 'Restaurants'.

Expone operaciones HTTP estándar (GET, POST, PATCH, DELETE) en formato JSON,
delegando la lógica de negocio a `RestaurantService`.
"""

from fastapi import APIRouter, Query
from app.services.restaurant_service import RestaurantService
from app.domain.schemas import RestaurantCreate, RestaurantUpdate

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])
service = RestaurantService()


@router.get("", summary="Listar restaurantes")
async def list_restaurants(
    category: str | None = Query(default=None, description="Filtrar por categoría"),
    city: str | None = Query(default=None, description="Filtrar por ciudad"),
    price: int | None = Query(default=None, ge=1, le=4, description="Filtrar por precio (1-4)"),
    order_by: str = Query(default="name", description="Campo para ordenar resultados"),
    limit: int = Query(default=20, ge=1, le=100, description="Cantidad máxima de resultados"),
    start_after: str | None = Query(default=None, description="ID del último documento para paginar")
):
    """Retorna el listado de restaurantes en JSON aplicando filtros y paginación."""
    return service.list(
        category=category,
        city=city,
        price=price,
        order_by=order_by,
        limit=limit,
        start_after=start_after
    )


@router.get("/{restaurant_id}", summary="Obtener detalle de un restaurante")
async def get_restaurant(restaurant_id: str):
    """Retorna la información de un restaurante específico mediante su ID."""
    return service.get(restaurant_id)


@router.post("", status_code=201, summary="Crear restaurante")
async def create_restaurant(payload: RestaurantCreate):
    """Crea un nuevo restaurante a partir de un payload JSON validado."""
    return service.create(payload)


@router.patch("/{restaurant_id}", summary="Actualizar restaurante")
async def update_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    """Actualiza parcialmente los datos de un restaurante existente."""
    return service.update(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=204, summary="Eliminar restaurante")
async def delete_restaurant(restaurant_id: str):
    """Elimina permanentemente un restaurante por su ID."""
    service.delete(restaurant_id)