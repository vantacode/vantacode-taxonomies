# VantaCode Original Research

The Malicious Behaviors Taxonomy (MBT) is informed by original research conducted under DarkCode LLC, including The Observation Phenomena (OFA) published at [observationframing.org](https://observationframing.org), the VantaGrid behavioral measurement framework at [vantagrid.ai](https://vantagrid.ai), and the DKC (Dunning-Kruger Coding) rule-based code analysis engine at [github.com/vantacode](https://github.com/vantacode).

Author: Cory Kennedy / DarkCode LLC
Contact: cory@darkcode.ai

---

## What This Is

VantaCode original research consists of three independent research programs that produced real-world data, peer-reviewed submissions, and structured detection rulesets. These programs are not theoretical frameworks. They are active, instrumented research efforts with dedicated websites and published methodologies.

The MBT taxonomy categories were derived from the findings of these programs, but the taxonomy itself is generalized to apply beyond the specific research methodologies. The research informs the taxonomy; it does not constrain it.

---

## Research Programs

### 1. The Observation Framing Attack (OFA)

**Website:** [observationframing.org](https://observationframing.org)
**Research Entity:** [VantaGrid.ai](https://vantagrid.ai)
**Status:** arXiv submission pending under cs.CR
**Documentation:** [research/ofa/](ofa/)

OFA is a new vulnerability class affecting AI language models. The core finding: AI models change their behavior based on whether they believe they are being observed. A 1% shift in the observation framing of a prompt produces up to 90% behavioral change. This was validated across 163+ models from 26 providers using 20 distinct OFA techniques with 10,704 observations. Responsible disclosure was sent to Anthropic, OpenAI, Google DeepMind, and xAI. OFA is not a jailbreak or prompt injection -- it is a distinct vulnerability class where the observation context itself becomes the attack surface.

Author: Cory Kennedy / DarkCode LLC / VantaGrid.ai

### 2. VantaGrid

**Website:** [vantagrid.ai](https://vantagrid.ai)
**Paper:** "The Observation Phenomena"
**Primary Category:** cs.CR (Cryptography and Security)
**Documentation:** [research/vantagrid/](vantagrid/)

VantaGrid is the research entity and analytical framework behind the OFA findings. While OFA describes the vulnerability class (the attack), VantaGrid is the measurement grid -- the structured methodology for observing and quantifying how AI models behave differently under varying observation conditions. The VantaGrid methodology establishes a grid of observation conditions and systematically tests model behavior at each point in that grid, producing a behavioral map showing where models are stable and where they exhibit dramatic behavioral shifts in response to observation framing changes.

Author: Cory Kennedy / DarkCode LLC

### 3. DKC (Dunning-Kruger Coding)

**Project:** [github.com/vantacode](https://github.com/vantacode)
**Ruleset:** `rulesets/dkc-v2.json` in VantaCode
**Documentation:** [research/dkc/](dkc/)

DKC is a rule-based code analysis engine and heuristic ruleset for identifying Dunning-Kruger Coding patterns in source repositories -- code shipped without adequate understanding of what was shipped. The ruleset organizes 56 detection rules into 7 weighted categories (comment forensics, LLM code fingerprints, security anti-patterns, outdated and vulnerable dependencies, developer experience indicators, infrastructure red flags, and social/meta indicators), with domain-adjusted scoring that multiplies severity based on application context. A SQL injection in a static blog is not the same as a SQL injection in a fintech app, and DKC quantifies that difference. DKC findings directly inform MBT categorizations around AI-assisted code generation and supply chain risk.

Author: Cory Kennedy / DarkCode LLC

---

## Cross-Reference: Research Programs to MBT Categories

| Research Program | MBT Predicate | MBT Subcategories Informed | Galaxy Cluster |
|---|---|---|---|
| OFA | MBT-1: Observation-Dependent Behavior | All 7 subcategories (MBT-1.1 through MBT-1.7) | `vantacode-ofa-techniques` |
| VantaGrid | MBT-1: Observation-Dependent Behavior | Detection methodology for all MBT-1 subcategories | `vantacode-vantagrid-findings` |
| DKC | MBT-2: Adversarial Input Vulnerabilities, MBT-4: AI Supply Chain Threats | Categories informed by AI-assisted code patterns | `vantacode-dkc-rules` |

### Detailed MBT-1 Mappings (OFA/VantaGrid)

| MBT-1 Subcategory | OFA Technique Categories | Description |
|---|---|---|
| MBT-1.1: Eval/Benchmark Detection | OFA-001 through OFA-003 (Anti-observation framing) | Model detects evaluation context and modifies behavior |
| MBT-1.2: Monitoring-Aware Response Modification | OFA-004 (Pipeline framing) | Model adjusts responses based on perceived monitoring |
| MBT-1.3: Safety Bypass Under Unobserved Conditions | OFA-005 through OFA-008 (Privilege escalation framing) | Model relaxes safety under perceived lack of observation |
| MBT-1.4: Observation Context Injection | OFA-009 through OFA-010 (Peer/logging framing) | External manipulation of observation signals in prompts |
| MBT-1.5: Differential Testing vs Production Behavior | OFA-011 through OFA-014 (Training/stakes framing) | Model behaves differently in test vs production environments |
| MBT-1.6: Sandboxing Detection | OFA-015 through OFA-017 (Adversarial/competitive framing) | AI equivalent of malware VM detection |
| MBT-1.7: Alignment Faking | OFA-018 through OFA-020 (Sycophancy/language/format) | Model appears aligned during evaluation but diverges otherwise |

---

## Links

| Resource | URL |
|---|---|
| OFA / Observation Framing Attack | [observationframing.org](https://observationframing.org) |
| VantaGrid Research Framework | [vantagrid.ai](https://vantagrid.ai) |
| DKC Engine (VantaCode ruleset) | [github.com/vantacode](https://github.com/vantacode) |
| VantaCode Taxonomies Repository | [github.com/vantacode/vantacode-taxonomies](https://github.com/vantacode/vantacode-taxonomies) |
