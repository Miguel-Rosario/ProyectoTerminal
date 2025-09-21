document.getElementById("formArchivo").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);

  try {
    const resp = await fetch("/subir", {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();

    if (resp.ok) {
      alert("✅ Documento subido correctamente");
      window.location.href = "index.html"; // 🔄 Regresa a la principal
    } else {
      alert("❌ Error: " + (data.error || "No se pudo subir"));
    }
  } catch (err) {
    console.error("Error:", err);
    alert("⚠️ Ocurrió un problema al subir el archivo");
  }
});