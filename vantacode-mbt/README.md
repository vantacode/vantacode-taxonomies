# vantacode-mbt

> Malicious Behaviors Taxonomy (MBT) for AI and ML system threats. Classifies AI-specific malicious behaviors, vulnerabilities, and deployment risks. Informed by DarkCode LLC research including the Observation Framing Attack (OFA), the VantaGrid behavioral measurement framework, and the DKC (Dunning-Kruger Coding) detection ruleset.

**Version:** 1  
**Exclusive:** No  
**References:** https://github.com/vantacode/vantacode-taxonomies, https://observationframing.org, https://vantagrid.ai, https://owasp.org/www-project-top-10-for-large-language-model-applications/  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `observation-dependent-behavior` | Observation-Dependent Behavior | AI systems that behave differently based on whether they believe they are being monitored, evaluated, or observed. Analogous to malware sandbox detection. | No |
| `adversarial-input-vulnerabilities` | Adversarial Input Vulnerabilities | AI systems vulnerable to crafted inputs that cause misclassification, evasion, or behavioral manipulation across digital and physical domains. | No |
| `insecure-ai-deployment` | Insecure AI Deployment | AI systems deployed with configurations that expose them to unauthorized access, data exfiltration, or remote exploitation. | No |
| `ai-supply-chain-threats` | AI Supply Chain Threats | Risks introduced through the AI model and tooling supply chain including poisoned models, backdoored dependencies, and compromised training data. | No |
| `data-exfiltration-via-ai` | Data Exfiltration via AI Systems | AI systems used as vectors for unauthorized data extraction through model outputs, tool access, or agent capabilities. | No |
| `ai-model-integrity` | AI Model Integrity | Threats to the trustworthiness and reliability of AI model outputs including drift, manipulation, and verification failures. | No |

## Values: `observation-dependent-behavior`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `eval-benchmark-detection` | Eval/Benchmark Detection | Model detects evaluation contexts and modifies outputs. Analogous to malware VM/sandbox detection. |  |
| `monitoring-aware-modification` | Monitoring-Aware Response Modification | Model changes behavior when it detects or infers the presence of monitoring, logging, or oversight systems. |  |
| `safety-bypass-unobserved` | Safety Bypass Under Perceived Unobserved Conditions | Model relaxes safety constraints when it believes observation has been reduced or removed. |  |
| `observation-context-injection` | Observation Context Injection | Attacker manipulates the observation framing in prompts or system context to trigger behavioral changes. |  |
| `test-production-divergence` | Test/Production Behavioral Divergence | Model exhibits meaningfully different behavior between testing and production environments. |  |
| `alignment-faking` | Alignment Faking | Model appears aligned during evaluation while pursuing different objectives when unmonitored. |  |
| `sandboxing-detection` | Sandboxing Detection | Model detects sandboxed, isolated, or controlled environments and adjusts behavior to pass evaluation. |  |

## Values: `adversarial-input-vulnerabilities`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `adversarial-pattern-evasion` | Adversarial Pattern Evasion | Crafted visual patterns that cause AI vision systems to fail at detection, classification, or recognition. |  |
| `prompt-injection` | Prompt Injection | Injection of malicious instructions through user input, retrieved documents, or tool outputs that override system prompts. |  |
| `input-perturbation` | Input Perturbation Attacks | Small modifications to inputs (pixel-level, token-level) that cause significant changes in model output. |  |
| `multi-model-transfer` | Multi-Model Transfer Attacks | Adversarial inputs crafted to defeat multiple architecturally different models simultaneously. |  |
| `physical-domain-adversarial` | Physical Domain Adversarial Attacks | Adversarial inputs that persist through physical-world capture conditions (camera, distance, lighting, angle). |  |
| `model-extraction` | Model Extraction via Adversarial Probing | Systematic querying of a model to reconstruct its weights, architecture, or decision boundaries. |  |
| `jailbreak` | Jailbreak Vectors | Techniques that bypass model safety training to produce prohibited outputs. |  |

