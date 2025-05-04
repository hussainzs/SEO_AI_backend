## Contributing Guidelines

- Start all work from creating a GitHub Issue describing the change.
   - Assign the Issue to yourself and add a label (e.g., `bug`, `enhancement`, `feature`, etc.).

- Create your own branch. Branch _from_ `main` using clear prefixes: `feature/`, `fix/`, or `chore/`.
    - Example: `feature/add-keyword-suggestion` or `fix/typo-in-readme` or `chore/update-dependencies`.
    - Remember branch FROM main. 
- In your branch, make small, self-contained commits with clear messages.
    - Example: `Add keyword suggestion function` or `Fix typo in README` or `Update dependencies`.
    - Avoid large commits with multiple unrelated changes.
- Once you have tested everything works in your branch, open a Pull Request (PR) against `main`.

    - Link the PR to the Issue by mentioning it in the PR description (e.g., `Fixes #123`).
    - Add relevant labels to the PR (e.g., `bug`, `enhancement`, `feature`, etc.).
    - Assign at least one reviewer to the PR.

- Request review, address feedback, and update your branch as needed.

- Once PR is approved, pull the latest `main` before merging your branch INTO `main`.
- Close the Issue when done.