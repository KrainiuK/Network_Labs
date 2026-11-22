# Lab 05 — Google Cloud Network Troubleshooting & Python Automation

## Overview

In this lab, I built a small private network environment in **Google Cloud** and developed two Python tools to help investigate network problems.

The environment has two separate VPC networks connected through **VPC Network Peering**. A Linux client is designed to access an HTTP service on a Linux server in the other VPC. Both VMs use private IP addresses, and administration is done through **Identity-Aware Proxy (IAP) SSH**.

My main goal was to understand how cloud routing, firewall rules, Linux networking, and Python automation work together. I also wanted to learn how to collect evidence when something goes wrong, rather than guess at the cause.

This is **version 1** of the project. It includes a Google Cloud configuration audit and two documented troubleshooting cases. More advanced incident testing is planned for later.

## Technologies Used

- **Google Cloud Compute Engine** — Linux virtual machines
- **Google Cloud VPC** — custom networks and subnets
- **VPC Network Peering** — private connectivity between VPCs
- **Google Cloud VPC firewall rules** — controlled ingress access
- **Identity-Aware Proxy (IAP)** — SSH access without public VM IP addresses
- **Debian Linux** — client and server operating systems
- **Python 3** — DNS, TCP, HTTP, routing, and cloud configuration diagnostics
- **Compute Engine REST API** — read-only cloud resource inventory
- **Cloud Shell and gcloud CLI** — cloud administration and testing

## Network Architecture

```text
                       GOOGLE CLOUD PROJECT

       lab05-client-vpc                  lab05-server-vpc
        10.10.10.0/24                     10.20.20.0/24
              |                                 |
       lab05-client-vm                    lab05-server-vm
        10.10.10.10                         10.20.20.10
         netdiag.py                       HTTP service :8080
              |                                 |
              +---------- VPC Peering ----------+

       Google Cloud firewall: TCP 8080 from client subnet
       Cloud Shell ---> IAP SSH (TCP 22) ---> both private VMs

       Cloud Shell: gcp_audit.py ---> Compute Engine REST API
```

### IP Addressing

| Resource | Network / Subnet | Address | Purpose |
| --- | --- | --- | --- |
| Client VPC | `lab05-client-vpc` | — | Separate client network |
| Client subnet | `lab05-client-subnet` | `10.10.10.0/24` | Client address range |
| Client VM | Client subnet | `10.10.10.10` | Run connectivity diagnostics |
| Server VPC | `lab05-server-vpc` | — | Separate application network |
| Server subnet | `lab05-server-subnet` | `10.20.20.0/24` | Server address range |
| Server VM | Server subnet | `10.20.20.10` | HTTP service on TCP `8080` |

Both VMs were deployed in **`us-central1-a`** without external IPv4 addresses. VPC Peering allows eligible subnet routes to be exchanged, but it does **not** automatically allow traffic through firewall rules.

### Firewall and Access Design

| Source | Destination | Protocol | Purpose |
| --- | --- | --- | --- |
| IAP range `35.235.240.0/20` | Client VM | TCP `22` | Private SSH administration |
| IAP range `35.235.240.0/20` | Server VM | TCP `22` | Private SSH administration |
| Client subnet `10.10.10.0/24` | Server VM | TCP `8080` | Internal HTTP access |

The SSH rules use VM network tags so that they apply to the intended instances. The HTTP rule is an ingress rule in the **server VPC**.

## Python Tools

### 1. Network Diagnostics — `netdiag.py`

File: [`scripts/netdiag.py`](scripts/netdiag.py)

This tool checks a destination from the Linux machine where it runs. It collects:

- Hostname resolution results using Python `socket`
- The Linux route selected for the destination using `ip route get`
- TCP connection status and connection time
- Optional HTTP response status and request time
- A timestamped JSON report

Example from the client VM, after transferring the script:

```bash
python3 netdiag.py 10.20.20.10 8080 --http --output healthy.json
```

This checks **guest-level connectivity**. A timeout is a symptom, not proof of a particular root cause. For example, it can result from firewall filtering, routing problems, or packet loss.

### 2. Google Cloud Configuration Audit — `gcp_audit.py`

File: [`scripts/gcp_audit.py`](scripts/gcp_audit.py)

This script runs in **Cloud Shell** and uses authenticated, read-only requests to the Compute Engine REST API. It checks seven expected properties of the lab:

1. Client-to-server VPC Peering is active.
2. Server-to-client VPC Peering is active.
3. The client VM matches the expected network configuration.
4. The server VM matches the expected network configuration.
5. The client IAP SSH allow rule matches the expected settings.
6. The server IAP SSH allow rule matches the expected settings.
7. The HTTP ingress allow rule matches the expected settings.

Install the Python dependencies in an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install google-auth requests
```

Run the audit from the repository folder in Cloud Shell:

```bash
python3 scripts/gcp_audit.py \
  --project YOUR_PROJECT_ID \
  --zone us-central1-a \
  --output reports/gcp-audit.json
```

The tool uses Google Cloud Application Default Credentials available in the running environment. It does not require storing a service account key in this repository.

**Scope:** This is a lab-specific **configuration audit**, not a complete reachability or security-policy simulator. It looks for particular matching allow rules and VM settings; it does not fully evaluate every firewall policy, rule priority, or Linux firewall. An audit `PASS` does not by itself prove that the HTTP application is working.

## Troubleshooting and Results

### INC-001 — IAP SSH Connection Failure

SSH through IAP initially failed with error `4003` (`failed to connect to backend`, port `22`). I checked VM state, the cloud connectivity diagnostics, firewall settings, and the server's serial boot output.

The server's IAP SSH firewall rule allowed `35.235.240.0/24` instead of Google's complete IAP TCP forwarding range, `35.235.240.0/20`. Later audit evidence shows both IAP rules configured with `/20` and passing the script's checks.

**Evidence limit:** The supplied logs do not show a successful interactive SSH connection after the correction. The incorrect CIDR was a confirmed configuration issue, but the available evidence does not prove it was the only cause of the original error.

Read the full report: [`INC-001 — IAP SSH`](incidents/INC-001-IAP-SSH.md).

### INC-002 — Disabled HTTP Firewall Rule

I tested whether my cloud audit could detect a disabled HTTP allow rule. The rule `lab05-allow-http` was present but disabled, so the audit failed its HTTP rule check. After the rule was enabled, all seven checks passed.

| Audit snapshot | Passed | Failed | HTTP firewall rule |
| --- | ---: | ---: | --- |
| [Blocked](reports/gcp-audit-blocked.json) | 6 | 1 | Disabled |
| [Restored](reports/gcp-audit-restored.json) | 7 | 0 | Enabled |

The reports also show both VPC Peering relationships as `ACTIVE` and both VMs with their expected private IP addresses.

**Evidence limit:** These JSON reports verify cloud **configuration**, not a successful HTTP response after the fix. An HTTP `200` result from the client would be a separate end-to-end verification.

Read the full report: [`INC-002 — HTTP Firewall`](incidents/INC-002-HTTP-Firewall.md).

## Lessons Learned

- Cloud VPC routing and firewall permission are separate parts of connectivity.
- A VM can be `RUNNING` while remote administration or an application connection still fails.
- IAP access depends on the correct source CIDR, destination port, target tags, and account permissions.
- A Google Cloud Connectivity Test describes the modeled network path; it does not prove that an SSH or HTTP service accepts connections.
- Linux diagnostic commands show the guest's view of networking, while Compute Engine APIs show configuration managed outside the VM.
- Structured JSON reports make it easier to compare a failed configuration with a restored one.

## Repository Structure

```text
05-GCP-Network-Troubleshooting/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── netdiag.py
│   └── gcp_audit.py
├── reports/
│   ├── gcp-audit-blocked.json
│   └── gcp-audit-restored.json
└── incidents/
    ├── INC-001-IAP-SSH.md
    └── INC-002-HTTP-Firewall.md
```

The infrastructure was built using Google Cloud CLI commands. This version does **not** yet include an automated deployment script or Terraform configuration, so cloning the repository does not recreate the cloud environment automatically.

## Future Improvements

- Add automated Python tests and more detailed error handling.
- Compare failed and restored JSON reports automatically.
- Add more realistic DNS, routing, application, and firewall incidents.
- Improve CIDR and firewall policy evaluation in the audit tool.
- Investigate TCP packet captures, HTTP load balancing, and Kubernetes networking.
- Add Terraform to make the lab infrastructure reproducible.

## Security and Cost Notes

- Neither VM needs a public IPv4 address for the private application flow.
- Keep access restricted to the required IAP and HTTP sources.
- Do not commit access tokens, private keys, service account credentials, or `.env` files.
- Google Cloud budget alerts are not hard spending limits. Stop or delete unused VMs and check remaining disks and other resources to avoid ongoing charges.
