# vantacode-sector

> Mapping of repositories to CISA PPD-21 critical infrastructure sectors and emerging sectors relevant to cybersecurity research.

**Version:** 1  
**Exclusive:** No  
**References:** https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors, https://github.com/vantacode/vantacode-taxonomies  

## Predicates

| Predicate | Expanded | Description | Exclusive |
|-----------|----------|-------------|-----------|
| `critical-infrastructure` | Critical Infrastructure Sector | CISA PPD-21 designated critical infrastructure sectors. | No |
| `emerging` | Emerging Sector | Sectors not in PPD-21 but increasingly relevant to cybersecurity. | No |

## Values: `critical-infrastructure`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `chemical` | Chemical Sector | Manufacturing, storing, and transporting chemical substances. SRMA: DHS. |  |
| `commercial-facilities` | Commercial Facilities Sector | Sites drawing large crowds for shopping, business, entertainment, or lodging. SRMA: DHS. |  |
| `communications` | Communications Sector | Infrastructure for telecommunications, broadcasting, cable, and internet services. SRMA: DHS. |  |
| `critical-manufacturing` | Critical Manufacturing Sector | Production of essential materials and goods like metals, machinery, and vehicles. SRMA: DHS. |  |
| `dams` | Dams Sector | Dam projects, navigation locks, levees, hurricane barriers, mine tailings, and water retention systems. SRMA: DHS. |  |
| `defense-industrial-base` | Defense Industrial Base Sector | Research, development, production, delivery, and maintenance of military weapons systems and components. SRMA: DOD. |  |
| `emergency-services` | Emergency Services Sector | Resources providing response services during and after incidents. SRMA: DHS. |  |
| `energy` | Energy Sector | Electricity, oil, and natural gas infrastructure. SRMA: DOE. |  |
| `financial-services` | Financial Services Sector | Banks, credit unions, insurance, securities, and investment institutions. SRMA: Treasury. |  |
| `food-agriculture` | Food + Agriculture Sector | Farms, restaurants, and food manufacturing, processing, and storage. SRMA: USDA/HHS. |  |
| `government-facilities` | Government Facilities Sector | Buildings, grounds, and infrastructure owned by federal, state, local, tribal, or territorial governments. SRMA: DHS/GSA. |  |
| `healthcare-public-health` | Healthcare + Public Health Sector | Public and private healthcare providers, health insurance, medical equipment, and public health systems. SRMA: HHS. |  |
| `information-technology` | Information Technology Sector | Hardware, software, IT systems, and services including internet infrastructure. SRMA: DHS. |  |
| `nuclear` | Nuclear Reactors, Materials, and Waste Sector | Nuclear power plants, research and test reactors, fuel cycle facilities, radioactive waste. SRMA: DHS. |  |
| `transportation-systems` | Transportation Systems Sector | Aviation, highway, maritime, mass transit, pipeline, freight rail, and postal shipping. SRMA: DHS/DOT. |  |
| `water-wastewater` | Water + Wastewater Systems Sector | Drinking water and wastewater treatment and distribution systems. SRMA: EPA. |  |

## Values: `emerging`

| Value | Expanded | Description | Colour |
|-------|----------|-------------|--------|
| `education` | Education | K-12 and higher education institutions. Increasingly targeted by ransomware and data theft. |  |
| `space-systems` | Space Systems | Satellite infrastructure, ground stations, and space-based communications. Covered by SPD-5. |  |
| `cryptocurrency-defi` | Cryptocurrency + DeFi | Cryptocurrency exchanges, DeFi protocols, blockchain infrastructure, and digital asset custody. |  |
| `ai-systems` | AI Systems + Infrastructure | AI model hosting, training infrastructure, agent platforms, and ML pipelines as critical infrastructure. |  |

## Tag Format Examples

```
vantacode-sector:critical-infrastructure="chemical"
vantacode-sector:emerging="education"
```

---

*20 tags across 2 predicates.*
