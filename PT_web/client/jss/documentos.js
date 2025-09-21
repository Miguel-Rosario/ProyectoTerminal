
// Variable global para el documento en edición
let documentoEditando = null;

document.addEventListener("DOMContentLoaded", () => {
  listarDocumentos();

  const form = document.getElementById("formSubir");
  if (form) {
    form.addEventListener("submit", async e => {
      e.preventDefault();
      await subirDocumento();
    });
  }
  const guardarBtn = document.getElementById("guardarCambios");
  if (guardarBtn) {
    guardarBtn.addEventListener("click", guardarCambios);
  }
});


async function subirDocumento() {
  const archivo = document.getElementById("archivo").files[0];
  if (!archivo) return alert("Selecciona un archivo");

  const usuario_id = localStorage.getItem("usuario_id");
  if (!usuario_id) return alert("Debes iniciar sesión");

  const formData = new FormData();
  formData.append("archivo", archivo);
  formData.append("usuario_id", usuario_id);

  try {
    const resp = await fetch(`${API_URL}/subir`, {
      method: "POST",
      body: formData
    });

    const data = await resp.json();
    alert(data.message || "Archivo subido");

    document.getElementById("archivo").value = "";
    listarDocumentos(); //  refrescar lista después de subir
  } catch (err) {
    console.error(err);
    alert("Error al subir archivo");
  }
}

async function listarDocumentos() {
  const lista = document.getElementById("listaDocumentos");
  lista.innerHTML = "<p>Cargando...</p>";

  try {
    const resp = await apiGet("/documentos");

    lista.innerHTML = "";
    if (resp.length === 0) {
      lista.innerHTML = "<p>No hay documentos.</p>";
      return;
    }

    resp.forEach(doc => {
      const div = document.createElement("div");
      div.classList.add("documento");
      div.innerHTML = `
        <p><b>${doc.nombre}</b> (v${doc.version})</p>
        <p>SHA256: ${doc.hash}</p>
        <p>Última edición por: Usuario ${doc.usuario_version}</p>
        <button onclick="verDocumento('${doc.id}')">Ver</button>
        <button onclick="editarDocumento('${doc.id}')">✏️ Editar</button>
        <button onclick="descargarVersionFetch('${doc.version_id}')">⬇️ Descargar</button>
      `;
      lista.appendChild(div);
    });
  } catch (err) {
    console.error(err);
    lista.innerHTML = "<p>Error al cargar documentos</p>";
  }
}

async function listarMisDocumentos() {
  const usuario_id = localStorage.getItem("usuario_id");
  if (!usuario_id) return alert("Debes iniciar sesión");

  const lista = document.getElementById("listaDocumentos");
  lista.innerHTML = "<p>Cargando tus documentos...</p>";

  try {
    const resp = await apiGet(`/mis_documentos/${usuario_id}`);
    lista.innerHTML = "";

    if (resp.length === 0) {
      lista.innerHTML = "<p>No tienes documentos propios.</p>";
      return;
    }

    resp.forEach(doc => {
      const div = document.createElement("div");
      div.classList.add("documento");
      div.innerHTML = `
        <p><b>${doc.nombre}</b> (v${doc.version})</p>
        <p>Tipo: ${doc.tipo} | SHA256: ${doc.hash}</p>
        <p>Estado firma: ${doc.estado_firma} | Últ. actualización: ${doc.actualizado}</p>
        <button onclick="verDocumento('${doc.id}')">Ver</button>
      `;
      lista.appendChild(div);
    });
  } catch (err) {
    console.error(err);
    lista.innerHTML = "<p>Error al cargar tus documentos.</p>";
  }
}



async function verDocumento(id) {
  try {
    const resp = await apiGet(`/documentos/${id}`);
    alert("Contenido:\n" + JSON.stringify(resp, null, 2));
  } catch (err) {
    console.error(err);
    alert("Error al obtener documento");
  }
}

