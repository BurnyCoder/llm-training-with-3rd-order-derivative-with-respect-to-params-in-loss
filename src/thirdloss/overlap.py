"""Split documents before tokenization, using exact hashes and verified shingle overlap."""

import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable


def canonical(text: str) -> str:
    """Make whitespace, case and Unicode compatibility variants equal for leakage checks."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def content_hash(text: str) -> str:
    """Use a stable identity across processes, files and operating systems."""
    return hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Document:
    """Preserve the source text for tokenization and its normalized identity for audits."""

    source_id: str
    text: str
    digest: str
    submitted: str = ""

    @classmethod
    def make(cls, source_id: str, text: str, submitted: str = "") -> "Document":
        return cls(source_id, text.strip(), content_hash(text), submitted)


def shingles(text: str) -> set[str]:
    """Use distinct five-word runs and one whole-text key for very short documents."""
    words = re.findall(r"\w+", canonical(text))
    if len(words) < 5:
        return {" ".join(words) if words else canonical(text)}
    return {" ".join(words[i:i + 5]) for i in range(len(words) - 4)}


def prefix_size(size: int) -> int:
    """At 4/5 Jaccard, at most floor(size/5) items may be outside the intersection."""
    return size // 5 + 1


class ShingleIndex:
    """Index a higher-priority split using the lossless prefix filtering lemma.

    For Jaccard >= 4/5 the overlap must cover at least 4/5 of each set. Under
    a common term order, its first shared term falls in both indexed prefixes.
    Full set comparison verifies all candidates. See Xiao et al., section 2.2:
    https://archives.iw3c2.org/www2008/papers/pdf/p131-xiaoA.pdf
    """

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.frequency = Counter()
        self.postings = defaultdict(list)
        self.lengths = []
        # A rare-first order reduces overlap from generic story openings.
        for doc in documents:
            self.frequency.update(shingles(doc.text))
        for index, doc in enumerate(documents):
            terms = shingles(doc.text)
            self.lengths.append(len(terms))
            for term in self._prefix(terms):
                self.postings[term].append(index)

    def _prefix(self, terms: set[str]) -> list[str]:
        """Unknown terms sort first and cannot appear in any reference posting."""
        known = [term for term in terms if term in self.frequency]
        count = prefix_size(len(terms)) - (len(terms) - len(known))
        if count <= 0:
            return []
        known.sort(key=lambda term: (self.frequency[term], term))
        return known[:count]

    def match(self, terms: set[str]) -> Document | None:
        """Return the earliest source match; exact integer arithmetic decides the cutoff."""
        candidates = set()
        for term in self._prefix(terms):
            candidates.update(self.postings.get(term, ()))
        for index in sorted(candidates):
            n, m = len(terms), self.lengths[index]
            if 5 * min(n, m) < 4 * max(n, m):
                continue
            doc = self.documents[index]
            common = len(terms.intersection(shingles(doc.text)))
            if 5 * common >= 4 * (n + m - common):
                return doc
        return None


def clean_splits(raw: dict[str, list[Document]], log: Callable[[str], None]) -> tuple[dict, dict, list]:
    """Protect test, then dev, then train; retain an audit trail without publishing text."""
    retained: dict[str, list[Document]] = {}
    seen: dict[str, tuple[str, str]] = {}
    protected: list[tuple[str, ShingleIndex]] = []
    rejections = []
    summary = {}
    for split in ("test", "dev", "train"):
        retained[split] = []
        reasons = Counter()
        for row, doc in enumerate(raw[split]):
            if row and row % 25000 == 0:
                log(f"audited {row:,}/{len(raw[split]):,} {split} documents")
            reason, other_split, other_id = "", "", ""
            if not canonical(doc.text):
                reason = "empty"
            elif doc.digest in seen:
                reason = "exact"
                other_split, other_id = seen[doc.digest]
            elif protected:
                terms = shingles(doc.text)
                for name, reference in protected:
                    match = reference.match(terms)
                    if match is not None:
                        reason, other_split, other_id = "near", name, match.source_id
                        break
            if reason:
                reasons[reason] += 1
                rejections.append(dict(split=split, source_id=doc.source_id, sha256=doc.digest,
                                       reason=reason, reference_split=other_split, reference_id=other_id))
            else:
                seen[doc.digest] = (split, doc.source_id)
                retained[split].append(doc)
        summary[split] = dict(input=len(raw[split]), kept=len(retained[split]),
                              exact=reasons["exact"], cross_split_near=reasons["near"], empty=reasons["empty"])
        log(f"{split} overlap audit {summary[split]}")
        if split != "train":
            protected.append((split, ShingleIndex(retained[split])))
    return retained, summary, rejections
