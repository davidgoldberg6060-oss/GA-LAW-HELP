/** Read aloud using the free Web Speech API. Two original voices, not based on any person or character. */

import { getLang, getVoice, t, type VoiceId } from "./i18n.ts";

export type VoiceInfo = {
  id: VoiceId;
  label: string;
  locale: string;
  localeEs: string;
  pitch: number;
  rate: number;
  introEn: string;
  introEs: string;
};

export const VOICES: Record<Exclude<VoiceId, "off">, VoiceInfo> = {
  butler: {
    id: "butler",
    label: "The Butler",
    locale: "en-GB",
    localeEs: "es-ES",
    pitch: 0.85,
    rate: 0.88,
    introEn: "Allow me to read this for you.",
    introEs: "Permítame leérselo.",
  },
  nanny: {
    id: "nanny",
    label: "The Nanny",
    locale: "en-US",
    localeEs: "es-US",
    pitch: 1.12,
    rate: 1.06,
    introEn: "All right, dear, here is what this says.",
    introEs: "Está bien, querida, esto es lo que dice.",
  },
};

export function spokenText(body: string, voiceId: VoiceId = getVoice(), lang = getLang()): string {
  const text = (body || "").trim();
  if (!text) return "";
  const notice = t("notice", lang);
  const info = voiceId === "off" ? undefined : VOICES[voiceId];
  let spoken = text;
  if (info) {
    const intro = lang === "es" ? info.introEs : info.introEn;
    if (!spoken.startsWith(intro)) spoken = intro + "\n\n" + spoken;
  }
  if (!spoken.includes(notice)) spoken = spoken.trim() + "\n\n" + notice;
  const trans = t("translationNotice", lang);
  if ((/traducci[oó]n/i.test(text) || /translation is for understanding/i.test(text)) && !spoken.includes(trans)) {
    spoken += "\n\n" + trans;
  }
  return spoken.trim();
}

function pickEngineVoice(locale: string): SpeechSynthesisVoice | undefined {
  const voices = window.speechSynthesis?.getVoices?.() || [];
  const lang = locale.toLowerCase();
  return (
    voices.find((v) => v.lang.toLowerCase() === lang) ||
    voices.find((v) => v.lang.toLowerCase().startsWith(lang.slice(0, 2))) ||
    voices[0]
  );
}

export function isSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
}

export function stop() {
  if (isSupported()) window.speechSynthesis.cancel();
}

export function speak(body: string, voiceId: VoiceId = getVoice(), lang = getLang()): boolean {
  if (!isSupported() || !body.trim() || voiceId === "off") return false;
  const info = VOICES[voiceId];
  const text = spokenText(body, voiceId, lang);
  stop();
  const utter = new SpeechSynthesisUtterance(text);
  const locale = lang === "es" ? info.localeEs : info.locale;
  utter.lang = locale;
  utter.pitch = info.pitch;
  utter.rate = info.rate;
  const chosen = pickEngineVoice(locale);
  if (chosen) utter.voice = chosen;
  window.speechSynthesis.speak(utter);
  return true;
}
