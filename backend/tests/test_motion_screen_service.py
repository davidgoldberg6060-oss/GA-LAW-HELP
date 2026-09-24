from app.motion_screen_service import motion_screen_prompt


class Query:
    def __init__(self, rows): self.rows = rows
    def filter(self, *_args, **_kwargs): return self
    def all(self): return self.rows


class DB:
    def __init__(self, authorities, versions):
        self.authorities = authorities
        self.versions = versions
    def query(self, model):
        from app import models
        return Query(self.authorities if model is models.LegalAuthority else self.versions)


class Authority:
    id = 1
    citation = 'Example Citation'
    title = 'Example'
    text = 'The motion to suppress evidence was denied.'
    status = 'UNVERIFIED'
    source_url = 'https://official.example/opinion'


class Version:
    authority_id = 1
    verification_status = 'VERIFIED'
    source_url = 'https://official.example/version'


def test_prompt_injects_only_verified_registry_context():
    prompt, coverage = motion_screen_prompt(DB([Authority()], [Version()]), 'Case facts here')
    assert 'VERIFIED MOTION REGISTRY' in prompt
    assert 'Motion to Suppress Evidence' in prompt
    assert 'Example Citation' in prompt
    assert 'Case facts here' in prompt
    assert coverage['VERIFIED_CURRENT'] >= 1


def test_prompt_fails_closed_when_no_authority_is_verified():
    prompt, coverage = motion_screen_prompt(DB([Authority()], []), 'Case facts here')
    assert 'No motion candidate currently satisfies the verified-current authority gate' in prompt
    assert 'do not invent a citation' in prompt.lower()
    assert coverage['VERIFIED_CURRENT'] == 0
