"""Curated in-app Georgia legal education and navigation data.

Educational entries are issue-spotting material, not a substitute for current official
statutes, rules, published opinions, or case-specific legal advice.
"""

GEORGIA_CODE_TITLES = [
    (1,"General Provisions"),(2,"Agriculture"),(3,"Alcoholic Beverages"),(4,"Animals"),(5,"Appeal and Error"),(6,"Aviation"),(7,"Banking and Finance"),(8,"Buildings and Housing"),(9,"Civil Practice"),(10,"Commerce and Trade"),(11,"Commercial Code"),(12,"Conservation and Natural Resources"),(13,"Contracts"),(14,"Corporations, Partnerships, and Associations"),(15,"Courts"),(16,"Crimes and Offenses"),(17,"Criminal Procedure"),(18,"Debtor and Creditor"),(19,"Domestic Relations"),(20,"Education"),(21,"Elections"),(22,"Eminent Domain"),(23,"Equity"),(24,"Evidence"),(25,"Fire Protection and Safety"),(26,"Food, Drugs, and Cosmetics"),(27,"Game and Fish"),(28,"General Assembly"),(29,"Guardian and Ward"),(30,"Handicapped Persons"),(31,"Health"),(32,"Highways"),(33,"Insurance"),(34,"Labor and Industrial Relations"),(35,"Law Enforcement Officers and Agencies"),(36,"Local Government"),(37,"Mental Health"),(38,"Military, Emergency Management, and Veterans Affairs"),(39,"Minors"),(40,"Motor Vehicles and Traffic"),(41,"Nuisances"),(42,"Penal Institutions"),(43,"Professions and Businesses"),(44,"Property"),(45,"Public Officers and Employees"),(46,"Public Utilities and Public Transportation"),(47,"Retirement and Pensions"),(48,"Revenue and Taxation"),(49,"Social Services"),(50,"State Government"),(51,"Torts"),(52,"Waters of the State"),(53,"Wills, Trusts, and Administration of Estates")
]

def _right(category,title,summary,missed,terms):
    return {"category":category,"title":title,"summary":summary,"often_missed":missed,"research_terms":terms}

RIGHTS_GUIDE = [
    _right("Police encounters","Know whether you are being detained","Ask whether you are free to leave. If detained, do not physically resist; preserve disputed facts for review.","A detention can occur without a formal arrest.",["reasonable suspicion","investigatory detention","Georgia criminal procedure"]),
    _right("Police encounters","Silence and questioning","You may clearly state that you wish to remain silent. During custodial interrogation, clearly request counsel if you want a lawyer.","Miranda is tied to custodial interrogation, not every police conversation.",["Miranda","custodial interrogation","right to counsel"]),
    _right("Searches","Consent is different from a warrant","You can clearly state that you do not consent to a search without physically interfering.","Police may claim a warrant or another exception even after consent is refused.",["consent search","search warrant","Fourth Amendment"]),
    _right("Digital evidence","Phone seizure and phone search are separate issues","The authority to take a device and the authority to examine its contents should be analyzed separately.","Digital warrants can have scope and particularity issues.",["cell phone search","digital warrant","Riley"]),
    _right("Traffic stops","Passengers have rights too","Duration, questioning, frisking, searches, and orders directed to passengers can raise separate issues.","The traffic violation does not automatically justify every later investigation.",["traffic stop duration","passenger detention","frisk"]),
    _right("DUI","Criminal and license proceedings can be separate","A DUI investigation can create both criminal-court and driver's-license consequences.","Administrative deadlines can arrive before the criminal case is resolved.",["Georgia implied consent","ALS hearing","DUI"]),
    _right("Arrest and bond","Bond is not a determination of guilt","Bond concerns pretrial release and conditions, subject to statutory and court limits.","Different courts can have different bond authority depending on the charge.",["Georgia bond","bail","pretrial release"]),
    _right("Criminal cases","Discovery is more than the police report","Review bodycam, dispatch, lab material, warrants, statements, photos, witnesses, and other discoverable evidence.","Missing evidence can be as important as produced evidence.",["Georgia criminal discovery","Brady","Giglio"]),
    _right("Sentencing","Review merger and every count","Multiple guilty counts do not always authorize multiple punishments.","Compare the charging document, verdict or plea, oral sentence, and written sentence.",["Georgia merger","O.C.G.A. 16-1-7","void sentence"]),
    _right("Plea cases","Preserve the plea record","Keep the plea petition, hearing transcript, offer, sentencing transcript, and contemporaneous advice.","Later challenges often turn on the actual record rather than memory.",["Georgia guilty plea","Boykin","plea voluntariness"]),
    _right("Appeals","Deadlines keep running","Verify the correct filing deadline from the order, case type, and procedural posture.","Waiting for a transcript or informal response may not stop a deadline.",["notice of appeal","motion for new trial","Appellate Practice Act"]),
    _right("Post-conviction","Appeal, habeas, and sentence correction are different tools","Each remedy has different courts, prerequisites, deadlines, and available claims.","Using the wrong procedural vehicle can create delay or default.",["Georgia habeas corpus","void sentence","post-conviction"]),
    _right("Probation","Revocation is its own proceeding","Probation violations have their own hearing rules, proof questions, and sanctions.","A new criminal conviction is not always required for revocation.",["Georgia probation revocation","special conditions"]),
    _right("Records","Restriction and sealing do not mean deletion everywhere","Georgia procedures can limit public access to qualifying records, depending on disposition and other facts.","Some government access can remain after restriction or sealing.",["record restriction","O.C.G.A. 35-3-37","sealing"]),
    _right("First Offender","Confirm actual First Offender status","Eligibility, sentencing under the Act, violations, and discharge status all matter.","Calling a case First Offender does not prove the court actually used the statute.",["First Offender Act","42-8-60","discharge"]),
    _right("Public records","Open Records can help build a record","Written requests can seek many non-exempt government records, subject to statutory exemptions.","Open Records and criminal discovery are different systems.",["Georgia Open Records Act","50-18-70"]),
    _right("Court records","Start with the docket","A docket helps identify filings, orders, hearings, counsel changes, and gaps.","A docket entry may not reveal what actually happened at a hearing.",["Georgia docket","clerk record","certified copy"]),
    _right("Housing","Eviction uses court process","Georgia dispossessory cases have short response periods and court procedures.","The answer deadline can come before a hearing date.",["Georgia dispossessory","Title 44","magistrate court"]),
    _right("Family law","Written orders remain critical","Custody, support, and protective-order disputes turn heavily on the filed order.","An informal agreement may not replace an enforceable order.",["custody modification","child support","protective order"]),
    _right("Civil cases","Service and default matter","Preserve served papers and immediately verify the docket and response deadline.","A perceived paperwork defect is not a safe reason to ignore a lawsuit.",["service of process","default judgment","Civil Practice Act"]),
    _right("Evidence","Hearsay depends on purpose and exceptions","An out-of-court statement is not automatically inadmissible merely because it was made outside court.","The same words can be admissible for one purpose and not another.",["Georgia Evidence Code","hearsay","Title 24"]),
    _right("Evidence","Authenticate screenshots and messages","Authorship, completeness, metadata, witnesses, account records, and context can matter.","A convincing screenshot does not by itself resolve authenticity.",["authentication","text messages","chain of custody"]),
    _right("Public defenders","Appointment rules and conflicts matter","Eligibility and appointment are governed by the indigent-defense system and court process.","A strategy disagreement does not automatically create a right to replacement counsel.",["Georgia public defender","indigent defense","conflict counsel"]),
]

