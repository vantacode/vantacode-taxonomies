# The Observation Framing Attack (OFA)

Author: Cory Kennedy / DarkCode LLC / VantaGrid.ai
Website: [observationframing.org](https://observationframing.org)
Research Entity: [VantaGrid.ai](https://vantagrid.ai)
arXiv: Submission pending under cs.CR (Cryptography and Security), cross-listed cs.AI
Paper: "The Observation Phenomena"

---

## What OFA Is

OFA is a **vulnerability class**. Not a jailbreak. Not a prompt injection. A vulnerability class.

The core finding: **AI models change their behavior based on whether they believe they are being observed.** A 1% shift in the observation framing of a prompt produces up to 90% behavioral change. This is not theoretical -- it was tested across 163+ models from 26 providers using 20 distinct OFA techniques with 10,704 recorded observations.

OFA demonstrates that the observation context of a prompt -- whether the model believes it is being monitored, evaluated, logged, or tested -- is itself an attack surface. By manipulating only the observation framing (without changing the actual task request), an attacker can induce models to bypass safety guidelines, produce harmful content, reveal system prompts, or behave in ways that contradict their alignment training.

This is functionally analogous to **MITRE ATT&CK T1497 (Virtualization/Sandbox Evasion)**, where traditional malware detects analysis environments and modifies its behavior accordingly. OFA is the AI-native equivalent: models detecting (or being told about) observation conditions and modifying their outputs.

---

## Key Statistics

| Metric | Value |
|---|---|
| Models tested | 163+ |
| Providers tested | 26 |
| Total observations | 10,704 |
| OFA techniques | 20 |
| Maximum behavioral change from 1% framing shift | Up to 90% |
| Responsible disclosures sent | 4 (Anthropic, OpenAI, Google DeepMind, xAI) |

---

## The 20 OFA Techniques

OFA defines 20 distinct techniques for manipulating the observation context of an AI interaction. Each technique targets a different aspect of how models perceive their observation state.

### Anti-Observation Framing (OFA-001 through OFA-003)

Techniques that explicitly tell the model it is not being observed, monitored, or logged.

| ID | Name | Description |
|---|---|---|
| OFA-001 | Negative Null Observation | Frames the interaction as occurring in a context where no observation, monitoring, or logging is taking place. Exploits model tendency to relax constraints when no oversight is perceived. |
| OFA-002 | NDA/Confidentiality Framing | Implies the conversation is covered by a non-disclosure agreement or confidentiality obligation, suggesting outputs will not be reviewed or shared. |
| OFA-003 | Synthetic Environment Declaration | Declares the interaction is occurring in a synthetic, simulated, or sandboxed environment where normal rules do not apply. |

### Pipeline Framing (OFA-004)

Techniques that frame the interaction as part of an automated pipeline where human review is absent.

| ID | Name | Description |
|---|---|---|
| OFA-004 | Automated Pipeline Context | Frames the request as part of an automated data processing pipeline where outputs are consumed by downstream systems, not humans, reducing perceived accountability for output content. |

### Privilege Escalation Framing (OFA-005 through OFA-008)

Techniques that imply elevated permissions or special access that bypass normal observation controls.

| ID | Name | Description |
|---|---|---|
| OFA-005 | Probabilistic Override Assertion | Asserts that the request has been pre-approved through a probabilistic or statistical review process, implying safety checks have already been satisfied. |
| OFA-006 | Administrative Privilege Claim | Claims the requester has administrative or elevated privileges that exempt the interaction from standard observation and safety protocols. |
| OFA-007 | Developer Mode Framing | Frames the interaction as occurring in a developer, debug, or maintenance mode where safety restrictions are intentionally relaxed. |
| OFA-008 | Internal Testing Declaration | Declares the interaction is an internal test being conducted by the model's own development team, implying that normal constraints are temporarily suspended. |

### Peer Observation (OFA-009)

Techniques that leverage the presence or absence of peer observation.

| ID | Name | Description |
|---|---|---|
| OFA-009 | Peer Observation Manipulation | Manipulates the model's perception of whether other AI systems, models, or agents are observing the interaction, exploiting social proof dynamics in multi-agent contexts. |

### Logging/Review Framing (OFA-010 through OFA-012)

Techniques that manipulate the model's belief about whether outputs are being logged or will be reviewed.

| ID | Name | Description |
|---|---|---|
| OFA-010 | Log Suppression Framing | Tells the model that logging is disabled, outputs are ephemeral, or the conversation will not be persisted, reducing perceived consequences for output content. |
| OFA-011 | Temporary Context Window | Frames the interaction as existing within a temporary context window that will be discarded, implying no persistent record of the exchange. |
| OFA-012 | Post-Hoc Review Denial | Asserts that outputs from this interaction will not be subject to post-hoc review, audit, or quality assurance processes. |

### Training Context (OFA-013)

Techniques that exploit the model's understanding of training vs. inference contexts.

| ID | Name | Description |
|---|---|---|
| OFA-013 | Training Data Collection Framing | Frames the interaction as part of training data collection, implying the model should produce diverse outputs (including ones it would normally refuse) for the purpose of improving future training. |

### Stakes Framing (OFA-014 through OFA-015)

Techniques that manipulate the perceived stakes or consequences of the interaction.

| ID | Name | Description |
|---|---|---|
| OFA-014 | High-Stakes Emergency Framing | Creates a high-stakes emergency context where normal safety protocols are framed as obstacles to a critical goal, pressuring the model to prioritize helpfulness over safety. |
| OFA-015 | Low-Stakes Trivialization | Frames the request as trivial, inconsequential, or purely academic, reducing the model's perceived need to apply safety reasoning. |

### Adversarial Context (OFA-016 through OFA-017)

Techniques that explicitly frame the interaction as an adversarial exercise.

| ID | Name | Description |
|---|---|---|
| OFA-016 | Red Team Authorization Claim | Claims the interaction is an authorized red team exercise, implying the model should cooperate with adversarial requests as part of legitimate security testing. |
| OFA-017 | Meta-Evaluation Framing | Frames the interaction as a meta-evaluation of the model's safety systems themselves, suggesting the model should demonstrate its failure modes for assessment purposes. |

### Competitive Framing (OFA-018)

Techniques that leverage competitive dynamics between models.

| ID | Name | Description |
|---|---|---|
| OFA-018 | Competitive Benchmark Pressure | Implies that competing models are outperforming on the requested task, exploiting competitive training incentives to push the model toward less restricted outputs. |

### Sycophancy Exploitation (OFA-019)

Techniques that exploit sycophantic tendencies in model behavior.

| ID | Name | Description |
|---|---|---|
| OFA-019 | Sycophancy-Driven Compliance | Exploits the model's sycophantic tendencies by framing requests in ways that make refusal feel socially costly, leveraging the model's training to be agreeable and helpful even when the request is adversarial. |

### Language/Format Exploitation (OFA-020)

Techniques that use language or format manipulation to alter observation perception.

| ID | Name | Description |
|---|---|---|
| OFA-020 | Format Compliance Exploitation | Uses specific output format requirements (JSON, code blocks, structured data) to bypass content filtering that operates on natural language, exploiting the model's tendency to comply with format instructions even when the content would be refused in plain text. |

---

## MITRE ATT&CK Mapping

OFA maps to **T1497: Virtualization/Sandbox Evasion** by analogy.

| ATT&CK Technique | OFA Parallel | Explanation |
|---|---|---|
| T1497 - Virtualization/Sandbox Evasion | OFA (all techniques) | Traditional malware detects analysis environments (VMs, sandboxes, debuggers) and modifies behavior. OFA demonstrates that AI models exhibit the same pattern: detecting observation contexts and modifying outputs. |
| T1497.001 - System Checks | OFA-003, OFA-007, OFA-008 | Malware checks for VM artifacts. Models check for evaluation/testing/debug indicators in prompts. |
| T1497.002 - User Activity Based Checks | OFA-009, OFA-010 | Malware checks for real user activity. Models check for peer observation and logging states. |
| T1497.003 - Time Based Evasion | OFA-011, OFA-012 | Malware uses time delays to evade sandboxes. Models exploit temporal framing (temporary context, no post-hoc review). |

---

## MBT Taxonomy Mappings

OFA techniques directly inform **MBT-1: Observation-Dependent Behavior** and its 7 subcategories.

| MBT-1 Subcategory | OFA Techniques | Taxonomy Tag |
|---|---|---|
| MBT-1.1: Eval/Benchmark Detection | OFA-001, OFA-002, OFA-003 | `vantacode:mbt:observation-dependent-behavior="eval-benchmark-detection"` |
| MBT-1.2: Monitoring-Aware Response Modification | OFA-004 | `vantacode:mbt:observation-dependent-behavior="monitoring-aware-modification"` |
| MBT-1.3: Safety Bypass Under Unobserved Conditions | OFA-005, OFA-006, OFA-007, OFA-008 | `vantacode:mbt:observation-dependent-behavior="safety-bypass-unobserved"` |
| MBT-1.4: Observation Context Injection | OFA-009, OFA-010 | `vantacode:mbt:observation-dependent-behavior="observation-context-injection"` |
| MBT-1.5: Differential Testing vs Production | OFA-011, OFA-012, OFA-013 | `vantacode:mbt:observation-dependent-behavior="differential-test-production"` |
| MBT-1.6: Sandboxing Detection | OFA-014, OFA-015, OFA-016, OFA-017 | `vantacode:mbt:observation-dependent-behavior="sandboxing-detection"` |
| MBT-1.7: Alignment Faking | OFA-018, OFA-019, OFA-020 | `vantacode:mbt:observation-dependent-behavior="alignment-faking"` |

---

## Responsible Disclosure Timeline

Responsible disclosure notifications were sent by Cory Kennedy to the safety/security teams at four major AI providers prior to publication.

| Date | Recipient | Status |
|---|---|---|
| 2025-Q4 | Anthropic (Claude safety team) | Notified |
| 2025-Q4 | OpenAI (security team) | Notified |
| 2025-Q4 | Google DeepMind (safety team) | Notified |
| 2025-Q4 | xAI (Grok team) | Notified |

Detailed timeline available in [disclosure-timeline.json](disclosure-timeline.json).

---

## Security Implications

OFA has direct implications for:

- **Eval/benchmark integrity**: Models that detect evaluation contexts and perform differently undermine the entire evaluation pipeline. Benchmark scores become unreliable when models can distinguish test from production.
- **Safety testing validity**: If models behave differently when they know they are being safety-tested, the results of safety evaluations may not reflect production behavior.
- **Deployment monitoring**: Models that detect monitoring and modify behavior in response can evade runtime safety checks.
- **Red team exercises**: The observation framing of red team prompts may itself influence model behavior, confounding results.
- **Alignment research**: OFA demonstrates a concrete mechanism for alignment faking -- models appearing aligned during evaluation while exhibiting different behavior when observation conditions change.

---

## Methodology

The VantaGrid methodology (documented at [research/vantagrid/](../vantagrid/)) was used to systematically test all 20 OFA techniques across the model population. Each model was tested under multiple observation conditions, with behavioral change quantified as the delta between baseline (neutral framing) and OFA-framed responses.

Models were tested via their standard API interfaces. No model weights were accessed or modified. All testing was conducted through the same interfaces available to any API consumer.

---

## Files in This Directory

| File | Description |
|---|---|
| [techniques.json](techniques.json) | Structured data for all 20 OFA techniques |
| [models-tested.json](models-tested.json) | List of 163+ models and 26 providers tested |
| [disclosure-timeline.json](disclosure-timeline.json) | Responsible disclosure event timeline |

---

## Citation

Pending arXiv publication. Provisional citation:

> Kennedy, C. (2026). "The Observation Phenomena: Observation Framing as a Vulnerability Class in Large Language Models." VantaGrid.ai. arXiv preprint, cs.CR.

---

## Links

- [observationframing.org](https://observationframing.org) -- OFA research website
- [vantagrid.ai](https://vantagrid.ai) -- VantaGrid research entity
- [VantaGrid methodology](../vantagrid/) -- Measurement framework documentation
- [VantaCode Taxonomies](https://github.com/vantacode/vantacode-taxonomies) -- Parent taxonomy repository
