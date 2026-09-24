"""Case motion-screen preparation backed by verified Georgia authority versions."""
from . import models
from .motion_service import build_motion_registry, verified_motion_context


def registry_for_db(db):
    authorities = db.query(models.LegalAuthority).filter(
        models.LegalAuthority.jurisdiction.ilike('%Georgia%')
    ).all()
    authority_ids = [row.id for row in authorities]
    versions_by_authority = {authority_id: [] for authority_id in authority_ids}
    if authority_ids:
        versions = db.query(models.AuthorityVersion).filter(
            models.AuthorityVersion.authority_id.in_(authority_ids)
        ).all()
        for version in versions:
            versions_by_authority.setdefault(version.authority_id, []).append(version)
    return build_motion_registry(authorities, versions_by_authority)


def motion_screen_prompt(db, facts: str) -> tuple[str, dict]:
    registry = registry_for_db(db)
    verified_context = verified_motion_context(registry, limit=40)
    prompt = (
        'GEORGIA CRIMINAL CASE MOTION SCREEN. Analyze only supplied case facts. '
        'Identify potentially relevant procedural options, motions, or post-conviction remedies without predicting outcomes. '
        'Treat VERIFIED MOTION REGISTRY entries below as the only motion-specific authorities approved for specific citation. '
        'A motion absent from the verified registry may still be identified as a research lead, but clearly label it UNVERIFIED/RESEARCH REQUIRED and do not invent a citation. '
        'For each relevant option explain why it may apply, missing facts or records, timing issues to verify, likely State counterarguments, and the next record to obtain. '
        'Never invent statutes, cases, deadlines, judges, holdings, or local filing rules. '
        'Distinguish pretrial, trial, direct review, and post-conviction procedures. End with a prioritized verification checklist. '
        'VERIFIED MOTION REGISTRY:\n' + verified_context + '\nCASE INFORMATION:\n' + facts
    )
    return prompt, registry['coverage']
