# Contributing to Velora TPRM

Thank you for your interest in contributing to Velora TPRM. This guide will help you get started.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@velora.io.

---

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/archeon-dev/velora-tprm/issues)
2. If not, open a new issue using the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include reproduction steps, expected behavior, and actual behavior
4. Add relevant logs, screenshots, or error messages

### Suggesting Features

1. Check existing [Issues](https://github.com/archeon-dev/velora-tprm/issues) and [Discussions](https://github.com/archeon-dev/velora-tprm/discussions) for similar ideas
2. Open a new issue using the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Describe the use case, not just the solution

### Submitting Code

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. **Make your changes** following the coding standards below
5. **Write/update tests** for your changes
6. **Run the full test suite** locally
7. **Commit** with a clear, descriptive message
8. **Push** to your fork
9. **Open a Pull Request** against `main`

---

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 20+
- Docker & Docker Compose >= 2.20
- OPA CLI (for policy work)

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/velora-tprm.git
cd velora-tprm

# Copy environment variables
cp .env.example .env

# Start infrastructure
docker compose up postgres redis minio typesense temporal -d

# Backend: install shared library + a service
cd packages/velora-common && pip install -e . && cd ../..
cd services/auth && pip install -e ".[dev]" && cd ../..

# Frontend: install and run
cd frontend/web && npm install && npm run dev
```

### Running Tests

```bash
# Backend tests (from a service directory)
cd services/auth
pytest tests/ -v --cov=src --cov-report=term-missing

# Frontend tests
cd frontend/web
npm run test

# OPA policy tests
cd policies
opa test . -v

# Full integration tests
cd tests
pytest -v
```

---

## Coding Standards

### General

- Write clear, self-documenting code. Comments explain "why", not "what".
- Every public function/method must have a docstring.
- No hardcoded secrets, URLs, or environment-specific values.
- All user inputs must be validated. Never trust external input.

### Python (Backend Services)

- **Formatter**: `ruff format` (line length: 100)
- **Linter**: `ruff check` + `mypy --strict`
- **Style**: PEP 8 with type annotations on all functions
- **Testing**: pytest with minimum 80% coverage per service
- **Imports**: sorted by ruff (isort-compatible)
- **Error handling**: typed exceptions, no bare `except:`
- **Async**: use `async/await` consistently (FastAPI async endpoints)

```bash
# Check before committing
ruff check .
ruff format --check .
mypy src/ --strict
pytest tests/ -v --cov=src
```

### TypeScript (Frontend)

- **Linter**: ESLint with Next.js recommended config
- **Formatter**: Prettier (via ESLint plugin)
- **Style**: strict TypeScript (no `any` unless explicitly justified)
- **Components**: functional components with named exports
- **State**: React hooks, no class components
- **Styling**: Tailwind CSS utility classes, shadcn/ui components

```bash
# Check before committing
npm run lint
npx tsc --noEmit
npm run build
```

### OPA Policies (Rego)

- Every policy file must have corresponding test files in `policies/tests/`
- Use `deny` rules (default-deny pattern)
- Test both allow and deny paths

### SQL / Migrations

- Use Alembic for schema changes
- Every migration must be reversible (include downgrade)
- Use explicit column types, never rely on defaults
- All tables must have `tenant_id` for RLS isolation

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

**Scopes**: `auth`, `vendor`, `assessment`, `framework`, `scoring`, `evidence`, `monitoring`, `finding`, `communication`, `reporting`, `admin`, `ai`, `bff`, `workflow`, `frontend`, `common`, `infra`, `policies`

**Examples**:
```
feat(assessment): add AI-powered questionnaire auto-fill
fix(scoring): correct weighted average calculation for composite scores
docs(readme): update quick start instructions
test(vendor): add integration tests for bulk import endpoint
```

---

## Pull Request Guidelines

- Fill out the [PR template](.github/PULL_REQUEST_TEMPLATE.md) completely
- Keep PRs focused -- one feature or fix per PR
- Ensure CI passes (lint, type-check, tests, build)
- Update documentation if your change affects user-facing behavior
- Add tests for new functionality (target 80%+ coverage)
- Request review from at least one maintainer
- Squash commits before merging if the history is noisy

### PR Size Guidelines

| Size | Lines Changed | Review Time |
|------|--------------|-------------|
| Small | < 200 | Same day |
| Medium | 200-500 | 1-2 days |
| Large | 500+ | Split if possible |

---

## Project Structure

See [README.md](README.md#project-structure) for the full directory layout.

**Where to make changes:**

| Change Type | Location |
|-------------|----------|
| Backend service logic | `services/<service>/src/` |
| Shared backend utilities | `packages/velora-common/src/` |
| Frontend pages | `frontend/web/src/app/` |
| Frontend components | `frontend/web/src/components/` |
| Authorization policies | `policies/services/` |
| Database migrations | `services/<service>/alembic/` |
| Docker configuration | `infra/docker/` |
| CI/CD | `.github/workflows/` |

---

## License

By contributing to Velora TPRM, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