async function editarDocumento(id) {
  try {
    const verificacion = await apiGet(`/verificar/${id}`);

    // Solo mostrar alerta informativa, no preguntar
    if (!verificacion.valido && verificacion.mensaje !== "Documento no firmado") {
      alert(`⚠️ ${verificacion.mensaje}\nPuede editarlo pero la firma anterior era inválida.`);
    }

    const resp = await apiGet(`/documentos/${id}`);
    if (resp.error) {
      alert("Error: " + resp.error);
      return;
    }

    // 🔹 Identificar si es propietario o colaborador
    const usuario_id = localStorage.getItem("usuario_id");
    let esPropietario = (usuario_id && resp.propietario_id && parseInt(usuario_id) === parseInt(resp.propietario_id));

    let aviso = esPropietario 
      ? "Eres el propietario. Tus cambios reemplazarán el documento original y se volverá a firmar."
      : "No eres el propietario. Tus cambios se guardarán como una nueva versión.";

    alert(aviso);

    // Mostrar contenido
    document.getElementById("contenidoNuevo").value = resp.contenido || "";

    // Guardar id actual en memoria para después
    localStorage.setItem("doc_editando", id);

    // Mostrar editor
    document.getElementById("documentos").style.display = "none";
    document.getElementById("editor").style.display = "block";
  } catch (err) {
    console.error("Error cargando documento:", err);
    alert("No se pudo cargar el documento");
  }
}


async function guardarCambios() {
  try {
    const id = localStorage.getItem("doc_editando");
    const contenido = document.getElementById("contenidoNuevo").value;
    const usuario_id = localStorage.getItem("usuario_id");

    if (!id) {
      alert("No hay documento seleccionado para editar");
      return;
    }

    if (!contenido.trim()) {
      alert("El contenido no puede estar vacío");
      return;
    }

    if (!usuario_id) {
      alert("Debes iniciar sesión para guardar cambios");
      return;
    }

    // 🔹 RUTA CORRECTA: /modificar/{id}
    const response = await fetch(`${API_URL}/modificar/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contenido: contenido,   // 👈 nombre corregido
        usuario_id: usuario_id  // se manda para validar propietario
      })
    });

    const data = await response.json();

    if (response.ok) {
      alert(data.mensaje || "Cambios guardados correctamente"); // 👈 usa mensaje del backend
      cancelarEdicion();
      listarDocumentos();
    } else {
      alert("Error: " + (data.error || "No se pudieron guardar los cambios"));
    }

  } catch (error) {
    console.error("Error al guardar cambios:", error);
    alert("Error de conexión al guardar cambios");
  }
}


async function descargarVersionFetch(versionId) {
  try {
    const response = await fetch(`${API_URL}/descargar_version/${versionId}`);
    if (!response.ok) {
      // leer posible JSON de error para debug
      const text = await response.text();
      console.error("Error al descargar:", response.status, text);
      alert("Error al descargar: " + response.status);
      return;
    }

    const blob = await response.blob();

    // intentar obtener filename desde Content-Disposition
    const disposition = response.headers.get('Content-Disposition') || '';
    let filename = `version_${versionId}.txt`;
    let m;

    // busca filename*=UTF-8''... o filename="..."
    m = disposition.match(/filename\*=UTF-8''([^;]+)/);
    if (m && m[1]) {
      filename = decodeURIComponent(m[1]);
    } else {
      m = disposition.match(/filename="([^"]+)"/);
      if (m && m[1]) filename = m[1];
      else {
        m = disposition.match(/filename=([^;]+)/);
        if (m && m[1]) filename = m[1];
      }
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('Error:', error);
    alert('Error al descargar (ver consola)');
  }
}



function cancelarEdicion() {
  documentoEditando = null;
  document.getElementById("editor").style.display = "none";
  document.getElementById("documentos").style.display = "block";
  document.getElementById("contenidoNuevo").value = "";
  
}

function limpiarEditor() {
  documentoEditando = null;
  document.getElementById("contenidoNuevo").value = "";
  document.getElementById("editor").style.display = "none";
}

