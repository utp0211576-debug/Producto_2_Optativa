"""
Capa de acceso a datos (Repository) para la colección 'restaurants' en Firestore.

Encapsula todas las operaciones CRUD y consultas filtradas/paginadas contra
la base de datos NoSQL, aislando la lógica de negocio de los detalles de Firestore.
"""

from google.cloud.firestore_v1.base_query import FieldFilter
from app.core.firebase import db


class RestaurantRepository:
    """Repositorio encargado de la persistencia de restaurantes en Cloud Firestore."""

    def __init__(self):
        """Inicializa la referencia a la colección principal 'restaurants'."""
        self.collection = db.collection("restaurants")

    def create(self, data: dict) -> dict:
        """Crea un nuevo documento de restaurante con valores iniciales de calificación.

        Args:
            data (dict): Diccionario con los campos validados del restaurante.

        Returns:
            dict: Datos guardados incluyendo el `id` autogenerado por Firestore.
        """
        ref = self.collection.document()
        data["id"] = ref.id
        data["avgRating"] = 0.0
        data["numRatings"] = 0
        ref.set(data)
        return data

    def get(self, restaurant_id: str) -> dict | None:
        """Obtiene un restaurante por su identificador único.

        Args:
            restaurant_id (str): ID del documento en Firestore.

        Returns:
            dict | None: Diccionario con los datos e ID del restaurante, o `None` si no existe.
        """
        doc = self.collection.document(restaurant_id).get()
        if not doc.exists:
            return None
        return doc.to_dict() | {"id": doc.id}

    def list(
        self,
        category: str | None = None,
        city: str | None = None,
        price: int | None = None,
        order_by: str = "name",
        limit: int = 20,
        start_after: str | None = None
    ) -> list[dict]:
        """Lista restaurantes aplicando filtros opcionales, ordenamiento y paginación por cursor.

        Args:
            category (str, optional): Filtro exacto por categoría.
            city (str, optional): Filtro exacto por ciudad.
            price (int, optional): Filtro exacto por nivel de precio.
            order_by (str): Campo por el cual ordenar los resultados (por defecto 'name').
            limit (int): Número máximo de documentos a devolver.
            start_after (str, optional): ID del último documento recibido para paginación.

        Returns:
            list[dict]: Lista de restaurantes que coinciden con los criterios.
        """
        query = self.collection
        if category:
            query = query.where(filter=FieldFilter("category", "==", category))
        if city:
            query = query.where(filter=FieldFilter("city", "==", city))
        if price:
            query = query.where(filter=FieldFilter("price", "==", price))

        query = query.order_by(order_by).limit(limit)

        if start_after:
            last_doc = self.collection.document(start_after).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]

    def update(self, restaurant_id: str, data: dict) -> dict | None:
        """Actualiza parcialmente los campos de un restaurante existente.

        Args:
            restaurant_id (str): ID del documento a actualizar.
            data (dict): Diccionario con los campos y nuevos valores a modificar.

        Returns:
            dict | None: Documento actualizado completo, o `None` si el ID no existe.
        """
        ref = self.collection.document(restaurant_id)
        doc = ref.get()
        if not doc.exists:
            return None
        ref.update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        """Elimina un documento de restaurante de Firestore.

        Args:
            restaurant_id (str): ID del documento a eliminar.

        Returns:
            bool: `True` si el documento existía y fue eliminado; `False` en caso contrario.
        """
        ref = self.collection.document(restaurant_id)
        doc = ref.get()
        if not doc.exists:
            return False
        ref.delete()
        return True