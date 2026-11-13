import { useMemo, useState } from "react";
import { barDirectory, FIND_TOOL_URL, OFFICE_COUNT, outcomeNote, searchOffices, SOURCE_URL, CHECKED_ON, type Office } from "./publicDefenderOffices";
import { getLang, t, type Lang } from "./i18n";

type Props = {
  lang?: Lang;
  onOpenProblems?: () => void;
};

export default function PublicDefendersScreen({ lang = getLang(), onOpenProblems }: Props) {
  const [q, setQ] = useState("");
  const [picked, setPicked] = useState<string | null>(null);
  const bar = useMemo(() => barDirectory(lang), [lang]);
  const note = useMemo(() => outcomeNote(lang), [lang]);
  const rows = useMemo(() => searchOffices(q), [q]);
  const selected = rows.find((o) => o.id === picked) || null;
  return (
    <div className="prepPanel">
      <h2>{t("publicDefenders", lang)}</h2>
      <p className="muted">{t("publicDefendersHint", lang)}</p>
      <div className="ansQuick">
        <span className="ansQuickLabel">{lang === "es" ? "Respuesta rápida" : "Quick answer"}</span>
        <p className="ansQuickText">{t("publicDefendersQuick", lang)}</p>
      </div>
      <label className="prepLabel" htmlFor="pd-office-search">{t("findOffice", lang)}</label>
      <input id="pd-office-search" value={q} onChange={(e) => { setQ(e.target.value); setPicked(null); }} placeholder={t("findOfficePlaceholder", lang)} />
      <p className="muted">{lang === "es" ? `${rows.length} de ${OFFICE_COUNT} oficinas` : `${rows.length} of ${OFFICE_COUNT} offices`}</p>
      <ul className="pdOfficeList">
        {rows.map((office) => (
          <li key={office.id}>
            <button type="button" className={"pdOfficeBtn" + (picked === office.id ? " on" : "")} onClick={() => setPicked(picked === office.id ? null : office.id)}>
              <b>{office.circuit}</b>
              <span>{office.counties.join(", ")}{office.opt_out ? (lang === "es" ? " · oficina independiente" : " · independent office") : ""}</span>
            </button>
            {picked === office.id && selected && <OfficeCard office={selected} lang={lang} />}
          </li>
        ))}
      </ul>
      {rows.length === 0 && <p className="muted">{t("noOfficeMatch", lang)}</p>}
      <p className="muted">{lang === "es" ? `Fuente: Georgia Public Defender Council, revisado el ${CHECKED_ON}.` : `Source: Georgia Public Defender Council, checked ${CHECKED_ON}.`} <a href={SOURCE_URL} target="_blank" rel="noreferrer">circuits.json</a> · <a href={FIND_TOOL_URL} target="_blank" rel="noreferrer">{lang === "es" ? "Buscar en el sitio del GPDC" : "GPDC find tool"}</a></p>

      <div className="ansSec ansSec-info isOpen" style={{ padding: "0.8rem 0.95rem", marginTop: "0.8rem" }}>
        <h3 style={{ color: "#e2b54e", margin: "0 0 0.4rem" }}>{bar.label}</h3>
        <p>{bar.explainer}</p>
        <div className="ansActions">
          <a className="ansBuild" href={bar.url} target="_blank" rel="noreferrer">{t("openBarDirectory", lang)}</a>
          <a className="ansMaker" href={bar.disciplineUrl} target="_blank" rel="noreferrer">{t("publicDisciplineExplainer", lang)}</a>
        </div>
      </div>

      <div className="ansSec ansSec-info isOpen" style={{ padding: "0.8rem 0.95rem", marginTop: "0.8rem" }}>
        <h3 style={{ color: "#e2b54e", margin: "0 0 0.4rem" }}>{t("pdProblems", lang)}</h3>
        <p>{t("pdProblemsHint", lang)}</p>
        {onOpenProblems && (
          <div className="ansActions">
            <button type="button" className="ansBuild" onClick={onOpenProblems}>{t("pdProblems", lang)}</button>
          </div>
        )}
      </div>
      <p className="ansFootnote">{note} {t("notice", lang)}</p>
    </div>
  );
}

function OfficeCard({ office, lang }: { office: Office; lang: Lang }) {
  return (
    <div className="pdOfficeCard">
      {office.opt_out_note && <p className="muted">{office.opt_out_note}</p>}
      {office.defender ? <p><b>{lang === "es" ? "Defensor público del circuito: " : "Circuit public defender: "}</b>{office.defender}</p> : <p className="muted">{lang === "es" ? "El GPDC no publicó el nombre del defensor público de este circuito." : "GPDC did not publish the circuit public defender's name for this office."}</p>}
      {office.address && <p>{office.address}</p>}
      {office.phone && <p><a href={"tel:" + office.phone.replace(/[^0-9]/g, "")}>{office.phone}</a></p>}
      {office.fax && <p>Fax: {office.fax}</p>}
      {office.email && <p><a href={"mailto:" + office.email}>{office.email}</a></p>}
      {office.hours && <p>{office.hours}</p>}
      {office.website && <p><a href={office.website} target="_blank" rel="noreferrer">{office.website}</a></p>}
      {(office.additional_offices || []).map((extra, i) => (
        <p key={i}><b>{extra.location || (lang === "es" ? "Oficina satélite" : "Satellite office")}:</b> {[extra.address, extra.phone].filter(Boolean).join(" · ")}</p>
      ))}
      {office.juvenile && (office.juvenile.name || office.juvenile.phone) && (
        <p><b>{lang === "es" ? "Contacto juvenil publicado: " : "Published juvenile contact: "}</b>{[office.juvenile.name, office.juvenile.phone].filter(Boolean).join(" · ")}</p>
      )}
      <p><a href={office.page_url} target="_blank" rel="noreferrer">{lang === "es" ? "Página oficial del GPDC" : "Official GPDC office page"}</a></p>
    </div>
  );
}
