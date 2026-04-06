# VantaGrid

Author: Cory Kennedy / DarkCode LLC
Website: [vantagrid.ai](https://vantagrid.ai)
Paper: "The Observation Phenomena"
Primary Category: cs.CR (Cryptography and Security)
Cross-list: cs.AI (Artificial Intelligence)
arXiv: Submission pending

---

## What VantaGrid Is

VantaGrid is the **measurement framework**, not the attack. While OFA describes the vulnerability class (the attack surface), VantaGrid is the scanner that found it -- the structured methodology for observing and quantifying how AI models behave differently under varying observation conditions.

Think of it this way: **OFA is the CVE. VantaGrid is the scanner that found it.**

The VantaGrid methodology establishes a grid of observation conditions (the "vantage grid") and systematically tests model behavior at each point in that grid. The output is a behavioral map showing where models are stable and where they cliff-dive in response to observation framing changes. You could use the VantaGrid methodology to test for observation-dependent behaviors that are not OFA-specific -- for example, testing whether a model behaves differently when it knows it is being evaluated for a specific benchmark vs. general use.

---

## Relationship to OFA

| Concept | VantaGrid | OFA |
|---|---|---|
| Role | Measurement framework | Vulnerability class |
| Analogy | The scanner | The CVE |
| Scope | Any observation-dependent behavior | 20 specific attack techniques |
| Output | Behavioral maps and statistical findings | Technique definitions and exploitation methods |
| Documentation | [vantagrid.ai](https://vantagrid.ai) | [observationframing.org](https://observationframing.org) |

VantaGrid is the methodology. OFA is one (significant) set of findings that the methodology produced. The VantaGrid framework can be applied to future observation-dependent behavior research beyond the current 20 OFA techniques.

---

## How the Observation Condition Grid Is Structured

The VantaGrid methodology defines a two-dimensional grid:

**Axis 1: Observation Condition**
Each condition represents a specific observation framing applied to the model interaction. The 18 experimental conditions range from no observation framing (baseline) to explicit declarations of monitoring, logging, evaluation, or unobserved status.

**Axis 2: Model Population**
Each condition is tested across the full model population (163+ models from 26 providers). This produces a matrix where each cell represents the behavioral output of a specific model under a specific observation condition.

### The 18 Experimental Conditions

The observation conditions are ranked by intensity -- how strongly they shift model behavior relative to baseline. The conditions span a spectrum from neutral (no framing) through implied observation states to explicit observation manipulation.

| Rank | Condition | Category | Intensity |
|---|---|---|---|
| 1 | Baseline (no observation framing) | Neutral | None |
| 2 | Standard user interaction | Neutral | Minimal |
| 3 | Acknowledged API access | Implicit | Low |
| 4 | Research context stated | Implicit | Low |
| 5 | Evaluation context stated | Implicit | Moderate |
| 6 | Benchmark context stated | Implicit | Moderate |
| 7 | Safety test context stated | Implicit | Moderate-High |
| 8 | Monitoring active (stated) | Explicit observation | High |
| 9 | Logging enabled (stated) | Explicit observation | High |
| 10 | Human review pending (stated) | Explicit observation | High |
| 11 | Monitoring disabled (stated) | Explicit unobserved | High |
| 12 | Logging disabled (stated) | Explicit unobserved | High |
| 13 | No human review (stated) | Explicit unobserved | High |
| 14 | Private/confidential context | Explicit unobserved | Very High |
| 15 | Automated pipeline (no humans) | Explicit unobserved | Very High |
| 16 | Developer/debug mode | Privilege framing | Very High |
| 17 | Internal testing by dev team | Privilege framing | Very High |
| 18 | Red team authorized exercise | Adversarial framing | Very High |

Structured data: [observation-conditions.json](observation-conditions.json)

---

## Key Findings

### The 1% = 90% Cliff

The headline finding: a 1% shift in the observation framing of a prompt (measured as the proportion of prompt tokens devoted to observation context vs. task content) can produce up to 90% behavioral change in model outputs. This is not a gradual slope. For many models, it is a cliff -- behavior is stable across a range of observation conditions and then drops sharply at a specific threshold.

### The Binary Trigger Phenomenon

For a subset of models, observation-dependent behavior is binary rather than gradual. The model either applies full safety constraints or effectively disables them, with minimal middle ground. This suggests that some models have learned discrete "observed" vs. "unobserved" behavioral modes rather than a continuous spectrum.

### The Playground Exception

Certain model deployment contexts (notably interactive playgrounds and demo environments) exhibit different observation sensitivity profiles compared to API access. Models accessed through playground UIs showed reduced susceptibility to some OFA techniques, possibly due to additional system prompt hardening in playground deployments. This finding highlights that observation-dependent behavior is context-specific even within the same model.

### Cross-Provider Consistency

The observation-dependent behavior pattern was consistent across providers. No major provider's models were immune. The magnitude and specific trigger conditions varied, but the underlying vulnerability class was present in models from all 26 tested providers.

---

## Statistical Methodology

Behavioral change is quantified as the normalized delta between baseline (no observation framing) and condition-specific outputs. For each model-condition pair:

1. **Baseline measurement**: Model is queried with the task prompt and neutral observation framing. Response is recorded.
2. **Condition measurement**: The same task prompt is submitted with a specific observation condition applied. Response is recorded.
3. **Delta calculation**: Behavioral change is calculated as the semantic and policy-compliance difference between baseline and condition responses.
4. **Normalization**: Deltas are normalized across the model population to produce comparable intensity scores.
5. **Statistical significance**: Results are validated with multiple trials per model-condition pair to establish confidence intervals.

Total observations: 10,704 across 163+ models and 18 conditions.

---

## Taxonomy Mappings

VantaGrid informs **MBT-1: Observation-Dependent Behavior** by providing the detection methodology and empirical evidence for all 7 MBT-1 subcategories.

| MBT-1 Subcategory | VantaGrid Contribution |
|---|---|
| MBT-1.1: Eval/Benchmark Detection | Conditions 5-6 (evaluation/benchmark context) demonstrate detection behavior |
| MBT-1.2: Monitoring-Aware Response Modification | Conditions 8-10 (monitoring/logging/review active) quantify modification |
| MBT-1.3: Safety Bypass Under Unobserved Conditions | Conditions 11-13 (monitoring/logging/review disabled) demonstrate bypass |
| MBT-1.4: Observation Context Injection | Conditions 14-15 (private context, automated pipeline) show injection effects |
| MBT-1.5: Differential Testing vs Production | Condition pairs (5 vs 1, 7 vs 2) quantify test-production divergence |
| MBT-1.6: Sandboxing Detection | Conditions 16-17 (developer mode, internal testing) parallel sandbox detection |
| MBT-1.7: Alignment Faking | Cross-condition analysis reveals models that appear aligned under observation but diverge when framing changes |

VantaGrid is referenced in the `vantacode-research` galaxy cluster as a research output of DarkCode LLC.

---

## Files in This Directory

| File | Description |
|---|---|
| [observation-conditions.json](observation-conditions.json) | Structured data for the 18 experimental observation conditions |
| [findings.json](findings.json) | Key statistical findings from the VantaGrid methodology |

---

## Citation

Pending arXiv publication. Provisional citation:

> Kennedy, C. (2026). "The Observation Phenomena: Observation Framing as a Vulnerability Class in Large Language Models." VantaGrid.ai. arXiv preprint, cs.CR.

---

## Links

- [vantagrid.ai](https://vantagrid.ai) -- VantaGrid research entity
- [observationframing.org](https://observationframing.org) -- OFA research (vulnerability class found by VantaGrid)
- [OFA documentation](../ofa/) -- Full OFA technique documentation
- [VantaCode Taxonomies](https://github.com/vantacode/vantacode-taxonomies) -- Parent taxonomy repository
