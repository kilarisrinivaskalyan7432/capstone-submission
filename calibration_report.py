from dataclasses import dataclass

@dataclass
class Label:
    policy_type: str
    field: str
    confidence: float
    correct: bool

labels = [
    Label("auto", "premium_amount", 0.95, True),
    Label("auto", "premium_amount", 0.95, True),
    Label("auto", "premium_amount", 0.95, True),
    Label("umbrella", "exclusions", 0.93, False),
    Label("umbrella", "exclusions", 0.93, False),
    Label("home", "deductible", 0.90, True),
]

cells = {}
for x in labels:
    cells.setdefault((x.policy_type, x.field), []).append(x)

total = 0.0
for (ptype, field), group in sorted(cells.items()):
    conf = sum(x.confidence for x in group) / len(group)
    acc = sum(x.correct for x in group) / len(group)
    brier = sum((x.confidence - int(x.correct)) ** 2 for x in group) / len(group)
    total += brier * len(group)
    print(f"{ptype:9} {field:15} n={len(group)} conf={conf:.2f} acc={acc:.2f} brier={brier:.3f}")

print(f"OVERALL brier={total / len(labels):.3f}")
