# Contributing to VantaCode Taxonomies

Thank you for your interest in contributing to VantaCode Taxonomies. This document explains how to propose changes, add new content, and submit contributions.

## Types of Contributions

### Adding New Values to an Existing Taxonomy

If an existing predicate needs a new value (e.g., a new critical infrastructure sector or a new malicious behavior technique):

1. Open an issue using the [New Value](https://github.com/vantacode/vantacode-taxonomies/issues/new?template=new-value.md) template.
2. Fork the repository and edit the appropriate `machinetag.json` file.
3. Add the new value entry under the correct predicate in the `values` array.
4. Every new entry **must** include a UUID v4 in the `uuid` field.
5. Run validation before submitting:

```bash
python tools/validate.py
```

6. Submit a pull request using the PR template.

### Adding a New Predicate to an Existing Taxonomy

If an existing taxonomy needs a new predicate (e.g., a new ATT&CK tactic mapping or a new governance category):

1. Open an issue using the [New Predicate](https://github.com/vantacode/vantacode-taxonomies/issues/new?template=new-predicate.md) template.
2. Add the predicate to the `predicates` array in the taxonomy's `machinetag.json`.
3. Add a corresponding entry in the `values` array with at least one value.
4. Include UUIDs for all new entries.
5. Run validation and submit a pull request.

### Proposing a New Taxonomy

New taxonomies require discussion before implementation:

1. Open an issue using the [New Taxonomy](https://github.com/vantacode/vantacode-taxonomies/issues/new?template=new-taxonomy.md) template.
2. Include the proposed namespace, predicates, values, and rationale.
3. Wait for maintainer review and approval before starting work.
4. Once approved, create the taxonomy directory and `machinetag.json` following the [taxonomy schema](schema/taxonomy.schema.json).
5. Add the taxonomy to `MANIFEST.json`.
6. Run validation and submit a pull request.

### Contributing Galaxy Clusters

Galaxy clusters are the rich knowledge objects that provide detailed context for taxonomy tags:

1. Galaxy definitions go in `galaxies/<name>.json` following the [galaxy schema](schema/galaxy.schema.json).
2. Cluster data goes in `clusters/<name>.json` following the [cluster schema](schema/cluster.schema.json).
3. Every cluster value **must** include a UUID v4.
4. Include meaningful `meta` fields: refs, kill_chain mappings, related-taxonomies.
5. Run validation and submit a pull request.

## Validation Requirements

All contributions **must** pass validation before merge:

```bash
# Validate all taxonomy, galaxy, and cluster JSON
python tools/validate.py

# Verify machinetag generation
python tools/machinetag.py --all
```

The CI pipeline runs these checks automatically on every pull request.

## JSON Format Guidelines

- Use 2-space indentation in all JSON files.
- Keep keys in alphabetical order within objects.
- Machine-readable values use lowercase with hyphens: `eval-benchmark-detection`, not `Eval Benchmark Detection`.
- Human-readable `expanded` fields use title case: `Eval Benchmark Detection`.
- Descriptions should be concise and factual.
- UUIDs must be v4 format, generated fresh for each new entry. Do not reuse UUIDs.

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Make your changes following the guidelines above.
3. Run `python tools/validate.py` locally and confirm no errors.
4. Fill out the pull request template completely, including:
   - Description of what changed and why
   - Validation results
   - Any MISP compatibility considerations
5. A maintainer will review and may request changes.
6. Once approved, a maintainer will merge the PR.

## What Not to Submit

- Do not add entries with STRIKE or SecurityScorecard attribution.
- Do not submit taxonomy data with proprietary licensing restrictions. All taxonomy data must be compatible with CC0-1.0.
- Do not submit changes that break the MISP-compatible format.
- Do not submit entries without UUIDs.

## Code of Conduct

Contributors are expected to:

- Be respectful and constructive in all interactions.
- Provide evidence and rationale for proposed changes.
- Accept maintainer decisions on taxonomy scope and structure.
- Report security concerns directly to cory@darkcode.ai rather than opening public issues.

## Questions

If you have questions about contributing, open a discussion or contact the maintainer directly.

---

Maintained by DarkCode LLC / cory@darkcode.ai
