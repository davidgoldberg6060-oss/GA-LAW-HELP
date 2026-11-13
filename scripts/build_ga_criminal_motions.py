import json
SEARCH=r"\bsearch|searched|pulled (me |him |her |them |us )?over|traffic stop|\bstopped\b|\bfound (drugs|a gun|weed|it|something)|without a warrant|no warrant|warrantless|seiz|suppress|evidence"
STMT=r"statement|confess|interrogat|questioned|(talked|spoke|told) (to )?(the )?(police|cops|officers?|detectives?)|miranda|admitted|didn'?t read (me|him|her|them) (my|his|her|their)? ?rights"
DRUGS=r"\b(drugs?|marijuana|weed|cocaine|meth|pills|controlled substance|fentanyl|heroin)\b"
POST=r"convicted|found guilty|sentenced|verdict|after trial"
M=[]
def m(key,name,stages,goal,purpose,when,how,ocga=(),rules=(),unverified=(),deadline=None,template=None,triggers="",broad=False,default=False,deadline_source=None):
    M.append(dict(key=key,name=name,stages=list(stages),goal=goal,purpose=purpose,when_it_applies=when,how_it_helps=how,
        deadline=deadline,deadline_source=deadline_source,ocga=list(ocga),court_rules=list(rules),unverified_authority=list(unverified),
        template_key=template,triggers=triggers,broad_defense=broad,default_criminal=default))
B,T,O="beat_case","less_time","better_outcome"
# ---- arrest / bond
m("bond","Motion for bond (bond hearing)",["arrested","pretrial"],O,"Asks the judge to set bond so the person can be released while the case is pending.",
  "May apply when someone is being held and bond hasn't been set or was denied.","Release lets the person work, keep housing and help prepare the defense.",
  ocga=["17-6-1"],template="bond_reduction",triggers=r"\bbond\b|\bbail\b|held without bond|no bond|denied bond")
m("bond_reduction","Motion to reduce bond",["arrested","pretrial"],O,"Asks the judge to lower a bond that is more than the person can pay.",
  "May apply when bond was set too high for the person's income or circumstances.","A reachable bond means release before trial.",
  ocga=["17-6-1"],template="bond_reduction",triggers=r"reduce (the |my |his |her )?bond|bond (is |was )?(too high|high)|can'?t (afford|pay|make) (the )?bond|lower (the )?bond")
m("bond_modification","Motion to modify bond conditions",["arrested","pretrial"],O,"Asks the judge to change bond conditions (curfew, ankle monitor, no-contact, travel).",
  "May apply when bond conditions make it hard to work, care for family, or live at home.","Workable conditions lower the risk of a violation and re-arrest.",
  ocga=["17-6-1"],triggers=r"bond condition|ankle monitor|curfew|no[- ]contact|modify (the )?bond|travel (while|on) bond")
m("pretrial_habeas","Petition for writ of habeas corpus (unlawful pretrial detention)",["arrested","pretrial"],O,"Asks a superior court to review whether a person is being held unlawfully, for example with no bond decision.",
  "May apply when someone is held with no lawful basis or bond is denied without a proper hearing.","Can lead to release or a proper bond hearing.",
  ocga=["9-14-1"],triggers=r"held without (a )?(charge|bond|hearing)|illegal(ly)? (held|detained)|habeas")
m("appointed_counsel","Request for an appointed lawyer (public defender)",["arrested","pretrial","plea","trial","appeal"],O,"Asks the court to appoint a public defender for someone who can't afford a lawyer.",
  "May apply when the person can't afford a lawyer and faces a charge that requires one.","A lawyer is the single biggest help in finding and filing defenses.",
  ocga=["17-12-23","17-12-24"],triggers=r"public defender|can'?t afford (a )?(lawyer|attorney)|appointed (lawyer|attorney|counsel)|no lawyer")
