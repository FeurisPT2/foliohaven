# Context: Worker Remediation 1
Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_remediation_1
Project root: c:\Users\epicg\Downloads\icecream_ebook_reader_replica

Objective:
Remediate the Victory Audit finding:
1. In `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py`:
   Add `".taste-skill"` to `SKIP_DIRS`.
2. Clean up or delete the temporary `.taste-skill/` directory from `c:\Users\epicg\Downloads\icecream_ebook_reader_replica`.
3. Run all linters and tests to verify:
   - `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py replica/launch/listing.json` -> 0 errors, 0 warnings (exit 0)
   - `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json` -> Clean (exit 0, 0 hits)
   - `python tests/test_launch_artifacts.py` -> 5/5 pass (exit 0)
   - `python tests/test_challenger_adversarial_landing.py` -> pass (exit 0)
