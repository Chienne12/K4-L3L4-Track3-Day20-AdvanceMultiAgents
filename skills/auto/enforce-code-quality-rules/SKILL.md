---
name: enforce-code-quality-rules
description: Use this skill to ensure code changes comply with project-specific quality rules before submission.
---
- Always preserve original test files; add new test files for new tests or regressions instead of modifying existing ones.
- Verify that every public function (not starting with '_') has complete type annotations on all parameters and the return value.
- Add a regression test file with at least one test function per fixed bug; ensure this file passes all tests.
- Update the changelog under the "## Unreleased" section with a bullet for each fix, specifying the function name and a short description.
- Run all tests after changes to confirm no regressions or rule violations remain.
- Review code for correct handling of edge cases as described in docstrings or specifications.
- Use consistent formatting and naming conventions as per project guidelines.