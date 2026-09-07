"""Phrase-to-code tables: maps funder prose to citizenship, employer type,
career stage, funding type and ANZSRC FoR division codes.

All matching is case-insensitive, whole-word/phrase, and treats a hyphen and
a space as interchangeable inside a phrase (so "early-career" and
"early career" both match the same pattern).
"""

from __future__ import annotations

import re

from backend.ranking.models import CareerStage, EmployerType, FundingType

# --- helpers ---------------------------------------------------------------


def _flex(phrase: str) -> str:
    """Turn a phrase into a regex fragment where a hyphen or a space in the
    source phrase matches either a hyphen or a space (or run of either) in
    the text, e.g. "early career" -> matches "early-career" too.

    Each phrase is a small hand-written regex fragment, not a literal
    string: "citizens?", "compan(?:y|ies)" and similar rely on real regex
    syntax, so the space/hyphen split below must not escape the pieces
    (re.escape would turn "(?:y|ies)" into literal parenthesis characters).
    Any genuine literal character (e.g. the dots in "U.S.") is pre-escaped
    by the phrase itself, such as "u\\.s\\.".
    """
    parts = re.split(r"[ -]", phrase)
    return r"[ -]+".join(parts)


def _compile(phrases: list[str]) -> re.Pattern[str]:
    """Compile a case-insensitive, word-bounded regex matching any phrase in
    the list, with hyphen/space interchangeable inside each phrase."""
    alternatives = "|".join(_flex(phrase) for phrase in phrases)
    return re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)


# --- citizenship -------------------------------------------------------------

# Assumption: an "Australian permanent resident" is treated the same as an
# "Australian citizen" (both map to AU). PR status is not citizenship, but
# for the researcher's eligibility purposes here the two are grouped together
# because funders that admit PRs are, in practice, open to AU-based
# researchers regardless of citizenship status.
_CITIZENSHIP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        _compile(
            [
                "australian citizens?",
                "citizens? of australia",
                "australian permanent residents?",
                # Shared-subject phrasing: "Australian or New Zealand citizens".
                "australian (?:or|and) new zealand citizens?",
            ]
        ),
        "AU",
    ),
    (_compile(["new zealand citizens?"]), "NZ"),
    (_compile(["us citizens?", "u\\.s\\. citizens?", "united states citizens?"]), "US"),
    (_compile(["uk nationals?", "british citizens?", "uk citizens?"]), "GB"),
    (_compile(["canadian citizens?"]), "CA"),
]

# Phrases such as "any nationality", "all nationalities", "no citizenship
# requirements" and "no citizenship or residency requirements" set nothing
# deliberately: they are not in the table above, so they simply fail every
# pattern and find_citizenships returns [], which the ranker already reads
# as "unrestricted".


def find_citizenships(text: str | None) -> list[str]:
    """ISO 3166-1 alpha-2 codes mentioned as required citizenship, sorted and
    unique. Empty list means unrestricted (either nothing was said, or the
    text explicitly states there is no restriction)."""
    if not text:
        return []
    codes = {code for pattern, code in _CITIZENSHIP_PATTERNS if pattern.search(text)}
    return sorted(codes)


# --- employer type -----------------------------------------------------------

_EMPLOYER_PATTERNS: list[tuple[re.Pattern[str], EmployerType]] = [
    (_compile(["universit(?:y|ies)", "higher education"]), EmployerType.UNIVERSITY),
    (
        _compile(
            [
                "research institutes?",
                "medical research institute",
                "research organisations?",
                "research organizations?",
            ]
        ),
        EmployerType.RESEARCH_INSTITUTE,
    ),
    (
        _compile(["industry", "compan(?:y|ies)", "businesses?", "smes?"]),
        EmployerType.INDUSTRY,
    ),
    (
        _compile(
            [
                "philanthropic",
                "not-for-profit",
                "non-profit",
                "nonprofit",
                "charit(?:y|ies)",
                "ngos?",
            ]
        ),
        EmployerType.PHILANTHROPIC,
    ),
]


def find_employer_types(text: str | None) -> list[EmployerType]:
    """Employer types mentioned, sorted by enum declaration order."""
    if not text:
        return []
    found = {etype for pattern, etype in _EMPLOYER_PATTERNS if pattern.search(text)}
    return [e for e in EmployerType if e in found]


# --- career stage -------------------------------------------------------------

_UNDERGRADUATE_PATTERN = _compile(["undergraduates?"])
_GRADUATE_PATTERN = _compile(
    [
        "phd students?",
        "phd candidates?",
        "doctoral students?",
        "graduate students?",
        "postgraduates?",
        "masters students?",
        "enrolled students?",
    ]
)
_EARLY_CAREER_PATTERN = _compile(["early career", "ecrs?"])
_MID_CAREER_PATTERN = _compile(["mid career"])
_SENIOR_PATTERN = _compile(
    ["senior researchers?", "established researchers?", "professors?", "research leaders?"]
)
_POSTDOCTORAL_PATTERN = _compile(["postdoctoral", "postdocs?", "post-doctoral"])