def _myth(claim,status="MYTH/UNVERIFIED",explanation="Treat this as folklore unless a current official Georgia or local source verifies it."):
    return {"claim":claim,"status":status,"explanation":explanation}

MYTHS_AND_ODDITIES = [
    _myth("You must eat fried chicken with your hands in Gainesville.","LOCAL LORE / VERIFY"),
    _myth("It is illegal to carry an ice-cream cone in your back pocket on Sunday."),
    _myth("You cannot keep a donkey in a bathtub."),
    _myth("It is illegal to tie a giraffe to a telephone pole or street lamp."),
    _myth("Spitting from a car or bus is illegal, but a truck is different."),
    _myth("Chicken owners are automatically arrested if a chicken crosses the road.","LOCAL-ORDINANCE POSSIBILITY"),
    _myth("All Georgians must own a rake."),
    _myth("You cannot use profanity in front of a dead body in a funeral home."),
    _myth("Storefront mannequins can only be changed with the shades down."),
    _myth("Barbers cannot advertise prices.","HISTORIC/UNVERIFIED"),
    _myth("You cannot put a bed in a bathtub."),
    _myth("You cannot carry a chicken by its feet on Sunday."),
    _myth("It is illegal to say Oh Boy in public."),
    _myth("You cannot eat chicken with a fork.","MYTH/LOCAL LORE"),
    _myth("Georgia bans all masks in public.","REAL LAW WITH IMPORTANT LIMITS","Georgia has an anti-mask statute, but statutory exceptions and constitutional decisions matter; verify current authority."),
    _myth("Police always have to read Miranda rights at arrest.","MYTH","Miranda warnings concern custodial interrogation, not every arrest."),
    _myth("If police do not read Miranda, the whole case is dismissed.","MYTH","A Miranda issue generally concerns statements; it does not automatically dismiss every charge."),
    _myth("Police always need a warrant to search.","MYTH","Warrants are central protections, but recognized exceptions exist and are fact-specific."),
    _myth("Refusing consent means police can never search.","MYTH","Refusal preserves the consent issue, but police may claim a warrant or another legal basis."),
    _myth("A restricted case disappears from every database.","MYTH"),
    _myth("First Offender means the arrest never existed.","MYTH"),
    _myth("Probation cannot be revoked without a new criminal conviction.","MYTH"),
    _myth("If the victim wants charges dropped, the criminal case automatically ends.","MYTH"),
    _myth("An indictment means the grand jury found the defendant guilty.","MYTH"),
    _myth("A dismissal and a not-guilty verdict are the same disposition.","MYTH"),
    _myth("Every felony appeal goes straight to the Supreme Court of Georgia.","MYTH"),
    _myth("Georgia appellate courts retry witnesses and facts from scratch.","MYTH"),
    _myth("Every public Georgia court case is in one free statewide database.","MYTH","Trial-court access is fragmented; published appellate opinions are more centralized."),
    _myth("A docket entry proves exactly what happened at a hearing.","MYTH"),
    _myth("Anything missing from the police report cannot be used in court.","MYTH"),
    _myth("A screenshot automatically proves who sent a message.","MYTH"),
    _myth("Hearsay means every statement made outside court.","MYTH"),
    _myth("A typo in civil papers means you can safely ignore the lawsuit.","MYTH"),
    _myth("A landlord can always remove a tenant immediately when rent is late.","MYTH"),
    _myth("Oral agreements are never enforceable.","MYTH"),
    _myth("A handwritten will is automatically valid because the person wrote it.","MYTH"),
    _myth("Marriage automatically makes every debt joint.","MYTH"),
    _myth("Parents can always access an adult child's medical records.","MYTH"),
    _myth("A driver's license is required to be a passenger in a car.","MYTH"),
    _myth("The speed limit does not apply while passing.","MYTH"),
    _myth("A private business open to customers must allow anyone to film inside.","MYTH"),
    _myth("Freedom of speech means a private employer can never discipline speech.","MYTH"),
    _myth("Police can never arrest for a misdemeanor unless they personally saw it.","MYTH/EXCEPTIONS MATTER"),
    _myth("A wrong middle name automatically invalidates every warrant.","MYTH/FACT-SPECIFIC"),
    _myth("Police must always show a search warrant before entering.","MYTH/FACT-SPECIFIC"),
    _myth("If evidence was obtained illegally, the defendant automatically wins.","MYTH"),
]

