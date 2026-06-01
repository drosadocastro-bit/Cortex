# Synthetic Demo Workspace

The demo workspace is a tiny deterministic investigation made only from
synthetic inputs. It exists so maintainers and future UI work can see Cortex's
canonical path without using real UAP data.

## What It Builds

`DemoWorkspaceBuilder` creates:

- raw synthetic inputs
- evidence records
- provenance records
- source lineage records
- contamination flags
- candidate claims
- normalized claims
- claim evidence assessments
- claim review docket
- source review docket
- review session
- audit trail
- review bundle
- formatted Markdown bundle

## Synthetic Scenario

The fixture includes:

- `synthetic://demo-primary`: a primary-style note saying an observer saw a
  bright light moving west.
- `synthetic://demo-contradiction`: a note saying no bright light was seen
  moving west.
- `synthetic://demo-derivative`: a derivative repost tied to the primary
  source.
- `synthetic://demo-contaminated`: a speculative note with fictional
  contamination terms.
- `unknown:demo-incomplete`: an anonymous incomplete source with missing source
  URI, title, and date metadata.

## Boundaries

The demo is not evidence of anything outside the test fixture. It is not a
real-world validation of UAP claims, source reliability, or framework accuracy.

It is useful because it shows whether Cortex preserves:

- provenance
- lineage
- contradiction
- uncertainty
- contamination warnings
- unsupported claim state
- source review boundaries
- session audit history
- review-bundle limitations

## How To Run

Use the test suite:

```powershell
python -m pytest tests/test_phase23_demo_workspace.py
```

Or instantiate the builder in Python:

```python
from roswell_uap_cortex import DemoWorkspaceBuilder

result = DemoWorkspaceBuilder().build()
print(result.formatted_bundle)
```
