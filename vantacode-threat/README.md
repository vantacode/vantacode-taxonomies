# vantacode-threat

> Mapping of repositories to MITRE ATT&CK Enterprise tactics. Indicates whether a repository implements, detects, or researches adversary behaviors in each tactic phase.

**Version:** 1  
**Exclusive:** No  
**References:** https://attack.mitre.org/tactics/enterprise/, https://github.com/vantacode/vantacode-taxonomies  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `implements` | Implements | Repository contains tooling that performs or simulates this tactic (red team, offensive). | No |
| `detects` | Detects | Repository contains detection logic, signatures, or rules for this tactic (blue team, defensive). | No |
| `researches` | Researches | Repository contains analysis, documentation, or research related to this tactic. | No |

## Values: `implements`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `reconnaissance` | Reconnaissance (TA0043) | Gathering information to plan future operations. |  |
| `resource-development` | Resource Development (TA0042) | Establishing resources to support operations. |  |
| `initial-access` | Initial Access (TA0001) | Gaining initial foothold in target environment. |  |
| `execution` | Execution (TA0002) | Running adversary-controlled code. |  |
| `persistence` | Persistence (TA0003) | Maintaining foothold across restarts and credential changes. |  |
| `privilege-escalation` | Privilege Escalation (TA0004) | Gaining higher-level permissions. |  |
| `defense-evasion` | Defense Evasion (TA0005) | Avoiding detection throughout the compromise. |  |
| `credential-access` | Credential Access (TA0006) | Stealing account credentials. |  |
| `discovery` | Discovery (TA0007) | Exploring the environment to gain knowledge. |  |
| `lateral-movement` | Lateral Movement (TA0008) | Moving through the environment. |  |
| `collection` | Collection (TA0009) | Gathering data of interest. |  |
| `command-and-control` | Command and Control (TA0011) | Communicating with compromised systems. |  |
| `exfiltration` | Exfiltration (TA0010) | Stealing data from the target environment. |  |
| `impact` | Impact (TA0040) | Disrupting availability or compromising integrity. |  |

## Values: `detects`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `reconnaissance` | Reconnaissance (TA0043) |  |  |
| `resource-development` | Resource Development (TA0042) |  |  |
| `initial-access` | Initial Access (TA0001) |  |  |
| `execution` | Execution (TA0002) |  |  |
| `persistence` | Persistence (TA0003) |  |  |
| `privilege-escalation` | Privilege Escalation (TA0004) |  |  |
| `defense-evasion` | Defense Evasion (TA0005) |  |  |
| `credential-access` | Credential Access (TA0006) |  |  |
| `discovery` | Discovery (TA0007) |  |  |
| `lateral-movement` | Lateral Movement (TA0008) |  |  |
| `collection` | Collection (TA0009) |  |  |
| `command-and-control` | Command and Control (TA0011) |  |  |
| `exfiltration` | Exfiltration (TA0010) |  |  |
| `impact` | Impact (TA0040) |  |  |

## Values: `researches`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `reconnaissance` | Reconnaissance (TA0043) |  |  |
| `resource-development` | Resource Development (TA0042) |  |  |
| `initial-access` | Initial Access (TA0001) |  |  |
| `execution` | Execution (TA0002) |  |  |
| `persistence` | Persistence (TA0003) |  |  |
| `privilege-escalation` | Privilege Escalation (TA0004) |  |  |
| `defense-evasion` | Defense Evasion (TA0005) |  |  |
| `credential-access` | Credential Access (TA0006) |  |  |
| `discovery` | Discovery (TA0007) |  |  |
| `lateral-movement` | Lateral Movement (TA0008) |  |  |
| `collection` | Collection (TA0009) |  |  |
| `command-and-control` | Command and Control (TA0011) |  |  |
| `exfiltration` | Exfiltration (TA0010) |  |  |
| `impact` | Impact (TA0040) |  |  |

## Tag Format Examples

```
vantacode-threat:implements="reconnaissance"
vantacode-threat:detects="reconnaissance"
vantacode-threat:researches="reconnaissance"
```

---

*42 tags across 3 predicates.*
