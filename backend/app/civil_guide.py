"""Civil problem guide: one curated entry per everyday Georgia civil problem.

Used by AI Help ("Your Defense Plan" and normal answers) and by Civil Case Check so that every civil
problem -- divorce, a car wreck, a fall at a store, a work injury, an insurance denial, fire damage,
an eviction, a debt, a will, a name change, a protective order, and anything not listed -- gets
plain-English help: the Georgia Code sections to look up, verified deadline quotes, practical steps,
questions to ask a lawyer, and free or low-cost help.

Grounding rules (same contract as the rest of the app):
- ``sections`` are looked up by EXACT citation; anything not in the law database or not verified is
  dropped by the normal verified-hit filter, so this list can never add an unverified authority.
  Every section below was confirmed present in the law database on 2026-11-20 (2022 Code text).
- Deadlines are never written here. ``deadline_items`` quotes the sentence word-for-word from the
  stored text of a verified section, or returns nothing.
- Steps and questions are general, conservative, and contain no legal numbers, dollar limits, or
  deadlines.
- Help resources are ids from ``help_resources.R`` (checked against each provider's own page).
"""
from __future__ import annotations

import re

VERIFIED_ON = "2026-11-20"

# Words that mean the person is the one accused of a crime (then the criminal plan types win).
ACCUSED = (r"\b(charged|arrested|accused of|indicted|arraign\w*|booked|locked up|in jail|warrant for (my|his|her|their) arrest|"
           r"(got|gave me|received|wrote me) a (ticket|citation)|cited for|ticketed|plead(ed)? guilty|plea deal|probation officer|"
           r"public defender|prosecutor|district attorney|(police|cops) (say|said|think|claim) (i|he|she|they))\b")

_DEFEND = "defend"   # someone is coming after the user (eviction, debt suit): "How they'd build the case against you"
_CLAIM = "claim"     # the user wants to get something fixed, paid, or ordered

# Shown under "Key deadlines" for insurance and property-damage problems (no number on purpose: it depends on the policy).
POLICY_DEADLINE_NOTE = ("Your insurance policy may set its own deadline to sue the company, and it is often much shorter than the "
                        "general time limits in Georgia law. Look for a part called \"Suit against us\" or \"Legal action against us\" "
                        "in your policy, and ask a lawyer about it right away.")
# General catch-all limits. They are only added for another problem the text mentions when the main problem has no
# deadline of its own; otherwise "my boss says not to report my work injury" would get the 20-year statutory-rights limit.
GENERIC_DEADLINES = frozenset({"9-3-22", "9-3-24", "9-3-25"})