# ---- pretrial evidence
m("suppress","Motion to suppress evidence",["pretrial","trial"],B,"Asks the judge to throw out evidence from an illegal stop, search or seizure.",
  "May apply if evidence came from a stop or search done without a valid warrant, consent, or legal reason.","Without the key evidence, charges are often reduced or dropped.",
  ocga=["17-5-30","17-5-21"],rules=["Unif. Super. Ct. R. 31.1"],unverified=["Mapp v. Ohio, 367 U.S. 643 (1961)"],deadline="Usually within ten days after arraignment unless the judge extends it.",deadline_source="17-7-110",
  template="suppress",triggers=SEARCH,broad=True,default=True)
m("franks","Motion to suppress for a false or misleading warrant affidavit (Franks hearing)",["pretrial"],B,"Challenges a search warrant that was based on false statements or left out important facts.",
  "May apply if the officer's sworn statement for the warrant was untrue or misleading.","If the warrant falls, the evidence from it can be suppressed.",
  ocga=["17-5-30","17-5-21"],unverified=["Franks v. Delaware, 438 U.S. 154 (1978)"],deadline="Usually within ten days after arraignment unless the judge extends it.",deadline_source="17-7-110",
  template="suppress",triggers=r"(search )?warrant (was )?(based on|had) (lies|false)|lied (on|in) the (warrant|affidavit)|affidavit")
m("return_of_property","Motion for return of property",["pretrial","sentenced"],O,"Asks the court to return property police seized that isn't contraband or needed as evidence.",
  "May apply when police took a phone, money, car or other property.","Gets lawful property back.",ocga=["17-5-30"],
  triggers=r"return (of )?(my |his |her )?(property|phone|money|car)|took (my|his|her) (phone|money|car|property)|seized (my|his|her)")
m("suppress_statements","Motion to suppress statements (Jackson-Denno hearing)",["pretrial","trial"],B,"Asks the judge to hold a hearing and exclude statements to police that weren't voluntary or were taken in violation of Miranda.",
  "May apply if statements were made after threats or promises, while badly impaired, or after asking for a lawyer.","Removing a confession or admission can seriously weaken the case.",
  ocga=["24-8-824"],unverified=["Jackson v. Denno, 378 U.S. 368 (1964)","Miranda v. Arizona, 384 U.S. 436 (1966)"],deadline="With pretrial motions, usually within ten days after arraignment unless extended.",deadline_source="17-7-110",
  template="suppress_statements",triggers=STMT,broad=True)
m("suppress_identification","Motion to suppress an out-of-court identification",["pretrial"],B,"Challenges a lineup, photo array or show-up that was unfairly suggestive.",
  "May apply if a witness picked someone out under suggestive conditions.","A shaky identification can be excluded or attacked at trial.",
  unverified=["Neil v. Biggers, 409 U.S. 188 (1972)"],triggers=r"line ?up|photo (array|lineup)|identif(y|ied|ication)|picked (me|him|her) out|show[- ]?up|wrong (person|guy)|mistaken identity")
m("suppress_chemical_test","Motion to suppress a breath or blood test (DUI)",["pretrial"],B,"Challenges how a breath, blood or urine test was requested, given or recorded.",
  "May apply in a DUI case when implied-consent rules, testing procedures or the right to an independent test weren't followed.","Without the test result, a DUI case can become much weaker.",
  ocga=["40-6-392","40-5-67.1"],deadline="Usually within ten days after arraignment unless extended.",deadline_source="17-7-110",triggers=r"\bdui\b|under the influence|breath(alyzer)? test|blood test|implied consent|intoxilyzer")
# ---- pleadings
m("general_demurrer","General demurrer (motion to dismiss a charge that doesn't state a crime)",["pretrial"],B,"Argues the indictment or accusation doesn't charge a crime at all, even if everything in it were true.",
  "May apply when a required element of the crime is missing from the charging document.","If granted, that charge is dismissed.",
  ocga=["17-7-110","17-7-111","17-7-54"],deadline="Within ten days after arraignment unless the judge extends it.",deadline_source="17-7-110",
  template="demurrer",triggers=r"indictment|accusation|dismiss|thrown out|drop(ped)? (the )?charges?|wrong charge",broad=True)
