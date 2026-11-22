
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.auth.exceptions import GoogleAuthError
from requests.exceptions import RequestException


BASE_URL = "https://compute.googleapis.com/compute/v1"

LAB_VPCS = (
    "lab05-client-vpc",
    "lab05-server-vpc"
)


def api_list(session, project, resource_path):
    """Read all pages from a Google Cloud API list endpoint."""

    url = (
        f"{BASE_URL}/projects/"
        f"{quote(project, safe='')}/{resource_path}"
    )

    items = []
    page_token = None

    while True:
        params = {"pageToken": page_token} if page_token else None

        response = session.get(
            url,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        items.extend(data.get("items", []))

        page_token = data.get("nextPageToken")

        if not page_token:
            return items


def is_network(resource_url, network_name):
    """Check whether a resource URL points to a VPC."""
    return resource_url.endswith(f"/networks/{network_name}")


def peering_active(network, peer_name):
    """Check whether a VPC has active peering to another VPC."""

    return any(
        peer.get("state") == "ACTIVE"
        and is_network(peer.get("network", ""), peer_name)
        for peer in network.get("peerings", [])
    )


def vm_matches(vm, network_name, ip, tag):
    """Validate a VM's basic network configuration."""

    interfaces = vm.get("networkInterfaces", [])

    return (
        vm.get("status") == "RUNNING"
        and tag in vm.get("tags", {}).get("items", [])
        and any(
            is_network(nic.get("network", ""), network_name)
            and nic.get("networkIP") == ip
            and not nic.get("accessConfigs", [])
            for nic in interfaces
        )
    )


def firewall_matches(rules, network_name, source, target_tag, port):
    """Find an enabled ingress rule allowing specific TCP traffic."""

    return any(
        is_network(rule.get("network", ""), network_name)
        and rule.get("direction", "INGRESS") == "INGRESS"
        and not rule.get("disabled", False)
        and source in rule.get("sourceRanges", [])
        and target_tag in rule.get("targetTags", [])
        and any(
            item.get("IPProtocol") == "tcp"
            and str(port) in item.get("ports", [])
            for item in rule.get("allowed", [])
        )
        for rule in rules
    )


def main():
    parser = argparse.ArgumentParser(
        description="Read-only Google Cloud network audit"
    )

    parser.add_argument("--project", required=True)
    parser.add_argument("--zone", default="us-central1-a")
    parser.add_argument("--output", default="reports/gcp-audit.json")

    args = parser.parse_args()

    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        with AuthorizedSession(credentials) as session:
            networks = api_list(
                session, args.project, "global/networks"
            )

            firewalls = api_list(
                session, args.project, "global/firewalls"
            )

            instances = api_list(
                session, args.project,
                f"zones/{args.zone}/instances"
            )

    except (GoogleAuthError, RequestException, ValueError) as error:
        print(
            f"Cannot read Google Cloud configuration: {error}",
            file=sys.stderr
        )
        sys.exit(1)

    network_by_name = {n["name"]: n for n in networks}
    instance_by_name = {vm["name"]: vm for vm in instances}

    checks = []

    def check(name, passed):
        checks.append({
            "check": name,
            "result": "PASS" if passed else "FAIL"
        })

    client_net = network_by_name.get("lab05-client-vpc", {})
    server_net = network_by_name.get("lab05-server-vpc", {})

    check(
        "Client-to-server peering ACTIVE",
        peering_active(client_net, "lab05-server-vpc")
    )

    check(
        "Server-to-client peering ACTIVE",
        peering_active(server_net, "lab05-client-vpc")
    )

    check(
        "Client VM network configuration",
        vm_matches(
            instance_by_name.get("lab05-client-vm", {}),
            "lab05-client-vpc",
            "10.10.10.10",
            "lab05-client"
        )
    )

    check(
        "Server VM network configuration",
        vm_matches(
            instance_by_name.get("lab05-server-vm", {}),
            "lab05-server-vpc",
            "10.20.20.10",
            "lab05-server"
        )
    )

    check(
        "Client IAP SSH rule",
        firewall_matches(
            firewalls, "lab05-client-vpc",
            "35.235.240.0/20", "lab05-client", 22
        )
    )

    check(
        "Server IAP SSH rule",
        firewall_matches(
            firewalls, "lab05-server-vpc",
            "35.235.240.0/20", "lab05-server", 22
        )
    )

    check(
        "Client-to-server HTTP rule",
        firewall_matches(
            firewalls, "lab05-server-vpc",
            "10.10.10.0/24", "lab05-server", 8080
        )
    )

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": args.project,
        "checks": checks,
        "inventory": {
            "vpcs": [
                {
                    "name": net["name"],
                    "peerings": [
                        {
                            "name": p.get("name"),
                            "state": p.get("state")
                        }
                        for p in net.get("peerings", [])
                    ]
                }
                for net in networks
                if net.get("name") in LAB_VPCS
            ],
            "instances": [
                {
                    "name": vm["name"],
                    "status": vm.get("status"),
                    "internal_ips": [
                        nic.get("networkIP")
                        for nic in vm.get("networkInterfaces", [])
                    ],
                    "tags": vm.get("tags", {}).get("items", [])
                }
                for vm in instances
                if vm.get("name") in (
                    "lab05-client-vm", "lab05-server-vm"
                )
            ],
            "firewall_rules": [
                {
                    "name": rule["name"],
                    "disabled": rule.get("disabled", False),
                    "source_ranges": rule.get("sourceRanges", []),
                    "target_tags": rule.get("targetTags", []),
                    "allowed": rule.get("allowed", [])
                }
                for rule in firewalls
                if any(
                    is_network(rule.get("network", ""), name)
                    for name in LAB_VPCS
                )
            ]
        }
    }

    for result in checks:
        print(f"{result['result']:4} | {result['check']}")

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Report saved: {path}")


if __name__ == "__main__":
    main()
