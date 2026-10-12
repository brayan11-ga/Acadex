import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import Header from '../components/landing/Header';
import FormularioRestablecerContrasena from '../components/login/FormularioRestablecerContrasena';
import Footer from '../components/landing/Footer';
import '../styles/login.css';

export const RestablecerContrasena = () => (
    <div className="formulario-registro">
        <Header />
        <main className="login-main">
            <FormularioRestablecerContrasena />
        </main>
        <Footer />
    </div>
);

export default RestablecerContrasena;