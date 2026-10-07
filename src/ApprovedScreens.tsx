import { useState } from "react";
import {
  AI_HELP_LIMIT,
  APPEALS_OPINIONS_URL,
  CODE_REVISION_URL,
  SAFETY_NOTICE,
  UNANNOTATED_RELEASE_URL,
  courtLinks,
  drawerItems,
  formGroups,
  homeTiles,
  lawTitles,
  resourceLinks,
  rightsNotes,
  rightsTopics,
  type ScreenId,
} from "./approvedScreenCatalog";

type Scenario = "traffic" | "public" | "home" | "questioning" | "arrest" | "witness";
type ChatLine = { role: "you" | "guest"; text: string };

type Props = {
  signedIn: boolean;
  onSignIn: () => void;
  onCases: () => void;
  onAnalysis: () => void;
  onLogout: () => void;
  onRights: (scenario: Scenario) => void;
  onAsk: (question: string) => void;
};

export default function ApprovedScreens(props: Props) {
  const [drawer, setDrawer] = useState(false);
  const [panel, setPanel] = useState<ScreenId>("home");
  const [titleNumber, setTitleNumber] = useState(16);
  const [codeTab, setCodeTab] = useState(true);
  const [dark, setDark] = useState(true);
  const [question, setQuestion] = useState("");
  const [rightsId, setRightsId] = useState<(typeof rightsTopics)[number]["id"]>("encounter");
  const [chat, setChat] = useState<ChatLine[]>([
    { role: "guest", text: AI_HELP_LIMIT },
  ]);
  const title = lawTitles.find((row) => row.number === titleNumber) || lawTitles[0];

  function sendGuestQuestion(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    setChat((lines) => [
      ...lines,
      { role: "you", text: trimmed },
      { role: "guest", text: `${AI_HELP_LIMIT} ${SAFETY_NOTICE}` },
    ]);
    props.onAsk(trimmed);
    setQuestion("");
  }

  function open(id: ScreenId) {
    if ((id === "cases" || id === "analysis") && !props.signedIn) {
      props.onSignIn();
      return;
    }
    if (id === "cases") {
      props.onCases();
      return;
    }
    if (id === "analysis") {
      props.onAnalysis();
      return;
    }
    if (id === "logout") {
      props.onLogout();
      setDrawer(false);
      return;
    }
    if (id === "dark") {
      const next = !dark;
      setDark(next);
      document.documentElement.dataset.theme = next ? "navy" : "light";
      setPanel("dark");
      setDrawer(false);
      return;
    }
    if (id === "ai") {
      setPanel("ai");
      setDrawer(false);
      return;
    }
    if (id === "rights") props.onRights("public");
    setPanel(id);
    setDrawer(false);
  }

  return (
    <section className="approvedShell" aria-label="GA.LAW.HELP screens">
      <div className="approvedBar">
        <button type="button" onClick={() => setDrawer(true)} aria-label="Open menu">Menu</button>
        <b>GA.LAW.HELP</b>
        <button type="button" onClick={() => open("laws")}>Laws</button>
      </div>
      {drawer && (
        <div className="approvedDrawer" role="dialog" aria-label="Navigation">
          <button type="button" className="approvedClose" onClick={() => setDrawer(false)}>Close</button>
          {drawerItems.map((item) => (
            <button type="button" key={item.id} onClick={() => open(item.id)}>
              {item.label}
              <small>{item.requiresSignIn ? "Sign in required" : item.hint}</small>
            </button>
          ))}
        </div>
      )}
      <div className="approvedGrid">
        {homeTiles.map((item) => (
          <button type="button" key={item.id} className={item.id === "emergency" ? "approvedTile approvedEmergencyTile" : "approvedTile"} onClick={() => open(item.id)}>
            <strong>{item.label}</strong>
            <span>{item.hint}</span>
          </button>
        ))}
      </div>
      {panel !== "home" && (
        <div className="approvedPanel">
          {panel === "laws" && (
            <>
              <h2>Georgia Laws</h2>
              <p>Unannotated official indexes only. No Lexis editor notes and no pasted section text.</p>
              <div className="approvedChips">
                {lawTitles.map((row) => (
                  <button type="button" key={row.number} className={row.number === title.number ? "on" : ""} onClick={() => setTitleNumber(row.number)}>
                    Title {row.number} · {row.name}
                  </button>
                ))}
              </div>
              <div className="approvedTabs">
                <button type="button" className={codeTab ? "on" : ""} onClick={() => setCodeTab(true)}>Code</button>
                <button type="button" className={!codeTab ? "on" : ""} onClick={() => setCodeTab(false)}>Case Law</button>
              </div>
              {codeTab ? (
                <p>
                  <a href={title.codeIndexUrl}>Code Revision Commission</a>
                  {" · "}
                  <a href={UNANNOTATED_RELEASE_URL}>Unannotated electronic release</a>
                  {" · "}
                  <a href={CODE_REVISION_URL}>Official index</a>
                </p>
              ) : (
                <p>
                  <a href={title.caseLawIndexUrl}>Opinion index for Title {title.number}</a>
                  {" · "}
                  <a href={APPEALS_OPINIONS_URL}>Court of Appeals</a>
                </p>
              )}
              <label>
                Guest question
                <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask without opening a private case" />
              </label>
              <button type="button" onClick={() => props.onAsk(`Title ${title.number} ${title.name}. ${question}`.trim())}>Ask on guest research</button>
            </>
          )}
          {panel === "forms" && (
            <>
              <h2>Legal Forms</h2>
              {formGroups.map((group) => (
                <p key={group.id}><a href={group.url}>{group.label} forms index</a> — {group.note}</p>
              ))}
            </>
          )}
          {panel === "court" && (
            <>
              <h2>Court Info</h2>
              {courtLinks.map((link) => <p key={link.url}><a href={link.url}>{link.title}</a></p>)}
              <p>Court pages are indexes, not a claim that a rule or opinion is current.</p>
            </>
          )}
          {panel === "tools" && (
            <>
              <h2>Legal Tools</h2>
              <p>Public tools open official rule and code indexes. Motion screening for a saved case stays login-only.</p>
              <p><a href={CODE_REVISION_URL}>Unannotated code index</a> · <a href="https://www.gasupreme.us/rules/">Supreme Court rules</a></p>
            </>
          )}
          {panel === "rights" && (
            <>
              <h2>Know Your Rights</h2>
              <p>Guest help stays on /public/rights-assistant. {SAFETY_NOTICE}</p>
              <div className="approvedChips">
                {rightsTopics.map((topic) => (
                  <button type="button" key={topic.id} className={rightsId === topic.id ? "on" : ""} onClick={() => { setRightsId(topic.id); props.onRights(topic.scenario); }}>{topic.label}</button>
                ))}
              </div>
              <p>{rightsNotes[rightsId]}</p>
            </>
          )}
          {panel === "resources" && (
            <>
              <h2>Resources</h2>
              {resourceLinks.map((link) => <p key={link.url}><a href={link.url}>{link.title}</a></p>)}
            </>
          )}
          {panel === "emergency" && (
            <>
              <h2>Emergency Help</h2>
              <p>If someone is in immediate danger or needs medical help, call 911. Do not resist officers and do not lie.</p>
              <p><a href="https://www.georgialegalaid.org/">GeorgiaLegalAid.org</a></p>
            </>
          )}
          {panel === "ai" && (
            <>
              <h2>AI Help</h2>
              <div className="approvedChat" aria-live="polite">
                {chat.map((line, index) => (
                  <p key={`${line.role}-${index}`} className={line.role === "you" ? "you" : "guest"}>
                    <strong>{line.role === "you" ? "You" : "Guest help"}</strong> {line.text}
                  </p>
                ))}
              </div>
              <label>
                Question
                <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask without signing in" />
              </label>
              <button type="button" onClick={() => sendGuestQuestion(question)}>Send to guest research</button>
            </>
          )}
          {panel === "settings" && (
            <>
              <h2>Settings</h2>
              <p>{props.signedIn ? "Signed in. Private cases remain login-only." : "Guest mode. Sign in only for My Cases and Case Analysis."}</p>
              <p>Dark mode is {dark ? "on" : "off"}.</p>
            </>
          )}
          {panel === "dark" && <h2>Dark mode {dark ? "on" : "off"}</h2>}
        </div>
      )}
    </section>
  );
}
