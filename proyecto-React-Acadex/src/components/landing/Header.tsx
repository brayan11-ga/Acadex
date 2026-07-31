// src/components/landing/Header.tsx
import { useState } from 'react';
import logoAcadex from '../../assets/logo_acadex-preview.png';

export const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  const closeMenu = () => setIsMobileMenuOpen(false);

  return (
    <header className="header">
      <nav className="navbar container">
        <div className="logo">
          <a href="#inicio" aria-label="Ir al inicio">
            <img src={logoAcadex} alt="Acadex Logo" />
          </a>
        </div>

        <div className="nav-links">
          <a href="#inicio">Inicio</a>
          <a href="#funcionalidades">Funcionalidades</a>
          <a href="#como-funciona">¿Cómo funciona?</a>
          <a href="#beneficios">Beneficios</a>
        </div>

        <div className="nav-actions">
          <a href="/login.html" className="btn btn-ghost">Iniciar sesión</a>
          <a href="/register.html" className="btn btn-primary">Registrarse</a>
        </div>

        <button className="menu-toggle" aria-label="Abrir menú" onClick={toggleMobileMenu}>
          <i className="bi bi-list"></i>
        </button>
      </nav>

      {/* Menú móvil */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'active' : ''}`}>
        <a href="#inicio" onClick={closeMenu}>Inicio</a>
        <a href="#funcionalidades" onClick={closeMenu}>Funcionalidades</a>
        <a href="#como-funciona" onClick={closeMenu}>¿Cómo funciona?</a>
        <a href="#beneficios" onClick={closeMenu}>Beneficios</a>

        <div className="mobile-menu-actions">
          <a href="/login.html" className="btn btn-ghost">Iniciar sesión</a>
          <a href="/register.html" className="btn btn-primary">Registrarse</a>
        </div>
      </div>
    </header>
  );
};

export default Header;