# key, label, plan side, pattern, sections, deadline sections (in order), steps, lawyer questions, help ids, follow-ups
CATEGORIES: tuple[dict, ...] = (
    dict(key="protective_order", label="Protective order", side=_CLAIM,
         pattern=r"protective order|restraining order|\btpo\b|stalk\w*|(keeps?|kept) (threaten|following|harass|calling|texting|showing up)|"
                 r"threaten\w* (me|to (hurt|kill))|showing up at my (job|work|house|home|school)|domestic violence|family violence|"
                 r"(he|she|my ex|my (husband|wife|boyfriend|girlfriend|partner)) (hit|hits|beat|beats|choked|abuses?) me|abusive (ex|husband|wife|boyfriend|girlfriend|partner)",
         sections=("19-13-1", "19-13-3", "19-13-4", "16-5-90", "16-5-94"),
         deadlines=(),
         steps=("If you are in danger right now, call 911.",
                "Write down every threat, visit, call and text with dates, and save screenshots.",
                "Ask the superior court clerk in your county for the family violence or stalking protective order petition.",
                "Tell your job or school security so they can help keep the person away.",
                "Call the 24-hour domestic violence hotline for a safety plan and court help."),
         questions=("Do these facts fit a family violence or a stalking protective order?",
                    "What happens at the hearing, and what should I bring?",
                    "Can the order cover my job, my home, and my children?",
                    "What can I do if the person breaks the order?"),
         help=("dv_hotline",),
         follow_ups=("How do I file for a protective order in Georgia?", "What happens at a protective order hearing?",
                     "What if the person violates the protective order?")),
    dict(key="workers_comp", label="Work injury (workers' comp)", side=_CLAIM,
         pattern=r"workers'? ?comp\w*|work comp|(hurt|injur\w*|fell|broke|cut|burn\w*) .{0,40}\b(at|on the|on my) (work|job|shift)|"
                 r"(at|on the|on my) (work|job|shift)\b.{0,40}\b(hurt|injur\w*|fell|broke)|on[- ]the[- ]job injur\w*|"
                 r"(work|workplace|job) (injury|accident)|injured (employee|worker)|boss (says|said|told me) (not|don'?t) (to )?(file|report)",
         sections=("34-9-1", "34-9-11", "34-9-80", "34-9-81", "34-9-82", "34-9-200", "34-9-261", "34-9-262", "34-9-17"),
         deadlines=("34-9-80", "34-9-82"),
         steps=("Tell your employer or supervisor about the injury now, and also in writing. Keep a copy.",
                "Get medical care and tell the doctor it happened at work.",
                "Ask your employer for the list of approved workers' comp doctors (the panel of physicians).",
                "Write down how it happened, the date and time, and who saw it.",
                "You can file a claim with the State Board of Workers' Compensation, even if your boss says not to."),
         questions=("Is my injury covered by workers' comp, and what benefits could I get?",
                    "What if my employer refuses to report it or file the claim?",
                    "Can I choose my own doctor?",
                    "Could I also have a claim against someone other than my employer?",
                    "How are fees paid in a workers' comp case?"),
         help=("sbwc",),
         follow_ups=("How do I file a workers' comp claim in Georgia?", "Can I be fired for filing workers' comp?",
                     "What benefits does workers' comp pay in Georgia?")),
    dict(key="medical_malpractice", label="Medical mistake (malpractice)", side=_CLAIM,
         pattern=r"malpractice|misdiagnos\w*|wrong diagnosis|(doctor|surgeon|nurse|hospital|dentist|clinic|er\b|emergency room)\b.{0,60}\b(mistake|negligen\w*|messed up|left (a|an|the|something)|wrong (medicine|surgery|side|dose)|botched)|"
                 r"left .{0,20}(sponge|instrument|object) .{0,20}(in|inside) (me|my|him|her)|botched (surgery|procedure)",
         sections=("51-1-27", "9-3-71", "9-3-72", "9-3-73", "9-11-9.1", "51-12-4"),
         deadlines=("9-3-71", "9-3-72"),
         steps=("Ask the hospital and every doctor for a full copy of your medical records and bills.",
                "Write down dates, names, what you were told, and how the problem was found.",
                "Keep getting the care you need, and keep every bill and receipt.",
                "Talk to a medical malpractice lawyer soon. These cases usually need an expert's sworn statement to file."),
         questions=("Do my records show a mistake that could support a claim?",
                    "Which deadline applies to my case, and when did it start?",
                    "Will we need an expert, and who pays for that?",
                    "How are fees paid in a malpractice case?"),
         help=("medical_board",),
         follow_ups=("How long do I have to sue for medical malpractice in Georgia?", "What is an expert affidavit in a malpractice case?",
                     "How do I get my medical records?")),
    dict(key="car_wreck", label="Car wreck injury", side=_CLAIM,
         pattern=r"car (wreck|accident|crash)|\bwreck\b|rear[- ]?ended|t[- ]?boned|(auto|vehicle|motorcycle|truck|bus|uber|lyft|bike|bicycle|pedestrian) (accident|crash|wreck)|"
                 r"(hit|struck) (my car|me|my (son|daughter|kid|child|wife|husband)) .{0,30}(car|truck|driver|vehicle)|(another|other|a|the) (car|driver|truck) (hit|ran into|crashed into|backed into|rear)|"
                 r"fender[- ]bender|uninsured (motorist|driver)|(was|were|got) (in|into) (a|an) (accident|wreck|crash)|hit[- ]and[- ]run (driver|victim)|accident report",
         sections=("51-1-6", "51-12-4", "51-11-7", "51-12-33", "9-3-33", "9-3-31", "33-7-11", "33-4-7", "40-6-273"),
         deadlines=("9-3-33", "9-3-31"),
         steps=("Get medical care and keep every record, bill and receipt.",
                "Get the police accident report and the other driver's insurance information.",
                "Take photos of the cars, the scene and your injuries, and get witness names.",
                "Tell your own insurance company about the wreck.",
                "Don't sign a release or cash a settlement check until you know how badly you are hurt; once you sign, you usually can't ask for more."),
         questions=("What is my claim worth, counting medical bills, lost pay and pain?",
                    "Does my own uninsured motorist coverage apply?",
                    "Does it matter if I was partly at fault?",
                    "Should I accept the insurance offer, or wait?",
                    "How are fees usually paid in a car wreck case?"),
         help=("insurance_commissioner",),
         follow_ups=("How long do I have to file a car accident claim in Georgia?", "What if I was partly at fault for the wreck?",
                     "Should I accept the insurance company's first offer?")),
    dict(key="dog_bite", label="Dog bite or animal attack", side=_CLAIM,
         pattern=r"\bdog\b.{0,30}\b(bit|bite|bites|biting|attack\w*|mauled)|bitten by|(bit|attacked) by (a|the|my neighbor'?s?|their) (dog|animal|pit)|animal attack",
         sections=("51-2-7", "51-1-6", "51-12-4", "9-3-33", "4-8-25"),
         deadlines=("9-3-33",),
         steps=("Get medical care right away and keep the records and bills.",
                "Take photos of the injuries and of where it happened.",
                "Get the owner's name and address, and ask if the dog's shots are current.",
                "Report the bite to animal control in your county.",
                "Ask if the owner has homeowners' or renters' insurance, which often covers dog bites."),
         questions=("Can the owner be held responsible under Georgia law for this bite?",
                    "Does it matter that the dog got out of a fence or was off a leash?",
                    "Will the owner's insurance pay, and what is the claim worth?",
                    "How are fees usually paid in this kind of case?"),
         help=(),
         follow_ups=("Who is responsible when a dog bites someone in Georgia?", "How long do I have to file a dog bite claim?",
                     "Does homeowners insurance cover a dog bite?")),
    dict(key="slip_and_fall", label="Slip, trip or fall injury", side=_CLAIM,
         pattern=r"slip(ped|s)?\b|trip(ped)? (and fell|over|on)|\bfell\b.{0,40}\b(store|floor|stairs?|steps|sidewalk|parking lot|restaurant|apartment|hotel|ice|wet|hole|property)|"
                 r"wet floor|premises liability|(uneven|broken|loose) (floor|sidewalk|step|stair|railing)|fall at (a|the) (store|business)",
         sections=("51-3-1", "51-3-2", "51-1-6", "51-11-7", "51-12-4", "9-3-33"),
         deadlines=("9-3-33",),
         steps=("Get medical care and keep the records and bills.",
                "Report the fall to the manager and ask for a copy of the incident report.",
                "Take photos of what made you fall, like a wet floor or a broken step, before it's fixed.",
                "Get names of witnesses and ask the business to keep its camera video.",
                "Keep the shoes and clothes you wore."),
         questions=("Did the owner know, or should they have known, about the danger?",
                    "Does it matter that there was no warning sign?",
                    "Could they say I should have seen it?",
                    "How are fees usually paid in a fall case?"),
         help=(),
         follow_ups=("Can I sue a store for slipping on a wet floor in Georgia?", "What do I have to prove in a slip and fall case?",
                     "How long do I have to file an injury claim in Georgia?")),
    dict(key="insurance_claim", label="Insurance claim problem", side=_CLAIM,
         pattern=r"insur\w*.{0,80}\b(den\w*|refus\w*|won'?t pay|not paying|slow|delay\w*|lowball|low offer|offer\w*|cancel\w*|dropped|claim|adjuster|bad faith)|"
                 r"claim (was )?(denied|rejected|refused)|adjuster|bad faith|(homeowners'?|renters'?|auto|car|life|health|flood|fire) (insurance|policy|claim)",
         # No general contract limit (9-3-24, six years) here: an insurance policy usually sets its own, shorter
         # deadline to sue, so telling the user "six years" could make them miss it. See deadline_note.
         sections=("33-4-6", "33-4-7", "33-6-34", "33-24-40", "33-32-1", "13-6-11"),
         deadlines=(),
         deadline_note=POLICY_DEADLINE_NOTE,
         steps=("Get the denial or offer in writing, and ask for a full copy of your policy.",
                "Read the policy parts the company relies on, including any deadline to sue that the policy itself sets.",
                "Send the company everything it asks for, and keep copies and dates of every call and letter.",
                "Get your own repair estimates or medical records to show the real cost.",
                "You can file a free complaint with the Georgia Insurance Commissioner's office."),
         questions=("Does my policy cover this loss, and what does the exclusion they cite really say?",
                    "Is the company acting in bad faith, and would a demand letter help?",
                    "Does my policy set its own deadline to sue?",
                    "Should I hire a lawyer or a public adjuster, and what does each cost?"),
         help=("insurance_commissioner",),
         follow_ups=("What can I do if my insurance company denies my claim?", "What is insurance bad faith in Georgia?",
                     "How do I file a complaint with the Georgia Insurance Commissioner?")),
    dict(key="property_damage", label="Fire, water or property damage", side=_CLAIM,
         pattern=r"\b(house|home|apartment|garage|kitchen|building|car|property)\b.{0,20}\b(caught (on )?fire|burn(ed|t) (down|up)?)|caught (on )?fire|\bfire damage|smoke damage|house fire|apartment fire|"
                 r"water damage|burst pipe|flood(ed|ing)? (my|the|our) (house|home|basement|apartment)|tree fell|property damage|"
                 r"damaged (my|our) (house|home|car|fence|roof|property|yard)|vandaliz\w*|mold (in|damage)",
         sections=("51-1-6", "51-12-4", "9-3-30", "9-3-31", "33-4-6", "33-32-1", "44-7-14", "41-1-4"),
         deadlines=("9-3-30", "9-3-31"),
         deadline_note=POLICY_DEADLINE_NOTE,
         steps=("Make sure everyone is safe, and get the fire or police report.",
                "Take photos and video of all the damage before cleaning up, and keep damaged items if you can.",
                "Tell your insurance company in writing right away and ask for a copy of your policy.",
                "Keep receipts for hotel, food and repairs you pay for while out of your home.",
                "If someone else caused it (a neighbor, landlord or contractor), write down what happened and who saw it."),
         questions=("Who could be responsible for the damage, and can I recover from them as well as my insurer?",
                    "What does my policy cover for living costs while I'm out of my home?",
                    "What if the insurance company is slow or offers too little?",
                    "Which deadline applies to a property damage claim?"),
         help=("insurance_commissioner",),
         follow_ups=("Who pays when a neighbor's fire damages my house?", "What can I do if insurance is slow to pay a fire claim?",
                     "How long do I have to sue for property damage in Georgia?")),
    dict(key="divorce", label="Divorce", side=_CLAIM,
         pattern=r"divorc\w*|alimony|separat(ed|ing|ion) from (my )?(wife|husband|spouse)|split (the|our) (house|property|stuff|debts)|marital (property|home|debt)",
         sections=("19-5-1", "19-5-2", "19-5-3", "19-5-5", "19-6-1", "19-9-1", "19-9-3", "19-6-15"),
         deadlines=("19-5-2",),
         steps=("Gather papers on income, debts, the house, cars, bank and retirement accounts.",
                "If you both agree on everything, ask the superior court clerk about an uncontested divorce.",
                "If you have children, think through a parenting plan and child support.",
                "Keep copies of any agreements and messages about money or the kids.",
                "Don't hide or move money or property; the court can punish that."),
         questions=("Do we qualify for an uncontested divorce, and what forms do we need?",
                    "How will the house, debts and retirement be divided?",
                    "How will custody and child support be decided for our kids?",
                    "What will this cost, and can we use mediation?"),
         help=(),
         follow_ups=("How do I file for an uncontested divorce in Georgia?", "How is property divided in a Georgia divorce?",
                     "How is child support calculated in Georgia?")),
    dict(key="custody", label="Custody or child support", side=_CLAIM,
         pattern=r"(child|joint|sole|physical|legal|primary|full|shared) custody|\bcustody\b.{0,30}\b(kids?|child|children|son|daughter|order|case|modification|hearing)|"
                 r"visitation|parenting (plan|time)|child support|legitimat\w*|paternity|grandparents? (rights|visitation)",
         sections=("19-9-3", "19-9-1", "19-9-23", "19-6-15", "19-6-28", "19-7-2", "19-7-22"),
         deadlines=(),
         steps=("Keep a calendar of parenting time, missed visits and payments.",
                "Save texts and emails with the other parent; keep them polite.",
                "For child support, the Georgia Division of Child Support Services can help open, change or enforce a case.",
                "Ask the superior court clerk for the forms to start or change a custody or support order.",
                "Follow the current order until a judge changes it."),
         questions=("What will the judge look at in deciding what is best for my child?",
                    "Has something changed enough to modify the order?",
                    "How do I enforce an order the other parent isn't following?",
                    "What will it cost, and is mediation required in my county?"),
         help=("child_support_services",),
         follow_ups=("How do I change a custody order in Georgia?", "What can I do if my ex won't pay child support?",
                     "What does the court consider for custody in Georgia?")),
    dict(key="landlord_tenant", label="Eviction or landlord problem", side=_DEFEND,
         pattern=r"evict\w*|dispossessory|notice to (vacate|quit)|landlord|tenant|\blease\b|behind on (my |the |our )?rent|security deposit|"
                 r"(didn'?t|did not|can'?t|cannot|couldn'?t) pay (my |the |our )?rent|lock(ed|ing)? (me|us) out|repairs? (in|to) my (apartment|unit|rental)",
         sections=("44-7-50", "44-7-51", "44-7-52", "44-7-53", "44-7-54", "44-7-56", "44-7-13", "44-7-14", "44-7-34", "44-7-35"),
         deadlines=("44-7-51", "44-7-56", "44-7-34"),
         steps=("A notice on your door is not an eviction order. Only a judge can order you out.",
                "If you get court papers (a dispossessory summons), answer by the deadline on them, in writing or at the court.",
                "Keep paying what you can, and keep proof of every payment.",
                "Take photos of the unit and keep every text, letter and receipt from the landlord.",
                "Go to the hearing. If you miss it, you will likely lose."),
         questions=("What defenses do I have, like repairs or payment the landlord refused?",
                    "What deadline is on my court papers, and how do I answer?",
                    "Can I pay the rent owed to stop the eviction?",
                    "What happens at the hearing, and can I appeal?"),
         help=(),
         follow_ups=("What happens at a dispossessory hearing?", "Can I pay rent into the court registry?",
                     "How do I get my security deposit back in Georgia?")),
    dict(key="foreclosure", label="Foreclosure or mortgage problem", side=_DEFEND,
         pattern=r"foreclos\w*|mortgage|behind on (my |our )?(house|home|mortgage) payments?|deed under power|loan modification|lender (is )?taking (my|our) (house|home)",
         sections=("44-14-160", "44-14-162", "44-14-162.2", "9-11-65"),
         deadlines=("44-14-162.2",),
         steps=("Open every letter from the lender and write down the sale date if one is listed.",
                "Call the lender's loss-mitigation department and ask about a payment plan or loan modification.",
                "Talk to a free HUD-approved housing counselor right away.",
                "Keep copies of everything you send and the date and name for every call.",
                "Watch for foreclosure-rescue scams that ask for money up front."),
         questions=("Was I sent the notice Georgia law requires before the sale?",
                    "What options do I have to keep the house or slow the sale?",
                    "Would bankruptcy or a loan modification help in my situation?",
                    "What happens to any money left after a sale?"),
         help=("housing_counselor",),
         follow_ups=("How does foreclosure work in Georgia?", "What notice does the lender have to give before foreclosure?",
                     "How can I stop a foreclosure sale?")),
    dict(key="debt", label="Debt, collection or garnishment", side=_DEFEND,
         pattern=r"\bdebt\b|debt collector|collection agency|collections|garnish\w*|credit card (debt|company|bill|lawsuit)|repossess\w*|"
                 r"payday loan|medical bills?|judgment against me|levy on my (bank|account)",
         sections=("9-3-24", "9-3-25", "9-11-12", "9-11-55", "9-11-60", "18-4-1", "18-4-5", "18-4-6", "18-4-20", "11-9-609", "11-9-611"),
         deadlines=("9-3-24", "9-3-25"),
         steps=("Don't ignore court papers. Answer by the deadline on them.",
                "Ask the collector in writing to prove the debt and that they own it.",
                "Check whether the debt is old enough that the time to sue may have passed.",
                "If your pay or bank account is garnished, ask the court clerk how to claim money that is protected.",
                "Keep notes of every call; collectors must follow federal rules on how they contact you."),
         questions=("Is this debt valid, and does the collector own it?",
                    "Has the time to sue on this debt run out?",
                    "What income or property is protected from garnishment?",
                    "Can I set aside a default judgment I never knew about?"),
         help=("cfpb",),
         follow_ups=("How long can a creditor sue over a debt in Georgia?", "What income is protected from garnishment?",
                     "How do I answer a debt lawsuit?")),
    dict(key="identity_theft", label="Identity theft", side=_CLAIM,
         pattern=r"identity (theft|was stolen|stolen)|stole my identity|(opened|took out|used) .{0,40} in my name|in my name .{0,40}(account|card|loan)|"
                 r"someone used my (social|ssn|identity|name|credit)",
         sections=("10-1-914", "10-1-393.8", "16-9-121", "16-9-129", "9-3-25"),
         deadlines=(),
         steps=("Report it at IdentityTheft.gov to get a recovery plan and an identity theft report.",
                "Freeze your credit with Equifax, Experian and TransUnion; it's free.",
                "Make a police report and keep the report number.",
                "Write to each company and collector to dispute the accounts that aren't yours.",
                "Get your free credit reports and check them for other accounts."),
         questions=("How do I get these accounts and collections removed?",
                    "What if a collector sues me over a debt I didn't make?",
                    "Can I recover my losses from anyone?"),
         help=("identity_theft_gov", "cfpb"),
         follow_ups=("How do I freeze my credit in Georgia?", "What should I do if a collector sues me for an account that isn't mine?",
                     "How do I report identity theft?")),
    dict(key="consumer", label="Scam or bad business deal", side=_CLAIM,
         pattern=r"\bscam\w*|ripped off|car dealer|dealership|lied about|false advertis\w*|bait and switch|refund|warranty|lemon|defective|deceptive|overcharg\w*|"
                 r"won'?t (give|pay) (me )?(my money|a refund)|sold me",
         sections=("10-1-393", "10-1-399", "10-1-401", "51-6-1", "51-6-2", "13-5-5", "10-1-782", "10-1-784"),
         deadlines=("10-1-401",),
         steps=("Gather the receipt, contract, ads, texts and photos of the problem.",
                "Send the business a written demand that says what went wrong and what you want; keep a copy.",
                "File a free complaint with the Georgia Attorney General's Consumer Protection Division.",
                "If the amount is within the magistrate court limit, small claims court may be an option.",
                "For a new car with repeated defects, ask about Georgia's lemon law."),
         questions=("Is this a deceptive practice under Georgia's consumer law?",
                    "Do I need to send a demand letter before I sue?",
                    "Can I cancel the deal and get my money back?",
                    "Is small claims court a good fit for this?"),
         help=("consumer_protection",),
         follow_ups=("What can I do if a car dealer lied to me?", "How do I file a consumer complaint in Georgia?",
                     "What is the Georgia lemon law?")),
    dict(key="contract", label="Contract or money owed", side=_CLAIM,
         pattern=r"contract\w*|agreement|breach|(paid|gave) .{0,40}\b(and|but) (he|she|they) (never|didn'?t|won'?t|quit|left|disappeared)|"
                 r"owes? me (money|\$|\d)|didn'?t pay me back|won'?t pay me back|loan(ed)? (him|her|them|my (friend|cousin|brother|sister))|"
                 r"won'?t return my (money|calls|deposit)|quit (halfway|the job)",
         sections=("13-1-1", "13-3-1", "13-6-1", "13-6-2", "13-6-11", "9-3-24", "9-3-25", "9-3-26", "15-10-2"),
         deadlines=("9-3-24", "9-3-25"),
         steps=("Gather the contract, texts, receipts, checks and photos of the work.",
                "Send a written demand that says what is owed and a date to pay or finish; keep a copy.",
                "For contractors, check whether they were licensed and keep their business name and address.",
                "If the amount is within the magistrate court limit, you can file in small claims (magistrate) court without a lawyer."),
         questions=("Was there a contract, even if it wasn't written?",
                    "What can I recover: my money back, the cost to finish, or more?",
                    "Which court should I file in, and what does it cost?",
                    "Which deadline applies to my claim?"),
         help=(),
         follow_ups=("How do I sue a contractor in Georgia?", "What is the small claims limit in Georgia?",
                     "Is a text message agreement a contract?")),
    dict(key="employment", label="Job or wage problem", side=_CLAIM,
         pattern=r"(got|was|been|getting|being) (fired|terminated|laid off)|fired me|wrongful(ly)? (termination|terminated|fired)|\bwages?\b|paycheck|overtime|"
                 r"final pay|(didn'?t|did not|won'?t|never) pa(y|id) me|discriminat\w*|harass\w* at work|retaliat\w*|unemployment|minimum wage|"
                 r"my (boss|employer|manager|supervisor)\b",
         sections=("34-7-1", "34-7-2", "9-3-22", "34-4-3", "34-8-190", "34-8-194", "34-8-220"),
         deadlines=("9-3-22",),
         steps=("Write down your hours, pay dates, and what you were promised, and keep pay stubs.",
                "Ask your employer in writing for the pay you are owed; keep a copy.",
                "For unpaid wages or overtime, you can file a free complaint with the U.S. Labor Department's Wage and Hour Division.",
                "For discrimination or retaliation, contact the EEOC soon; its charge deadlines are short.",
                "If you lost your job, apply for unemployment with the Georgia Department of Labor right away."),
         questions=("Was my firing legal, or was it discrimination or retaliation?",
                    "How do I get unpaid wages or overtime back?",
                    "What deadline applies to an EEOC charge in my case?",
                    "Can I get unemployment benefits?"),
         help=("wage_hour", "eeoc", "ga_labor"),
         follow_ups=("How do I get my final paycheck in Georgia?", "What is the deadline to file a discrimination charge?",
                     "Can I get unemployment if I was fired?")),
    dict(key="probate", label="Will, estate or probate", side=_CLAIM,
         pattern=r"\b(a|my|the|his|her|their|no|without a|last) will\b|\bwills\b|probate|estate|inherit\w*|executor|administrator of|\bheirs?\b|"
                 r"passed away|died without|(my|our) (father|mother|dad|mom|husband|wife|grand\w+|brother|sister|son|daughter|aunt|uncle) (died|passed)|"
                 r"power of attorney|guardianship|conservator\w*",
         sections=("53-2-1", "53-4-20", "53-5-1", "53-5-21", "53-6-1", "53-6-20", "53-7-1", "15-9-30"),
         deadlines=(),
         steps=("Find any will and the death certificate.",
                "Contact the probate court in the county where the person lived; it handles wills and estates.",
                "Make a list of the person's property, bank accounts, debts and bills.",
                "Don't sell or give away the person's property until the court appoints someone to handle the estate.",
                "Ask the probate court clerk about the forms; many probate courts have self-help information."),
         questions=("Who inherits under Georgia law if there was no will?",
                    "Who should be appointed to handle the estate, and how?",
                    "What can we do about a relative living in the house or holding property?",
                    "What will the process cost and how long does it take?"),
         help=("probate_courts",),
         follow_ups=("Who inherits in Georgia if someone dies without a will?", "How do I open an estate in probate court?",
                     "What does an estate administrator do?")),
    dict(key="name_change", label="Name change", side=_CLAIM,
         pattern=r"change (my|our|his|her|their|my (son|daughter|child)'?s?) (last |first |legal )?name|name change|legally change .{0,20}name",
         sections=("19-12-1", "19-12-2", "19-12-3", "19-12-4"),
         deadlines=(),
         steps=("Ask the superior court clerk in your county for the name change petition and the filing fee.",
                "Ask the clerk how to publish the required notice in the county's legal newspaper.",
                "Go to the hearing if one is set, and bring photo ID.",
                "After the order, update your Social Security card, driver's license and bank accounts."),
         questions=("What forms do I need, and what will filing and publishing cost?",
                    "Is a hearing required in my county?",
                    "Are there special steps for changing a child's name?"),
         help=(),
         follow_ups=("How do I change my name in Georgia?", "How much does a name change cost in Georgia?",
                     "How do I change my child's name?")),
    dict(key="hoa_neighbor", label="Neighbor, HOA or property line", side=_CLAIM,
         pattern=r"\bhoa\b|homeowners'? association|condo association|covenants?|property line|boundary|easement|nuisance|"
                 r"neighbor'?s?\b.{0,60}\b(tree|fence|noise|drain\w*|driveway|parking|property line)|trespass\w* on (my|our)",
         sections=("44-3-106", "44-3-109", "44-3-232", "41-1-1", "41-1-4", "51-9-1", "9-3-30"),
         deadlines=("9-3-30",),
         steps=("Get a copy of the HOA covenants and rules, or your property survey and deed.",
                "Write down what happened with dates, and take photos.",
                "Send a polite written request first; keep a copy.",
                "Ask about mediation; many counties offer it at low cost.",
                "If the amount is within the magistrate court limit, small claims court may be an option."),
         questions=("Do the covenants or the law allow what the HOA or neighbor is doing?",
                    "Can the HOA put a lien on my home for these fines?",
                    "What can I recover for damage to my property?"),
         help=(),
         follow_ups=("Can my HOA fine me in Georgia?", "What can I do about a neighbor's tree damaging my property?",
                     "What is a private nuisance in Georgia?")),
    dict(key="small_claims", label="Small claims or lawsuit", side=_CLAIM,
         pattern=r"small claims|magistrate court|(sued|suing|lawsuit|summons|complaint|served (with )?(court )?papers?)|sue (him|her|them|someone|somebody|my|a|the)|take (him|her|them) to court",
         sections=("15-10-2", "15-10-41", "15-10-43", "15-10-45", "15-10-80", "9-11-12", "9-11-55", "9-11-60"),
         deadlines=("9-11-12",),
         steps=("If you were served, read the papers and write down the answer deadline and court date.",
                "Answer in writing by the deadline, or you can lose by default.",
                "Gather contracts, receipts, photos and texts, and make copies for the judge and the other side.",
                "If you want to sue, ask the magistrate court clerk for the statement of claim form and the fee.",
                "Settlement or mediation can save time and money; get any deal in writing."),
         questions=("Does my claim or defense hold up under Georgia law?",
                    "Which court is right for this amount?",
                    "What happens if I miss the deadline to answer?",
                    "Can I file a counterclaim?"),
         help=(),
         follow_ups=("How do I file in small claims court in Georgia?", "How do I answer a lawsuit in Georgia?",
                     "What happens if I miss the deadline to answer?")),
    dict(key="benefits", label="Government benefits", side=_CLAIM,
         pattern=r"\bsnap\b|food stamps|medicaid|peachcare|\bssi\b|\bssdi\b|disability benefits|social security (benefits|disability)|unemployment (benefits|denied|appeal|claim)|\bwic\b|tanf",
         sections=("34-8-190", "34-8-194", "34-8-220"),
         deadlines=(),
         steps=("Get the decision letter and write down any appeal deadline on it.",
                "Appeal in writing before that deadline, and keep proof you sent it.",
                "Gather pay stubs, medical records or other proof the agency asked for.",
                "Legal aid often helps with benefit appeals for free."),
         questions=("Why was I denied, and do I have grounds to appeal?",
                    "What is the appeal deadline on my letter?",
                    "Can I keep getting benefits while I appeal?"),
         help=("ga_labor",),
         follow_ups=("How do I appeal an unemployment denial in Georgia?", "How do I appeal a SNAP or Medicaid denial?",
                     "Can legal aid help with a benefits appeal?")),
)