m("special_demurrer","Special demurrer (defects in how the charge is written)",["pretrial"],B,"Challenges the form of the charge, such as a vague date, place or description.",
  "May apply when the charge is too vague to prepare a defense.","Forces the State to fix or narrow the charge; uncorrected defects can lead to dismissal of that count.",
  ocga=["17-7-111","17-7-113"],deadline="Before trial (form objections); pretrial motions are usually due within ten days after arraignment.",deadline_source="17-7-113",
  template="demurrer",triggers=r"indictment|accusation|vague|wrong date|charging document")
m("quash","Motion to quash the indictment or accusation",["pretrial"],B,"Asks the court to void a charging document because of a legal defect in how it was brought.",
  "May apply when the indictment or accusation was obtained or filed improperly.","A quashed charge must be re-brought; a second quashed indictment on the same charge can bar prosecution.",
  ocga=["17-7-111","17-7-53.1"],deadline="Usually within ten days after arraignment unless extended.",deadline_source="17-7-110",template="demurrer",triggers=r"quash|grand jury|indictment")
m("statute_of_limitations","Plea in bar: statute of limitation",["pretrial"],B,"Asks the court to dismiss a charge brought after the time limit for prosecution ran out.",
  "May apply when the alleged offense happened long before the charge was filed.","If the time ran out, the charge must be dismissed.",
  ocga=["17-3-1","17-3-2"],triggers=r"statute of limitation|time limit|years (ago|later)|too late to charge|long time ago")
m("double_jeopardy","Plea in bar: double jeopardy / former prosecution",["pretrial","trial"],B,"Asks the court to block a prosecution for the same crime and facts that were already prosecuted.",
  "May apply when the person was already tried, convicted or acquitted for the same conduct.","If it applies, the new prosecution ends.",
  ocga=["16-1-7","16-1-8"],triggers=r"double jeopardy|already (tried|charged|convicted|acquitted)|charged twice|same (crime|charge) again")
# ---- discovery
m("discovery","Discovery: get the prosecution's evidence",["pretrial"],B,"Formally opts into Georgia criminal discovery so the State must share statements, reports, witness lists and physical evidence.",
  "Applies in most felony cases once the defense opts in; the defense must share some of its own evidence too.","Knowing the evidence early shows weaknesses and the best defense.",
  ocga=["17-16-4","17-16-1","17-16-2"],deadline="The State must disclose no later than ten days before trial unless the court orders otherwise.",deadline_source="17-16-4",
  triggers=r"discovery|evidence (they|the state|prosecution) (have|has)|police report|body ?cam|dash ?cam|video",broad=True,default=True)
m("compel_discovery","Motion to compel discovery or for sanctions",["pretrial","trial"],B,"Asks the judge to order the State to turn over evidence it hasn't shared, or to exclude it.",
  "May apply when the State missed discovery deadlines or is holding back evidence.","Evidence the State didn't disclose can be excluded or the case delayed in the defense's favor.",
  ocga=["17-16-6"],triggers=r"compel|won'?t (give|turn over|share)|haven'?t (got|received|seen) (the )?(evidence|discovery|video|report)|withh[eo]ld")
m("brady","Brady motion for evidence favorable to the defense",["pretrial","trial"],B,"Asks the court to order the State to disclose evidence that helps the defense or hurts its witnesses' credibility.",
  "May apply in any case where the State may have favorable evidence (deals with witnesses, inconsistent statements, other suspects).","Favorable evidence can create reasonable doubt; hiding it can lead to a new trial.",
  unverified=["Brady v. Maryland, 373 U.S. 83 (1963)","Giglio v. United States, 405 U.S. 150 (1972)"],triggers=r"brady|exculpatory|evidence (that )?(helps|proves) (me|him|her)|hiding evidence|witness (got|has) a deal|snitch")
