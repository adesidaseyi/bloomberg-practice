from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class DocStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass
class Document:
    doc_id: str
    title: str
    status: DocStatus


class ApprovalService:
    """A document approval workflow. A submitted document is PENDING, and from
    there it can be approved, rejected, or withdrawn by its author. Those are
    terminal states."""

    def __init__(self) -> None:
        self._docs: dict[str, Document] = {}
        self._seq = 0

    def submit(self, title: str) -> Document:
        self._seq += 1
        did = f"D{self._seq}"
        doc = Document(did, title, DocStatus.PENDING)
        self._docs[did] = doc
        return doc

    def approve(self, doc_id: str) -> Document:
        doc = self._get(doc_id)
        doc.status = DocStatus.APPROVED
        return doc

    def reject(self, doc_id: str) -> Document:
        doc = self._get(doc_id)
        doc.status = DocStatus.REJECTED
        return doc

    def withdraw(self, doc_id: str) -> Document:
        doc = self._get(doc_id)
        doc.status = DocStatus.WITHDRAWN
        return doc

    def status(self, doc_id: str) -> DocStatus:
        return self._get(doc_id).status

    def pending_count(self) -> int:
        return len(self._docs)

    def _get(self, doc_id: str) -> Document:
        doc = self._docs.get(doc_id)
        if doc is None:
            raise ValueError("document not found")
        return doc
