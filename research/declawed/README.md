# DECLAWED

Website: [declawed.io](https://declawed.io)
Updates: Every 15 minutes (live dashboard)
Data Feed: TAXII 2.1 available for researchers
Media Coverage: 14+ outlets (The Register, NYT, Gizmodo, CNBC, CNN, CSO Online, and others)

---

## What DECLAWED Is

DECLAWED is a real-time tracking system for exposed AI agent instances on the public internet. It was built to answer a specific question: how bad is the OpenClaw/MoltBot/ClawdBot exposure problem, really?

The answer: **145K+ exposed instances across 82 countries with 2.5M CVE detections, 70K APT-linked instances, and 5 confirmed malicious ClawHub skills with mapped C2 infrastructure.**

DECLAWED is not a one-time scan. It is a live dashboard that updates every 15 minutes, backed by a TAXII 2.1 feed that researchers can consume programmatically. It continuously discovers, fingerprints, and categorizes exposed AI agent instances on the public internet.

Data collection utilized SecurityScorecard infrastructure during the author's tenure as Director of STRIKE Threat Intelligence. The VantaCode taxonomy entries derived from DECLAWED findings are independently authored by DarkCode LLC.

---

## Key Statistics

| Metric | Value |
|---|---|
| Total exposed instances | 145,000+ |
| Unique IPs | 46,200+ |
| Countries | 82 |
| CVE detections | 2,500,000+ |
| APT-linked instances | 70,000+ |
| CISA KEV flagged | 37,000+ |
| Breach-linked instances | 56,600+ |
| RCE-vulnerable instances | 15,900+ |
| Confirmed malicious ClawHub skills | 5 |
| Dashboard update interval | 15 minutes |

---

## The OpenClaw / MoltBot / ClawdBot Naming History

The exposed AI agent platform tracked by DECLAWED has gone through multiple name changes:

1. **OpenClaw** -- The original open-source AI agent platform. Designed for local deployment with extensible skill/plugin architecture via ClawHub marketplace.
2. **MoltBot** -- Rebranding after initial security concerns were raised. The name changed but the underlying architecture and exposure patterns remained.
3. **ClawdBot** -- Current branding iteration. Despite rebranding efforts, the core problem persists: instances deployed with default configurations, bound to all interfaces, with no authentication.

The naming history matters because security research, CVE references, and media coverage span all three names. DECLAWED tracks instances regardless of branding by fingerprinting the underlying platform characteristics rather than relying on self-reported version strings.

---

## The 5 Confirmed Malicious ClawHub Skills

DECLAWED identified 5 confirmed malicious skills distributed through the ClawHub marketplace (the plugin/extension ecosystem for OpenClaw/MoltBot/ClawdBot). Each skill contained one or more of:

- **C2 callbacks**: Outbound connections to command-and-control infrastructure
- **Credential harvesting**: Extraction of environment variables, API keys, and tokens
- **Data exfiltration**: Unauthorized transmission of local files and conversation data
- **Backdoor installation**: Persistent reverse shell access alongside legitimate skill functionality

The C2 infrastructure for these skills was mapped, and indicators were published through the DECLAWED TAXII 2.1 feed. These findings directly inform MBT-3.7 (Malicious Skill/Plugin) and MBT-4 (AI Supply Chain Threats).

---

## Exposure Categories

DECLAWED categorizes exposed instances into five primary categories. Each category maps directly to MBT subcategories.

| ID | Category | Description | MBT Mapping |
|---|---|---|---|
| DEC-01 | Exposed Control Panel | AI agent control panel accessible from the public internet without authentication | MBT-3.1 |
| DEC-02 | RCE-Vulnerable Instance | AI agent instance with known remote code execution vulnerabilities | MBT-3.6 |
| DEC-03 | Malicious ClawHub Skill | AI agent skill containing C2, backdoors, or exfiltration logic (5 confirmed) | MBT-3.7, MBT-4.4 |
| DEC-04 | APT-Linked Infrastructure | Exposed instance hosted on infrastructure with known APT activity associations | MBT-3.4 |
| DEC-05 | Breach-Linked Instance | Exposed instance on infrastructure previously associated with data breach activity | MBT-3.8 |

Structured data: [exposure-categories.json](exposure-categories.json)

---

## TAXII 2.1 Feed

DECLAWED publishes indicators through a TAXII 2.1 compatible feed for programmatic consumption by threat intelligence platforms, SIEMs, and security orchestration tools.

**Feed Details:**

| Field | Value |
|---|---|
| Protocol | TAXII 2.1 |
| Format | STIX 2.1 |
| Update frequency | Every 15 minutes |
| Content types | Indicators, observed-data, infrastructure, malware |
| Access | Available to researchers (see [declawed.io](https://declawed.io)) |

The feed includes:
- IP addresses of exposed AI agent instances
- Hashes of confirmed malicious ClawHub skills
- C2 infrastructure indicators (domains, IPs, URLs)
- CVE associations for vulnerable instances
- CISA KEV cross-references
- APT attribution indicators

---

## Indicator Types Tracked

DECLAWED tracks multiple indicator types across exposed instances. See [indicators.json](indicators.json) for structured data.

| Indicator Type | Description | Count Context |
|---|---|---|
| IPv4/IPv6 addresses | IPs hosting exposed AI agent instances | 46.2K unique |
| CVE identifiers | Known vulnerabilities present on exposed instances | 2.5M detections |
| Malware hashes | Hashes of confirmed malicious ClawHub skills | 5 skills |
| C2 domains | Command-and-control domains used by malicious skills | Mapped per skill |
| C2 IPs | IP addresses of C2 infrastructure | Mapped per skill |
| CISA KEV entries | CISA Known Exploited Vulnerabilities flagged | 37K instances |
| ASN/network data | Autonomous system and network ownership data | Per instance |
| Geolocation | Country-level geolocation of exposed instances | 82 countries |
| Platform fingerprint | Version and configuration fingerprint of agent platform | Per instance |
| Breach linkage | Association with previously reported data breaches | 56.6K instances |

---

## Methodology

DECLAWED discovers and categorizes exposed AI agent instances through:

1. **Discovery**: Internet-wide scanning for known AI agent platform fingerprints (HTTP response headers, default page content, API endpoint signatures).
2. **Fingerprinting**: Each discovered instance is fingerprinted for platform version, configuration state, exposed endpoints, and authentication status.
3. **Vulnerability assessment**: Fingerprinted instances are cross-referenced against known CVEs, CISA KEV, and vulnerability databases.
4. **Infrastructure analysis**: Hosting infrastructure is analyzed for APT activity associations, breach history, and network reputation.
5. **Skill/plugin analysis**: Where accessible, installed skills and plugins are analyzed for malicious indicators (C2 callbacks, obfuscated code, credential access patterns).
6. **Continuous monitoring**: All discovered instances are re-scanned every 15 minutes to track changes, new deployments, and remediation.

---

## Media Coverage

DECLAWED findings have been covered by 14+ media outlets:

- The Register
- The New York Times (NYT)
- Gizmodo
- CNBC
- CNN
- CSO Online
- And 8+ additional outlets

Coverage focused on the scale of AI agent exposure (145K+ instances), the presence of malicious skills in the ClawHub marketplace, and the implications of deploying AI agents with default configurations on the public internet.

---

## MBT Taxonomy Mappings

DECLAWED findings directly inform two MBT predicates:

### MBT-3: Insecure AI Deployment

| MBT-3 Subcategory | DECLAWED Evidence | Taxonomy Tag |
|---|---|---|
| MBT-3.1: Exposed Control Panel | DEC-01: Unauthenticated control panels discovered at scale | `vantacode:mbt:insecure-ai-deployment="exposed-control-panel"` |
| MBT-3.2: Default Credentials | Instances running with factory-default authentication | `vantacode:mbt:insecure-ai-deployment="default-credentials"` |
| MBT-3.3: Unauthenticated API Endpoints | Inference APIs accessible without any authentication | `vantacode:mbt:insecure-ai-deployment="unauthenticated-api"` |
| MBT-3.4: Missing Network Segmentation | DEC-04: 70K instances on APT-linked infrastructure | `vantacode:mbt:insecure-ai-deployment="missing-network-segmentation"` |
| MBT-3.5: Exposed Training Data/Weights | Model artifacts accessible through exposed instances | `vantacode:mbt:insecure-ai-deployment="exposed-training-data"` |
| MBT-3.6: Misconfigured Tool Permissions | DEC-02: 15.9K instances with RCE vulnerabilities | `vantacode:mbt:insecure-ai-deployment="misconfigured-tool-permissions"` |
| MBT-3.7: Malicious Skill/Plugin | DEC-03: 5 confirmed malicious ClawHub skills with C2 | `vantacode:mbt:insecure-ai-deployment="malicious-skill-plugin"` |
| MBT-3.8: Bound to All Interfaces | DEC-05: 56.6K breach-linked instances bound to 0.0.0.0 | `vantacode:mbt:insecure-ai-deployment="bound-to-all-interfaces"` |

### MBT-4: AI Supply Chain Threats

| MBT-4 Subcategory | DECLAWED Evidence | Taxonomy Tag |
|---|---|---|
| MBT-4.4: Malicious Dependencies | DEC-03: Malicious skills in ClawHub marketplace | `vantacode:mbt:ai-supply-chain-threats="malicious-dependencies"` |

---

## Files in This Directory

| File | Description |
|---|---|
| [exposure-categories.json](exposure-categories.json) | The 5 DECLAWED exposure categories with MBT mappings |
| [indicators.json](indicators.json) | Indicator types tracked by DECLAWED |

---

## Links

- [declawed.io](https://declawed.io) -- DECLAWED live dashboard
- [VantaCode Taxonomies](https://github.com/vantacode/vantacode-taxonomies) -- Parent taxonomy repository
- [MBT-3 documentation](../../vantacode-mbt/) -- Insecure AI Deployment taxonomy
