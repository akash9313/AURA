# Contributing to AURA AI Operating System

Thank you for your interest in contributing to **AURA AI Operating System**!

## Code of Conduct
We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors.

## Pull Request Process

1. **Fork & Branch**: Create a feature branch off `develop` (`git checkout -b feature/amazing-feature`).
2. **Coding Standards**:
   - PEP 8 compliance via `black` and `ruff`.
   - Explicit type hints on 100% of function signatures.
   - Maintain loose coupling via `EventBus`.
3. **Testing Requirements**:
   - Add unit test coverage in `backend/tests/` matching your new module.
   - Verify `python -m unittest discover -s backend/tests -t backend` passes with 100% success.
   - Verify `cd frontend && npx tsc` passes with zero errors.
4. **Pull Request Review**: Submit your PR matching `.github/PULL_REQUEST_TEMPLATE.md`.
