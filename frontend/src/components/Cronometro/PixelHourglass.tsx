import { useEffect, useState } from 'react';
import '../../styles/Pixelhourglass.css';

const FRAMES_COUNT = 10; // pasos de la animación de vaciado/llenado
const STEP_MS = 10; // duración de cada paso
const FLIP_MS = 10; // duración del giro al terminar el ciclo

// 1 = marco de vidrio del reloj
const FRAME: number[][] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
];

// Celdas de arena en la cámara de ARRIBA
const TOP_CELLS: [number, number][] = [
  [4, 4],
  [3, 3], [3, 4], [3, 5],
  [2, 2], [2, 3], [2, 4], [2, 5], [2, 6],
  [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7],
];

// Celdas de arena en la cámara de ABAJO,
const BOTTOM_CELLS: [number, number][] = [
  [9, 1], [9, 2], [9, 3], [9, 4], [9, 5], [9, 6], [9, 7],
  [8, 2], [8, 3], [8, 4], [8, 5], [8, 6],
  [7, 3], [7, 4], [7, 5],
  [6, 4],
];

const TOTAL_SAND = TOP_CELLS.length; 

interface PixelHourglassProps {
  className?: string;
}

export const PixelHourglass = ({ className }: PixelHourglassProps) => {
    const [step, setStep] = useState(0);
    const [flipping, setFlipping] = useState(false);

    useEffect(() => {
    const id = setInterval(() => {
        setStep((prev) => {
        const next = prev + 1;
        if (next > FRAMES_COUNT) {
            setFlipping(true);
            setTimeout(() => setFlipping(false), FLIP_MS);
            return 0;
        }
        return next;
        });
    }, STEP_MS);
    return () => clearInterval(id);
    }, []);

   const transferred = Math.round((step / FRAMES_COUNT) * TOTAL_SAND);
    const drainedTop = new Set(
    TOP_CELLS.slice(0, transferred).map(([r, c]) => `${r}-${c}`)
    );
    const filledBottom = new Set(
    BOTTOM_CELLS.slice(0, transferred).map(([r, c]) => `${r}-${c}`)
    );

    return (
    <div className={`pixel-hourglass-wrapper ${className ?? ''}`}>
        <div
        className={`pixel-hourglass ${flipping ? 'pixel-hourglass-flip' : ''}`}
        role="img"
        aria-label="Cargando"
        >
        {FRAME.map((row, r) =>
            row.map((cell, c) => {
            const key = `${r}-${c}`;
            let pixelClass = 'px px-empty';

            if (cell === 1) {
                pixelClass = 'px px-frame';
            } else if (
                TOP_CELLS.some(([tr, tc]) => tr === r && tc === c) &&
                !drainedTop.has(key)
            ) {
                pixelClass = 'px px-sand';
            } else if (filledBottom.has(key)) {
                pixelClass = 'px px-sand';
            }

            return <span key={key} className={pixelClass} />;
            })
        )}
        </div>
    </div>
    );
};

export default PixelHourglass;