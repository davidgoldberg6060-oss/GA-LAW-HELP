/** Citizen Help guides — legal information only; official Georgia sources. */
export const CITIZEN_DISCLAIMER =
  "This is legal information, not legal advice. STANDALONE ASSISTANT is not a lawyer and does not create an attorney-client relationship. Confirm forms, fees, deadlines and filing steps with the court or a licensed Georgia attorney before you act.";

export type CitizenLink = { label: string; url: string };
export type CitizenFeature = {
  id: string;
  title: string;
  blurb: string;
  links: CitizenLink[];
};

export const CITIZEN_FEATURES: CitizenFeature[] = [
  {
    id: "filing_coach",
    title: "Motion filing coach",
    blurb: "Prepare a PDF, then file it yourself — Affidavit of Indigence, PeachCourt / eFileGA, mail, prison path",
    links: [
      { label: "Guide & File", url: "https://www.guideandfile.com/" },
      { label: "E-file court chart", url: "https://georgiacourts.gov/efile-court-records/" },
      { label: "PeachCourt register", url: "https://www.peachcourt.com/Account/Registration" },
      { label: "eFileGA for self-represented", url: "https://www.odysseyefilega.com/prose.htm" },
      { label: "Find My Clerk", url: "https://www.gaclerks.org/Clerks/FindMyClerk.aspx" },
      { label: "O.C.G.A. § 9-15-2", url: "https://law.justia.com/codes/georgia/title-9/chapter-15/section-9-15-2/" },
      { label: "Inmate habeas form (PDF)", url: "https://jcaoc.georgiacourts.gov/wp-content/uploads/2024/03/Inmate-Form_Application-for-Writ-of-Habeas-Corpus-2023.pdf" }
    ]
  },
  {
    id: "record_restriction",
    title: "Record restriction wizard",
    blurb: "GJP DIY tools, GBI and Georgia Courts self-help",
    links: [
      { label: "GJP DIY record clearing", url: "https://www.gjp.org/diyrecordclearing/" },
      { label: "GBI record restrictions", url: "https://gbi.georgia.gov/services/georgia-criminal-history-record-restrictions" },
      { label: "A2J record restrictions", url: "https://georgiacourts.gov/a2j/self-help-resources/record-restrictions-expungement/" }
    ]
  },
  {
    id: "fines_fees",
    title: "Fines, fees & ability to pay",
    blurb: "O.C.G.A. § 42-8-102 hardship and hearing rules",
    links: [
      { label: "O.C.G.A. § 42-8-102", url: "https://law.justia.com/codes/georgia/title-42/chapter-8/article-6/section-42-8-102/" },
      { label: "Georgia Legal Aid", url: "https://www.georgialegalaid.org/" }
    ]
  },
  {
    id: "court_dates",
    title: "Court date reminders",
    blurb: "Use the Android app for on-device reminders; missing court can suspend a license",
    links: [
      { label: "DDS reinstate license (FTA)", url: "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/reinstate-license" }
    ]
  },
  {
    id: "public_defender",
    title: "Ask for a public defender",
    blurb: "Request appointed counsel through GPDC",
    links: [{ label: "Georgia Public Defender Council", url: "https://gapubdef.org/" }]
  },
  {
    id: "inmate_lookup",
    title: "Find someone in jail or prison",
    blurb: "GDC offender search and county sheriff sites",
    links: [
      { label: "GDC Find an Offender", url: "https://gdc.georgia.gov/offender-info/find-offender" },
      { label: "GDC offender query", url: "https://services.gdc.ga.gov/GDC/OffenderQuery/jsp/OffQryForm.jsp" }
    ]
  },
  {
    id: "parole_rights",
    title: "Parole, pardon & rights restoration",
    blurb: "Voting is automatic when the sentence ends; other rights need the Board",
    links: [
      { label: "PAP Pardons & Restoration", url: "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights" }
    ]
  },
  {
    id: "dds_reinstatement",
    title: "Driver’s license reinstatement",
    blurb: "DDS Online Services for Super Speeder, FTA, DUI and more",
    links: [
      { label: "DDS Reinstate license", url: "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/reinstate-license" },
      { label: "DDS Online Services", url: "https://online.dds.ga.gov/" }
    ]
  },
  {
    id: "eviction_answer",
    title: "Eviction Answer packet",
    blurb: "Guide & File dispossessory Answer — you file it yourself",
    links: [
      { label: "Guide & File", url: "https://www.guideandfile.com/" },
      { label: "Georgia Courts self-help", url: "https://georgiacourts.gov/a2j/self-help-resources/" }
    ]
  },
  {
    id: "voting",
    title: "Voting rights after a felony",
    blurb: "Automatic when the sentence is complete; re-register locally",
    links: [
      { label: "PAP restoration info", url: "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights" },
      { label: "Register to vote (SOS)", url: "https://sos.ga.gov/elections-division-office-secretary-state" }
    ]
  },
  {
    id: "traffic_stop",
    title: "Traffic stop rights",
    blurb: "Hands visible, ask if free to leave, no consent to search, silence and lawyer",
    links: [{ label: "Georgia Legal Aid", url: "https://www.georgialegalaid.org/" }]
  },
  {
    id: "reentry",
    title: "Reentry starter kit",
    blurb: "GJP, legal aid, DDS ID, 211 and 988",
    links: [
      { label: "GJP Resources", url: "https://www.gjp.org/resources/" },
      { label: "Georgia Legal Aid", url: "https://www.georgialegalaid.org/" },
      { label: "988 Lifeline", url: "https://988lifeline.org/" }
    ]
  }
];
