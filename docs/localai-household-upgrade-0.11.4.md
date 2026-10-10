# Household build based on Open WebUI 0.11.4

This fork merges the official `v0.11.4` tag at
`8bd8b4fac5e059578ac0c74b3c18d11139f88b7d` into the household 0.11.3 source
at `6b8080e49`. Release source:
<https://github.com/open-webui/open-webui/releases/tag/v0.11.4>.
The separately released 0.12.0 is outside this qualified update.

The household features remain: four-role model controls and technical tooltips,
private reviewed reference capsules, explicit URL provenance, incomplete-response
notices, per-request tool handling, local coarse location, file/code artifacts,
compact valves, and full-page OCR fallback. Seven upstream conflict files were
reviewed. The important integrations are:

- User settings use upstream's granular interface/system/parameter permissions;
  household restrictions on webhooks and direct tool servers remain.
- Incomplete completion status survives upstream continuation handling.
- Model tooltips and compact valves accept upstream localized descriptions/schema.
- A null Docling Markdown result still permits the household full-page OCR fallback;
  upstream conversion failures still fail instead of being hidden by OCR.
- The approved-preset exception to raw-provider access is explicit in source with
  `LOCALAI_COMPAT_RAW_BASE_PRESET`. Direct raw model access, ungranted presets,
  and registered base models without a read grant remain denied.
- `reverse-geocode==1.6.6` is now an explicit package dependency, preserving the
  existing local location resolver when installing a fresh runtime.

No upstream migration was added between 0.11.3 and 0.11.4. The household merge
head remains `b7e4c91a2f68`. A copied database passed `alembic upgrade head` and
integrity checking, with all 45 table row counts and content digests unchanged.
Application startup subsequently seeds seven additional upstream configuration
defaults; that is separate from the no-op schema migration.

## Build and qualification

Build with Python 3.12 and Node 22.14.0. Install the pinned backend requirements
with CPU PyTorch; this UI runtime has no GPU assignment. Install dependencies
using `npm ci`, then build with an explicit heap allowance:

```sh
NODE_OPTIONS=--max-old-space-size=12288 npm run build
```

The default Node heap exhausted during bundling; the explicit allowance completed.
For a wheel containing the already built frontend, install `build`/`hatchling`
and run `HATCH_BUILD_NO_HOOKS=true python -m build --wheel --no-isolation`.
Without that flag, the upstream hook runs another npm install/build. The
Pyodide preparer downloads and bundles browser packages: retain the exact built
wheel, generated lockfile, and its digest for deployment reproducibility.

Qualification on October 10, 2026 used an isolated network namespace with only
loopback, a copied database, a synthetic OpenAI-compatible provider, and Chromium
with desktop and mobile viewports. There were no model requests or production
service changes. The browser exercised streamed answers, progress completion,
output-limit notice, continuation, and Python execution using bundled Pyodide.
The copied API exercised all four household presets, admin and household login,
anonymous/admin/raw-model denials, protected settings, private reference denial,
and location resolution without persisted coordinates. Page and console error
lists were empty. This is browser/protocol proof, separate from model quality or
the later production gateway admission.

- Frontend Vitest: 7 tests pass.
- Backend household regressions: 20 tests pass, including null Docling content,
  combined OCR/layout content, and upstream conversion failure propagation.
- External deployment/watchdog/contract/progress/ACL test suite: 40 tests pass.
  Its ACL fixtures are exact function excerpts from official 0.11.3 and 0.11.4.
- `uv pip check` passes for the installed candidate environment.
- Full `svelte-check` is not clean: pristine upstream 0.11.4 reports 7,001 errors
  and 198 warnings; this merged tree reports 7,008 errors and 199 warnings.
  The two raw logs and per-file diagnostic comparison are retained. The build,
  focused unit tests, and rendered interactions above are the acceptance evidence;
  this update does not claim to repair upstream's broad static typing debt.

The final deployment manifest must be generated from the installed frontend and
all 15 required backend paths using the operator repository's
`openwebui-deployment-marker.py`. Startup verifies it before launching. The
operator owns the service switch, database rollback copy, production access
checks, and operational documentation. Keep the previous runtime and database
rollback point until those live checks pass.
