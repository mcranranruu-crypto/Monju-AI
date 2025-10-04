# src/monju_ai/cli.py
import click
from .storage import (
    add_entry,
    list_entries,
    search_entries,
    vote,
)

@click.group(help="Monju-AI: 共同知恵ストレージ用CLI")
def monju():
    pass

@monju.command("add")
@click.argument("topic")
@click.argument("text")
@click.option("--tags", multiple=True, help="タグを複数指定可（--tags ai --tags note）")
def cmd_add(topic, text, tags):
    e = add_entry(topic, text, tags=list(tags) if tags else None)
    click.echo(f"追加: #{e['id']} [{e['topic']}] {e['text']}")

@monju.command("list")
@click.option("--topic", default=None, help="トピックで絞り込み")
def cmd_list(topic):
    for e in list_entries(topic):
        click.echo(f"#{e['id']} [{e['topic']}] {e['text']} (votes={e['votes']})")

@monju.command("search")
@click.argument("query")
def cmd_search(query):
    for e in search_entries(query):
        click.echo(f"#{e['id']} [{e['topic']}] {e['text']} (votes={e['votes']})")

@monju.command("vote")
@click.argument("entry_id", type=int)
@click.option("--down", is_flag=True, help="ダウンボート（未指定ならアップボート）")
def cmd_vote(entry_id, down):
    e = vote(entry_id, -1 if down else 1)
    if e:
        click.echo(f"更新: #{e['id']} votes={e['votes']}")
    else:
        click.echo("指定IDが見つかりません", err=True)

if __name__ == "__main__":
    monju()
