import pytest

from app.private_case_policy import (
    PRIVATE_CASE_RESOURCE_TYPES,
    PUBLIC_CORPUS_RESOURCE_TYPES,
    assert_private_resources_not_public,
    private_storage_prefix,
    require_private_case_owner,
)


def test_private_and_public_resource_classes_never_overlap():
    assert PRIVATE_CASE_RESOURCE_TYPES.isdisjoint(PUBLIC_CORPUS_RESOURCE_TYPES)


def test_private_case_owner_allows_only_authenticated_owner():
    require_private_case_owner(owner_id=7, requester_id=7, authenticated=True)
    with pytest.raises(PermissionError):
        require_private_case_owner(owner_id=7, requester_id=8, authenticated=True)
    with pytest.raises(PermissionError):
        require_private_case_owner(owner_id=7, requester_id=7, authenticated=False)


def test_public_corpus_guard_rejects_every_private_case_resource():
    for resource_type in PRIVATE_CASE_RESOURCE_TYPES:
        with pytest.raises(ValueError):
            assert_private_resources_not_public([resource_type])


def test_public_corpus_guard_accepts_legal_authority_resources():
    assert_private_resources_not_public(PUBLIC_CORPUS_RESOURCE_TYPES)


def test_private_storage_prefix_is_user_and_case_scoped():
    assert private_storage_prefix(12, 34) == "private/users/12/cases/34"
    with pytest.raises(ValueError):
        private_storage_prefix(0, 34)
    with pytest.raises(ValueError):
        private_storage_prefix(12, 0)
