import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100

_PICTURE_OMIT = re.compile(r"\*\*==> picture.*?<==\*\*", re.DOTALL | re.IGNORECASE)
_BOUNDARY = re.compile(
    r"(?=^(?:"
    r"Art\.?\s*\d+(?:º|o)?"
    r"|Artigo\s+\d+"
    r"|§\s*\d+"
    r"|CAPÍTULO\s+[IVXLCDM\d]+"
    r"|Capítulo\s+[IVXLCDM\d]+"
    r"|CAPITULO\s+[IVXLCDM\d]+"
    r"|#{1,3}\s+"
    r"))",
    re.MULTILINE | re.IGNORECASE,
)
_SECTION_LABEL = re.compile(
    r"^(Art\.?\s*\d+(?:º|o)?|Artigo\s+\d+|§\s*\d+|"
    r"CAPÍTULO\s+\S+|Capítulo\s+\S+|CAPITULO\s+\S+|#{1,3}\s+.+)",
    re.IGNORECASE,
)


def _clean_text(text: str) -> str:
    return _PICTURE_OMIT.sub("", text).strip()


def _split_by_boundary(text: str) -> list[str]:
    starts = [match.start() for match in _BOUNDARY.finditer(text)]
    if not starts:
        return [text]

    sections: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)
    return sections


def _section_label(text: str) -> str:
    match = _SECTION_LABEL.match(text.strip())
    return match.group(1).strip() if match else "bloco"


def split_documents(documents: list[Document]) -> list[Document]:
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    oversized_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks: list[Document] = []

    for doc in documents:
        text = _clean_text(doc.page_content)
        if not text:
            continue

        sections = _split_by_boundary(text)
        if len(sections) <= 1:
            for index, piece in enumerate(fallback_splitter.split_text(text)):
                chunks.append(
                    Document(
                        page_content=piece,
                        metadata={
                            **doc.metadata,
                            "chunk_type": "recursivo",
                            "chunk_index": index,
                        },
                    )
                )
            continue

        for section in sections:
            label = _section_label(section)
            if len(section) <= MAX_CHUNK_SIZE:
                chunks.append(
                    Document(
                        page_content=section,
                        metadata={
                            **doc.metadata,
                            "chunk_type": "estrutural",
                            "secao": label,
                        },
                    )
                )
                continue

            for sub_index, piece in enumerate(oversized_splitter.split_text(section)):
                chunks.append(
                    Document(
                        page_content=piece,
                        metadata={
                            **doc.metadata,
                            "chunk_type": "estrutural",
                            "secao": label,
                            "sub_chunk": sub_index,
                        },
                    )
                )

    return chunks
