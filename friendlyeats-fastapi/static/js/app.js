document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("restaurant-form");

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const restaurantId = form.dataset.id;
      const formData = Object.fromEntries(new FormData(form));
      formData.price = Number(formData.price);

      const isEdit = Boolean(restaurantId);
      const url = isEdit ? `/api/v1/restaurants/${restaurantId}` : "/api/v1/restaurants";
      const method = isEdit ? "PATCH" : "POST";

      const response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      const message = document.getElementById("message");
      if (response.ok) {
        message.style.color = "green";
        message.textContent = isEdit ? "Restaurante actualizado correctamente" : "Restaurante creado correctamente";
        setTimeout(() => { window.location.href = "/"; }, 1200);
      } else {
        const error = await response.json();
        message.style.color = "red";
        message.textContent = error.detail || "Error al guardar";
      }
    });
  }
});

async function deleteRestaurant(id) {
  if (confirm("¿Estás seguro de eliminar este restaurante?")) {
    const response = await fetch(`/api/v1/restaurants/${id}`, { method: "DELETE" });
    if (response.ok) {
      window.location.href = "/";
    } else {
      alert("Error al eliminar el restaurante");
    }
  }
}