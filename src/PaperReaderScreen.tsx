import { useRef, useState } from "react";
import { structureAnswer } from "./answerSections";
import { getLang, getVoice, t, type Lang, type VoiceId } from "./i18n";
import { canAddMore, capIncoming, counterLabel, MAX_PAGES_PER_BATCH } from "./pageBatch";
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
  const [notice, setNotice] = useState("");
  const [result, setResult] = useState<PaperResult | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [awaitingNext, setAwaitingNext] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const voice = getVoice();
  const room = Math.max(0, MAX_PAGES_PER_BATCH - files.length);
  const addEnabled = canAddMore(files.length) && !busy && !awaitingNext;

  function takeFiles(list: File[]) {
    if (awaitingNext) return;
    const next = capIncoming(files, list, MAX_PAGES_PER_BATCH, lang);
    setFiles(next.pages);
    setNotice(next.message);
    if (next.message) setError("");
  }

  function clearFileInputs() {
    if (fileRef.current) fileRef.current.value = "";
    if (cameraRef.current) cameraRef.current.value = "";
  }

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
    setNotice("");
    setBusy(translate ? "Photographing and translating…" : "Reading your paper…");
    try {
      const out = await readPaper(list, { translate, sessionId: sessionId || undefined });
      setResult(out);
      if (out.session_id) setSessionId(out.session_id);
      setFiles([]);
      clearFileInputs();
      setAwaitingNext(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The paper could not be read.");
    } finally {
      setBusy("");
    }
  }

  function addMorePages() {
    setAwaitingNext(false);
    setFiles([]);
    setError("");
    setNotice("");
    clearFileInputs();
  }

  function startNewCase() {
    setAwaitingNext(false);
    setSessionId("");
    setFiles([]);
    setResult(null);
    setError("");
    setNotice("");
    clearFileInputs();
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
  const totalPages = result?.pages_total || result?.pages_this_batch || 0;

  return (
    <div className="paperPanel">
      <h2>{t("paperReader", lang)}</h2>
      <p className="muted">{t("paperHint", lang)}</p>
      <p className="pageCounter" aria-live="polite">
        <strong>{counterLabel(awaitingNext ? 0 : files.length, MAX_PAGES_PER_BATCH, lang)}</strong>
        <span className="pageLimitNote">{t("pageLimitNote", lang)}</span>
      </p>
      {awaitingNext ? (
        <div className="paperContinue">
          <p className="muted">
            {totalPages > 0 ? (lang === "es" ? `${totalPages} páginas leídas en este caso. ` : `${totalPages} page${totalPages === 1 ? "" : "s"} read in this case. `) : ""}
            {t("afterBatchHint", lang)}
          </p>
          <div className="paperActions">
            <button type="button" className="ansBuild" onClick={addMorePages}>{t("addMorePages", lang)}</button>
            <button type="button" className="ansMaker" onClick={startNewCase}>{t("startNewCase", lang)}</button>
          </div>
        </div>
      ) : (
        <>
          <div className="paperActions">
            <button type="button" className="ansBuild" disabled={!addEnabled} onClick={() => cameraRef.current?.click()}>{t("takePhoto", lang)}</button>
            <button type="button" className="ansMaker" disabled={!addEnabled} onClick={() => fileRef.current?.click()}>{t("chooseFile", lang)}</button>
            <button type="button" className="ansMaker" disabled={!files.length || !!busy} onClick={() => void run(files, true)}>{t("photoAndTranslate", lang)}</button>
            <button type="button" className="ansBuild" disabled={!files.length || !!busy} onClick={() => void run(files, false)}>{t("readPaper", lang)}</button>
          </div>
          <input ref={cameraRef} className="fileHidden" type="file" accept="image/*" capture="environment" multiple
            onChange={(e) => { takeFiles(Array.from(e.target.files || [])); e.target.value = ""; }} />
          <input ref={fileRef} className="fileHidden" type="file" accept="image/*,application/pdf" multiple
            onChange={(e) => { takeFiles(Array.from(e.target.files || [])); e.target.value = ""; }} />
          {files.length > 0 && (
            <ul className="pageList">
              {files.map((file, i) => (
                <li key={file.name + i}>
                  <span>{file.name || `Page ${i + 1}`}</span>
                  <button type="button" className="pageRemove" onClick={() => { setFiles(files.filter((_, j) => j !== i)); setNotice(""); }}>{t("removePage", lang)}</button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
      {room === 0 && !awaitingNext && <p className="muted">{t("afterBatchHint", lang)}</p>}
      {notice && <p className="paperNotice" role="status">{notice}</p>}
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
