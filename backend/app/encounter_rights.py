"""In-app encounter reference for the Georgia assistant.

Educational material for the app's own answers. Not legal advice, not a filing,
and not a claim that every Georgia statute or public docket is stored here.
"""

DISCLAIMER = (
    "This is general Georgia and federal rights information stored in the app. "
    "It is not legal advice, not a prediction of what an officer will do, and not a "
    "substitute for a lawyer. Do not physically resist. False statements to Georgia "
    "law enforcement can be a crime under OCGA 16-10-20."
)

ENCOUNTERS = [
    {
        "id": "traffic_stop",
        "title": "Traffic stop",
        "open_with": "You are in a traffic stop. You can comply with lawful orders and still protect your rights.",
        "script": [
            "Pull over safely, window down enough to talk, hands visible.",
            "A driver must show a license on request during a traffic stop. OCGA 40-5-29.",
            "You can ask: am I free to leave, or am I being detained?",
            "You can say: I do not consent to a search of me, my passengers, or the car.",
            "You do not have to answer questions about where you are going, what you have been doing, or whether you have been drinking. You can say you are choosing not to answer.",
            "Passengers can ask if they are free to leave. A stop can include orders to stay in or step out of the car.",
            "If asked to do field sobriety tests, those are generally optional. Implied-consent testing after a DUI arrest is a separate issue under OCGA 40-5-55 and 40-5-67.1, with license consequences for refusal.",
            "Do not reach into pockets, the glove box, or under seats until asked, and then say what you are doing.",
            "You may record police in public if you do not interfere. Do not hide or destroy a recording.",
        ],
        "authorities": ["OCGA 40-5-29", "OCGA 40-6-1 et seq.", "OCGA 40-5-55", "OCGA 40-5-67.1", "OCGA 17-5-30", "Fourth Amendment"],
    },
    {
        "id": "at_home",
        "title": "Police at the home",
        "open_with": "You are at home. The door is a constitutional line. You do not have to open it just because someone knocks.",
        "script": [
            "You can speak through the door. You can ask them to identify themselves and why they are there.",
            "You can say: I do not consent to entry or a search.",
            "Without consent, police generally need a warrant, or a recognized exception such as emergency, hot pursuit, or another fact-specific exception, to enter a home.",
            "If they say they have a warrant, you can ask to see it. Do not physically block them.",
            "A warrant to arrest someone inside is different from a warrant to search the house. Scope matters.",
            "Roommates and guests can create separate consent issues. Consent by one person may not cover a space only you control.",
            "If they enter anyway, say clearly that you do not consent, then do not interfere. Write down names, times, and what was taken.",
        ],
        "authorities": ["Fourth Amendment", "OCGA 17-5-21", "OCGA 17-5-30", "Ga. Const. art. I, sec. I, par. XIII"],
    },
    {
        "id": "interrogation",
        "title": "Questioning and interrogation room",
        "open_with": "You are being questioned. Custodial interrogation is different from a voluntary conversation.",
        "script": [
            "Ask: am I under arrest, and am I free to leave?",
            "If you are in custody and they question you, you can say: I am invoking my right to remain silent, and I want a lawyer.",
            "After you clearly ask for a lawyer, questioning about the case should stop until you have counsel or you restart the conversation.",
            "Silence is safer than a story. Do not lie. OCGA 16-10-20 makes a false statement to a government agency a crime.",
            "Miranda warnings are for custodial interrogation. A missing warning does not automatically dismiss the case. It is mainly about statements.",
            "You can refuse consent to a phone search. Taking the phone and searching the phone are separate issues.",
            "Do not sign a statement, consent form, or waiver you do not understand. You can ask for a lawyer first.",
        ],
        "authorities": ["Fifth Amendment", "Sixth Amendment", "OCGA 16-10-20", "OCGA 17-16-1 et seq.", "OCGA 24-8-824"],
    },
    {
        "id": "street",
        "title": "Street encounter",
        "open_with": "A conversation on the street is not automatically a detention.",
        "script": [
            "Ask whether you are free to leave. If yes, you can leave calmly.",
            "If detained, do not run or fight. Ask what you are suspected of.",
            "Georgia does not have a general stop-and-identify statute for pedestrians. A driver in a car is different.",
            "You can refuse consent to a frisk or search. A frisk can still be argued if the officer claims a safety basis.",
            "State that you do not consent, then do not resist.",
        ],
        "authorities": ["Fourth Amendment", "OCGA 17-4-20", "OCGA 16-10-24"],
    },
]

LANDMARKS = [
    {"cite": "Miranda v. Arizona, 384 U.S. 436 (1966)", "holding": "Before custodial interrogation, police must warn of the right to silence and counsel if they want to use the statements."},
    {"cite": "Terry v. Ohio, 392 U.S. 1 (1968)", "holding": "A brief stop needs reasonable suspicion. A limited frisk needs a safety basis."},
    {"cite": "Rodriguez v. United States, 575 U.S. 348 (2015)", "holding": "A traffic stop may not be prolonged for a dog sniff after the traffic mission is done, unless there is separate reasonable suspicion."},
    {"cite": "Riley v. California, 573 U.S. 373 (2014)", "holding": "Police generally need a warrant to search a cell phone seized during an arrest."},
    {"cite": "Payton v. New York, 445 U.S. 573 (1980)", "holding": "Entering a home to arrest someone generally requires a warrant, absent a recognized exception."},
    {"cite": "Georgia v. Randolph, 547 U.S. 103 (2006)", "holding": "A physically present resident's refusal can defeat another resident's consent to a home search."},
    {"cite": "Edwards v. Arizona, 451 U.S. 477 (1981)", "holding": "After a suspect clearly asks for counsel, police may not reinitiate interrogation until counsel is available."},
    {"cite": "Whren v. United States, 517 U.S. 806 (1996)", "holding": "A traffic stop is judged by whether there was a traffic violation, not the officer's hidden motive."},
    {"cite": "OCGA 17-5-30", "holding": "Georgia provides a motion to suppress evidence obtained by an unlawful search and seizure."},
    {"cite": "OCGA 40-5-67.1", "holding": "Georgia implied-consent notice and testing rules apply after a qualifying DUI arrest, separate from field tests."},
    {"cite": "OCGA 16-10-24", "holding": "Obstruction of an officer is its own crime. Verbal disagreement is not the same as physical resistance."},
    {"cite": "OCGA 9-11-7(b)", "holding": "In civil court, any application for an order is a motion. There is no closed list of motion names."},
]

COURTS = [
    "Supreme Court of Georgia",
    "Court of Appeals of Georgia",
    "Superior Court",
    "State Court",
    "Magistrate Court",
    "Probate Court",
    "Juvenile Court",
    "Municipal Court",
    "Georgia Office of State Administrative Hearings",
]


def encounter_pack():
    return {
        "disclaimer": DISCLAIMER,
        "encounters": ENCOUNTERS,
        "landmarks": LANDMARKS,
        "courts": COURTS,
        "coverage_limit": (
            "Stored here: encounter scripts, core statutes, and leading public holdings. "
            "Not yet complete here: the full Official Code of Georgia Annotated (public domain since Georgia v. Public.Resource.Org, 2020; imported in batches with release-date provenance) and every public trial-court file. "
            "Trial dockets are fragmented and often contain private facts. Appellate opinions are the right reference layer to ingest next."
        ),
    }
