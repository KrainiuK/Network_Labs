# INC-001 — IAP SSH Connection Failure

**Date:** 2026-11-22  
**Environment:** Google Cloud Compute Engine, `us-central1-a`  
**Affected resources:** `lab05-server-vm` and `lab05-client-vm`  
**Incident type:** Administration / SSH connectivity  
**Status:** Firewall configuration corrected in later audit; successful SSH login not independently captured in the supplied evidence

## Customer impact

SSH access through Identity-Aware Proxy (IAP) failed for the private lab VMs. This prevented remote administration through the normal connection method. The VMs had no external IPv4 addresses, so direct public-IP SSH was not an option.

## Architecture

- Client VM: `10.10.10.10` in `lab05-client-vpc`
- Server VM: `10.20.20.10` in `lab05-server-vpc`
- Both VMs: private IP addresses, with SSH intended through IAP
- Required IAP TCP forwarding source range: `35.235.240.0/20`
- SSH destination: TCP port `22`

## Symptoms

Connecting from Cloud Shell through IAP failed:

```bash
gcloud compute ssh lab05-server-vm \
  --zone=us-central1-a \
  --tunnel-through-iap
```

The reported error included:

```text
Error 4003: failed to connect to backend
Failed to connect to port 22
```

The same `4003` / port `22` error was also observed when connecting to `lab05-client-vm`.

## Investigation and evidence

| Check | Observed result | Interpretation |
|---|---|---|
| VM information | Server VM `RUNNING`; internal IP `10.20.20.10`; tag `lab05-server` | VM and expected network identity existed |
| Connectivity Test through SSH troubleshooter | Forward path: `REACHABLE`; return path: `REACHABLE` | The simulated Google Cloud network path appeared reachable; this does not establish an SSH session |
| IAM troubleshooting | `0 issue(s) found` | No permission issue was identified by this diagnostic |
| VM serial output | `Started ssh.service - OpenBSD Secure Shell server` | The SSH daemon started during boot; this does not prove it stayed available |
| Server IAP firewall rule | `tcp:22`, target tag `lab05-server`, enabled | Basic port and target settings matched |
| Server IAP source range | `35.235.240.0/24` | Too narrow for the complete IAP TCP forwarding range |

Relevant commands:

```bash
gcloud compute instances describe lab05-server-vm \
  --zone=us-central1-a \
  --format="yaml(status,tags,networkInterfaces)"

gcloud compute firewall-rules describe server-iap-ssh \
  --format="yaml(sourceRanges,targetTags,allowed,disabled)"

gcloud compute ssh lab05-server-vm \
  --zone=us-central1-a \
  --tunnel-through-iap --troubleshoot
```

**Important observation:** The troubleshooter used an example source address of `35.235.240.123`, which falls inside the incorrectly configured `/24`. This helps explain why the simulated test could report `REACHABLE` despite an incomplete IAP source allowance.

## Root cause assessment

A **confirmed configuration defect** was found: the server SSH firewall rule permitted `35.235.240.0/24`, not the documented full IAP TCP forwarding range `35.235.240.0/20`.

The smaller CIDR excludes some valid IAP source addresses and can cause IAP backend connection failures. The logs do **not** identify the actual IAP source IP used for the failed session, so the supplied evidence does not conclusively establish that this was the only cause of error `4003`.

## Remediation

The intended remediation is to correct the existing SSH firewall rule rather than open SSH to the entire internet:

```bash
gcloud compute firewall-rules update server-iap-ssh \
  --source-ranges=35.235.240.0/20
```

The later Google Cloud audit report confirms that both the client and server IAP SSH rules were enabled and used `35.235.240.0/20`.

## Verification and current outcome

The later configuration audit recorded **PASS** for both IAP SSH firewall checks. This verifies that the expected rules were present according to the audit script's criteria.

A successful interactive SSH login **was not included in the supplied evidence**, so final end-to-end SSH recovery remains unverified in this report.

**Recommended final verification:** Connect through IAP to both VMs and record the successful login and `hostname` output.

## Prevention and lessons learned

- Validate firewall **source CIDR**, destination port, and target tags together.
- Use the full documented `35.235.240.0/20` range for IAP TCP forwarding, not `/24`.
- Treat Connectivity Tests as **configuration-path analysis**, not proof that a guest service is accepting connections.
- Keep a simple cloud configuration audit to catch expected-rule mismatches.
- Avoid replacing restricted IAP access with public SSH simply to bypass troubleshooting.

## Evidence references

- Cloud Shell IAP error output, troubleshooting output, and VM serial log (captured during the lab; add sanitized screenshots or logs if available).
- [`gcp-audit-restored.json`](../reports/gcp-audit-restored.json) — later audit showing the corrected IAP SSH source ranges.

## Customer-facing update (example)

> We identified an SSH firewall rule that allowed only part of the required IAP source IP range. The configuration was corrected, and the cloud configuration audit now passes. A final interactive SSH test is needed to confirm that remote access has been fully restored.
