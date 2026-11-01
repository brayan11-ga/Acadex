export function sonarAlarma() {
    try {
    const ctx = new AudioContext();
    const notas = [659.25, 880]; // Mi5 → La5
    const duracion = 0.65; //duracion

    notas.forEach((frecuencia, i) => {
      const inicio = ctx.currentTime + i * 0.25;
        const osc = ctx.createOscillator();
        const ganancia = ctx.createGain();

        osc.type = "sine";
        osc.frequency.value = frecuencia;

        ganancia.gain.setValueAtTime(0.0001, inicio);
        ganancia.gain.exponentialRampToValueAtTime(1, inicio + 0.02);//volumen del sonido
        ganancia.gain.exponentialRampToValueAtTime(0.0001, inicio + duracion);

        osc.connect(ganancia);
        ganancia.connect(ctx.destination);
        osc.start(inicio);
        osc.stop(inicio + duracion);
    });

    setTimeout(() => void ctx.close(), 1000);
    } catch {
    // sin soporte de audio
    }
}