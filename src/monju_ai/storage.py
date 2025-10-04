from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re
import argparse

# リポジトリ直下の data/ に保存
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "knowledge.json"


def _ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_entries() -> List[Dict]:
    _ensure_data_file()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # 壊れていたらバックアップして初期化
        DATA_FILE.rename(DATA_FILE.with_suffix(".bak"))
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []


def save_entries(entries: List[Dict]) -> None:
    DATA_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def now_iso() -> str:
    return datetime.now().isoformat()


def add_entry(topic: str, text: str, tags: List[str] | None = None) -> Dict:
    entries = load_entries()
    entry = {
        "id": len(entries) + 1,
        "topic": topic.strip(),
        "text": text.strip(),
        "tags": [t.strip() for t in (tags or [])],
        "votes": 0,
        "created_at": now_iso(),
    }
    entries.append(entry)
    save_entries(entries)
    return entry


def list_entries(topic: str | None = None) -> List[Dict]:
    entries = load_entries()
    if topic:
        entries = [e for e in entries if e["topic"] == topic]
    return sorted(entries, key=lambda e: (-int(e["votes"]), e["created_at"]))


def search_entries(query: str) -> List[Dict]:
    q = query.strip()
    if not q:
        return list_entries()
    rx = re.compile(re.escape(q), re.IGNORECASE)
    return [e for e in load_entries() if rx.search(e["text"]) or rx.search(e["topic"])]


def vote(entry_id: int, delta: int = 1) -> Dict | None:
    entries = load_entries()
    for e in entries:
        if e["id"] == entry_id:
            e["votes"] += delta
            save_entries(entries)
            return e
    return None


# CLI エントリーポイント
def main() -> None:
    p = argparse.ArgumentParser(prog="monju", description="Monju AI Knowledge CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="知見を追加")
    p_add.add_argument("topic")
    p_add.add_argument("text")
    p_add.add_argument("--tags", nargs="*", default=[])

    # list
    p_ls = sub.add_parser("list", help="一覧表示")
    p_ls.add_argument("--topic")

    # search
    p_s = sub.add_parser("search", help="全文検索")
    p_s.add_argument("query")

    # vote
    p_v = sub.add_parser("vote", help="投票 (+1/-1)")
    p_v.add_argument("id", type=int)
    p_v.add_argument("--down", action="store_true")

    args = p.parse_args()

    if args.cmd == "add":
        e = add_entry(args.topic, args.text, args.tags)
        print(f"追加: #{e['id']} [{e['topic']}] {e['text']}")
    elif args.cmd == "list":
        for e in list_entries(args.topic):
            print(f"#{e['id']} [{e['topic']}] {e['text']} (votes={e['votes']})")
    elif args.cmd == "search":
        for e in search_entries(args.query):
            print(f"#{e['id']} [{e['topic']}] {e['text']} (votes={e['votes']})")
    elif args.cmd == "vote":
        e = vote(args.id, -1 if args.down else 1)
        if e:
            print(f"更新: #{e['id']} votes={e['votes']}")
        else:
            print("指定IDが見つかりません")


if __name__ == "__main__":
    main()
