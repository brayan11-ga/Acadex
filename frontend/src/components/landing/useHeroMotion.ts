import { useLayoutEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export function useHeroMotion(isAmbientPaused = false) {
  const heroRef = useRef<HTMLElement>(null);
  const pausedRef = useRef(isAmbientPaused);
  const syncAmbientRef = useRef<(() => void) | null>(null);

  useLayoutEffect(() => {
    pausedRef.current = isAmbientPaused;
    syncAmbientRef.current?.();
  }, [isAmbientPaused]);

  useLayoutEffect(() => {
    const hero = heroRef.current;
    if (!hero || typeof window.matchMedia !== 'function') return;

    gsap.registerPlugin(ScrollTrigger);
    const media = gsap.matchMedia();

    media.add(
      {
        motion: '(prefers-reduced-motion: no-preference)',
        desktop: '(min-width: 960px)',
      },
      (context) => {
        if (!context.conditions?.motion) return;

        const ambient = gsap.timeline({ paused: true, defaults: { ease: 'sine.inOut', repeat: -1, yoyo: true } })
          .to('.landing-hero__stars > span', { opacity: 0.35, duration: 3.2, stagger: 1.6 }, 0)
          .to('.landing-hero__beacon > span', { opacity: 0.45, duration: 2.4, stagger: 0.8 }, 0.4);

        let hasEntered = false;
        let isInView = false;
        const syncAmbient = () => ambient.paused(!hasEntered || !isInView || pausedRef.current);
        syncAmbientRef.current = syncAmbient;

        // Continuous motion runs only after the entrance, while visible, and unless the user pauses it.
        const visibility = ScrollTrigger.create({
          trigger: hero,
          start: 'top bottom',
          end: 'bottom top',
          onToggle: (self) => {
            isInView = self.isActive;
            syncAmbient();
          },
        });
        isInView = visibility.isActive;

        gsap.timeline({
          defaults: { ease: 'power3.out', duration: 0.65 },
          onComplete: () => {
            hasEntered = true;
            syncAmbient();
          },
        })
          .from('[data-hero-enter]', { y: 18, opacity: 0, stagger: 0.08 }, 0)
          .from('[data-hero-scene]', { y: 22, scale: 0.97, opacity: 0, duration: 0.95 }, 0.05)
          .from('[data-hero-beam]', { scaleY: 0, transformOrigin: '50% 100%', duration: 0.7 }, 0.2);

        if (context.conditions.desktop) {
          ambient
            .to('.landing-hero__moon', { x: 2, y: -4, duration: 6.4 }, 0)
            .to('.landing-hero__beam', { opacity: 0.55, duration: 4.8 }, 0.8)
            .fromTo('.landing-hero__station-aura', { opacity: 0.2 }, { opacity: 0.65, duration: 3.2 }, 0)
            .to('.landing-hero__station-brand > span', { opacity: 0.45, duration: 1.6 }, 1.2)
            .to('.landing-hero__task-pixels i', { opacity: 0.4, duration: 1.6, stagger: 0.4 }, 0.8)
            .fromTo('.landing-hero__circuit--bright',
              { strokeDasharray: '16 144', strokeDashoffset: 0 },
              { strokeDashoffset: -160, duration: 4.8, ease: 'none', yoyo: false }, 0)
            .fromTo('.landing-hero__signal',
              { strokeDasharray: '8 56', strokeDashoffset: 0 },
              { strokeDashoffset: -64, duration: 3.2, ease: 'none', yoyo: false }, 0.8);

          // Nested planes keep the station close to its platform; copy and CTAs never move with scroll.
          gsap.timeline({
            defaults: { ease: 'none', duration: 1 },
            scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 0.8 },
          })
            .to('[data-hero-depth="far"]', { y: 32 }, 0)
            .to('[data-hero-depth="near"]', { y: -20 }, 0)
            .to('[data-hero-depth="island"]', { y: -22 }, 0)
            .to('[data-hero-depth="station"]', { y: -8 }, 0);
        }

        return () => { syncAmbientRef.current = null; };
      },
      hero,
    );

    // MatchMedia owns its timelines, ScrollTriggers and inline styles, including StrictMode remounts.
    return () => media.revert();
  }, []);

  return heroRef;
}
