# Contributing

## Scope

This repository contains the Home Assistant-facing integration, contracts, validation scripts, and BDD coverage for smart home presence intelligence.

## Before You Start

- Open an issue for bugs, proposed features, or significant behavior changes before writing code.
- Keep changes small and vertically sliced.
- Update user-facing docs when behavior or operator workflows change.
- Do not commit secrets, credentials, private keys, or personal data.

## Local Setup

```bash
make install
make check
make quality-gates
```

## Required Quality Gates

Every behavior-changing change must:

- include or update executable `.feature` coverage
- pass `make check`
- pass `make quality-gates`
- keep `VERSION`, `CHANGELOG.md`, and the Home Assistant manifest aligned when release metadata changes

## Pull Requests

Pull requests should:

- use conventional commits
- describe behavior changes and operator impact clearly
- include validation evidence
- call out contract, schema, or release-surface changes explicitly

## Commit Style

Use focused conventional commits such as:

- `feat(hacs): add room policy sensors`
- `fix(validation): accept published HACS release tags`
- `docs(readme): rewrite for public integration usage`

## Review Expectations

- Expect review on behavior, validation coverage, contract drift, and Home Assistant operator experience.
- Avoid unrelated refactors in feature PRs.
- Preserve existing public contracts unless a breaking change is deliberate and documented.