# Numeric year ranges, only meaningful alongside a PhD/doctorate/completion
# mention. Group 1/2 are the low/high bounds; "up to"/"within" have no low
# bound (assumed 0). Ordered most-specific first: `_years_context_stages`
# skips a match whose span was already claimed by an earlier, more specific
# pattern, so "2 and up to 7 years" is read as one range (2, 7) rather than
# also being re-read as "up to 7 years" -> (0, 7).
_RANGE_PATTERNS = [
    re.compile(r"\bbetween\s*(\d+)\s*and\s*(\d+)\s*years\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*and\s*up\s*to\s*(\d+)\s*years\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*-\s*(\d+)\s*years\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*to\s*(\d+)\s*years\b", re.IGNORECASE),
    re.compile(r"\bup\s*to\s*(\d+)\s*years\b", re.IGNORECASE),
    re.compile(r"\bwithin\s*(\d+)\s*years\b", re.IGNORECASE),
]
_PHD_CONTEXT_PATTERN = re.compile(r"\b(phd|doctorate|doctoral|completion)\b", re.IGNORECASE)

# Postdoc band edges: (low, high) with high=None meaning open-ended.
_POSTDOC_BANDS: list[tuple[int, int | None, CareerStage]] = [
    (0, 2, CareerStage.POSTDOC_0_2),
    (2, 5, CareerStage.POSTDOC_2_5),
    (5, 10, CareerStage.POSTDOC_5_10),
    (10, None, CareerStage.POSTDOC_10_PLUS),
]


def stages_for_years(low: int, high: int | None) -> list[CareerStage]:
    """Postdoc bands overlapping the numeric range [low, high] (high=None
    means open-ended, i.e. no upper bound)."""
    stages = []
    for band_low, band_high, stage in _POSTDOC_BANDS:
        band_is_open = band_high is None
        range_is_open = high is None
        overlaps = (low < band_high if not band_is_open else True) and (
            band_low < high if not range_is_open else True
        )
        if overlaps:
            stages.append(stage)
    return stages


def _years_context_stages(text: str) -> set[CareerStage]:
    """Numeric N-M-years phrases that describe time since PhD completion."""
    stages: set[CareerStage] = set()
    if not _PHD_CONTEXT_PATTERN.search(text):
        return stages
    # Spans already consumed by an earlier, more specific pattern.
    claimed: list[tuple[int, int]] = []
    for pattern in _RANGE_PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(start < c_end and c_start < end for c_start, c_end in claimed):
                continue
            claimed.append((start, end))
            groups = match.groups()
            if len(groups) == 2:
                low, high = int(groups[0]), int(groups[1])
            else:
                low, high = 0, int(groups[0])
            stages |= set(stages_for_years(low, high))
    return stages


def find_career_stages(text: str | None) -> list[CareerStage]:
    """Career stages mentioned, sorted by enum declaration order."""
    if not text:
        return []
    found: set[CareerStage] = set()
    if _UNDERGRADUATE_PATTERN.search(text):
        found.add(CareerStage.UNDERGRADUATE)
    if _GRADUATE_PATTERN.search(text):
        found.add(CareerStage.GRADUATE_STUDENT)
    if _EARLY_CAREER_PATTERN.search(text):
        found.add(CareerStage.POSTDOC_0_2)
        found.add(CareerStage.POSTDOC_2_5)
    if _MID_CAREER_PATTERN.search(text):
        found.add(CareerStage.POSTDOC_5_10)
    if _SENIOR_PATTERN.search(text):
        found.add(CareerStage.POSTDOC_10_PLUS)
    if _POSTDOCTORAL_PATTERN.search(text):
        found.update(
            [
                CareerStage.POSTDOC_0_2,
                CareerStage.POSTDOC_2_5,
                CareerStage.POSTDOC_5_10,
                CareerStage.POSTDOC_10_PLUS,
            ]
        )
    found |= _years_context_stages(text)
    return [s for s in CareerStage if s in found]


# --- funding type ------------------------------------------------------------

_SALARY_PATTERN = _compile(
    ["salary", "salaries", "stipends?", "living allowance", "fellowship salary"]
)
_CONSUMABLES_PATTERN = _compile(
    [
        "consumables",
        "research costs",
        "project costs",
        "direct costs",
        "operating costs",
        "travel",
    ]
)
_EQUIPMENT_PATTERN = _compile(["equipment", "infrastructure", "instruments?", "instrumentation"])

