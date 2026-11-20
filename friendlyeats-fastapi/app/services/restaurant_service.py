"""
Capa de lógica de negocio (Service) para la gestión de restaurantes.

Coordina las validaciones de dominio, transforma los esquemas Pydantic a diccionarios
y gestiona las excepciones HTTP adecuadas cuando un recurso no existe o la petición
es inválida.
"""

from fastapi import HTTPException
from app.repositories.restaurant_repository import RestaurantRepository
from app.domain.schemas import RestaurantCreate, RestaurantUpdate


class RestaurantService:
    """Servicio que implementa las reglas de negocio sobre restaurantes."""

    def __init__(self):
        """Inicializa el servicio instanciando su repositorio de datos."""
        self.repository = RestaurantRepository()

    def create(self, payload: RestaurantCreate) -> dict:
        """Registra un nuevo restaurante.

        Args:
            payload (RestaurantCreate): Datos validados del nuevo restaurante.

        Returns:
            dict: Restaurante recién creado con su ID asignado.
        """
        return self.repository.create(payload.model_dump())

    def get(self, restaurant_id: str) -> dict:
        """Recupera un restaurante por su ID o lanza error 404 si no existe.

        Args:
            restaurant_id (str): Identificador del restaurante.

        Raises:
            HTTPException: 404 si el restaurante no se encuentra en la base de datos.

        Returns:
            dict: Información del restaurante solicitado.
        """
        restaurant = self.repository.get(restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
        return restaurant

    def list(
        self,
        category: str | None = None,
        city: str | None = None,
        price: int | None = None,
        order_by: str = "name",
        limit: int = 20,
        start_after: str | None = None
    ) -> list[dict]:
        """Obtiene una lista filtrada y paginada de restaurantes.

        Args:
            category (str, optional): Categoría a filtrar.
            city (str, optional): Ciudad a filtrar.
            price (int, optional): Nivel de precio a filtrar.
            order_by (str): Campo de ordenamiento.
            limit (int): Límite de registros a retornar.
            start_after (str, optional): Cursor de paginación.

        Returns:
            list[dict]: Colección de restaurantes encontrados.
        """
        return self.repository.list(
            category=category,
            city=city,
            price=price,
            order_by=order_by,
            limit=limit,
            start_after=start_after
        )

    def update(self, restaurant_id: str, payload: RestaurantUpdate) -> dict:
        """Actualiza parcialmente un restaurante existente.

        Args:
            restaurant_id (str): Identificador del restaurante a editar.
            payload (RestaurantUpdate): Campos opcionales a actualizar.

        Raises:
            HTTPException: 400 si no se envió ningún campo para actualizar.
            HTTPException: 404 si el restaurante no existe.

        Returns:
            dict: Datos actualizados del restaurante.
        """
        data = payload.model_dump(exclude_unset=True)
        if not data:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        restaurant = self.repository.update(restaurant_id, data)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
        return restaurant

    def delete(self, restaurant_id: str) -> None:
        """Elimina un restaurante por su ID.

        Args:
            restaurant_id (str): Identificador del restaurante a borrar.

        Raises:
            HTTPException: 404 si el restaurante no existe.
        """
        deleted = self.repository.delete(restaurant_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")