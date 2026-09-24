"""Normaliser: turns the crawler's raw rows into structured Opportunity records.

Pipeline stage 3. The crawler (backend/crawler) stores page text plus a few
raw signals; the ranker (backend/ranking) needs structured fields. This
package sits between them. Deterministic rules run first (decision 3), an
optional LLM extractor fills the prose-derived gaps, and the result is
written to its own SQLite table that backend/data/sqlite_repository reads.
Design record: docs/09-architectural-design/adr/ADR-003-normaliser.md.
"""
