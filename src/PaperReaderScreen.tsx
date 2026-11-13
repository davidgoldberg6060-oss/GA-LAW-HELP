import { useRef, useState } from "react";
import { structureAnswer } from "./answerSections";
import { getLang, getVoice, t, type Lang, type VoiceId } from "./i18n";
import { downloadPdf } from "./planPdf";
import { isSupported, speak, stop } from "./readAloud";
import type { PaperResult, ReadPaper, TranslatePaper } from "./paperApi";

type Props = {
  lang?: Lang;
  readPaper?: ReadPaper;
  translatePaper?: TranslatePaper;
  onDefense?: (result: PaperResult) => void;
  onPrep?: (caseType: string | null) => void;
};

export default function PaperReaderScreen({ lang = getLang(), readPaper, translatePaper, onDefense, onPrep }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<PaperResult | null>(null);
  const [speaking, setSpeaking] = useState(false);
  const voice = getVoice();

  async function run(list: File[], translate: boolean) {
    if (!readPaper) {
      setError("Paper reading is not connected right now.");
      return;
    }
    if (!list.length) {
      setError("Add a photo or PDF of the paper first.");
      return;
    }
    setError("");
    setBusy(translate ? "Photographing and translating…" : "Reading your paper…");
    try {
      const out = await readPaper(list, { translate });
      setResult(out);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The paper could not be read.");
    } finally {
      setBusy("");
    }
  }

  async function translateExisting() {
    if (!result || !translatePaper) return;
    setBusy("Translating to Spanish…");
    setError("");
    try {
      setResult(await translatePaper(result));
    } catch (err) {
      setError(err instanceof Error ? err.message : "The paper could not be translated.");
    } finally {
      setBusy("");
    }
  }

  const answer = result?.answer || "";
  const structured = answer ? structureAnswer(answer) : null;
  const caseType = result?.defense_plan && typeof (result.defense_plan as { case_type?: string }).case_type === "string"
    ? (result.defense_plan as { case_type?: string }).case_type || null
    : null;

  return (
    <div className="paperPanel">
      <h2>{t("paperReader", lang)}</h2>
      <p className="muted">{t("paperHint", lang)}</p>
      <div className="paperActions">
        <button type="button" className="ansBuild" onClick={() => cameraRef.current?.click()}>{t("takePhoto", lang)}</button>
        <button type="button" className="ansMaker" onClick={() => fileRef.current?.click()}>{t("chooseFile", lang)}</button>
        <button type="button" className="ansMaker" onClick={() => {
          const list = files.length ? files : Array.from(cameraRef.current?.files || []);
          void run(list, true);
        }}>{t("photoAndTranslate", lang)}</button>
      </div>
      <input ref={cameraRef} className="fileHidden" type="file" accept="image/*" capture="environment" multiple
        onChange={(e) => { const list = Array.from(e.target.files || []); setFiles(list); if (list.length) void run(list, false); }} />
      <input ref={fileRef} className="fileHidden" type="file" accept="image/*,application/pdf" multiple
        onChange={(e) => { const list = Array.from(e.target.files || []); setFiles(list); if (list.length) void run(list, false); }} />
      {files.length > 0 && <p className="muted">{files.length} file{files.length === 1 ? "" : "s"} selected.</p>}
      {busy && <p className="chatNotice" role="status">{busy}</p>}
      {error && <p className="paperError" role="alert">{error}</p>}
      {structured && (
        <div className="chatAnswer paperResult">
          {structured.quick && (
            <div className="ansQuick">
              <span className="ansQuickLabel">Quick answer</span>
              <p className="ansQuickText">{structured.quick}</p>
            </div>
          )}
          <div className="ansSections">
            {structured.sections.map((section) => (
              <details key={section.id} className={"ansSec ansSec-" + section.kind}>
                <summary className="ansSum">
                  <span className="ansSecTitle">{section.title}{section.items.length > 0 && <span className="ansCount"> ({section.items.length})</span>}</span>
                  <span className="ansChevron" aria-hidden />
                  {section.items[0] && <span className="ansPeek">{section.items[0].head}</span>}
                </summary>
                <div className="ansBody isStatic">
                  <ul className="ansItems">
                    {section.items.map((item, i) => (
                      <li key={i}>
                        <span className="ansHead">{item.head}</span>
                        {item.detail && <span className="ansDetail">{item.detail}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              </details>
            ))}
          </div>
          {structured.note && <p className="ansFootnote">{structured.note}</p>}
          {result?.translation_notice && <p className="ansFootnote translationNotice">{result.translation_notice}</p>}
          <div className="ansActions">
            {onDefense && <button type="button" className="ansBuild" onClick={() => onDefense(result!)}>{t("buildDefense", lang)}</button>}
            {onPrep && <button type="button" className="ansMaker" onClick={() => onPrep(caseType)}>{t("courtroomPrep", lang)}</button>}
            {translatePaper && !result?.answer_es && (
              <button type="button" className="ansMaker" onClick={() => void translateExisting()}>{t("translateSpanish", lang)}</button>
            )}
            <button type="button" className="ansMaker" onClick={() => downloadPdf("Paper reading", answer, t("notice", lang))}>{t("downloadPdf", lang)}</button>
            {isSupported() && voice !== "off" && (
              <button type="button" className="ansMaker" onClick={() => {
                if (speaking) { stop(); setSpeaking(false); return; }
                const text = result?.answer_es || answer;
                setSpeaking(speak(text, voice as VoiceId, result?.answer_es ? "es" : lang));
              }}>{speaking ? t("stopReading", lang) : t("readAloud", lang)}</button>
            )}
          </div>
          {result?.defense_plan?.answer && (
            <div className="paperPlan">
              <p className="ansPlan">Your Defense Plan</p>
              <p className="muted">A defense plan was built from this paper. Open it below or tap Build my defense to rebuild it.</p>
              <details>
                <summary>Show the defense plan</summary>
                <pre className="planPre">{result.defense_plan.answer}</pre>
                <button type="button" className="ansMaker" onClick={() => downloadPdf("Your Defense Plan", result.defense_plan?.answer || "", t("notice", lang))}>{t("sharePdf", lang)}</button>
              </details>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