m("informant","Motion to reveal a confidential informant",["pretrial"],B,"Asks the court to require the State to identify an informant who witnessed or took part in the alleged crime.",
  "May apply when an informant was a key witness or participant, such as a controlled buy.","Lets the defense test the informant's story and credibility.",
  unverified=["Roviaro v. United States, 353 U.S. 53 (1957)"],triggers=r"informant|\bci\b|snitch|controlled buy|undercover")
m("independent_testing","Motion for independent testing of evidence",["pretrial"],B,"Asks to examine or test physical evidence (drugs, DNA, firearms) with a defense expert.",
  "May apply when lab results are central to the State's case.","An independent result can contradict the State's lab.",
  ocga=["17-16-4"],triggers=r"lab (test|result|report)|crime lab|\bgbi\b|test(ed)? the (drugs|evidence|dna)|\bdna\b|fingerprint|ballistic")
m("in_limine","Motion in limine (keep unfair evidence out before trial)",["pretrial","trial"],B,"Asks the judge in advance to exclude unfairly prejudicial evidence, such as unrelated past acts or hearsay.",
  "May apply when the State may try to use prior acts, character attacks or misleading evidence.","Keeps the jury focused on the actual charge.",
  ocga=["24-4-403","24-4-404","24-8-802"],triggers=r"in limine|prior (record|acts|charges)|past (crimes|record)|character|hearsay|keep (that|it|evidence) out")
m("severance","Motion to sever (separate trials)",["pretrial"],O,"Asks for a separate trial from co-defendants, or on unrelated counts.",
  "May apply when a co-defendant's evidence or defense would unfairly hurt the person's own case.","Avoids guilt by association with co-defendants.",
  ocga=["17-8-4"],triggers=r"co-?defendant|charged (with|together with) (someone|others|my friend)|jointly|sever")
m("change_of_venue","Motion for change of venue",["pretrial"],O,"Asks to move the trial to another county because a fair jury can't be found locally.",
  "May apply when heavy local publicity or bias makes a fair trial unlikely.","A fairer jury pool.",
  ocga=["17-7-150"],triggers=r"change (of )?venue|publicity|news coverage|whole (town|county) knows|move the trial")
m("recusal","Motion to recuse the judge",["pretrial","trial","sentenced"],O,"Asks a judge to step aside because of bias or a conflict.",
  "May apply when the judge has a personal conflict or has shown bias in the case.","A neutral judge.",
  rules=["Unif. Super. Ct. R. 25.1"],deadline="Court rule: within five days after learning of the grounds, with a supporting affidavit.",
  triggers=r"recus|judge (is|was) (biased|unfair)|conflict of interest|judge knows")
m("continuance","Motion for continuance",["pretrial","trial"],O,"Asks the court for more time before a hearing or trial.",
  "May apply when the defense needs time to get evidence, a witness or a lawyer.","Prevents being forced to trial unprepared.",
  ocga=["17-8-20","17-8-22"],triggers=r"continuance|more time|postpone|not ready|need time")
# ---- defenses and mental health
m("immunity","Motion for self-defense immunity",["pretrial","trial"],B,"Asks for a pretrial hearing to declare the person immune from prosecution for force used in lawful self-defense or defense of others.",
  "May apply only if force was used to defend against an unlawful attack.","If granted, the case ends before trial.",
  ocga=["16-3-24.2","16-3-21"],deadline="Before trial.",template="immunity",triggers=r"self[- ]?defen[cs]e|stand (my|your|their|his|her) ground|defend(ing|ed)? (my ?self|him ?self|her ?self|someone)|immunity")
m("competency","Motion for a competency evaluation",["pretrial"],O,"Asks the court to evaluate whether the person can understand the case and help the lawyer.",
  "May apply when there are signs of serious mental illness or intellectual disability.","A person who isn't competent can't be tried until competency is restored.",
  ocga=["17-7-129","17-7-130"],triggers=r"competen|mental(ly)? (ill|illness|health|disab)|intellectual disab|doesn'?t understand (the|his|her) case|psych(iatric)? eval")
