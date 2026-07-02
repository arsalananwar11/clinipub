# Contributing to clinipub

Thank you for contributing to `clinipub`.
This repository is designed for clinical data scientists and authors who need reproducible, publication-ready tabulation and audit reporting.

## How to contribute

1. Fork the repository and create a feature branch from `main`.
   - Branch name format: `feature/<short-description>` or `fix/<issue-number>-<short-description>`.

2. Keep changes small and focused.
   - One issue per branch.
   - Prefer incremental commits with descriptive messages.

3. Run tests locally before submitting a pull request.
   - Use the project development workflow with `uv`.
   - Recommended command:
     ```bash
     uv run pytest
     ```

4. Follow the project style.
   - Keep code readable and consistent with PEP 8.
   - Use clear variable names and concise docstrings.

## Reporting issues

- Open a GitHub issue for bugs, enhancement requests, or documentation improvements.
- Provide a minimal reproduction example and expected behavior.
- Include the Python version and package versions when relevant.

## Pull request guidelines

- Target the `main` branch.
- Provide a short summary of the change and the motivation.
- Mention related issues when applicable.
- Ensure all tests pass and no new warnings are introduced.

## Development notes

- `clinipub` is a pandas-centric package. New features should preserve compatibility with typical clinical analysis workflows.
- Use the existing `src/clinipub` package layout and keep public API changes minimal unless necessary.
- Update `README.md` or add examples if the change affects usage.

## License

By contributing, you agree that your contributions will be licensed under the repository's existing license.
