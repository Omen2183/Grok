"""FTS5 semantic lore index — events, recaps, NPCs, lore_summary (SQLite-backed)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import get_campaign_path

LORE_INDEX_VERSION = "4.0.0"


def _db_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "campaign_index.sqlite"


def _ensure_fts(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS lore_fts USING fts5(
            doc_type,
            doc_id,
            title,
            body,
            tokenize='porter'
        )
        """
    )


def init_lore_index(campaign_name: str) -> Path:
    path = _db_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        _ensure_fts(conn)
        conn.commit()
    flag = path.parent / "sqlite_enabled.flag"
    flag.write_text("enabled\n", encoding="utf-8")
    return path


def _index_doc(
    campaign_name: str,
    *,
    doc_type: str,
    doc_id: str,
    title: str,
    body: str,
) -> None:
    init_lore_index(campaign_name)
    with sqlite3.connect(_db_path(campaign_name)) as conn:
        _ensure_fts(conn)
        conn.execute(
            "DELETE FROM lore_fts WHERE doc_type = ? AND doc_id = ?",
            (doc_type, doc_id),
        )
        conn.execute(
            "INSERT INTO lore_fts (doc_type, doc_id, title, body) VALUES (?, ?, ?, ?)",
            (doc_type, doc_id, title, body),
        )
        conn.commit()


def index_event(campaign_name: str, event: Dict[str, Any], *, event_id: str) -> None:
    tags = ", ".join(event.get("tags", []))
    body = f"{event.get('description', '')} tags:{tags} type:{event.get('type', '')}"
    _index_doc(
        campaign_name,
        doc_type="event",
        doc_id=event_id,
        title=event.get("description", "")[:80],
        body=body,
    )


def index_lore_summary(campaign_name: str) -> int:
    path = get_campaign_path(campaign_name) / "state" / "lore_summary.md"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    _index_doc(
        campaign_name,
        doc_type="lore_summary",
        doc_id="main",
        title=f"Lore Summary — {campaign_name}",
        body=text,
    )
    return 1


def index_recaps(campaign_name: str) -> int:
    recap_dir = get_campaign_path(campaign_name) / "recaps"
    if not recap_dir.exists():
        return 0
    count = 0
    for recap_path in sorted(recap_dir.glob("session_*.md")):
        text = recap_path.read_text(encoding="utf-8")
        _index_doc(
            campaign_name,
            doc_type="recap",
            doc_id=recap_path.stem,
            title=recap_path.name,
            body=text,
        )
        count += 1
    return count


def index_npcs(campaign_name: str) -> int:
    npc_dir = get_campaign_path(campaign_name) / "npcs"
    index_path = npc_dir / "index.json"
    if not index_path.exists():
        return 0
    index = json.loads(index_path.read_text(encoding="utf-8"))
    count = 0
    for entry in index.get("npcs", []):
        npc_id = entry.get("id") or entry.get("name", "unknown")
        npc_path = npc_dir / f"{npc_id}.json"
        if npc_path.exists():
            data = json.loads(npc_path.read_text(encoding="utf-8"))
        else:
            data = entry
        body = json.dumps(data, ensure_ascii=False)
        _index_doc(
            campaign_name,
            doc_type="npc",
            doc_id=str(npc_id),
            title=data.get("name", str(npc_id)),
            body=body,
        )
        count += 1
    return count


def rebuild_lore_index(campaign_name: str) -> Dict[str, Any]:
    """Full reindex from campaign files + events.json."""
    init_lore_index(campaign_name)
    events_path = get_campaign_path(campaign_name) / "logs" / "events.json"
    event_count = 0
    if events_path.exists():
        raw = json.loads(events_path.read_text(encoding="utf-8"))
        event_list = raw if isinstance(raw, list) else raw.get("events", [])
        for i, event in enumerate(event_list):
            if isinstance(event, dict):
                index_event(campaign_name, event, event_id=str(i))
                event_count += 1
    return {
        "lore_summary": index_lore_summary(campaign_name),
        "recaps": index_recaps(campaign_name),
        "npcs": index_npcs(campaign_name),
        "events": event_count,
        "version": LORE_INDEX_VERSION,
    }


def search_lore(
    campaign_name: str,
    query: str,
    *,
    limit: int = 10,
    doc_type: Optional[str] = None,
) -> Dict[str, Any]:
    """FTS5 search across indexed lore. Falls back to substring if index empty."""
    db = _db_path(campaign_name)
    if not db.exists():
        rebuild_lore_index(campaign_name)

    safe_query = " ".join(query.split())
    if not safe_query:
        return {"query": query, "count": 0, "results": [], "engine": "fts5"}

    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        _ensure_fts(conn)
        fts_query = " OR ".join(f'"{term}"' for term in safe_query.split() if term)
        sql = """
            SELECT doc_type, doc_id, title, snippet(lore_fts, 3, '[[', ']]', '…', 24) AS excerpt,
                   bm25(lore_fts) AS rank
            FROM lore_fts
            WHERE lore_fts MATCH ?
        """
        params: List[Any] = [fts_query]
        if doc_type:
            sql += " AND doc_type = ?"
            params.append(doc_type)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            rows = []

    results = [
        {
            "doc_type": row["doc_type"],
            "doc_id": row["doc_id"],
            "title": row["title"],
            "excerpt": row["excerpt"],
            "rank": row["rank"],
        }
        for row in rows
    ]
    return {
        "query": query,
        "count": len(results),
        "results": results,
        "engine": "fts5",
        "version": LORE_INDEX_VERSION,
    }