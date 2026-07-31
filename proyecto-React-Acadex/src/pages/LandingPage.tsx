// src/pages/LandingPage.tsx
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

// Importa los componentes modulares
import Header from '../components/landing/Header';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Workflow from '../components/landing/Workflow';
import Benefits from '../components/landing/Benefits';
import CtaSection from '../components/landing/CtaSection';
import Footer from '../components/landing/Footer';

// Importa los estilos CSS globales
import '../css/global.css';

export const LandingPage = () => {
  useEffect(() => {
    AOS.init({
      once: true,
      offset: 80,
    });
  }, []);

  return (
    <div className="landing-container">
      <Header />
      <main>
        <Hero />
        <Features />
        <Workflow />
        <Benefits />
        <CtaSection />
      </main>
      <Footer />
    </div>
  );
};

export default LandingPage;