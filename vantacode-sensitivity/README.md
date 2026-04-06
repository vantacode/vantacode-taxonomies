# vantacode-sensitivity

> Data sensitivity and classification markings for repositories. Determines handling requirements and access controls.

**Version:** 1  
**Exclusive:** Yes  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `classification` | Data Classification | Sensitivity level of the repository contents. | Yes |

## Values: `classification`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `public` | Public | Open source or publicly shareable. No access restrictions. | `#2ecc71` |
| `internal` | Internal | Available to org members. Not for public distribution. | `#3498db` |
| `confidential` | Confidential | Restricted to specific teams. Contains sensitive business or security data. | `#f39c12` |
| `restricted` | Restricted | Highest sensitivity. Contains exploit code, credentials, PII, or active operation data. Need-to-know access only. | `#e74c3c` |

## Tag Format Examples

```
vantacode-sensitivity:classification="public"
```

---

*4 tags across 1 predicates.*