OTHER = dict(key="other_civil", label="Other civil problem", side=_CLAIM, pattern="", sections=("15-10-2", "9-3-24", "9-3-25", "9-3-33", "9-3-31"),
             deadlines=(),
             steps=("Write down what happened, with dates, names and amounts.",
                    "Keep every paper, letter, text, photo and receipt about the problem.",
                    "If you got court papers, find the deadline on them and don't miss it.",
                    "Try a written request or demand first, and keep a copy.",
                    "Contact free legal aid for your county; they handle many kinds of civil problems."),
             questions=("Do I have a claim or a defense under Georgia law?",
                        "What deadline applies to my problem?",
                        "Which court or agency handles this?",
                        "What will it cost, and are there free or low-cost options?"),
             help=(), follow_ups=())

_BY_KEY = {c["key"]: c for c in CATEGORIES + (OTHER,)}
_COMPILED = tuple((c, re.compile(c["pattern"], re.I)) for c in CATEGORIES)

# A civil problem the catalog doesn't name still gets the catch-all guide when the person describes their own problem.
_CIVIL_HINT = re.compile(r"\b(sue|sued|suing|lawsuit|court|judge|claim|damages|owe[sd]?|money|pay|paid|refund|landlord|neighbor|company|business|"
                         r"contract|insurance|property|house|home|car|job|boss|bill|fee|fine|lien|deposit|loan|account|policy|agency|benefits?|"
                         r"county|city|school|hoa|bank|hurt|injur\w*|damage\w*)\b", re.I)


