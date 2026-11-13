import { useMemo, useState } from "react";
import { CASE_TYPES, prepFor, prepText, type Prep } from "./courtroomPrep";
import { getLang, t, type Lang } from "./i18n";
import { downloadPdf } from "./planPdf";
import { getVoice, type VoiceId } from "./i18n";
import { speak, stop, isSupported } from "./readAloud";

type Props = {
  caseType?: string | null;
  lang?: Lang;
  onDefense?: (caseType: string | null) => void;
  onSpeakChange?: (on: boolean) => void;
  speaking?: boolean;
};

export default function CourtroomPrepScreen({ caseType, lang = getLang(), onDefense, speaking, onSpeakChange }: Props) {
  const [kind, setKind] = useState(caseType || "");
  const pack = useMemo(() => prepFor(kind, lang), [kind, lang]);
  return (
    <div className="prepPanel">
      <h2>{t("courtroomPrep", lang)}</h2>
      <p className="muted">{t("courtroomHint", lang)}</p>
      <label className="prepLabel" htmlFor="prep-type">Case type</label>
      <select id="prep-type" value={kind} onChange={(e) => setKind(e.target.value)}>
        {CASE_TYPES.map((row) => (
          <option key={row.id || "general"} value={row.id}>{lang === "es" ? row.label_es : row.label}</option>
        ))}
      </select>
      <PrepBody pack={pack} speaking={speaking} onSpeakChange={onSpeakChange} />
      <div className="ansActions">
        {onDefense && (
          <button type="button" className="ansBuild" onClick={() => onDefense(pack.caseType)}>{t("buildDefense", lang)}</button>
        )}
        <button type="button" className="ansMaker" onClick={() => downloadPdf(pack.title, prepText(pack), pack.notice)}>{t("downloadPdf", lang)}</button>
      </div>
      <p className="ansFootnote">{pack.disclaimer} {pack.notice}</p>
    </div>
  );
}

export function PrepBody({ pack, speaking, onSpeakChange }: { pack: Prep; speaking?: boolean; onSpeakChange?: (on: boolean) => void }) {
  const voice = getVoice();
  return (
    <>
      <div className="ansQuick">
        <span className="ansQuickLabel">{pack.language === "es" ? "Respuesta rápida" : "Quick answer"}</span>
        <p className="ansQuickText">{pack.quick}</p>
      </div>
      {isSupported() && voice !== "off" && (
        <div className="ansActions">
          <button type="button" className="ansMaker" onClick={() => {
            if (speaking) { stop(); onSpeakChange?.(false); return; }
            const ok = speak(prepText(pack), voice as VoiceId, pack.language);
            onSpeakChange?.(ok);
          }}>{speaking ? t("stopReading", pack.language) : t("readAloud", pack.language)}</button>
        </div>
      )}
      <div className="ansSections">
        {pack.sections.map((section) => (
          <details key={section.id} className="ansSec ansSec-info">
            <summary className="ansSum">
              <span className="ansSecTitle">{section.title}<span className="ansCount"> ({section.items.length})</span></span>
              <span className="ansChevron" aria-hidden="true" />
              <span className="ansPeek">{section.items[0]}</span>
            </summary>
            <div className="ansBody isStatic">
              <ul className="ansItems">
                {section.items.map((item, i) => <li key={i}><span className="ansHead">{item}</span></li>)}
              </ul>
            </div>
          </details>
        ))}
      </div>
    </>
  );
}
