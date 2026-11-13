import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { formatAnswer } from "./chatFormat";
import { continuityLine, lineId, loadThread, saveThread, type ChatLine } from "./chatThread";
import type { AiHelpReply, Continuity } from "./guestPublic";
import { aiHelpQuestionOnOpen } from "./aiHelpNav";
import { CITIZEN_DISCLAIMER, CITIZEN_FEATURES } from "./citizenHelp";
import {
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
  rightsTopics,
  type ScreenId,
} from "./approvedScreenCatalog";

type Scenario = "traffic" | "public" | "home" | "questioning" | "arrest" | "witness";

type Props = {
  signedIn: boolean;
  onSignIn: () => void;
  onCases: () => void;
  onAnalysis: () => void;
  onLogout: () => void;
  onRights: (scenario: Scenario) => void;
  onAsk: (question: string) => void;
  /** Current text of the page's main question field (read-only; AI Help never writes to it). */
  heroDraft?: string;
  askGuest?: (question: string) => Promise<AiHelpReply>;
  /** Server side of per-screen continuity (device token); every call may resolve to null for plain guests. */
  chatScreen?: {
    load: (feature: string) => Promise<Continuity | null>;
    startFresh: (feature: string) => Promise<void>;
    forgetTurn: (turn: number) => Promise<void>;
  };
};

const AI_FEATURE = "ai_help";
const AI_LABEL = "AI Help";
const browserStore = () => (typeof window !== "undefined" ? window.localStorage : undefined);

/** One answer, laid out as short sections instead of a wall of text. */
function AnswerBody({ text }: { text: string }) {
  return (
    <div className="chatAnswer">
      {formatAnswer(text).map((block, i) =>
        block.kind === "heading" ? (
          <h4 key={i}>{block.text}</h4>
        ) : block.kind === "list" ? (
          <ul key={i}>
            {block.items.map((item, j) => (
              <li key={j}>{item.lead && <b>{item.lead}: </b>}{item.text}</li>
            ))}
          </ul>
        ) : (
          <p key={i}>{block.text}</p>
        ),
      )}
    </div>
  );
}