def get(key: str | None) -> dict | None:
    return _BY_KEY.get(key or "")


def _text(text: str) -> str:
    from .civil_topics import current_question
    return re.sub(r"\s+", " ", current_question(text or "") or str(text or "")).strip()


def is_accused(text: str) -> bool:
    return bool(re.search(ACCUSED, _text(text), re.I))


def detect_all(text: str) -> list[dict]:
    """Every civil category the text mentions, in catalog order."""
    q = _text(text)
    return [c for c, rx in _COMPILED if rx.search(q)]


def detect(text: str, *, fallback: bool = False) -> dict | None:
    """The main civil category for ``text`` (or None). With ``fallback``, a described civil problem that
    matches no category gets the catch-all ``other_civil`` guide."""
    found = detect_all(text)
    if found:
        return found[0]
    if fallback and _CIVIL_HINT.search(_text(text)):
        return OTHER
    return None


def sections_for(cat: dict | None, text: str = "", limit: int = 14) -> list[str]:
    """The category's sections (deadline sections included), then those of any other category the text names."""
    if not cat:
        return []
    out = list(dict.fromkeys(tuple(cat["sections"]) + tuple(cat["deadlines"])))
    out += [x for x in deadline_secs(cat, text) if x not in out]
    others = detect_all(text) if text else []
    others.sort(key=lambda c: c["key"] != "small_claims")  # "can I take him to small claims?" keeps the court sections
    for other in others:
        if other["key"] != cat["key"]:
            out += [s for s in other["sections"][:4] if s not in out and not ((cat.get("deadlines") or cat.get("deadline_note")) and s in GENERIC_DEADLINES)]
    return out[:limit]