m("insanity_notice","Notice of insanity or mental illness defense and evaluation",["pretrial"],B,"Gives notice that the defense will raise insanity or mental illness and asks for an evaluation.",
  "May apply if, at the time of the offense, the person couldn't tell right from wrong or acted under a delusional compulsion.","Can lead to a not-guilty-by-reason-of-insanity verdict or a guilty-but-mentally-ill outcome with treatment.",
  ocga=["17-7-130.1","17-7-131","16-3-2","16-3-3"],rules=["Unif. Super. Ct. R. 31.1"],triggers=r"insan|delusion|psychotic|schizo|mental(ly)? ill|didn'?t know (right from wrong|what (he|she|i) was doing)")
m("expert_funds","Motion for funds for a defense expert",["pretrial"],O,"Asks the court to pay for an expert when the person can't afford one and the issue is critical.",
  "May apply when the case turns on science, mental health or forensic evidence and the person is indigent.","An expert can rebut the State's expert.",
  unverified=["Ake v. Oklahoma, 470 U.S. 68 (1985)"],triggers=r"expert|forensic|can'?t afford (an )?expert")
m("alibi_notice","Notice of alibi",["pretrial"],B,"Tells the State the defense will show the person was somewhere else, with alibi witnesses.",
  "May apply when the person was somewhere else when the crime happened.","Proper notice keeps alibi witnesses from being excluded.",
  ocga=["17-16-5"],triggers=r"alibi|wasn'?t (even )?there|somewhere else|out of town|at work (when|at the time)")
m("speedy_trial","Demand for speedy trial",["pretrial"],B,"Formally demands trial; if the State doesn't try the case within the time the law sets, the law requires acquittal.",
  "May apply when the defense is ready for trial and the State may not be.","Can end the case with an acquittal if the State delays.",
  ocga=["17-7-170","17-7-171"],deadline="File at the court term when the indictment or accusation is filed or the next regular term (later only with court permission).",deadline_source="17-7-170",
  template="speedy_trial",triggers=r"speedy|delay|taking (so|too) long|been (months|a year|years)|no trial date|waiting (on|for) (court|trial)|indict",broad=True,default=True)
m("speedy_trial_constitutional","Motion to dismiss for violation of the constitutional speedy-trial right",["pretrial"],B,"Asks the court to dismiss because a long, unjustified delay hurt the defense.",
  "May apply after a long delay caused mostly by the State that harmed the defense (lost witnesses, faded memories).","Dismissal of the charges.",
  unverified=["Barker v. Wingo, 407 U.S. 514 (1972)","Ga. Const. Art. I, Sec. I, Para. XI"],triggers=r"speedy|delay|taking (so|too) long|(a|two|three|four|five|\d+) years?|no trial date")
# ---- outcome reducers
m("conditional_discharge","Conditional discharge (first drug possession)",["pretrial","plea"],T,"Lets the court defer proceedings for a first drug-possession case and dismiss it after probation.",
  "May apply to a first drug-possession case with no prior drug conviction.","No conviction if probation is completed.",
  ocga=["16-13-2"],deadline="Ask before sentencing.",template="conditional_discharge",triggers=DRUGS)
m("first_offender","First Offender treatment",["plea","sentenced"],T,"Lets the judge defer a judgment of guilt; completing the sentence means no conviction.",
  "May apply if there is no prior felony conviction (some offenses are excluded).","Avoids a conviction and can keep the record restricted.",
  ocga=["42-8-60"],deadline="Ask before sentencing.",template="first_offender",triggers=r"first offen|first time|no (prior )?record|never been (in trouble|arrested)|\bplea\b|plead",broad=True,default=True)
