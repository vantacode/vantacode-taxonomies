# vantacode-governance

> Governance baseline compliance scoring for repositories. Measures adherence to VantaCode repository standards across multiple governance areas.

**Version:** 1  
**Exclusive:** No  
**References:** https://github.com/vantacode/vantacode-taxonomies  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `documentation` | Documentation | Presence and quality of README, CONTRIBUTING, SECURITY, LICENSE, CODEOWNERS, and other standard documentation. | Yes |
| `branch-protection` | Branch Protection | Branch protection rules, review requirements, and merge policies. | Yes |
| `ci-cd` | CI/CD | Continuous integration and deployment pipeline configuration and enforcement. | Yes |
| `security` | Security Posture | Dependabot, secret scanning, push protection, SAST, SBOM generation. | Yes |
| `code-quality` | Code Quality | Linting, formatting, testing, type checking, and code hygiene. | Yes |

## Values: `documentation`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `full` | Full Compliance | All required documentation present and current. | `#2ecc71` |
| `partial` | Partial Compliance | Some required documentation missing or outdated. | `#f39c12` |
| `minimal` | Minimal Compliance | Only basic documentation present (README only). | `#e67e22` |
| `none` | Non-Compliant | No standard documentation present. | `#e74c3c` |

## Values: `branch-protection`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `full` | Full Compliance |  | `#2ecc71` |
| `partial` | Partial Compliance |  | `#f39c12` |
| `minimal` | Minimal Compliance |  | `#e67e22` |
| `none` | Non-Compliant |  | `#e74c3c` |

## Values: `ci-cd`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `full` | Full Compliance |  | `#2ecc71` |
| `partial` | Partial Compliance |  | `#f39c12` |
| `minimal` | Minimal Compliance |  | `#e67e22` |
| `none` | Non-Compliant |  | `#e74c3c` |

## Values: `security`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `full` | Full Compliance |  | `#2ecc71` |
| `partial` | Partial Compliance |  | `#f39c12` |
| `minimal` | Minimal Compliance |  | `#e67e22` |
| `none` | Non-Compliant |  | `#e74c3c` |

## Values: `code-quality`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `full` | Full Compliance |  | `#2ecc71` |
| `partial` | Partial Compliance |  | `#f39c12` |
| `minimal` | Minimal Compliance |  | `#e67e22` |
| `none` | Non-Compliant |  | `#e74c3c` |

## Tag Format Examples

```
vantacode-governance:documentation="full"
vantacode-governance:branch-protection="full"
vantacode-governance:ci-cd="full"
vantacode-governance:security="full"
vantacode-governance:code-quality="full"
```

---

*20 tags across 5 predicates.*
