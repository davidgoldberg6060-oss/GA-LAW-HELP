export const GLOSSARY: [string, string][] = [
 [
  "Arraignment",
  "The first court hearing where the charges are read and a plea (usually not guilty) is entered."
 ],
 [
  "Bond",
  "Money or a promise the court accepts so a person can be released from jail while the case goes on."
 ],
 [
  "Indictment",
  "A formal charge issued by a grand jury in a felony case."
 ],
 [
  "Accusation",
  "A formal charge filed by the prosecutor, usually in misdemeanor cases."
 ],
 [
  "Plea",
  "The defendant's answer to the charge: guilty, not guilty, or no contest (nolo contendere)."
 ],
 [
  "First Offender",
  "A Georgia program where a first-time offender's case can end without a conviction if the sentence is completed."
 ],
 [
  "Probation",
  "Serving a sentence in the community under supervision and conditions instead of in custody."
 ],
 [
  "Parole",
  "Early release from prison, supervised by the State Board of Pardons and Paroles."
 ],
 [
  "Habeas corpus",
  "A court case that challenges whether someone is being held legally."
 ],
 [
  "Motion",
  "A written request asking the judge to do something in the case."
 ],
 [
  "Suppress",
  "To ask the judge to keep evidence out of the case, for example because of an illegal search."
 ],
 [
  "Demurrer",
  "A motion saying the charging document itself is legally defective."
 ],
 [
  "Discovery",
  "The process of getting the evidence the other side has, like police reports and videos."
 ],
 [
  "Immunity",
  "Protection from being prosecuted at all; in Georgia it can apply to lawful self-defense."
 ],
 [
  "Justification",
  "A legal defense that the act was allowed, such as self-defense."
 ],
 [
  "Lesser included offense",
  "A less serious crime contained within the charged crime that a jury can consider instead."
 ],
 [
  "Speedy trial",
  "The right to have the trial happen without unreasonable delay; Georgia has a formal demand process."
 ],
 [
  "Sentence modification",
  "Asking the sentencing judge to reduce or change a sentence within the allowed time."
 ],
 [
  "Appeal",
  "Asking a higher court to review and correct mistakes made in the trial court."
 ],
 [
  "Public defender",
  "A lawyer provided free to someone charged with a crime who cannot afford one."
 ],
 [
  "Ombudsman",
  "An office that looks into complaints and concerns about people in custody."
 ],
 [
  "Grievance",
  "A written complaint filed through the facility's official process."
 ],
 [
  "Revocation",
  "Ending probation or parole and sending the person back to custody."
 ],
 [
  "Warrant",
  "A court order allowing police to arrest someone or search a place."
 ],
 [
  "Felony",
  "A serious crime that can be punished by more than a year in prison."
 ],
 [
  "Misdemeanor",
  "A less serious crime, usually punished by up to 12 months in jail or a fine."
 ],
 [
  "Pro se",
  "Representing yourself in court without a lawyer."
 ],
 [
  "Next friend",
  "Someone who brings a court case on behalf of another person who cannot do it themselves."
 ]
];
export function glossaryFor(text: string): [string, string][] {
  return GLOSSARY.filter(([t]) => new RegExp('\\b' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(text));
}
