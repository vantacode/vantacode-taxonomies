# vantacode-status

> Repository lifecycle status classification. Indicates the current maintenance and development status of a repository.

**Version:** 1  
**Exclusive:** Yes  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `lifecycle` | Lifecycle Status | Current lifecycle stage of the repository. | Yes |

## Values: `lifecycle`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `active` | Active Development | Repository is under active development with regular commits and maintenance. | `#2ecc71` |
| `maintenance` | Maintenance Only | Repository receives bug fixes and security patches but no new features. | `#3498db` |
| `experimental` | Experimental | Repository contains experimental or proof-of-concept code. Not production-ready. | `#f39c12` |
| `stale` | Stale | Repository has had no meaningful activity in 90+ days. May need triage. | `#e67e22` |
| `deprecated` | Deprecated | Repository has been superseded. A successor exists. Should not be used for new work. | `#e74c3c` |
| `archived` | Archived | Repository is read-only. Preserved for reference but no longer maintained. | `#7f8c8d` |

## Tag Format Examples

```
vantacode-status:lifecycle="active"
```

---

*6 tags across 1 predicates.*
