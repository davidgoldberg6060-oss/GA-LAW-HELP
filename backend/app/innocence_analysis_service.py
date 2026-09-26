"""Orchestrate innocence-focused issue spotting with verified Georgia authority screening."""
from .intelligence.innocence_analysis import CaseNarrative, analyze_narrative, next_questions
from .motion_screen_service import motion_screen_response


def _signal_dict(signal):
    return {
        'issue': signal.issue,
        'kind': signal.kind.value,
        'matched_signals': signal.matched_signals,
        'questions_to_ask': signal.questions_to_ask,
        'possible_avenues': signal.possible_avenues,
        'note': signal.note,
    }


def innocence_analysis_response(db, case, additional_facts: str, ask_fn) -> dict:
    narrative_text = (case.narrative or '').strip()
    if additional_facts:
        narrative_text += ('\n' if narrative_text else '') + additional_facts

    narrative = CaseNarrative(
        narrative=narrative_text,
        charges=[],
        stage=(case.stage or 'unknown'),
        event_date=None,
        county=(case.county or None),
        user_claims_innocence=None,
    )
    signals = analyze_narrative(narrative)
    questions = next_questions(narrative, signals)

    facts = (
        'Case title: ' + (case.title or '') + '\n'
        'Case number: ' + (case.case_number or 'Not entered') + '\n'
        'Georgia county: ' + (case.county or 'Not entered') + '\n'
        'Case type: ' + (case.case_type or 'Not entered') + '\n'
        'Current stage: ' + (case.stage or 'Not entered') + '\n'
        'User-supplied narrative (not independently verified): ' + (narrative_text or 'Not entered') + '\n'
        'Structured issue signals (not legal conclusions): ' +
        ', '.join(signal.issue for signal in signals)
    )
    if len(facts) > 12000:
        facts = facts[:12000] + '\n[Case text truncated for analysis]'

    motion_result = motion_screen_response(db, facts, ask_fn)
    return {
        'innocence_review': {
            'issue_signals': [_signal_dict(signal) for signal in signals],
            'follow_up_questions': questions,
            'interpretation': (
                'Affirmative innocence evidence is analyzed separately from reasonable-doubt '
                'or insufficiency issues. Signals are investigation leads, not findings of innocence or guilt.'
            ),
        },
        'motion_and_remedy_review': motion_result,
        'verification_mode': 'VERIFIED_REGISTRY_ONLY',
        'notice': (
            'Legal information, not legal advice. User-supplied facts are not independently verified. '
            'A suggested issue or procedural avenue is not a conclusion that a person is innocent or '
            'that a motion will succeed. Verify the record, current controlling authority, deadlines, '
            'preservation requirements, and local filing rules.'
        ),
    }