_FUNDING_PATTERNS: list[tuple[re.Pattern[str], FundingType]] = [
    (_SALARY_PATTERN, FundingType.SALARY),
    (_CONSUMABLES_PATTERN, FundingType.CONSUMABLES),
    (_EQUIPMENT_PATTERN, FundingType.EQUIPMENT),
]

_NEGATION_PATTERN = _compile(["not", "no", "does not", "is not available", "excluding", "excludes"])
# Six words either side of the phrase. Checked in both directions: a funder
# usually negates before the phrase ("excluding travel"), but the NHMRC
# fixture negates after it ("Salary support ... is not available"), so a
# preceding-only window would miss that real case.
_NEGATION_WINDOW_WORDS = 6
_WORD_PATTERN = re.compile(r"\S+")


def _is_negated(text: str, match: re.Match[str]) -> bool:
    """True when a negation word appears within six words of the matched
    phrase, before or after it."""
    words = list(_WORD_PATTERN.finditer(text))
    overlapping = [
        i
        for i, word in enumerate(words)
        if word.start() < match.end() and word.end() > match.start()
    ]
    if not overlapping:
        return False
    first_idx, last_idx = overlapping[0], overlapping[-1]
    window_start = max(0, first_idx - _NEGATION_WINDOW_WORDS)
    window_end = min(len(words), last_idx + 1 + _NEGATION_WINDOW_WORDS + 1)
    window_text = " ".join(word.group() for word in words[window_start:window_end])
    return bool(_NEGATION_PATTERN.search(window_text))


def find_funding_types(text: str | None) -> list[FundingType]:
    """Funding types mentioned, excluding ones negated within the six words
    before the phrase, sorted by enum declaration order."""
    if not text:
        return []
    found: set[FundingType] = set()
    for pattern, ftype in _FUNDING_PATTERNS:
        for match in pattern.finditer(text):
            if not _is_negated(text, match):
                found.add(ftype)
                break
    return [f for f in FundingType if f in found]


# --- ANZSRC FoR divisions -----------------------------------------------------

_FOR_KEYWORDS: dict[str, list[str]] = {
    "30": ["agriculture", "agricultural", "crop", "livestock", "farming", "veterinary"],
    "31": [
        "biology",
        "biological",
        "ecology",
        "ecosystem",
        "marine",
        "coral",
        "reef",
        "genetics",
        "species",
        "zoology",
        "botany",
    ],
    "32": [
        "biomedical",
        "cancer",
        "oncology",
        "clinical",
        "genomic",
        "neuroscience",
        "immunology",
        "medical research",
        "disease",
    ],
    "33": ["architecture", "urban planning", "construction", "building design"],
    "34": ["chemistry", "chemical", "catalysis"],
    "35": ["management", "marketing", "accounting", "business administration"],
    "36": ["creative arts", "music", "visual arts", "performing arts", "design practice"],
    "37": [
        "climate",
        "geoscience",
        "oceanography",
        # "ocean" added alongside the plan's "oceanography": ocean-topic text
        # (e.g. "ocean acidification") should read as earth sciences without
        # requiring the longer derived word to appear verbatim.
        "ocean",
        "atmospheric",
        "geology",
        "earth science",
    ],
    "38": ["economics", "econometrics"],
    "39": ["education", "pedagogy", "teaching and learning"],
    "40": [
        "engineering",
        "battery",
        "energy storage",
        "grid",
        "renewable",
        "materials engineering",
        "robotics",
    ],
    "41": ["environmental", "conservation", "biodiversity", "pollution"],
    "42": ["health", "public health", "epidemiology", "nursing", "health services"],
    "43": ["history", "heritage", "archaeology"],
    "44": ["sociology", "social science", "anthropology", "policy", "criminology"],
    "45": ["indigenous", "aboriginal", "torres strait", "first nations"],
    "46": [
        "machine learning",
        "artificial intelligence",
        "computing",
        "computer science",
        "software",
        "data science",
        "algorithm",
        "cybersecurity",
    ],
    "47": [
        "linguistics",
        "literature",
        "languages",
        "communication studies",
        "media studies",
    ],
    "48": ["law", "legal", "jurisprudence"],
    "49": ["mathematics", "mathematical", "statistics", "statistical"],
    "50": ["philosophy", "ethics", "theology", "religious studies"],
    "51": ["physics", "quantum", "astronomy", "astrophysics", "photonics"],
    "52": ["psychology", "psychological", "cognitive science"],
}

_FOR_PATTERNS: dict[str, re.Pattern[str]] = {
    code: _compile(keywords) for code, keywords in _FOR_KEYWORDS.items()
}


def find_for_divisions(text: str | None) -> list[str]:
    """Two-digit ANZSRC 2020 division codes whose keywords appear in the
    text, sorted alphabetically (which is also numeric order here)."""
    if not text:
        return []
    codes = {code for code, pattern in _FOR_PATTERNS.items() if pattern.search(text)}
    return sorted(codes)