m("accountability_court","Request for an accountability court (drug, mental health or veterans court)",["pretrial","plea","probation"],T,"Asks to have the case handled in a treatment-focused court instead of the regular track.",
  "May apply when substance use, mental illness, or military service is connected to the charge.","Treatment instead of jail, and charges can be reduced or dismissed on completion in many programs.",
  ocga=["15-1-15","15-1-16","15-1-17"],triggers=DRUGS+r"|addict|substance|mental(ly)? ill|mental health|veteran|drug court")
m("nolo","Request to enter a nolo contendere (no contest) plea",["plea"],O,"A plea that accepts a sentence without admitting guilt; the court must agree.",
  "May apply to non-capital cases when a plea is being considered.","Can limit some collateral effects compared with a guilty plea.",
  ocga=["17-7-95"],triggers=r"no contest|nolo|plea (deal|offer|bargain)")
m("withdraw_plea","Motion to withdraw guilty plea",["plea","sentenced"],B,"Asks to take back a guilty plea.",
  "Before sentence is pronounced it can be withdrawn; after, only to correct a manifest injustice (for example, the plea wasn't knowing or voluntary).","Restores the right to fight the charge.",
  ocga=["17-7-93"],rules=["Unif. Super. Ct. R. 33.12"],deadline="Before judgment is pronounced as of right; after that, only on a timely motion showing manifest injustice.",deadline_source="17-7-93",
  triggers=r"withdraw (my |his |her |the )?(guilty )?plea|take back (my |the )?plea|regret (taking|the) plea|pleaded guilty")
# ---- trial
m("directed_verdict","Motion for directed verdict of acquittal",["trial"],B,"Asks the judge to acquit because the State's evidence can't support a conviction.",
  "May apply at trial when the evidence, even viewed for the State, demands acquittal.","Ends the case with an acquittal on that charge.",
  ocga=["17-9-1"],triggers=r"directed verdict|not enough evidence|state (has|had) no (evidence|proof)|at trial")
m("mistrial","Motion for mistrial",["trial"],O,"Asks the judge to stop the trial because something happened that makes a fair verdict impossible.",
  "May apply when improper statements or evidence reach the jury and an instruction can't fix it.","A new trial with a new jury.",
  ocga=["17-8-75"],triggers=r"mistrial|jury (heard|saw) something|prosecutor said|improper (argument|statement)")
m("lesser_offenses","Request for jury instructions on lesser offenses",["pretrial","trial"],T,"Asks that the jury be allowed to consider a lesser crime.",
  "May apply when the evidence supports a lesser included offense (for example voluntary manslaughter instead of murder).","Can mean a much lower sentence.",
  ocga=["16-1-6"],template="lesser_offenses",triggers=r"murder|manslaughter|homicide|lesser (charge|offense)")
m("jury_charge_justification","Request for jury charge on justification (self-defense)",["trial"],B,"Asks the judge to instruct the jury that justified force is a complete defense.",
  "May apply at trial when there is evidence of self-defense or defense of others.","Gives the jury a legal path to acquittal.",
  ocga=["16-3-20","17-8-58"],template="jury_charge_justification",triggers=r"self[- ]?defen[cs]e.*trial|trial.*self[- ]?defen[cs]e|jury (charge|instruction)")
# ---- post-trial
m("new_trial","Motion for new trial",["sentenced"],B,"Asks the trial judge for a new trial because of legal errors, a verdict against the evidence, ineffective counsel or new evidence.",
  "May apply after a trial with errors or other problems.","A new trial, and it preserves issues for appeal.",
  ocga=["5-5-40","5-5-20","5-5-21","5-5-23"],deadline="Within 30 days after entry of the judgment.",deadline_source="5-5-40",template="new_trial",
  triggers=r"new trial|found guilty|verdict|convicted at trial|lost (at|the) trial")
m("arrest_of_judgment","Motion in arrest of judgment",["sentenced"],B,"Challenges a judgment for a non-amendable defect that appears on the face of the record, such as an indictment that charges no crime.",
  "May apply right after judgment when the record itself shows a fatal defect.","Can void the judgment.",
  ocga=["17-9-61"],deadline="During the court term in which the judgment was obtained.",deadline_source="17-9-61",triggers=r"arrest of judgment|defect in the (indictment|record)")