export default function ApprovedScreens(props: Props) {
  const [drawer, setDrawer] = useState(false);
  const [panel, setPanel] = useState<ScreenId>("home");
  const [titleNumber, setTitleNumber] = useState(16);
  const [codeTab, setCodeTab] = useState(true);
  const [dark, setDark] = useState(true);
  const [question, setQuestion] = useState("");
  const aiQuestionRef = useRef<HTMLTextAreaElement>(null);
  // AI Help keeps its own thread on this device and resumes it; other screens keep theirs.
  const [chat, setChat] = useState<ChatLine[]>(() => loadThread(browserStore(), AI_FEATURE));
  const [chatBusy, setChatBusy] = useState(false);
  const [chatNotice, setChatNotice] = useState("");
  const [carryLine, setCarryLine] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);
  const title = lawTitles.find((row) => row.number === titleNumber) || lawTitles[0];

  async function sendGuestChat() {
    const textValue = question.trim();
    if (!textValue || chatBusy) return;
    const asked: ChatLine = { id: lineId(), role: "user", text: textValue };
    setChat((rows) => [...rows, asked]);
    setQuestion("");
    setChatBusy(true);
    setChatNotice("");
    try {
      if (!props.askGuest) {
        props.onAsk(textValue);
        setChat((rows) => [...rows, { id: lineId(), role: "assistant", text: "Sent to guest research on /public/rights-assistant. This chat does not open a private case." }]);
        return;
      }
      const reply = await props.askGuest(textValue);
      const turn = reply.turnId;
      setChat((rows) => [
        ...rows.map((row) => (row.id === asked.id ? { ...row, turn } : row)),
        { id: lineId(), role: "assistant", text: reply.answer || "No grounded answer was returned.", turn },
      ]);
      const carried = continuityLine(reply.continuity, AI_LABEL);
      if (carried) setCarryLine(carried);
      setChatNotice(reply.notice || "");
    } catch (error) {
      setChatNotice(error instanceof Error ? error.message : "Guest research is unavailable.");
    } finally {
      setChatBusy(false);
      aiQuestionRef.current?.focus();
    }
  }

  function deleteLine(line: ChatLine) {
    if (!window.confirm("Delete this message? It will be removed from this chat. This can't be undone.")) return;
    // Deleting either half of a question-and-answer also stops the AI from building on it.
    setChat((rows) => rows.filter((row) => row.id !== line.id && !(line.turn && row.turn === line.turn)));
    if (line.turn) props.chatScreen?.forgetTurn(line.turn).catch(() => undefined);
  }

  function startFresh() {
    if (!window.confirm("Start fresh? This screen's messages will be deleted and the AI won't build on them. This can't be undone.")) return;
    setChat([]);
    setCarryLine("");
    setChatNotice("");
    props.chatScreen?.startFresh(AI_FEATURE).catch(() => undefined);
  }

  useEffect(() => saveThread(browserStore(), AI_FEATURE, chat), [chat]);

  // Signing out clears saved chats; show the (now empty) saved thread.
  useEffect(() => {
    if (!props.signedIn) setChat(loadThread(browserStore(), AI_FEATURE));
  }, [props.signedIn]);

  // Opening AI Help shows at most one quiet line about the last topic elsewhere in the app.
  useEffect(() => {
    if (panel !== "ai" || !props.chatScreen) return;
    let live = true;
    props.chatScreen.load(AI_FEATURE).then((c) => { if (live) setCarryLine(continuityLine(c, AI_LABEL)); }).catch(() => undefined);
    return () => { live = false; };
  }, [panel, props.chatScreen]);

  // Keep the newest message (or the typing indicator) in view, without jumping.
  useLayoutEffect(() => {
    if (panel !== "ai") return;
    const end = chatEndRef.current;
    if (!end || typeof end.scrollIntoView !== "function") return;
    const reduce = typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    end.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "end" });
  }, [chat.length, chatBusy, panel]);

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
      // Opening AI Help must not invent or submit a question, or touch the main search field.
      setQuestion((current) => aiHelpQuestionOnOpen(current, props.heroDraft));
    }
    if (id === "rights") props.onRights("public");
    setPanel(id);
    setDrawer(false);
  }

  useEffect(() => {
    if (panel === "ai") aiQuestionRef.current?.focus();
  }, [panel]);

  return (
    <section className="approvedShell" aria-label="STANDALONE ASSISTANT screens">
      <div className="approvedBar">
        <button type="button" onClick={() => setDrawer(true)} aria-label="Open menu">Menu</button>
        <b>STANDALONE ASSISTANT</b>
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
          <button type="button" key={item.id} className="approvedTile" onClick={() => open(item.id)}>
            <strong>{item.label}</strong>
            <span>{item.hint}</span>
          </button>
        ))}
      </div>
      <button type="button" className="approvedEmergency" onClick={() => open("emergency")}>
        Emergency Help
        <small>Important contacts. Call 911 if someone is in danger.</small>
      </button>
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
                  <button type="button" key={topic.id} onClick={() => props.onRights(topic.scenario)}>{topic.label}</button>
                ))}
              </div>
            </>
          )}
          {panel === "resources" && (
            <>
              <h2>Resources</h2>
              <p className="muted">{CITIZEN_DISCLAIMER}</p>
              <h3>Citizen Help</h3>
              <ul className="citizenHelpList">
                {CITIZEN_FEATURES.map((f) => (
                  <li key={f.id}>
                    <b>{f.title}</b>
                    <span> — {f.blurb}</span>
                    <div className="citizenHelpLinks">
                      {f.links.map((l) => (
                        <a key={l.url} href={l.url} target="_blank" rel="noreferrer">{l.label}</a>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>

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
              <div className="chatHead">
                <h2>AI Help</h2>
                {chat.length > 0 && (
                  <button type="button" className="chatFresh" onClick={startFresh}>Start fresh</button>
                )}
              </div>
              {carryLine && <p className="chatCarry">{carryLine}</p>}
              <div className="approvedChat" aria-live="polite" aria-busy={chatBusy}>
                {chat.length === 0 && !chatBusy && (
                  <p className="chatEmpty">Ask a Georgia legal question. Follow-ups build on what you asked before. Answers are information, not legal advice.</p>
                )}
                {chat.map((line) => (
                  <div key={line.id} className={line.role === "user" ? "chatMsg approvedUser" : "chatMsg approvedAssistant"}>
                    {line.role === "user" ? <p className="chatText">{line.text}</p> : <AnswerBody text={line.text} />}
                    <button type="button" className="approvedChatDelete" aria-label="Delete this message" title="Delete this message" onClick={() => deleteLine(line)}>
                      Delete
                    </button>
                  </div>
                ))}
                {chatBusy && (
                  <div className="chatMsg approvedAssistant chatTyping" role="status" aria-label="Getting your answer">
                    <span /><span /><span />
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              <div className="chatComposer">
                <label className="chatLabel" htmlFor="ai-help-question">Question</label>
                <textarea
                  ref={aiQuestionRef}
                  id="ai-help-question"
                  rows={2}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                      event.preventDefault();
                      void sendGuestChat();
                    }
                  }}
                  placeholder={chat.length ? "Ask a follow-up…" : "Example: what should I say if I am stopped?"}
                />
                <button type="button" onClick={sendGuestChat} disabled={chatBusy || !question.trim()}>Send</button>
              </div>
              {chatNotice && <p className="chatNotice">{chatNotice}</p>}
              <p className="chatNotice">{SAFETY_NOTICE}</p>
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
