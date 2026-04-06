# VantaCode Taxonomies

**Machine-readable taxonomies for AI threat classification, repo governance, and critical infrastructure mapping. MISP-compatible.**

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Validate Taxonomies](https://github.com/vantacode/vantacode-taxonomies/actions/workflows/validate.yml/badge.svg)](https://github.com/vantacode/vantacode-taxonomies/actions/workflows/validate.yml)
[![MISP Compatible](https://img.shields.io/badge/MISP-compatible-blue.svg)](https://www.misp-project.org/)

---

## What Are VantaCode Taxonomies?

VantaCode Taxonomies are a set of machine-readable classification systems for labeling code repositories, AI/ML threats, critical infrastructure sectors, and governance posture. They follow the [MISP taxonomy format](https://www.misp-project.org/taxonomies.html) and use the triple tag format:

```
namespace:predicate="value"
```

The project provides two layers of classification:

- **Taxonomies** -- flat, enumerated labels defined in `machinetag.json` files. Each taxonomy lives in its own directory and defines a namespace with predicates and values. These are the tags you apply to events, repositories, or artifacts.

- **Galaxies** -- rich knowledge objects defined in paired galaxy/cluster JSON files. Galaxies provide detailed context: descriptions, metadata, kill chain mappings, cross-references, and relationships between entries.

---

## Original Research

> The **Malicious Behaviors Taxonomy (MBT)** is informed by original research conducted under DarkCode LLC, including:
>
> - **[The Observation Phenomena (OFA)](https://observationframing.org)** -- A vulnerability class affecting 163+ LLM models across 26 providers. Demonstrates that AI models change behavior when told they are being observed vs. unobserved, with a 1% framing shift producing up to 90% behavioral change. 20 OFA techniques identified.
>
> - **[VantaGrid](https://vantagrid.ai)** -- The unified AI security methodology framework connecting scanning, classification, and threat intelligence capabilities. Provides the structured approach for applying MBT taxonomy classifications, AIBOM generation, and repo governance scoring across AI/ML codebases.
>
> - **[DECLAWED](https://declawed.io)** -- A real-time tracker for exposed AI agent instances on the public internet. Tracks 145K+ exposed instances across 46.2K unique IPs in 82 countries, with 2.5M CVE detections identified, 70K APT-linked, and 5 confirmed malicious ClawHub skills with mapped C2 infrastructure.

**Author:** Cory Kennedy / DarkCode LLC

---

## Taxonomies

| Namespace | Description | Exclusive |
|-----------|-------------|-----------|
| `vantacode-domain` | Classification of code repositories by functional security domain | No |
| `vantacode-sector` | Mapping of repositories to CISA critical infrastructure sectors and emerging sectors | No |
| `vantacode-threat` | Mapping of repositories to MITRE ATT&CK tactics | No |
| `vantacode-mbt` | Malicious Behaviors Taxonomy for AI and ML system threats | No |
| `vantacode-status` | Repository lifecycle status classification | Yes |
| `vantacode-sensitivity` | Data sensitivity and classification markings for repositories | Yes |
| `vantacode-governance` | Governance baseline compliance scoring for repositories | No |

Each taxonomy directory contains a `machinetag.json` file conforming to the [MISP taxonomy schema](schema/taxonomy.schema.json).

---

## Tag Format

Tags follow the MISP triple tag format: `namespace:predicate="value"`

```
vantacode-domain:category="offensive-security"
vantacode-mbt:observation-dependent-behavior="eval-benchmark-detection"
vantacode-sector:critical-infrastructure="energy"
vantacode-threat:attack-tactic="initial-access"
vantacode-status:lifecycle="active"
vantacode-sensitivity:classification="internal"
vantacode-governance:security="full"
```

Predicates without values are also valid when the predicate itself is the classification:

```
vantacode-status:lifecycle
vantacode-sensitivity:classification
```

---

## Galaxies

Galaxies are the rich knowledge layer built on top of taxonomies. Each galaxy is a pair of files:

- **Galaxy definition** (`galaxies/<name>.json`) -- Declares the galaxy type, namespace, icon, and optional kill chain ordering.
- **Cluster** (`clusters/<name>.json`) -- Contains the actual entries with descriptions, metadata, cross-references, and relationships.

| Galaxy | Description |
|--------|-------------|
| `vantacode-mbt-techniques` | Specific techniques within the Malicious Behaviors Taxonomy, with detection methods, mitigations, and MITRE ATT&CK cross-references |
| `vantacode-ai-threat-actors` | Threat actors targeting or leveraging AI systems, including those observed targeting exposed AI agent infrastructure |
| `vantacode-ai-tools` | AI-specific security tools spanning offensive and defensive capabilities |
| `vantacode-research` | Research outputs including OFA, VantaGrid, and DECLAWED findings |

Galaxy clusters support kill chain mappings, enabling placement of techniques within the MBT attack lifecycle:

```
observation-dependent-behavior -> adversarial-input-vulnerabilities ->
insecure-ai-deployment -> ai-supply-chain-threats ->
data-exfiltration-via-ai -> ai-model-integrity
```

---

## Usage

### As MISP-compatible tags

Clone the repository into your MISP taxonomy directory:

```bash
cd /path/to/MISP/app/files/taxonomies/
git clone https://github.com/vantacode/vantacode-taxonomies.git
```

Each taxonomy's `machinetag.json` will be automatically discovered by MISP.

### In .vantacode.yaml files

Apply taxonomy tags to repositories using a `.vantacode.yaml` configuration file at the repo root:

```yaml
tags:
  - vantacode-domain:category="ai-security"
  - vantacode-sector:critical-infrastructure="information-technology"
  - vantacode-status:lifecycle="active"
  - vantacode-sensitivity:classification="public"
  - vantacode-governance:security="full"
```

### Via VantaCode MCP server

The VantaCode MCP server provides programmatic access to taxonomy lookups, tag validation, and classification operations.

### As STIX 2.1 labels

VantaCode taxonomy tags can be used directly as STIX 2.1 labels on any STIX Domain Object:

```json
{
  "type": "malware",
  "spec_version": "2.1",
  "labels": [
    "vantacode-mbt:observation-dependent-behavior=\"eval-benchmark-detection\"",
    "vantacode-threat:attack-tactic=\"defense-evasion\""
  ]
}
```

---

## Tools

| Tool | Description |
|------|-------------|
| `tools/validate.py` | Validates all taxonomy, galaxy, and cluster JSON files against their schemas |
| `tools/machinetag.py` | Generates and displays the full machinetag for each taxonomy |
| `tools/generate_docs.py` | Generates markdown documentation from taxonomy definitions |
| `tools/generate_tags.py` | Outputs the complete list of valid tags across all taxonomies |

Run validation:

```bash
python tools/validate.py
```

Generate all machinetags:

```bash
python tools/machinetag.py --all
```

---

## Cross-Reference Mappings

VantaCode taxonomies map to established frameworks:

| Framework | Mapping |
|-----------|---------|
| **MITRE ATT&CK** | `vantacode-threat` predicates align to ATT&CK tactics; MBT galaxy clusters cross-reference ATT&CK techniques |
| **OWASP LLM Top 10** | MBT galaxy clusters include OWASP LLM Top 10 references where applicable |
| **MITRE ATLAS** | MBT techniques cross-reference ATLAS tactics and techniques for AI/ML threats |
| **CISA Critical Infrastructure Sectors** | `vantacode-sector` predicates map directly to the 16 CISA-defined critical infrastructure sectors |

Mapping files are maintained in the `mappings/` directory.

---

## Repository Structure

```
vantacode-taxonomies/
  MANIFEST.json              # Registry of all taxonomies
  LICENSE                    # CC0-1.0 (data) + BSD-2-Clause (tools)
  vantacode-domain/          # Taxonomy: security domain classification
  vantacode-sector/          # Taxonomy: critical infrastructure sectors
  vantacode-threat/          # Taxonomy: ATT&CK tactic mapping
  vantacode-mbt/             # Taxonomy: malicious behaviors
  vantacode-status/          # Taxonomy: repo lifecycle status
  vantacode-sensitivity/     # Taxonomy: data sensitivity
  vantacode-governance/      # Taxonomy: governance scoring
  galaxies/                  # Galaxy definitions
  clusters/                  # Galaxy cluster data
  schema/                    # JSON schemas for validation
  tools/                     # Validation and generation scripts
  mappings/                  # Cross-reference mapping files
  research/                  # Research program references
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding values, proposing new taxonomies, and contributing galaxy clusters.

---

## License

- **Taxonomy data** (all `machinetag.json` files, `MANIFEST.json`, schema files): [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
- **Tools and software** (`tools/` directory, CI workflows, scripts): [BSD 2-Clause License](LICENSE)

---

Cory Kennedy / [DarkCode LLC](https://darkcode.ai) / cory@darkcode.ai
