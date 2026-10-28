# replica-architect Skill Reference Copy
Source: C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-architect\SKILL.md

Core Methodology:
Plans the stack, database schema and API for an app clone, from the recon map. Picks boring, managed tech, turns the inferred data model into real SQL with indexes and access rules, lists every route/module by flow, and orders the build as a thin vertical slice first.
- Step 1: The stack (layer, selection, rationale).
- Step 2: The schema (IDs, relations, foreign keys with ON DELETE, indexes, check constraints, UTC timestamps).
- Step 3: The API / service interfaces.
- Step 4: The parts that bite (edge cases, file sizes, format quirks, race conditions, offline handling).
- Step 5: Build order (vertical slice -> must-haves -> should-haves -> could-haves).
