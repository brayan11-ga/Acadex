import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import Header from '../components/landing/Header';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Workflow from '../components/landing/Workflow';
import Benefits from '../components/landing/Benefits';
import CtaSection from '../components/landing/CtaSection';
import Footer from '../components/landing/Footer';

export const LandingPage = () => {
  useEffect(() => {
    AOS.init({
      once: true,
      offset: 80,
    });

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('[data-reveal]').forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
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