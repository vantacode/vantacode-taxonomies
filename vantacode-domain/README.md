# vantacode-domain

> Classification of code repositories by functional security domain. Repositories may carry multiple domain tags. Derived from the NoDataFound portfolio classification system.

**Version:** 1  
**Exclusive:** No  
**References:** https://github.com/vantacode/vantacode-taxonomies  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `category` | Domain Category | The functional security domain a repository belongs to. | No |

## Values: `category`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `offensive-security` | Offensive Security | Exploit development, red team tooling, vulnerability research, fuzzing, payload generation, C2 frameworks, post-exploitation. | `#e74c3c` |
| `defensive-security` | Defensive Security | Detection engineering, SIEM rules, YARA signatures, incident response tooling, forensics, blue team automation. | `#2ecc71` |
| `threat-intelligence` | Threat Intelligence | CTI platform tooling, indicator management, STIX/TAXII, threat feeds, actor tracking, campaign analysis, IOC enrichment. | `#3498db` |
| `ai-security` | AI + Security | Adversarial ML, LLM security, AI red teaming, model exploitation, AI-powered security tools, prompt injection, model poisoning. | `#9b59b6` |
| `hardware-rf` | Hardware + RF | Hardware hacking, SDR, RF analysis, firmware reversing, embedded systems, IoT exploitation. | `#e67e22` |
| `malware-research` | Malware Research | Malware analysis, reverse engineering, unpacking, deobfuscation, sandbox analysis, behavioral analysis. | `#c0392b` |
| `osint-recon` | OSINT + Recon | Open source intelligence collection, reconnaissance automation, data mining, domain/IP enumeration. | `#1abc9c` |
| `infrastructure-devops` | Infrastructure + DevOps | Infrastructure automation, CI/CD, container orchestration, cloud security, IaC, monitoring, deployment tooling. | `#34495e` |
| `visualization-data` | Visualization + Data | Data visualization, dashboards, reporting tools, graph analysis, network visualization, threat landscape mapping. | `#f39c12` |
| `community-education` | Community + Education | Conference talks, CTF challenges, training materials, workshops, community tools, educational content. | `#16a085` |
| `crypto-finance` | Crypto + Finance | Cryptocurrency research, blockchain analysis, smart contract auditing, DeFi security, financial fraud detection. | `#27ae60` |
| `vulnerability-research` | Vulnerability Research | CVE research, vulnerability discovery, PoC development, patch analysis, advisory writing, responsible disclosure. | `#e74c3c` |
| `privacy-anti-surveillance` | Privacy + Anti-Surveillance | Privacy tools, anti-surveillance tech, anonymization, adversarial fashion, counter-tracking, anti-fingerprinting. | `#8e44ad` |
| `governance-compliance` | Governance + Compliance | Policy enforcement, compliance automation, SBOM/AIBOM generation, audit tooling, standards validation, repo governance. | `#7f8c8d` |

## Tag Format Examples

```
vantacode-domain:category="offensive-security"
```

---

*14 tags across 1 predicates.*
