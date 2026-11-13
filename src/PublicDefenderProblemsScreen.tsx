import { useMemo, useState } from "react";
import { guide, guideText, type GuideTemplate } from "./publicDefenderProblems";
import { getLang, t, type Lang } from "./i18n";
import { downloadPdf } from "./planPdf";

type Props = {
  lang?: Lang;
  onOpenMotions?: (motionKey: string) => void;
  onOpenDefenders?: () => void;
};

export default function PublicDefenderProblemsScreen({ lang = getLang(), onOpenMotions, onOpenDefenders }: Props) {
  const pack = useMemo(() => guide(lang), [lang]);
  const [openTmpl, setOpenTmpl] = useState<string | null>("motion_discharge");
  return (
    <div className="prepPanel">
      <h2>{pack.title}</h2>
      <p className="muted">{pack.hint}</p>
      {onOpenDefenders && (
        <div className="ansActions">
          <button type="button" className="ansMaker" onClick={onOpenDefenders}>{t("publicDefenders", lang)}</button>
        </div>
      )}
      <div className="ansQuick">
        <span className="ansQuickLabel">{lang === "es" ? "Respuesta rápida" : "Quick answer"}</span>
        <p className="ansQuickText">{pack.quick}</p>
      </div>
      <div className="ansSections">
        {pack.sections.map((section, idx) => (
          <details key={section.id} className="ansSec ansSec-info" open={idx < 2}>
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
        <details className="ansSec ansSec-info" open>
          <summary className="ansSum">
            <span className="ansSecTitle">{lang === "es" ? "Plantillas" : "Templates"}<span className="ansCount"> ({pack.templates.length})</span></span>
            <span className="ansChevron" aria-hidden="true" />
            <span className="ansPeek">{pack.templates[0]?.title}</span>
          </summary>
          <div className="ansBody isStatic">
            <div className="ansItems">
              {pack.templates.map((tmpl) => (
                <TemplateBlock
                  key={tmpl.id}
                  tmpl={tmpl}
                  open={openTmpl === tmpl.id}
                  onToggle={() => setOpenTmpl(openTmpl === tmpl.id ? null : tmpl.id)}
                  lang={lang}
                  onOpenMotions={onOpenMotions}
                />
              ))}
            </div>
          </div>
        </details>
      </div>
      <div className="ansActions">
        <button type="button" className="ansMaker" onClick={() => downloadPdf(pack.title, guideText(pack), pack.notice)}>{t("downloadPdf", lang)}</button>
      </div>
      <p className="ansFootnote">{pack.disclaimer} {pack.notice}</p>
      <p className="citizenHelpLinks">
        {pack.links.map((link) => (
          <a key={link.url} href={link.url} target="_blank" rel="noreferrer">{link.label}</a>
        ))}
      </p>
    </div>
  );
}

function TemplateBlock({ tmpl, open, onToggle, lang, onOpenMotions }: {
  tmpl: GuideTemplate; open: boolean; onToggle: () => void; lang: Lang; onOpenMotions?: (motionKey: string) => void;
}) {
  return (
    <div>
      <button type="button" className="ansChip" onClick={onToggle}>{tmpl.title}</button>
      {open && (
        <>
          <pre className="pdTemplate">{tmpl.body}</pre>
          <div className="ansActions">
            {tmpl.motionKey && onOpenMotions && (
              <button type="button" className="ansBuild" onClick={() => onOpenMotions(tmpl.motionKey!)}>{t("openMotionMaker", lang)}</button>
            )}
            <button type="button" className="ansMaker" onClick={() => { void navigator.clipboard?.writeText(tmpl.body); }}>{lang === "es" ? "Copiar" : "Copy"}</button>
          </div>
        </>
      )}
    </div>
  );
}
