package help.galaw.standalone

/**
 * Curated in-app starting points. Legal rules can be fact-specific and change; the app's
 * authority corpus remains the source for current citations and case-specific research.
 */
object GeorgiaKnowledge {
    val rightsTopics = listOf(
        "Police stops & questioning" to "You can ask whether you are free to leave. You may clearly say you wish to remain silent. Do not physically resist. If you are in custody and being questioned, clearly request a lawyer.",
        "Searches & consent" to "You can clearly state that you do not consent to a search. A search may still occur under a warrant or a recognized exception; do not physically interfere. Record the facts for later legal review.",
        "Arrest & first appearance" to "Ask what you are charged with, request counsel, and preserve paperwork. Deadlines and release decisions can move quickly, so record dates and court information.",
        "Right to counsel" to "Criminal defendants can have important rights to counsel. If you cannot afford counsel, ask the court about appointed counsel or the public defender process.",
        "Bail & bond" to "Bond conditions are court orders. Read every condition before release and do not assume a condition is optional. Ask counsel or the court how to request a modification.",
        "Plea offers" to "A guilty plea can waive major rights. Before accepting one, understand the exact counts, sentencing exposure, negotiated terms, immigration or supervision consequences, and what appeal rights may be waived.",
        "Sentencing & merger" to "The sentence should be checked count by count against the offense date, statute, verdict or plea, merger rules, and the written sentence. Keep the sentencing transcript and final order.",
        "Appeal deadlines" to "Appeal and post-judgment deadlines can be short and procedural rules matter. Keep the judgment date, docket, notices, transcripts and orders together and get case-specific advice promptly.",
        "Probation" to "Know every written condition, reporting requirement, payment obligation and restriction. Keep proof of reporting and payments. Alleged violations can lead to hearings and sanctions.",
        "Record restriction" to "Georgia record restriction eligibility depends on the disposition and other facts. An arrest does not automatically mean every record can be erased. Verify the current statutory process for the specific case.",
        "Landlord / tenant" to "Eviction and dispossessory cases have procedural deadlines. Keep the lease, notices, payment records, photographs and court papers; do not ignore a summons.",
        "Family violence orders" to "Protective-order proceedings can affect contact, housing, firearms and family matters. Read temporary orders carefully and attend the scheduled hearing.",
        "Traffic stops" to "Keep hands visible, provide documents the law requires, and avoid physical confrontation. You can preserve objections to a search or seizure without resisting on the roadside.",
        "Recording encounters" to "Recording law can depend on where you are, who is speaking, privacy expectations and whether recording interferes with lawful duties. Preserve original files and metadata when a recording may become evidence.",
        "Court papers & service" to "Do not ignore papers because you think the claim is wrong. Response periods and service rules can determine what happens before the merits are ever reached.",
        "Evidence preservation" to "Keep originals. Avoid editing potentially important photos, audio or video. Preserve messages, timestamps, file metadata, receipts and documents, and make a separate working copy when possible."
    )

    val resourceTopics = listOf(
        "Crisis / suicide support" to "988 Suicide & Crisis Lifeline — call or text 988. Use 911 for immediate danger.",
        "Substance-use treatment" to "SAMHSA National Helpline: 1-800-662-HELP (4357). Treatment referral and information; emergency danger still belongs with 911.",
        "Alcohol recovery support" to "SAMHSA's helpline can provide treatment referral. The app should present recovery resources as assistance, not as legal advice.",
        "Domestic violence safety" to "National Domestic Violence Hotline: 1-800-799-SAFE (7233). If immediate danger exists, use 911.",
        "Legal representation" to "Use the app's case workspace and Georgia-law search for information; representation and case-specific court action should be handled through qualified counsel or an appropriate Georgia legal-services provider."
    )

    val myths = listOf(
        "Myth: Police must always read Miranda rights immediately after an arrest." to "Miranda generally concerns custodial interrogation; an arrest by itself does not mean warnings must be recited at that instant.",
        "Myth: If an officer did not read Miranda, the whole case is automatically dismissed." to "The usual issue is whether particular statements can be used; dismissal is not an automatic result.",
        "Myth: Refusing consent guarantees police cannot search." to "Stating non-consent preserves the issue, but a warrant or recognized exception may independently authorize a search.",
        "Myth: A case disappears from every record when charges are dropped." to "Court, criminal-history and private records can be governed by different rules. Record restriction is a separate question.",
        "Myth: Paying rent late means a landlord can immediately remove a tenant personally." to "Georgia dispossessory proceedings have legal process requirements; self-help assumptions can be dangerous.",
        "Myth: A verbal promise from a prosecutor or lawyer is always enough." to "Important plea and sentencing terms should be confirmed in the formal record and documents.",
        "Myth: An appeal is simply a new trial." to "Appeals generally review alleged legal error using a record and procedural rules; they are not automatically a complete do-over.",
        "Myth: Every mistake by police makes evidence inadmissible." to "Suppression depends on the legal rule, facts, preservation and available remedies; not every error has the same consequence.",
        "Myth: You can ignore a civil lawsuit if the allegations are false." to "Failure to respond can have serious procedural consequences even when you dispute the claim.",
        "Myth: A not-guilty verdict and a dismissal are the same procedural event." to "Both can end a prosecution, but they arise differently and can have different legal consequences.",
        "Myth: Probation means you are completely free as long as you avoid a new arrest." to "Probation commonly includes additional written conditions; violations can be alleged without a new criminal conviction.",
        "Myth: The maximum sentence printed online always answers a person's actual exposure." to "Offense date, count structure, recidivist rules, enhancements, merger and other statutes can matter.",
        "Myth: If two charges come from one incident they automatically merge." to "Merger is a legal analysis, not simply a same-incident rule.",
        "Myth: Deleted texts can never matter in court." to "Copies, backups, screenshots, recipient devices, provider records or other evidence may still exist; authenticity and admissibility are separate issues.",
        "Myth: A private agreement can always override a court order." to "Parties should not assume they can privately disregard an existing order; modifications may require court action.",
        "Myth: 'Funny law' lists on the internet are reliable statements of current Georgia law." to "Many viral lists confuse repealed provisions, local ordinances, proposed bills, old cases and folklore. GA.LAW.HELP should label an item verified only when an authoritative source supports it."
    )
}
