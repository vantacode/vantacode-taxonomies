# VantaCode Original Research

The Malicious Behaviors Taxonomy (MBT) is informed by original research conducted under DarkCode LLC, including The Observation Phenomena (OFA) published at [observationframing.org](https://observationframing.org), the VantaGrid behavioral measurement framework at [vantagrid.ai](https://vantagrid.ai), and the DECLAWED AI agent exposure tracker at [declawed.io](https://declawed.io).

Author: Cory Kennedy / DarkCode LLC
Contact: cory@darkcode.ai

---

## What This Is

VantaCode original research consists of three independent research programs that produced real-world data, responsible disclosures, peer-reviewed submissions, and media coverage. These programs are not theoretical frameworks. They are active, instrumented research efforts with dedicated websites, live dashboards, and structured data feeds.

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

### 3. DECLAWED

**Website:** [declawed.io](https://declawed.io)
**Updates:** Every 15 minutes (live dashboard)
**Coverage:** 14+ media outlets
**Documentation:** [research/declawed/](declawed/)

DECLAWED is a real-time tracking system for exposed AI agent instances on the public internet. It tracks 145K+ exposed instances across 46.2K unique IPs in 82 countries, with 2.5M CVE detections, 70K APT-linked instances, 37K CISA KEV flagged, 56.6K breach-linked, and 15.9K RCE-vulnerable. The research identified 5 confirmed malicious ClawHub skills with mapped C2 infrastructure. DECLAWED is not a one-time scan -- it is a live dashboard backed by a TAXII 2.1 feed that researchers can consume programmatically.

---

## Cross-Reference: Research Programs to MBT Categories

| Research Program | MBT Predicate | MBT Subcategories Informed | Galaxy Cluster |
|---|---|---|---|
| OFA | MBT-1: Observation-Dependent Behavior | All 7 subcategories (MBT-1.1 through MBT-1.7) | `vantacode-mbt-techniques` (MBT-1.*) |
| VantaGrid | MBT-1: Observation-Dependent Behavior | Detection methodology for all MBT-1 subcategories | `vantacode-research` ("VantaGrid") |
| DECLAWED | MBT-3: Insecure AI Deployment | All 8 subcategories (MBT-3.1 through MBT-3.8) | `vantacode-mbt-techniques` (MBT-3.*) |
| DECLAWED | MBT-4: AI Supply Chain Threats | MBT-4.4: Malicious Skill/Plugin | `vantacode-mbt-techniques` (MBT-4.*) |

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

### Detailed MBT-3/MBT-4 Mappings (DECLAWED)

| MBT Subcategory | DECLAWED Category | Description |
|---|---|---|
| MBT-3.1: Exposed Control Panel | DEC-01 | AI agent control panels accessible without authentication |
| MBT-3.2: Default Credentials | -- | Default or missing credentials on agent platforms |
| MBT-3.3: Unauthenticated API Endpoints | -- | Model inference endpoints with no auth |
| MBT-3.4: Missing Network Segmentation | DEC-04 | APT-linked infrastructure hosting AI agents |
| MBT-3.5: Exposed Training Data/Weights | -- | Accessible model artifacts |
| MBT-3.6: Misconfigured Tool Permissions | DEC-02 | RCE-vulnerable agent instances |
| MBT-3.7: Malicious Skill/Plugin | DEC-03 | 5 confirmed malicious ClawHub skills with C2 |
| MBT-3.8: Bound to All Interfaces | DEC-05 | Breach-linked exposed instances |
| MBT-4.4: Malicious Dependencies | DEC-03 | Supply chain compromise via agent marketplace |

---

## Links

| Resource | URL |
|---|---|
| OFA / Observation Framing Attack | [observationframing.org](https://observationframing.org) |
| VantaGrid Research Framework | [vantagrid.ai](https://vantagrid.ai) |
| DECLAWED Live Dashboard | [declawed.io](https://declawed.io) |
| VantaCode Taxonomies Repository | [github.com/vantacode/vantacode-taxonomies](https://github.com/vantacode/vantacode-taxonomies) |
