import { Link } from 'react-router-dom';
import '../styles/legal-information.css';

type LegalInformationProps = { type: 'privacy' | 'cookies' };

const VERSION = 'Borrador de proyecto académico · v2 · 2026-10-11';

function DraftNotice() {
  return (
    <aside className="legal-draft" role="note">
      <strong>Aviso general para el prototipo académico; requiere validación antes de producción.</strong>
      <p>La entidad o persona que opere una versión real debe confirmar responsables, canales de atención, plazos de conservación y condiciones de los proveedores.</p>
    </aside>
  );
}

function PrivacyContent() {
  return (
    <>
      <DraftNotice />
      <h2>Sobre Acadex y el responsable</h2>
      <p>Acadex es un proyecto académico de software desarrollado en contexto de formación con el SENA. Esa relación académica no significa por sí sola que el SENA opere la aplicación o sea el responsable del tratamiento. La persona o entidad que publique y opere una versión real deberá identificarse y habilitar un canal para atender solicitudes de privacidad.</p>
      <h2>Datos y finalidades identificadas</h2>
      <p>El registro solicita correo, nombre de usuario y contraseña; la contraseña se guarda como hash. Al usar la aplicación también se procesan datos de perfil, tareas, grupos y archivos para ofrecer sus funciones.</p>
      <p>Si el usuario activa el autocompletado con IA, el documento seleccionado se envía a Google Gemini para analizarlo. Los archivos adjuntos también se guardan en el almacenamiento configurado por quien opera el backend. Antes de producción, el operador debe confirmar las condiciones de tratamiento y conservación aplicables a esos proveedores.</p>
      <h2>Derechos de habeas data</h2>
      <p>El titular puede solicitar conocer, actualizar y rectificar sus datos, pedir su supresión cuando proceda y revocar la autorización en los casos previstos por la ley. El operador deberá publicar un canal y un procedimiento accesibles para ejercer estos derechos.</p>
      <h2>Conservación y cambios</h2>
      <p>Los plazos concretos de conservación, la eliminación de cuentas y archivos, y el manejo de respaldos dependen de la instancia que despliegue Acadex. Deben definirse y comunicarse antes de tratar datos reales.</p>
    </>
  );
}

function CookiesContent() {
  return (
    <>
      <DraftNotice />
      <h2>Cookies</h2>
      <p>En el código actual del proyecto no se encontró configuración de cookies propias, analítica o publicidad. Si quien opera la aplicación incorpora estas tecnologías, deberá actualizar el aviso y solicitar las preferencias que correspondan antes de activarlas.</p>
      <h2>Almacenamiento local del navegador</h2>
      <p>El frontend usa <code>localStorage</code> para mantener la sesión y guardar preferencias del tema y del cronómetro. Este almacenamiento funciona en el navegador y no es una cookie. La persona usuaria puede borrarlo desde la configuración del navegador; al hacerlo, algunas funciones dejarán de recordar su estado.</p>
      <h2>Recursos de terceros</h2>
      <p>La interfaz solicita fuentes y un favicon a Google. Esas solicitudes contactan un servicio externo; quien despliegue Acadex debe revisar sus condiciones y decidir si mantiene esos recursos.</p>
    </>
  );
}

export default function LegalInformation({ type }: LegalInformationProps) {
  const isPrivacy = type === 'privacy';
  return (
    <main className="legal-page">
      <article className="legal-card">
        <p className="legal-version">{VERSION}</p>
        <h1>{isPrivacy ? 'Política de tratamiento de datos' : 'Aviso de cookies y almacenamiento local'}</h1>
        {isPrivacy ? <PrivacyContent /> : <CookiesContent />}
        <Link className="legal-back" to="/registrarse">Volver al registro</Link>
      </article>
    </main>
  );
}
