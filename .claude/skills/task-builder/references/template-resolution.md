# Template Resolution

Schema definitions, path mapping format, and banned patterns for platform builds.

## Platform Schema

Every platform in the isagawa-qa org follows this structure:

### Required Directories

```
framework/interfaces/              ← Layer 1: domain wrapper
framework/_reference/<objects>/    ← Read-only example Layer 2 objects
framework/_reference/tasks/        ← Read-only example Layer 3
framework/_reference/roles/        ← Read-only example Layer 4
framework/_reference/tests/        ← Read-only example Layer 5
framework/<objects>/               ← Live Layer 2 code
framework/tasks/                   ← Live Layer 3
framework/roles/                   ← Live Layer 4
framework/resources/config/        ← Environment configuration
framework/resources/utilities/     ← Shared utilities (autologger)
tests/                             ← Top-level live Layer 5
tests/data/                        ← Test fixtures and data
```

### Required Files

```
framework/interfaces/<domain>_interface.py   ← Layer 1 wrapper
framework/resources/utilities/autologger.py  ← @autologger decorator
framework/resources/config/environment_config.json
tests/conftest.py                            ← pytest configuration
FRAMEWORK.md                                 ← Detailed 5-layer architecture doc (>50 lines)
CONTRIBUTING.md                              ← Architecture rules + PR gates
README.md                                    ← Full setup guide
requirements.txt | package.json              ← Dependencies
```

### Banned Patterns

These paths are NEVER correct in a platform build:

| Pattern | Why |
|---------|-----|
| `framework/_reference/*_interface.py` | Interface must be in `framework/interfaces/` |
| `framework/_reference/tests/` as the only test dir | Tests must also exist at top-level `tests/` |
| `framework/_reference/fixtures/` | Fixtures go in `tests/data/` |
| Config as `.py` file in `resources/` | Use `environment_config.json` in `framework/resources/config/` |

## Template File Map Format

`_context/template-file-map.json`:

```json
{
  "template_repo": "isagawa-qa/platform-docker",
  "template_commit": "abc1234",
  "files": [
    "framework/interfaces/image_interface.py",
    "framework/_reference/image_objects/base_image.py",
    "framework/image_objects/",
    "framework/resources/config/environment_config.json",
    "framework/resources/utilities/autologger.py",
    "tests/conftest.py",
    "tests/data/test_images.json",
    "FRAMEWORK.md",
    "CONTRIBUTING.md",
    "README.md",
    "requirements.txt"
  ]
}
```

## Path Mapping Format

`_context/path-mapping.json`:

```json
{
  "mappings": [
    {
      "template": "framework/interfaces/image_interface.py",
      "target": "framework/interfaces/ssh_interface.py",
      "layer": 1
    },
    {
      "template": "framework/_reference/image_objects/",
      "target": "framework/_reference/validators/",
      "layer": 2
    },
    {
      "template": "framework/image_objects/",
      "target": "framework/validators/",
      "layer": 2
    },
    {
      "template": "tests/",
      "target": "tests/",
      "layer": 5
    },
    {
      "template": "FRAMEWORK.md",
      "target": "FRAMEWORK.md",
      "layer": null
    }
  ],
  "domain_objects_name": "validators",
  "domain_name": "ssh"
}
```

## How Downstream Steps Use This

| Step | Consumption |
|------|-------------|
| Step 4 (Decompose) | Phase structure matches template's layer organization |
| Step 5 (Atomize) | Every BUILD task path validated against path-mapping.json |
| Step 6 (Write Tasks) | `_context/` directory included in task folder |
| Step 8 (Structural Audit) | Output diffed against template-file-map.json |
