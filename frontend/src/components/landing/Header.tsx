import { useState } from 'react';
import logoAcadex from '../../assets/logos/logo_acadex-preview.png';
import logoAcadexLight from '../../assets/logos/logo_acadex_light.png';
import { Link } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';
import { useTheme } from '../../contexts/ThemeContext';

export const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isDarkMode } = useTheme();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  const closeMenu = () => setIsMobileMenuOpen(false);

  return (
    <header className="header">
      <nav className="navbar container">
        <div className="logo">
          <a href="/#inicio" aria-label="Ir al inicio">
            {/* Logo dinámico: usa el oscuro si isDarkMode es true, de lo contrario usa el claro */}
            <img 
              src={isDarkMode ? logoAcadex : logoAcadexLight} 
              alt="Acadex Logo" 
            />
          </a>
        </div>

        <div className="nav-links">
          <a href="/#inicio">Inicio</a>
          <a href="/#funcionalidades">Funcionalidades</a>
          <a href="/#como-funciona">¿Cómo funciona?</a>
          <a href="/#beneficios">Beneficios</a>
        </div>

        {/* Acciones principales unificadas (Botones + ThemeToggle alineados en fila) */}
        <div className="nav-actions">
          <Link to="/iniciarSesion" className="btn btn-ghost">Iniciar sesión</Link>
          <Link to="/registrarse" className="btn btn-primary">Registrarse</Link>
          <ThemeToggle />
        </div>

        <button className="menu-toggle" aria-label="Abrir menú" onClick={toggleMobileMenu}>
          <i className="bi bi-list"></i>
        </button>
      </nav>

      {/* Menú móvil */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'active' : ''}`}>
        <a href="/#inicio" onClick={closeMenu}>Inicio</a>
        <a href="/#funcionalidades" onClick={closeMenu}>Funcionalidades</a>
        <a href="/#como-funciona" onClick={closeMenu}>¿Cómo funciona?</a>
        <a href="/#beneficios" onClick={closeMenu}>Beneficios</a>

        <div className="mobile-menu-actions">
          <Link to="/iniciarSesion" className="btn btn-ghost" onClick={closeMenu}>Iniciar sesión</Link>
          <Link to="/registrarse" className="btn btn-primary" onClick={closeMenu}>Registrarse</Link>
        </div>
      </div>
    </header>
  );
};

export default Header;