export function obtenerMensajeErrorRegistro(error: unknown): string {
  if (!(error instanceof Error)) {
    return "No fue posible crear tu cuenta. Inténtalo de nuevo.";
  }

  const mensaje = error.message.trim();
  const mensajeNormalizado = mensaje.toLocaleLowerCase("es");

  if (/correo.*ya est[aá] registrado/.test(mensajeNormalizado)) {
    return "Este correo ya tiene una cuenta. Inicia sesión o recupera tu contraseña.";
  }

  if (error.name === "TypeError" || /failed to fetch|networkerror|network request failed/i.test(mensaje)) {
    return "No pudimos conectar con Acadex. Revisa tu conexión e inténtalo de nuevo.";
  }

  if (!mensaje || /^(error al registrar el usuario|error inesperado|internal server error)$/i.test(mensaje)) {
    return "No fue posible crear tu cuenta. Inténtalo de nuevo.";
  }

  return mensaje;
}
