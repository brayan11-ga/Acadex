import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

import Header from '../components/landing/Header';
import FormularioLogin from '../components/login/FormularioLogin';
import Footer from '../components/landing/Footer';

import '../styles/login.css';



export const Login = () =>{
    return (
        
        <div className="formulario-registro">
            <Header />
            <main className="login-main">
                <FormularioLogin />
            </main>
            <Footer />
        </div>
    );
};

export default Login;