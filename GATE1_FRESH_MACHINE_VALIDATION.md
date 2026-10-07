# Gate 1 Fresh User-Machine Validation

This procedure is the remaining environment-level acceptance check from Issue #8. It is intentionally separate from CI because a hosted runner does not prove operation on a fresh end-user machine.

Use a clean machine or a clean OS-level user environment that has Python 3.11 or newer and no editable checkout of The-Doctor-Lives installed.

From a clean release checkout at the exact candidate SHA, create and activate a virtual environment, then install the project non-editably from a wheel. Run the validation script with a new empty state directory and preserve its JSON output together with the Python version, OS/platform version, installed dependency versions, and exact Git SHA.

Example shell sequence on macOS/Linux:

```sh
python -m venv .gate1-venv
. .gate1-venv/bin/activate
python -m pip install --upgrade pip
python -m pip wheel . --no-deps --wheel-dir dist
python -m pip install dist/*.whl
python tools/gate1_fresh_install_validate.py \
  --source-root "$(pwd)" \
  --state "$HOME/pretorius-gate1-state" \
  --output gate1-validation.json
python --version > gate1-environment.txt
python -m pip freeze >> gate1-environment.txt
git rev-parse HEAD >> gate1-environment.txt
```

On Windows PowerShell, use the equivalent virtual-environment activation and pass the repository path explicitly to --source-root.

Acceptance requires status: pass, zero recorded network events during runtime validation, package_path outside the source checkout, restart digest/tick preservation, preserved Deep-History and canonical-evidence versions, preserved lived-memory classification and wording provenance, recovered relationship and commitment state, renderer read-only behavior, and identical repeated historical retrieval.

Do not close Issue #8 until the resulting files are attached to that issue or otherwise preserved with the exact candidate SHA. CI artifacts from gate1-fresh-install-validation are supporting evidence, not a substitute for this physical or equivalent end-user environment check.