_TIME = re.compile(r"\b(within|after|before|not later than|no later than|more than|at least)\b[^.;]{0,80}?\b(\d+|one|two|three|four|five|six|seven|"
                   r"ten|fifteen|twenty|thirty|sixty|ninety)\b[^.;]{0,12}?\b(days?|months?|years?)\b", re.I)


def _sentences(text: str) -> list[str]:
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    return [s.strip() for s in re.split(r"(?<=[.;])\s+(?=\(?[A-Z(])", t) if s.strip()]


def deadline_quote(text: str) -> str | None:
    """The first sentence of a stored law text that states a time limit, copied word for word (or None)."""
    for s in _sentences(text)[:12]:
        if _TIME.search(s) and 20 <= len(s) <= 700:
            return s
    return None


def deadline_secs(cat: dict | None, text: str = "") -> list[str]:
    """Deadline sections for the category, then for any other category the text names."""
    if not cat:
        return []
    out = list(cat.get("deadlines") or ())
    own = bool(out or cat.get("deadline_note"))
    for other in detect_all(text) if text else []:
        if other["key"] == cat["key"]:
            continue
        out += [s for s in other.get("deadlines") or () if s not in out and not (own and s in GENERIC_DEADLINES)]
    return out[:4]


def deadline_note(cat: dict | None) -> str:
    """A fixed caution for the category's "Key deadlines" (insurance policies set their own deadline to sue), or ''."""
    return str((cat or {}).get("deadline_note") or "")


