# INC-002 — HTTP Firewall Rule Disabled

**Date:** 2026-11-22  
**Environment:** Google Cloud Compute Engine, two peered VPCs  
**Affected flow:** `10.10.10.10` → `10.20.20.10:8080`  
**Incident type:** Ingress firewall configuration  
**Status:** Configuration recovered and verified by API audit; end-to-end HTTP recovery not captured in the supplied reports

## Customer impact / scenario

The lab client needs to reach an internal HTTP service on TCP port `8080` in a different VPC. During a controlled test, the ingress firewall rule intended to permit that connection was disabled.

This is a **simulated fault** for troubleshooting practice. The available evidence confirms the configuration problem; it does not include an actual failed HTTP request or a measured customer outage.

## Architecture

```text
lab05-client-vpc                      lab05-server-vpc
10.10.10.0/24                         10.20.20.0/24

lab05-client-vm                       lab05-server-vm
10.10.10.10       <-- VPC Peering -->  10.20.20.10:8080

               Ingress allow rule on server VPC:
               lab05-allow-http
               Source: 10.10.10.0/24
               Target tag: lab05-server
               Protocol/port: TCP 8080
```

The Python tool `gcp_audit.py` ran in Cloud Shell and read configuration from the Compute Engine API.

## Detection

The API audit included seven lab-specific checks covering:

- VPC Peering in both directions
- Client and server VM network configuration
- Client and server IAP SSH rules
- The expected HTTP ingress firewall rule

At **19:38 UTC**, the blocked-state report recorded:

```text
PASS | Client-to-server peering ACTIVE
PASS | Server-to-client peering ACTIVE
PASS | Client VM network configuration
PASS | Server VM network configuration
PASS | Client IAP SSH rule
PASS | Server IAP SSH rule
FAIL | Client-to-server HTTP rule
```

The rule inventory showed:

```json
{
  "name": "lab05-allow-http",
  "disabled": true,
  "source_ranges": ["10.10.10.0/24"],
  "target_tags": ["lab05-server"],
  "allowed": [{"IPProtocol": "tcp", "ports": ["8080"]}]
}
```

## Investigation

The two peering checks were `PASS`, so the audit found both peering configurations active. Both VM network configuration checks also passed. The expected HTTP rule was present but **disabled**.

The audit script explicitly requires a matching ingress `ALLOW` rule to be enabled. Because `disabled` was `true`, the HTTP rule check returned `FAIL`.

The relevant configuration change can be inspected with:

```bash
gcloud compute firewall-rules describe lab05-allow-http \
  --format="yaml(disabled,sourceRanges,targetTags,allowed)"
```

## Confirmed configuration cause

The firewall rule `lab05-allow-http` was disabled. Therefore **this specific rule did not permit** new HTTP connections from the client subnet to the server VM.

This is a confirmed configuration defect. The audit is not a complete firewall-policy simulator, so it does not by itself prove that no other rule could have allowed the same traffic.

## Resolution

The HTTP rule was restored to the enabled state. The command for this change is:

```bash
gcloud compute firewall-rules update lab05-allow-http \
  --no-disabled
```

## Verification and observed outcome

| Audit report | Timestamp (UTC) | Passed | Failed | HTTP rule |
|---|---|---:|---:|---|
| `gcp-audit-blocked.json` | 2026-11-22 19:38 | 6 | 1 | Disabled |
| `gcp-audit-restored.json` | 2026-11-22 19:51 | 7 | 0 | Enabled |

The restored report shows that **all seven configuration checks passed**, including the expected HTTP ingress rule. The server VM and VPC Peering entries remained in the expected state.

**Evidence limit:** These reports are API configuration snapshots. They do not show an actual TCP connection or HTTP `200` response after the fix. For full end-to-end verification, run `netdiag.py` from `lab05-client-vm` or use `curl`:

```bash
curl --noproxy '*' --connect-timeout 5 \
  http://10.20.20.10:8080/
```

A successful HTTP response would strengthen the incident report.

## Report naming note

The file originally named `gcp-audit-healthy.json` was captured at **19:30 UTC**, but it also showed **6 PASS / 1 FAIL** and the HTTP rule disabled. It is **not a healthy baseline**. Do not describe it as one; either omit it from the published repository or rename it `gcp-audit-initial-failure.json`.

## Prevention and lessons learned

- Audit important ingress firewall rules, including their enabled state, source ranges, target tags and destination ports.
- Distinguish **configuration checks** from actual TCP/HTTP connectivity tests.
- Record evidence from both the failed and restored states.
- Use an automated audit to detect configuration drift, but confirm final recovery with an application-level test.

## Evidence references

- [`gcp-audit-blocked.json`](../reports/gcp-audit-blocked.json) — expected HTTP allow rule disabled; 6 PASS, 1 FAIL.
- [`gcp-audit-restored.json`](../reports/gcp-audit-restored.json) — HTTP allow rule enabled; 7 PASS, 0 FAIL.
- [`gcp_audit.py`](../scripts/gcp_audit.py) — read-only Google Cloud configuration audit.

## Customer-facing update (example)

> We found that the expected firewall rule for TCP port 8080 was disabled. After restoring it, our cloud configuration audit passed all seven checks. We still recommend a client-to-server HTTP test to confirm that the application is reachable end to end.
