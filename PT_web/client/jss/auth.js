async function login() {
  const usuario = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  const resp = await apiPost("/login", { usuario, password });

  if (resp.usuario_id) {
    alert(" Sesión iniciada");
    localStorage.setItem("usuario_id", resp.usuario_id);
    // Guardar nombre completo
    localStorage.setItem("usuario_nombre", resp.nombre + " " + resp.apellido);
    
    
    document.getElementById("login").style.display = "none";
    document.getElementById("registro").style.display = "none";
    document.getElementById("documentos").style.display = "block";
    
    const nombreUsuario = document.getElementById("usuarioNombre");
    if (nombreUsuario) {
      nombreUsuario.innerText = resp.nombre + " " + resp.apellido;
    }

    listarDocumentos();
    

  } else {
    alert(" Error: " + (resp.message || "Usuario o contraseña incorrectos"));
  }
}

async function registrar() {
  const usuario = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;
  const nombre = document.getElementById("reg-nombre").value;
  const apellido = document.getElementById("reg-apellido").value;
  if (!usuario || !password || !nombre || !apellido) {
    alert("Todos los campos son obligatorios");
    return;
  }

  const resp = await apiPost("/registro", { usuario, password, nombre, apellido  });
  //alert("Registrado correctamente"+resp.message);
  if (resp.ok || resp.usuario_id) {
    alert(" Registrado correctamente: " + resp.message );
    // Después del registro, regreso al login
    mostrarLogin();
  } else {
    alert(" Error al registrar: " + (resp.message || "Inténtalo de nuevo"));
  }
}
function mostrarApp() {
  document.getElementById("auth").style.display = "none";
  document.getElementById("documentos").style.display = "block";
}

function cerrarSesion() {

  localStorage.removeItem("usuario_id");
  localStorage.removeItem("usuario_nombre");

  document.getElementById("documentos").style.display = "none";
  document.getElementById("editor").style.display = "none";
  document.getElementById("login").style.display = "block";

  if (typeof limpiarEditor === 'function') {
    limpiarEditor();
  }
}