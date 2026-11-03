import { StrictMode } from 'react';
import { act, cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Hero from '../src/components/landing/Hero';

describe('Hero cinematográfico de Acadex', () => {
  let reducedMotion = false;
  let desktop = true;

  beforeEach(() => {
    reducedMotion = false;
    desktop = true;
    vi.stubGlobal('matchMedia', vi.fn((query: string) => ({
      matches: query.includes('prefers-reduced-motion')
        ? (query.includes('no-preference') ? !reducedMotion : reducedMotion)
        : query.includes('min-width: 960px') && desktop,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })));
    vi.spyOn(window, 'scrollTo').mockImplementation((optionsOrX?: number | ScrollToOptions, y?: number) => {
      vi.stubGlobal('pageYOffset', typeof optionsOrX === 'object' ? optionsOrX.top ?? 0 : y ?? 0);
    });
    const getBounds = HTMLElement.prototype.getBoundingClientRect;
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (this: HTMLElement) {
      return this.tagName === 'SECTION'
        ? new DOMRect(0, 0, 1280, 800)
        : getBounds.call(this);
    });
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  const renderHero = () => render(
    <StrictMode>
      <MemoryRouter>
        <div className="landing-container"><Hero /></div>
      </MemoryRouter>
    </StrictMode>,
  );

  const timelineFor = (element: Element) => {
    let animation: gsap.core.Animation = gsap.getTweensOf(element)[0];
    while (animation.parent && animation.parent !== gsap.globalTimeline) animation = animation.parent;
    return animation as gsap.core.Timeline;
  };

  test('mantiene registro, inicio de sesión y exploración accesibles durante la entrada', () => {
    renderHero();
    const hero = screen.getByRole('region', { name: /Tu mundo, en orden\./i });

    expect(within(hero).getByRole('link', { name: 'Crear mi espacio' })).toHaveAttribute('href', '/registrarse');
    expect(within(hero).getByRole('link', { name: 'Iniciar sesión' })).toHaveAttribute('href', '/iniciarSesion');
    expect(within(hero).getByRole('link', { name: 'Explora Acadex' })).toHaveAttribute('href', '#funcionalidades');
    expect(within(hero).getByRole('link', { name: 'Crear mi espacio' })).toBeVisible();
    expect(within(hero).queryByText(/120|35|80%/)).not.toBeInTheDocument();
    expect(hero.querySelector('[data-hero-scene]')).toHaveAttribute('aria-hidden', 'true');
    expect(within(hero).getByText(/Vista conceptual/)).toBeInTheDocument();
  });

  test('StrictMode no duplica ScrollTriggers y desmontar elimina animaciones y estilos', () => {
    const { container, unmount } = renderHero();
    const targets = Array.from(container.querySelectorAll<HTMLElement | SVGElement>('.landing-hero *'));

    expect(ScrollTrigger.getAll()).toHaveLength(2);
    expect(ScrollTrigger.getAll().filter((trigger) => trigger.vars.scrub)).toHaveLength(1);
    expect(gsap.getTweensOf(container.querySelector('.landing-hero__moon'))).toHaveLength(1);
    expect(gsap.getTweensOf(targets).length).toBeGreaterThan(0);

    unmount();

    expect(ScrollTrigger.getAll()).toHaveLength(0);
    expect(gsap.getTweensOf(targets)).toHaveLength(0);
    targets.forEach((target) => {
      expect(target.style.cssText).toBe('');
    });
  });

  test('movimiento reducido muestra el contenido sin animaciones ni parallax', () => {
    reducedMotion = true;
    const { container } = renderHero();
    const targets = Array.from(container.querySelectorAll<HTMLElement | SVGElement>('.landing-hero *'));

    expect(ScrollTrigger.getAll()).toHaveLength(0);
    expect(gsap.getTweensOf(targets)).toHaveLength(0);
    expect(screen.getByRole('heading', { level: 1 })).toBeVisible();
    targets.forEach((target) => expect(target.style.cssText).toBe(''));
  });

  test('activar movimiento reducido revierte una escena ya animada', () => {
    const { container } = renderHero();
    const targets = Array.from(container.querySelectorAll<HTMLElement | SVGElement>('.landing-hero *'));
    expect(ScrollTrigger.getAll()).toHaveLength(2);

    reducedMotion = true;
    act(() => gsap.matchMediaRefresh());

    expect(ScrollTrigger.getAll()).toHaveLength(0);
    expect(gsap.getTweensOf(targets)).toHaveLength(0);
    targets.forEach((target) => expect(target.style.cssText).toBe(''));
  });

  test('pantallas pequeñas conservan la entrada sin parallax', () => {
    desktop = false;
    const { container } = renderHero();

    expect(ScrollTrigger.getAll()).toHaveLength(1);
    expect(ScrollTrigger.getAll().some((trigger) => trigger.vars.scrub)).toBe(false);
    const moon = container.querySelector('.landing-hero__moon');
    const circuit = container.querySelector<SVGElement>('.landing-hero__circuit--bright');
    expect(gsap.getTweensOf(moon)).toHaveLength(0);
    expect(circuit?.style.strokeDasharray).toBe('');
    expect(gsap.getTweensOf(container.querySelector('.landing-hero__beacon > span'))).toHaveLength(1);
    expect(screen.getByRole('link', { name: 'Crear mi espacio' })).toBeVisible();
  });

  test('pausar y reanudar el ambiente conserva la entrada completada y los ScrollTriggers', async () => {
    const user = userEvent.setup();
    const { container } = renderHero();
    const entrance = timelineFor(screen.getByRole('heading', { level: 1 }));
    const ambient = timelineFor(container.querySelector('.landing-hero__beacon > span')!);

    expect(ambient.paused()).toBe(true);
    act(() => { entrance.progress(1); });
    expect(ambient.paused()).toBe(false);

    await user.click(screen.getByRole('button', { name: 'Pausar ambiente' }));
    expect(ambient.paused()).toBe(true);
    expect(entrance.progress()).toBe(1);
    expect(ScrollTrigger.getAll()).toHaveLength(2);

    await user.click(screen.getByRole('button', { name: 'Reanudar ambiente' }));
    expect(ambient.paused()).toBe(false);
    expect(entrance.progress()).toBe(1);
  });

  test('el ambiente desplaza energía y varía luces sin deformar circuitos ni mover el texto', () => {
    const { container } = renderHero();
    const heading = screen.getByRole('heading', { level: 1 });
    const circuit = container.querySelector<SVGElement>('.landing-hero__circuit--bright')!;
    const moon = container.querySelector<HTMLElement>('.landing-hero__moon')!;
    const stars = container.querySelector<HTMLElement>('.landing-hero__stars > span')!;
    const ambient = timelineFor(stars);
    const path = circuit.getAttribute('d');
    act(() => { timelineFor(heading).progress(1); ambient.totalTime(1); });
    const firstFrame = { offset: circuit.style.strokeDashoffset, moon: moon.style.transform, stars: stars.style.opacity };

    act(() => { ambient.totalTime(2); });

    expect(circuit.style.strokeDashoffset).not.toBe(firstFrame.offset);
    expect(moon.style.transform).not.toBe(firstFrame.moon);
    expect(stars.style.opacity).not.toBe(firstFrame.stars);
    expect(circuit.getAttribute('d')).toBe(path);
    expect(Number(gsap.getProperty(heading, 'y'))).toBe(0);
    expect(screen.getByRole('link', { name: 'Crear mi espacio' })).toBeVisible();
  });

  test('salir de pantalla pausa el ambiente y regresar respeta la pausa manual', async () => {
    const user = userEvent.setup();
    const { container } = renderHero();
    const ambient = timelineFor(container.querySelector('.landing-hero__beacon > span')!);
    const visibility = ScrollTrigger.getAll().find((trigger) => !trigger.vars.scrub)!;
    act(() => { timelineFor(screen.getByRole('heading', { level: 1 })).progress(1); });

    act(() => { visibility.scroll(1000); ScrollTrigger.update(); });
    expect(ambient.paused()).toBe(true);
    act(() => { visibility.scroll(0); ScrollTrigger.update(); });
    expect(ambient.paused()).toBe(false);

    await user.click(screen.getByRole('button', { name: 'Pausar ambiente' }));
    act(() => { visibility.scroll(1000); ScrollTrigger.update(); });
    act(() => { visibility.scroll(0); ScrollTrigger.update(); });
    expect(ambient.paused()).toBe(true);
  });

  test('cambiar a móvil revierte circuitos y profundidad sin perder la pausa manual', async () => {
    const user = userEvent.setup();
    const { container } = renderHero();
    await user.click(screen.getByRole('button', { name: 'Pausar ambiente' }));

    desktop = false;
    act(() => gsap.matchMediaRefresh());

    expect(ScrollTrigger.getAll()).toHaveLength(1);
    expect(ScrollTrigger.getAll().some((trigger) => trigger.vars.scrub)).toBe(false);
    expect(container.querySelector<SVGElement>('.landing-hero__circuit--bright')?.style.cssText).toBe('');
    expect(container.querySelector<HTMLElement>('[data-hero-depth="station"]')?.style.cssText).toBe('');
    act(() => { timelineFor(screen.getByRole('heading', { level: 1 })).progress(1); });
    expect(timelineFor(container.querySelector('.landing-hero__beacon > span')!).paused()).toBe(true);
  });
});
