"""Message classification: does this look like a ticket, and how strongly?

Keywords cover both English and Indonesian phrasings; the detection itself is
language-neutral. Only the injected text (hooks/messages/*.json) is localized.
"""

import re
from typing import Optional

STRONG = re.compile(
    r"tiket|ticket|bug|repo|branch|commit|merge|pull request|\bpr\b|deploy|refactor|refaktor|"
    r"endpoint|\bapi\b|komponen|component|codebase|unit test|integration test|\be2e\b|vitest|"
    r"lint|npm|pnpm|migration|migrasi|\bschema\b|\bquery\b|\bsql\b|crud|\bocr\b|typescript|"
    r"javascript|react|express|tailwind|```|\.(?:tsx?|jsx?|py|sql|json|mjs)\b"
)
WEAK = re.compile(
    r"\bfix\b|perbaiki|benerin|tambah(?:kan)?|hapus|ubah|ganti|rename|error|gagal|crash|"
    r"implement\w*|fitur|halaman|\bform\b|validasi|\bauth\b|login|\bdatabase\b|fungsi|"
    r"\bdir\b|\bfolder\b|\bscript\b|\bjalankan\b|bikin|buat(?:kan)?"
)
DOC = re.compile(
    r"\bdocs?\b|documentation|readme|changelog|essay|thesis|dissertation|manuscript|"
    r"\bchapter\b|abstract|naskah|\bbab\b|paragraf|\bdraf\b|docx|sitasi|kutipan"
)


def classify(message: str) -> Optional[str]:
    """Return "full", "short", or None for a lowercased user message."""
    if STRONG.search(message):
        return "full"
    if WEAK.search(message):
        return "short" if DOC.search(message) else "full"
    return None
