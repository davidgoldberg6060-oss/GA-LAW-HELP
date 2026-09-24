"""Build auditable motion/remedy candidates from the indexed Georgia corpus."""
from .motion_discovery import discover_from_authorities
from .motion_registry import classify_verification, coverage_summary, seed_catalog, normalize_motion_name


def build_motion_registry(authorities, versions_by_authority: dict[int, list] | None = None) -> dict:
    versions_by_authority = versions_by_authority or {}
    discovered = discover_from_authorities(authorities)
    records: dict[str, dict] = {}

    for seed in seed_catalog():
        key = normalize_motion_name(seed["name"])
        records[key] = {
            **seed,
            "normalized_name": key,
            "verification_status": "UNRECOGNIZED_RESEARCH_REQUIRED",
            "occurrence_count": 0,
            "authority_refs": [],
        }
        for alias in seed.get("aliases", ()):
            records.setdefault(normalize_motion_name(alias), records[key])

    canonical = {}
    for key, value in records.items():
        canonical[normalize_motion_name(value["name"])] = value

    for item in discovered:
        key = item["normalized_name"]
        record = canonical.get(key)
        if record is None:
            record = {
                "name": item["display_name"].title(),
                "aliases": (),
                "practice_area": "unknown",
                "stage": "unknown",
                "purpose": "Discovered in indexed Georgia authority; classification pending review.",
                "normalized_name": key,
                "verification_status": "UNRECOGNIZED_RESEARCH_REQUIRED",
                "occurrence_count": 0,
                "authority_refs": [],
            }
            canonical[key] = record
        record["occurrence_count"] += item["occurrence_count"]
        record["authority_refs"].extend(item["authority_refs"])

    output = []
    for record in canonical.values():
        statuses = []
        has_official_source = False
        refs = []
        for ref in record["authority_refs"]:
            authority_id = ref.get("authority_id")
            statuses.append(ref.get("authority_status", "UNVERIFIED"))
            source = str(ref.get("source_url") or "")
            if source.startswith("https://"):
                has_official_source = True
            for version in versions_by_authority.get(authority_id, []):
                status = str(getattr(version, "verification_status", "UNVERIFIED") or "UNVERIFIED")
                version_source = str(getattr(version, "source_url", "") or "")
                statuses.append(status)
                if version_source.startswith("https://") and status.upper() in {"VERIFIED", "OFFICIAL", "CURRENT"}:
                    has_official_source = True
                refs.append({
                    "authority_id": authority_id,
                    "citation": ref.get("citation", ""),
                    "source_url": version_source or source,
                    "verification_status": status,
                })
        record["verification_status"] = classify_verification(statuses, has_official_source)
        record["verified_authorities"] = [r for r in refs if str(r["verification_status"]).upper() in {"VERIFIED", "OFFICIAL", "CURRENT"} and str(r["source_url"]).startswith("https://")]
        # Keep raw discovery refs out of AI-facing output when a verified version exists.
        output.append(record)

    unique = {normalize_motion_name(row["name"]): row for row in output}
    rows = sorted(unique.values(), key=lambda row: (row["verification_status"] != "VERIFIED_CURRENT", -row["occurrence_count"], row["name"]))
    return {"motions": rows, "coverage": coverage_summary(rows)}


def verified_motion_context(registry: dict, limit: int = 30) -> str:
    lines = []
    for row in registry.get("motions", []):
        if row.get("verification_status") != "VERIFIED_CURRENT":
            continue
        authorities = row.get("verified_authorities", [])
        citations = "; ".join(filter(None, [str(item.get("citation") or "") for item in authorities[:3]]))
        lines.append(f"- {row['name']} | stage: {row.get('stage','unknown')} | purpose: {row.get('purpose','')} | verified authority: {citations or 'verified source in corpus'}")
        if len(lines) >= limit:
            break
    return "\n".join(lines) or "No motion candidate currently satisfies the verified-current authority gate. Do not invent a motion-specific citation."
