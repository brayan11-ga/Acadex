import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

import Header from '../components/landing/Header';
import FormularioRegistro from '../components/register/Formularioregister';
import Footer from '../components/landing/Footer';

import '../styles/login.css';



export const Register = () => {
    return (

        <div className="formulario-registro">
            <Header />
            <main className="login-main">
                <FormularioRegistro />
            </main>
            <Footer />
        </div>
    );
};

export default Register;