# Verification Methods

3-tier verification system for gate contracts. Each gate has exactly one method.

## Tier 1: Structural (fastest, most reliable)

| Method | Action | Example |
|--------|--------|---------|
| `file_exists` | `test -f {{path}}` | `test -f .claude/hooks/my-hook.py` |
| `grep` | `grep -q '{{pattern}}' {{file}}` | `grep -q 'def main' src/app.py` |
| `json_valid` | `python -c "import json; json.load(open('{{path}}'))"` | Validate config.json parseable |

Use for: file presence, content patterns, config validity.

## Tier 2: Functional (slower, tests behavior)

| Method | Action | Example |
|--------|--------|---------|
| `run_code` | Execute command, exit 0 = PASS | `python -c "from src.config import Settings"` |
| `run_test` | Run test suite, exit 0 = PASS | `pytest tests/ -v` or `npm test` |
| `mock_data` | Fixture → process → compare output | See fixture format below |

Use for: imports, execution, data processing, integration.

### Mock Data Fixture Format

**Input fixture** (`_test/fixtures/{{GATE-ID}}-input.json`):
```json
{
  "gate_id": "DATA-01",
  "description": "Pipeline processes valid input",
  "mock_input": { ... },
  "pipeline_step": "step name or number",
  "instructions": "Process this input through [step]"
}
```

**Expected output** (`_test/expected/{{GATE-ID}}-expected.json`):
```json
{
  "gate_id": "DATA-01",
  "expected_output": { ... },
  "match_type": "contains_keys",
  "required_keys": ["status", "result"],
  "required_values": { "status": "success" }
}
```

### Match Types:

| Type | Logic |
|------|-------|
| `exact_match` | result == expected (deep equality) |
| `contains_keys` | result has all required_keys + required_values match |
| `pattern_match` | regex match on required_values |
| `shape_match` | same keys and value types (not values) |

### Test Data Principles:
- **Real data over mocks** — use production-representative data whenever possible. Don't mock unless the real thing is unavailable (external API, paid service, credentials required).
- **Create test data that matches prod** — same structure, same edge cases, same volume patterns. If prod processes 100-field forms, test with 100-field forms, not 3-field toy examples.
- **Mock only when necessary** — external APIs behind auth, paid services, destructive operations. Document WHY each mock exists.
- **Fixture data from domain research** — use data found during step 2 (research), not invented data. Real job postings, real config formats, real API responses.

### Fixture Rules:
- One fixture pair per `mock_data` gate (never share)
- Use realistic domain data, not lorem ipsum or toy examples
- Edge cases get dedicated fixtures — sourced from actual pain points identified in research
- Fixtures ship with the project for re-validation
- If creating synthetic data, model it on real examples (same field count, same value ranges, same edge cases)

## Tier 3: Semantic (slowest, LLM judgment)

| Method | Action | Example |
|--------|--------|---------|
| `manual` | LLM reads artifact, judges against pass criteria | "README explains install flow clearly" |

Use for: documentation quality, content clarity, design decisions. Last resort only.

## Retry Decision Tree

When a gate fails, categorize the failure to determine retry scope:

```
Gate failed?
  │
  ├─ Fixture problem (bad input/expected data)?
  │  └─ Fix fixture → re-run gate verification only
  │
  ├─ Task problem (implementation wrong)?
  │  └─ Fix implementation → re-run from that task
  │
  ├─ Spec/design problem (gate references wrong thing)?
  │  └─ Fix gate contract → regenerate tasks → re-run cycling
  │
  └─ Environment problem (missing deps, wrong config)?
     └─ Fix environment → re-run full cycle

Max 3 retries per failure type. After 3: skip gate, document in report.
```