m("sentence_mod","Motion to modify or reduce sentence",["sentenced","prison","probation"],T,"Asks the sentencing judge to reduce, suspend or probate the sentence.",
  "May apply after sentencing, if filed in time.","Less time in custody or on probation.",
  ocga=["17-10-1"],deadline="Within one year after sentencing, or 120 days after the remittitur following an appeal, whichever is later.",deadline_source="17-10-1",
  template="sentence_mod",triggers=r"sentenc|reduce (my|the|his|her|their) (time|sentence)|too much time|less time|get (out|home) (early|sooner)")
m("void_sentence","Motion to vacate a void (illegal) sentence",["sentenced","prison","probation"],T,"Asks the court to correct a sentence the law doesn't allow, such as one above the legal maximum.",
  "May apply when the sentence is outside what the law permits for that offense.","A lawful (often shorter) sentence.",
  ocga=["17-9-4","17-10-1"],triggers=r"illegal sentence|void sentence|over the (max|maximum)|more than the (law|max)")
m("time_credit","Motion for jail-time credit",["sentenced","prison"],T,"Makes sure days in custody before sentencing count toward the sentence.",
  "May apply when pretrial custody days weren't credited.","Shortens the time left to serve.",
  ocga=["17-10-11"],template="time_credit",triggers=r"time served|credit for (time|days)|jail credit|days (in jail|locked up) (before|didn'?t count)")
m("concurrent","Request for concurrent sentences",["plea","sentenced"],T,"Asks that sentences on multiple counts or cases run at the same time.",
  "May apply when there are sentences on more than one count or case.","Less total time.",
  ocga=["17-10-10"],template="concurrent",triggers=r"consecutive|concurrent|back to back|stacked|multiple (counts|charges|cases)")
m("appeal","Notice of appeal",["sentenced","appeal"],B,"Starts an appeal to a higher court.",
  "May apply after a conviction or certain rulings.","Errors at trial can lead to reversal or a new trial.",
  ocga=["5-6-38"],deadline="Within 30 days after the judgment, or after the ruling on a timely motion for new trial.",deadline_source="5-6-38",template="appeal",
  triggers=r"\bappeal|found guilty|convicted")
m("out_of_time_appeal","Out-of-time appeal (now usually through habeas)",["appeal","prison"],B,"Seeks an appeal after the deadline passed because the lawyer failed to file one.",
  "May apply when a requested appeal was never filed. Georgia's Supreme Court has limited trial-court motions for this, so it is usually raised through habeas.","Restores a lost appeal.",
  ocga=["9-14-42"],unverified=["Cook v. State, 313 Ga. 471 (2022)"],triggers=r"out[- ]of[- ]time|never filed (my|an|the) appeal|missed the appeal|lawyer didn'?t (file|appeal)")
m("habeas","Petition for writ of habeas corpus",["appeal","prison"],B,"Challenges a conviction or sentence for constitutional violations, such as ineffective assistance of counsel.",
  "May apply after the conviction is final, within the time limits.","Can vacate the conviction or sentence.",
  ocga=["9-14-42","9-14-43","9-14-44"],deadline="Generally within four years for a felony and one year for a misdemeanor from when the conviction became final.",deadline_source="9-14-42",
  template="habeas",triggers=r"habeas|ineffective|bad lawyer|lawyer (never|didn'?t|did not)|constitutional")
m("extraordinary_mnt","Extraordinary motion for new trial",["prison","sentenced"],B,"Seeks a new trial based on important evidence found after the regular deadline.",
  "May apply when material new evidence turns up that couldn't have been found before trial.","A new trial.",
  ocga=["5-5-41"],template="extraordinary_mnt",triggers=r"new evidence|recant|new witness|found out (later|after)")
