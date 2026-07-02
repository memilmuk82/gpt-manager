from __future__ import annotations

from html import escape
from pathlib import Path

from markupsafe import Markup


ROOT_DIR = Path(__file__).resolve().parents[2]
LEGAL_DOCUMENTS = {
    "terms": ROOT_DIR / "docs" / "legal" / "TERMS.md",
    "privacy": ROOT_DIR / "docs" / "legal" / "PRIVACY_POLICY.md",
}


class LegalDocumentError(RuntimeError):
    pass


def render_legal_markdown(document_key: str) -> Markup:
    path = LEGAL_DOCUMENTS.get(document_key)
    if path is None:
        raise LegalDocumentError("지원하지 않는 법적 문서입니다.")
    if not path.exists():
        raise LegalDocumentError("법적 문서를 찾을 수 없습니다.")
    return Markup(_markdown_to_html(path.read_text(encoding="utf-8")))


def _markdown_to_html(markdown_text: str) -> str:
    html: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            html.append(f'<p class="leading-7 text-slate-700">{"<br>".join(paragraph)}</p>')
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            html.append(f"</{list_type}>")
            list_type = None

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped == "---":
            flush_paragraph()
            close_list()
            html.append('<hr class="my-8 border-slate-200">')
            continue

        heading_level = _heading_level(stripped)
        if heading_level:
            flush_paragraph()
            close_list()
            text = stripped[heading_level + 1 :].strip()
            tag = f"h{min(heading_level, 3)}"
            classes = {
                1: "text-3xl font-bold text-slate-950",
                2: "mt-8 text-2xl font-semibold text-slate-950",
                3: "mt-6 text-xl font-semibold text-slate-950",
            }[min(heading_level, 3)]
            html.append(f'<{tag} class="{classes}">{escape(text)}</{tag}>')
            continue

        unordered = stripped.startswith("- ")
        ordered = _is_ordered_list_item(stripped)
        if unordered or ordered:
            flush_paragraph()
            target_list = "ul" if unordered else "ol"
            if list_type != target_list:
                close_list()
                list_class = "list-disc" if target_list == "ul" else "list-decimal"
                html.append(f'<{target_list} class="ml-6 space-y-2 {list_class} text-slate-700">')
                list_type = target_list
            item_text = stripped[2:] if unordered else stripped.split(".", 1)[1].strip()
            html.append(f"<li>{escape(item_text)}</li>")
            continue

        close_list()
        paragraph.append(escape(stripped))

    flush_paragraph()
    close_list()
    return "\n".join(html)


def _heading_level(line: str) -> int:
    if not line.startswith("#"):
        return 0
    count = 0
    for char in line:
        if char == "#":
            count += 1
        else:
            break
    if count and len(line) > count and line[count] == " ":
        return count
    return 0


def _is_ordered_list_item(line: str) -> bool:
    prefix, separator, rest = line.partition(".")
    return bool(separator and prefix.isdigit() and rest.startswith(" "))
