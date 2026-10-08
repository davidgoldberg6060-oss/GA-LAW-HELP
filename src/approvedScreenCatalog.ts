/** Navy and gold screen catalog. Official indexes only; no invented code text. */
export const NAVY = "#02111d";
export const GOLD = "#e2b54e";

export type ScreenId =
  | "home"
  | "cases"
  | "ai"
  | "tools"
  | "laws"
  | "court"
  | "forms"
  | "analysis"
  | "rights"
  | "resources"
  | "emergency"
  | "dark"
  | "settings"
  | "logout";

export type ScreenItem = { id: ScreenId; label: string; hint: string; requiresSignIn: boolean };

export const homeTiles: ScreenItem[] = [
  { id: "cases", label: "My Cases", hint: "Track and manage", requiresSignIn: true },
  { id: "ai", label: "AI Help", hint: "Ask legal questions", requiresSignIn: false },
  { id: "tools", label: "Legal Tools", hint: "Official rules indexes", requiresSignIn: false },
  { id: "laws", label: "Georgia Laws", hint: "Statutes and cases", requiresSignIn: false },
  { id: "court", label: "Court Info", hint: "Courts and procedure", requiresSignIn: false },
  { id: "forms", label: "Legal Forms", hint: "Criminal, civil, family", requiresSignIn: false },
  { id: "analysis", label: "Case Analysis", hint: "Upload stays private", requiresSignIn: true },
  { id: "rights", label: "Know Your Rights", hint: "Guest rights help", requiresSignIn: false },
  { id: "resources", label: "Resources", hint: "Help and support", requiresSignIn: false },
];

export const drawerItems: ScreenItem[] = [
  { id: "home", label: "Home", hint: "Dashboard", requiresSignIn: false },
  ...homeTiles,
  { id: "emergency", label: "Emergency Help", hint: "Call 911 for danger", requiresSignIn: false },
  { id: "dark", label: "Dark Mode", hint: "Navy and gold", requiresSignIn: false },
  { id: "settings", label: "Settings", hint: "Account and notices", requiresSignIn: false },
  { id: "logout", label: "Log Out", hint: "End this session", requiresSignIn: false },
];

export type LawTitle = { number: number; name: string; codeIndexUrl: string; caseLawIndexUrl: string };

export const CODE_REVISION_URL = "https://www.legis.ga.gov/joint-offices/code-revision";
export const UNANNOTATED_RELEASE_URL = "https://archive.org/details/gov.ga.ocga.2018";
export const SUPREME_OPINIONS_URL = "https://www.gasupreme.us/opinions/";
export const APPEALS_OPINIONS_URL = "https://www.gaappeals.us/";

export const lawTitles: LawTitle[] = [
  { number: 16, name: "Crimes and Offenses", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: SUPREME_OPINIONS_URL },
  { number: 17, name: "Criminal Procedure", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: SUPREME_OPINIONS_URL },
  { number: 19, name: "Domestic Relations", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: APPEALS_OPINIONS_URL },
  { number: 40, name: "Motor Vehicles and Traffic", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: APPEALS_OPINIONS_URL },
  { number: 42, name: "Penal Institutions", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: SUPREME_OPINIONS_URL },
  { number: 44, name: "Property", codeIndexUrl: CODE_REVISION_URL, caseLawIndexUrl: APPEALS_OPINIONS_URL },
];

export const formGroups = [
  { id: "criminal", label: "Criminal", url: "https://georgiacourts.gov/inmate-forms/", note: "Official Administrative Office of the Courts inmate civil-action and habeas form index. A blank form, not a completed pleading or advice to resist." },
  { id: "civil", label: "Civil", url: "https://georgiacourts.gov/forms-and-records/", note: "Official Georgia Courts forms and records index. Local clerk rules still control filing." },
  { id: "family", label: "Family", url: "https://georgiacourts.gov/a2j/self-help-resources/family-law/", note: "Official family-law self-help index, including divorce forms. Not advice about custody or support." },
];

export const rightsTopics = [
  { id: "arrest", label: "Arrest", scenario: "arrest" },
  { id: "encounter", label: "Police encounter", scenario: "public" },
  { id: "court", label: "Court", scenario: "questioning" },
  { id: "jail", label: "Jail", scenario: "arrest" },
  { id: "constitutional", label: "Constitutional rights", scenario: "questioning" },
] as const;

export const resourceLinks = [
  { title: "Georgia Legal Services Program", url: "https://www.glsp.org/" },
  { title: "State Bar of Georgia — Find Legal Help", url: "https://www.gabar.org/" },
  { title: "Georgia Courts", url: "https://georgiacourts.gov/" },
];

export const courtLinks = [
  { title: "Supreme Court of Georgia", url: "https://www.gasupreme.us/" },
  { title: "Court of Appeals of Georgia", url: "https://www.gaappeals.us/" },
  { title: "Georgia Courts directory", url: "https://georgiacourts.gov/" },
];

export const SAFETY_NOTICE =
  "Do not resist, run, lie, or destroy evidence. Ask whether you are free to leave, state that you choose to remain silent, and ask for a lawyer. This is not a substitute for a licensed Georgia attorney.";
