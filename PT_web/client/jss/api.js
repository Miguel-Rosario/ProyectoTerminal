const API_URL = "http://127.0.0.1:5000"; // tu backend Flask

async function apiGet(endpoint) {
  try {
    const response = await fetch(API_URL + endpoint);
    if (!response.ok) {
      throw new Error(`Error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error en apiGet:", error);
    return [];
  }
}

async function apiPost(ruta, datos) {
  const resp = await fetch(`${API_URL}${ruta}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos)
  });
  return resp.json();
}


