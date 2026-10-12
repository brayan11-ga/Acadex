import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import Header from '../components/landing/Header';
import FormularioOlvidoContrasena from '../components/login/FormularioOlvidoContrasena';
import Footer from '../components/landing/Footer';
import '../styles/login.css';

export const OlvideContrasena = () => (
    <div className="formulario-registro">
        <Header />
        <main className="login-main">
            <FormularioOlvidoContrasena />
        </main>
        <Footer />
    </div>
);

export default OlvideContrasena;