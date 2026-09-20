from pathlib import Path

from app import storage


def test_supabase_s3_client_uses_path_style_and_no_unsupported_sse(monkeypatch, tmp_path: Path):
    captured = {}

    class FakeClient:
        def upload_file(self, *args, **kwargs):
            captured["upload_args"] = args
            captured["upload_kwargs"] = kwargs

    def fake_client(*args, **kwargs):
        captured["client_args"] = args
        captured["client_kwargs"] = kwargs
        return FakeClient()

    monkeypatch.setenv("S3_ENDPOINT_URL", "https://example.storage.supabase.co/storage/v1/s3")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setattr("boto3.client", fake_client)
    monkeypatch.setattr(storage, "BACKEND", "s3")
    monkeypatch.setattr(storage, "BUCKET", "ga-law-help-evidence")

    source = tmp_path / "evidence.bin"
    source.write_bytes(b"evidence")
    storage.put_file(source, "1/2/evidence.bin")

    config = captured["client_kwargs"]["config"]
    assert config.s3["addressing_style"] == "path"
    assert captured["upload_kwargs"] == {}
    assert not source.exists()
