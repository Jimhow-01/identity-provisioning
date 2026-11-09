"""Testes do filtro de e-mails usado no offboarding em lote."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))

import filter_directory_export as fde  # noqa: E402


def write_export(tmp_path, users):
    src = tmp_path / "users_info.json"
    src.write_text(json.dumps({"users": users}), encoding="utf-8")
    return src


def test_keeps_only_emails_matching_the_domain(tmp_path):
    src = write_export(tmp_path, [
        {"Email Address [Required]": "ana.silva@example.com"},
        {"Email Address [Required]": "bruno@example.com"},
        {"Email Address [Required]": "pessoa@outraempresa.com"},
        {"Email Address [Required]": "sem-email"},
    ])
    out = tmp_path / "emails.json"
    fde.filtrar_emails(str(src), str(out))
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result == ["ana.silva@example.com", "bruno@example.com"]


def test_domain_match_is_anchored_to_the_end(tmp_path):
    """`@example.com` no meio de um dominio diferente nao deve passar."""
    src = write_export(tmp_path, [
        {"Email Address [Required]": "x@example.com.evil.net"},
    ])
    out = tmp_path / "emails.json"
    fde.filtrar_emails(str(src), str(out))
    assert not out.exists()


def test_missing_email_key_is_tolerated(tmp_path):
    src = write_export(tmp_path, [{"Nome": "sem campo de e-mail"}])
    out = tmp_path / "emails.json"
    fde.filtrar_emails(str(src), str(out))
    assert not out.exists()


def test_empty_users_list_does_not_crash(tmp_path):
    src = write_export(tmp_path, [])
    out = tmp_path / "emails.json"
    fde.filtrar_emails(str(src), str(out))
    assert not out.exists()