def deadline_items(cat: dict | None, hits: list[dict], text: str = "") -> list[dict]:
    """{title, quote, hit} for the category's deadline sections, quoted verbatim from verified ``hits``."""
    secs = deadline_secs(cat, text)
    if not secs:
        return []
    from .grounded_legal_assistant import _SECTION_RE
    by = {}
    for h in hits:
        for s in _SECTION_RE.findall(str(h.get("citation") or "")):
            by.setdefault(s, h)
    out = []
    for sec in secs:
        h = by.get(sec)
        if not h:
            continue
        quote = deadline_quote(h.get("full_text") or h.get("excerpt") or "")
        if quote:
            title = re.sub(r"^O\.C\.G\.A\. § [\d.-]+\.?\s*", "", str(h.get("title") or "")).strip() or "Deadline"
            out.append({"title": title[:120], "quote": quote, "hit": h})
    return out


def lookup_deadlines(db, cat: dict | None, text: str = "") -> list[dict]:
    """Exact-citation lookup of the deadline sections (verified only), then ``deadline_items``."""
    secs = deadline_secs(cat, text)
    if db is None or not secs:
        return []
    from .charge_check_service import lookup_sections
    from .grounded_legal_assistant import _verified_hits
    try:
        with db.begin_nested():
            found = lookup_sections(db, secs)
    except Exception:
        return []
    return deadline_items(cat, _verified_hits({"hits": found}), text)


def deadline_bullets(items: list[dict]) -> list[str]:
    return [f"• {i['hit'].get('citation')}: \"{i['quote']}\"" for i in items]


def help_ids(text: str) -> list[str]:
    """Agency help for the main civil problem in ``text`` (a work injury -> the Workers' Comp Board ...)."""
    cat = detect(text)
    return list(cat["help"]) if cat else []


def steps_section(cat: dict) -> str:
    return "Steps to take now\n" + "\n".join("• " + s for s in cat["steps"])


def label_for(key: str | None) -> str:
    c = get(key)
    return c["label"] if c else ""
