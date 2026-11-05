import {useEffect, useState} from 'react';

/** Short rotating loading phrases with a subtle fade. Cycle every ~2s. */
export const LOADING = {
  laws: ['Searching Georgia law…', 'Opening the stored text…', 'Almost ready…'],
  ai: ['Checking the Georgia Code…', 'Pulling up case law…', 'Lining up your options…', 'Weighing what comes next…', 'Almost ready…'],
  docs: ['Gathering your files…', 'Lining up your documents…', 'Almost ready…'],
  paper: ['Reading your paper line by line…', 'Spotting dates and charges…', 'Finding deadlines…', 'Almost ready…'],
} as const;

export function LoadingPhrase({lines, label = 'Loading'}: {lines: readonly string[]; label?: string}) {
  const [i, setI] = useState(0);
  const [fade, setFade] = useState(true);
  useEffect(() => {
    if (lines.length < 2) return;
    const id = setInterval(() => {
      setFade(false);
      setTimeout(() => { setI((n) => (n + 1) % lines.length); setFade(true); }, 180);
    }, 2000);
    return () => clearInterval(id);
  }, [lines]);
  const text = lines[i] || lines[0] || 'Loading…';
  return (
    <p className="lawLoading" aria-live="polite" aria-label={label + '. ' + text}>
      <span className="lawSpinner" aria-hidden />
      <span className={'loadingPhrase' + (fade ? ' on' : '')}>{text}</span>
    </p>
  );
}
