export const HELP_NOTE = "These are the services the Georgia Department of Corrections lists for state prisons. Riverbend Private Prison still uses Access Securepak for packages. County jails use their own vendors: check the county sheriff's website for how to send money, call or visit. GA.LAW.HELP never takes payments; always pay on the vendor's own site.";
export const HELP_LINKS: [string, string][] = [
 [
  "Find where they are (GDC offender search)",
  "https://services.gdc.ga.gov/GDC/OffenderQuery/jsp/OffQryForm.jsp"
 ],
 [
  "Send money: GDC's instructions (JPay)",
  "https://gdc.georgia.gov/friends-and-family/how-do-i-send-money-offender"
 ],
 [
  "JPay: send money, email and video visits",
  "https://www.jpay.com/login.aspx"
 ],
 [
  "Phone calls: GDC's Securus instructions and rates",
  "https://gdc.georgia.gov/offender-info/contact-offender"
 ],
 [
  "Securus Technologies: set up a phone account",
  "https://www.securustech.net/"
 ],
 [
  "Food and property packages: GDC rules (Union Supply)",
  "https://gdc.georgia.gov/friends-and-family/sending-packages-offenders"
 ],
 [
  "Union Supply GA package ordering",
  "https://gainmatepackage.com/Home.aspx"
 ],
 [
  "Visitation rules and how to become a visitor",
  "https://gdc.georgia.gov/friends-and-family/visit-inmate"
 ],
 [
  "Schedule a visit (GDConnect)",
  "https://gdconnect.gdc.ga.gov/visitation"
 ],
 [
  "Questions about your loved one / Ombudsman",
  "https://gdc.georgia.gov/friends-and-family/questions-about-your-loved-ones"
 ]
];
export const CUSTODY = /\b(jail|prison|locked up|incarcerat|inmate|in custody|serving (a|his|her|their|my) (sentence|time)|commissary|on (the )?books|visitation|gdc)\b/i;
