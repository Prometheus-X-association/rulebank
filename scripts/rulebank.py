"""Checks the rule bank and keeps the status table of the README up to date.

    python scripts/rulebank.py validate        # schema and cross-checks, exit 1 on error
    python scripts/rulebank.py status          # print the status table
    python scripts/rulebank.py status --write  # write it into README.md
"""

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
SCHEMA = ROOT / "schema" / "rule-record.schema.json"
README = ROOT / "README.md"

PREFIXES = {
    "ptx:": "https://w3id.org/ptx/",
    "dssc:": "https://w3id.org/dssc/rulebook/",
}
STATUS_START = "<!-- status:start -->"
STATUS_END = "<!-- status:end -->"


def load_rules():
    return [(path, json.loads(path.read_text(encoding="utf-8"))) for path in sorted(RULES.rglob("*.json"))]


def local_name(rule_id):
    return rule_id.split("/")[-1].split(":")[-1]


def expand(rule_id):
    for prefix, iri in PREFIXES.items():
        if rule_id.startswith(prefix):
            return iri + rule_id[len(prefix):]
    return rule_id


def check_artifact(rule_id, artifact, errors, where):
    path = ROOT / artifact
    if not path.is_file():
        errors.append(f"{where}: artifact {artifact} not found")
        return
    if path.suffix == ".ttl":
        try:
            Graph().parse(path, format="turtle")
        except Exception as e:
            errors.append(f"{where}: {artifact} is not valid Turtle: {e}")
            return
        if f"<{expand(rule_id)}>" not in path.read_text(encoding="utf-8"):
            errors.append(f"{where}: {artifact} does not point back to {rule_id}")
    elif path.suffix == ".json":
        source = json.loads(path.read_text(encoding="utf-8")).get("dsif:sourceRule")
        if source != rule_id:
            errors.append(f"{where}: {artifact} has dsif:sourceRule {source!r}, expected {rule_id!r}")


def validate():
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    rules = load_rules()
    ids = {}
    errors = []

    for path, rec in rules:
        where = path.relative_to(ROOT).as_posix()
        for err in sorted(validator.iter_errors(rec), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{where}: {loc}: {err.message}")
        rule_id = rec.get("@id", "")
        if rule_id in ids:
            errors.append(f"{where}: duplicate @id {rule_id}, also in {ids[rule_id]}")
        ids[rule_id] = where
        if path.stem != local_name(rule_id):
            errors.append(f"{where}: file name should be {local_name(rule_id)}.json")
        if path.parent.name != f"L{rec.get('level')}":
            errors.append(f"{where}: level {rec.get('level')} but stored in {path.parent.name}/")
        for expr in rec.get("expressions", []):
            if "artifact" in expr:
                check_artifact(rule_id, expr["artifact"], errors, where)

    for path, rec in rules:
        parent = rec.get("parent")
        if parent and parent.get("rule") not in ids:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: parent {parent.get('rule')} not in the bank")

    if README.is_file() and status_table(rules) not in README.read_text(encoding="utf-8"):
        errors.append("README.md: status table is out of date, run `python scripts/rulebank.py status --write`")

    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(rules)} rules checked, {len(errors)} errors")
    return 1 if errors else 0


def expression_status(rec):
    exprs = rec["expressions"]
    types = [e["type"] for e in exprs]
    if all(t == "none" for t in types):
        return "checked by people"
    if all(t == "not-yet-specified" for t in types):
        return "remains to do"
    if "not-yet-specified" in types or any(e.get("coverage") == "partial" for e in exprs):
        return "partial"
    return "expressed"


def status_table(rules):
    lines = [
        "| Rule | Title | Decision | Class | Expression | Expression status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for path, rec in sorted(rules, key=lambda r: (r[1]["level"], r[1]["@id"])):
        link = f"[`{rec['@id']}`]({path.relative_to(ROOT).as_posix()})"
        types = ", ".join(sorted({e["type"] for e in rec["expressions"]}))
        lines.append(
            f"| {link} | {rec['title']} | {rec['decisionStatus']} | {rec['enforcementClass']} | {types} | {expression_status(rec)} |"
        )
    return "\n".join(lines)


def status(write):
    table = status_table(load_rules())
    if not write:
        print(table)
        return 0
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(STATUS_START) + ".*?" + re.escape(STATUS_END), re.S)
    if not pattern.search(text):
        print(f"README.md has no {STATUS_START} marker")
        return 1
    README.write_text(pattern.sub(lambda _: f"{STATUS_START}\n{table}\n{STATUS_END}", text), encoding="utf-8")
    print("README.md status table updated")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["validate"]:
        sys.exit(validate())
    if args[:1] == ["status"]:
        sys.exit(status("--write" in args))
    print(__doc__)
    sys.exit(2)