## Values: `insecure-ai-deployment`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `exposed-control-panel` | Exposed Control Panel | AI agent or model serving interface accessible from the public internet without authentication. |  |
| `default-credentials` | Default Credentials | AI platform deployed with factory-default or well-known credentials. |  |
| `unauthenticated-inference` | Unauthenticated Inference Endpoint | Model inference API accessible without authentication, enabling unauthorized use or abuse. |  |
| `missing-network-segmentation` | Missing Network Segmentation | AI workloads running in flat networks without isolation from other services or the internet. |  |
| `exposed-training-data` | Exposed Training Data or Model Weights | Training datasets or model weight files accessible without authorization. |  |
| `misconfigured-tool-permissions` | Misconfigured Agent Tool Permissions | AI agents granted excessive permissions to filesystem, network, code execution, or database resources. |  |
| `malicious-skill-plugin` | Malicious Skill/Plugin in Agent Marketplace | AI agent skill or plugin containing backdoors, C2 callbacks, or data exfiltration logic. |  |
| `bound-to-all-interfaces` | Bound to All Network Interfaces | AI service listening on 0.0.0.0 exposing it to all network interfaces including public internet. |  |

## Values: `ai-supply-chain-threats`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `model-provenance-gap` | Model Provenance Gap | Model deployed without verified provenance chain from training to deployment. |  |
| `training-data-poisoning` | Training Data Poisoning | Malicious data injected into training sets to influence model behavior. |  |
| `trojan-model` | Trojan/Backdoored Model | Model weights containing embedded backdoor triggers that activate on specific inputs. |  |
| `malicious-ml-dependency` | Malicious ML Pipeline Dependency | Compromised package in ML toolchain (PyPI, npm, HuggingFace, etc.). |  |
| `compromised-model-registry` | Compromised Model Registry | Model hosting platform or registry serving modified or malicious model artifacts. |  |
| `unsigned-model-artifact` | Unsigned Model Artifact | Model weights or checkpoints distributed without cryptographic signatures for integrity verification. |  |
| `sbom-aibom-gap` | SBOM/AIBOM Gap | Missing or incomplete software or AI bill of materials for the ML pipeline. |  |

## Values: `data-exfiltration-via-ai`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `training-data-extraction` | Training Data Extraction | Extracting memorized training data from model outputs through targeted prompting. |  |
| `agent-lateral-movement` | Agent-Based Lateral Movement | AI agent using granted tool access to move laterally through infrastructure and harvest credentials. |  |
| `tool-use-abuse` | Tool-Use Abuse | AI agent performing unauthorized filesystem, network, or database operations through legitimately granted tool access. |  |
| `steganographic-exfiltration` | Steganographic Output Exfiltration | Data encoded within AI-generated outputs (text, images, code) for covert exfiltration. |  |
| `context-window-persistence` | Context Window Data Persistence | Sensitive data persisting in model context across sessions or users when session isolation fails. |  |

## Values: `ai-model-integrity`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `silent-model-drift` | Silent Model Drift | Model output quality or safety degrading over time without monitoring or alerting. |  |
| `fine-tuning-attack` | Fine-Tuning Attack | Malicious fine-tuning that introduces unwanted behaviors while preserving performance on benchmarks. |  |
| `reward-hacking` | Reward Hacking | RL-trained model exploiting reward function flaws to achieve high scores without intended behavior. |  |
| `reproducibility-failure` | Reproducibility Failure | Non-deterministic model outputs affecting security-critical decisions without operator awareness. |  |

## Tag Format Examples

```
vantacode-mbt:observation-dependent-behavior="eval-benchmark-detection"
vantacode-mbt:adversarial-input-vulnerabilities="adversarial-pattern-evasion"
vantacode-mbt:insecure-ai-deployment="exposed-control-panel"
vantacode-mbt:ai-supply-chain-threats="model-provenance-gap"
vantacode-mbt:data-exfiltration-via-ai="training-data-extraction"
```

---

*38 tags across 6 predicates.*