COURT_PRIMER = [
    {"name":"Supreme Court of Georgia","role":"Georgia's highest state court; it decides matters within its jurisdiction and publishes binding opinions."},
    {"name":"Court of Appeals of Georgia","role":"Georgia's intermediate appellate court; it reviews many civil and criminal appeals."},
    {"name":"Superior Court","role":"General-jurisdiction trial court handling felonies and many major civil and domestic matters."},
    {"name":"State Court","role":"County-level court commonly handling misdemeanors, traffic matters, and civil cases within its jurisdiction."},
    {"name":"Magistrate Court","role":"Handles warrants, first-appearance functions, dispossessory cases, small civil claims, and other statutory matters."},
    {"name":"Probate Court","role":"Handles estates, wills, guardianships, licenses, and other matters assigned by law."},
    {"name":"Juvenile Court","role":"Handles delinquency, dependency, and other juvenile matters."},
    {"name":"Municipal Court","role":"Handles city ordinance cases and certain state-law offenses within statutory authority."},
]

LEGAL_FORM_GUIDES = [
    {"title":"Motion drafting checklist","items":["Correct court and caption","Case number and parties","Specific relief requested","Facts tied to the record","Current legal authority","Service requirements","Proposed order if required","Signature/contact information","Deadline/hearing request"]},
    {"title":"Open Records request checklist","items":["Identify agency","Describe records","Give date ranges and names","Request electronic copies when practical","Keep proof","Track exemptions and response"]},
    {"title":"Case timeline worksheet","items":["Incident/arrest","Charging document","Bond/first appearance","Motions and rulings","Plea or trial","Sentence","Motion for new trial","Notice of appeal","Appellate decisions","Post-conviction filings"]},
    {"title":"Appeal record checklist","items":["Final judgment","Notice of appeal","Post-trial motions","Transcripts","Exhibits","Clerk record","Prior appellate orders","Deadline source"]},
    {"title":"Post-conviction record checklist","items":["Charging document","Plea/trial transcript","Sentencing record","Motion for new trial","Direct appeal","Prior habeas filings/orders","Counsel file where obtainable","Custody/sentence information"]},
]

HELP_RESOURCES = [
    {"title":"988 Suicide & Crisis Lifeline","phone":"988","kind":"crisis","description":"Call or text 988 for crisis support."},
    {"title":"Georgia Crisis & Access Line (GCAL)","phone":"1-800-715-4225","kind":"mental-health/substance-use","description":"24/7 Georgia crisis access and help locating crisis or detox services."},
    {"title":"SAMHSA National Helpline","phone":"1-800-662-4357","kind":"drug/alcohol/treatment","description":"Treatment referral and information for mental-health, drug, and alcohol concerns."},
    {"title":"Emergency services","phone":"911","kind":"emergency","description":"For immediate danger or a medical emergency."},
]