m("dna_testing","Motion for post-conviction DNA testing",["prison","sentenced"],B,"Asks the court to order DNA testing that could show innocence in a serious felony case.",
  "May apply when DNA testing wasn't done or new methods could change the result.","DNA evidence can prove innocence.",
  ocga=["5-5-41"],template="extraordinary_mnt",triggers=r"\bdna\b")
m("retroactive_first_offender","Petition for retroactive First Offender treatment",["sentenced","prison","probation","record"],O,"Asks the court to apply First Offender status after the fact when the person qualified but wasn't told.",
  "May apply if the person was eligible for First Offender at sentencing but wasn't informed, and the prosecutor consents.","Exoneration and discharge without a conviction.",
  ocga=["42-8-66"],triggers=r"first offender|wasn'?t told|didn'?t (know|tell me) about first offender|retroactive")
m("record_restriction","Record restriction (expungement)",["record"],O,"Restricts access to criminal history records for eligible arrests and convictions.",
  "May apply to dismissed or dropped charges, some completed sentences and pardoned offenses.","Fewer barriers to jobs and housing.",
  ocga=["35-3-37"],triggers=r"expung|record restrict|clear (my|his|her) record|seal (my|the) record|criminal record")
m("early_termination_probation","Request for early termination of probation",["probation"],T,"Asks the court to end probation early for good compliance.",
  "May apply after a period of compliance; long probated sentences are reviewed for early termination.","Ends supervision sooner.",
  ocga=["42-8-37"],triggers=r"early termination|end (my|his|her) probation|get off probation|probation early")
m("probation_revocation_hearing","Defense at a probation revocation hearing",["probation"],T,"Contests an alleged probation violation and asks for a lesser sanction.",
  "May apply when a violation is alleged.","Avoids or limits revocation time.",
  ocga=["42-8-38","42-8-34"],triggers=r"violat(ed|ion) (of )?(my |his |her )?probation|probation violation|\bvop\b|revoc")
m("parole","Parole application support",["prison"],T,"Supports a parole request with programs, letters and a release plan.",
  "May apply when the person is or will soon be eligible for parole.","Earlier release.",
  ocga=["42-9-42","42-9-43"],template="parole",triggers=r"parole|board of pardons|release date|tentative parole")
m("pardon","Pardon application",["record","prison"],O,"Asks the State Board of Pardons and Paroles for a pardon after the sentence.",
  "May apply after completing a sentence and a waiting period set by the Board.","Restores rights and can help with jobs.",
  ocga=["42-9-42"],triggers=r"pardon|restore (my )?rights|gun rights back|clemency")
m("medical_reprieve","Medical reprieve / compassionate release request",["prison"],T,"Asks the Board of Pardons and Paroles for relief from a sentence because of serious illness or incapacity.",
  "May apply when someone in custody is seriously ill or incapacitated.","Release to receive care.",
  ocga=["42-9-42"],triggers=r"compassionate release|medical reprieve|terminal(ly)? ill|dying|serious(ly)? ill")
m("federal_habeas","Federal habeas corpus petition",["appeal","prison"],B,"Asks a federal court to review a state conviction for federal constitutional violations.",
  "May apply after state appeals and state habeas are finished; strict federal deadlines apply.","Can vacate an unconstitutional conviction.",
  unverified=["28 U.S.C. § 2254","28 U.S.C. § 2244(d)"],triggers=r"federal habeas|2254|federal court")
json.dump({"version":"2026-11-12","note":"Georgia criminal motions catalog. Legal information, not legal advice. 'ocga' and 'court_rules' were confirmed present in the GA.LAW.HELP law database on 2026-11-12 (O.C.G.A. text is the 2022 edition) and are re-checked at answer time; 'unverified_authority' is never shown to users.","motions":M},open(__import__('pathlib').Path(__file__).resolve().parents[1]/'backend/app/data/ga_criminal_motions.json','w'),indent=1,ensure_ascii=False)
print(len(M))
