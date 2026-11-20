"""
Esquemas de validación y serialización de datos (Pydantic) para restaurantes.

Define los contratos de entrada y salida utilizados por la API REST (v1)
y la capa de servicios para validar tipos, longitudes y rangos permitidos.
"""

from pydantic import BaseModel, Field


class RestaurantBase(BaseModel):
    """Atributos base compartidos por los esquemas de restaurante."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre comercial del restaurante."
    )
    category: str = Field(
        min_length=1,
        max_length=50,
        description="Categoría culinaria (ej. Italiana, Mexicana, Sushi)."
    )
    city: str = Field(
        min_length=1,
        max_length=50,
        description="Ciudad donde se encuentra el establecimiento."
    )
    price: int = Field(
        ge=1,
        le=4,
        description="Rango de precio del 1 ($) al 4 ($$$$)."
    )
    photoUrl: str | None = Field(
        default=None,
        description="URL opcional de la fotografía del restaurante."
    )


class RestaurantCreate(RestaurantBase):
    """Esquema requerido para crear un nuevo restaurante vía API."""
    pass


class RestaurantUpdate(BaseModel):
    """Esquema para actualizaciones parciales (PATCH) de un restaurante.

    Todos los campos son opcionales; solo se modificarán aquellos enviados
    explícitamente en el cuerpo de la petición.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None, ge=1, le=4)
    photoUrl: str | None = None


class RestaurantResponse(RestaurantBase):
    """Esquema de respuesta que incluye metadatos generados por el sistema."""

    id: str = Field(description="Identificador único del documento en Firestore.")
    avgRating: float = Field(default=0.0, description="Promedio de calificaciones.")
    numRatings: int = Field(default=0, description="Cantidad total de reseñas recibidas.")