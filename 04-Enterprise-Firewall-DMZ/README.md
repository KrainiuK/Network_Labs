# Lab 04 — Enterprise Firewall & DMZ

## Overview

In this lab, I built a small enterprise network using **OPNsense** as a stateful firewall. I separated the network into **IT**, **STAFF**, and **DMZ** zones, connected the firewall to a simulated ISP, and hosted an Apache web server in the DMZ.

The main goal was to understand how a firewall controls traffic between different networks: new connections are blocked unless a rule allows them, while return traffic for permitted connections is handled through connection tracking.

I also practiced source NAT, destination NAT (port forwarding), firewall logging, and troubleshooting connectivity problems.

## Technologies Used

- **EVE-NG 7.4** — network emulation
- **OPNsense 26.7** — stateful firewall, NAT, and logging
- **Cisco IOSv** — simulated ISP router
- **Debian Linux and Apache2** — DMZ web server
- **VPCS** — IT and STAFF test hosts
- **Fedora Linux, KVM/QEMU, and Firefox** — host environment and firewall management

## Network Topology

![Lab 04 network topology](04-Enterprise-Firewall-DMZ/screenshots/topology.png)

The OPNsense firewall has four interfaces. Each network has a separate subnet and uses OPNsense as its gateway. The **Management** cloud in EVE-NG connects the IT network to my Fedora host so I can access the OPNsense web interface.

### IP Addressing

| Device / Zone | Interface | IP Address | Purpose |
| --- | --- | --- | --- |
| ISP | Gi0/0 | `198.51.100.2/30` | Simulated external router |
| ISP | Loopback0 | `203.0.113.10/32` | Simulated external destination |
| OPNsense WAN | `vtnet1` | `198.51.100.1/30` | Connection to ISP |
| OPNsense LAN / IT | `vtnet0` | `192.168.10.1/24` | IT gateway and management |
| OPNsense STAFF | `vtnet2` | `192.168.20.1/24` | STAFF gateway |
| OPNsense DMZ | `vtnet3` | `192.168.50.1/24` | DMZ gateway |
| IT PC | eth0 | `192.168.10.10/24` | IT test client |
| STAFF PC | eth0 | `192.168.20.20/24` | STAFF test client |
| Debian web server | e0 | `192.168.50.10/24` | Apache HTTP server |
| Fedora management | `virbr1` | `192.168.10.2/24` | OPNsense web management |

The ISP network uses reserved documentation addresses and **does not provide real internet access**.

![OPNsense interface assignments](04-Enterprise-Firewall-DMZ/screenshots/InterfaceAssignments.png)

## Firewall Security Policy

I used OPNsense's **default-deny behavior** on the newly assigned STAFF and DMZ interfaces and added specific pass rules for required traffic.

| Source | Destination | Protocol / Service | Policy |
| --- | --- | --- | --- |
| IT | Other networks | IPv4 | Allowed by the default LAN rule |
| STAFF | IT | New connections without a matching pass rule | Blocked by default |
| STAFF | ISP loopback `203.0.113.10` | ICMP | Allowed |
| STAFF | DMZ web server `192.168.50.10` | TCP 80 | Allowed by a configured rule |
| DMZ | DMZ gateway `192.168.50.1` | ICMP | Allowed |
| DMZ server | Firewall `192.168.50.1` | DNS, TCP/UDP 53 | Allowed |
| DMZ | IT / STAFF | Unmatched new connections | Blocked by default |
| ISP `198.51.100.2` | DMZ web server | TCP 80 via WAN port forwarding | Allowed |

**Stateful filtering:** Once OPNsense permits a connection, matching return traffic can use the existing firewall state. A separate broad reverse-direction allow rule is not required.

![Configured firewall rules](04-Enterprise-Firewall-DMZ/screenshots/FirewallRules.png)

## NAT Configuration

### Source NAT (Outbound NAT)

I kept **Automatic Source NAT rule generation** enabled. OPNsense uses outbound NAT for traffic leaving through WAN, allowing internal clients to communicate with the simulated external network using the firewall's WAN address.

![Automatic Source NAT mode](04-Enterprise-Firewall-DMZ/screenshots/SrcNAT.png)

### Destination NAT (Port Forwarding)

I configured a WAN port forward to publish the Apache web server in the DMZ:

| Setting | Value |
| --- | --- |
| Incoming interface | WAN |
| Protocol | TCP |
| Allowed source | `198.51.100.2` |
| Original destination | `198.51.100.1:80` |
| Translated destination | `192.168.50.10:80` |
| Firewall rule | Allow ISP HTTP to DMZ |

The NAT rule changes the destination address, while the WAN firewall rule permits the matching connection. The source restriction means this test rule is intended for the simulated ISP, not the public internet.

![Destination NAT rule](04-Enterprise-Firewall-DMZ/screenshots/DestNAT.png)

## Verification and Testing

I tested permitted and denied traffic and checked the results in **Firewall → Log Files → Live View**.

| Test | Expected | Observed |
| --- | --- | --- |
| OPNsense WAN → ISP loopback (`203.0.113.10`) | Allow | Ping successful |
| STAFF → IT (`192.168.10.10`) | Block | Blocked by default deny |
| STAFF → ISP loopback (`203.0.113.10`) | Allow ICMP | Allowed by STAFF rule |
| DMZ server → IT (`192.168.10.10`) | Block | Blocked by default deny |
| DMZ server → STAFF (`192.168.20.20`) | Block | Blocked by default deny |
| DMZ server → DMZ gateway (`192.168.50.1`) | Allow ICMP | Allowed by DMZ gateway rule |
| DMZ server → firewall DNS (`192.168.50.1:53`) | Allow | Passed by DNS rule in logs |
| Fedora (IT) → Apache (`192.168.50.10:80`) | Allow | Website opened successfully |
| ISP → WAN (`198.51.100.1:80`) | Forward to DMZ | TCP connection opened; WAN and DMZ pass logs recorded |

**Note:** A STAFF-to-DMZ HTTP pass rule was configured, but an end-to-end HTTP request from a STAFF client was not separately verified. The ISP Telnet test confirms that TCP port 80 accepted a connection; it is not a complete HTTP application test.

### Blocked Traffic

The firewall logs show ICMP attempts from the DMZ server to IT and STAFF being blocked by the default deny rule.

![Blocked DMZ traffic](04-Enterprise-Firewall-DMZ/screenshots/DMZrestrictions.png)

They also show STAFF-to-IT traffic blocked while STAFF-to-ISP ICMP is allowed.

![STAFF traffic verification](04-Enterprise-Firewall-DMZ/screenshots/STAFFrestrictions.png)

### Allowed HTTP Traffic

From the ISP router, I tested the WAN HTTP port:

`ISP#telnet 198.51.100.1 80`

`Trying 198.51.100.1, 80 ... Open`

OPNsense recorded the permitted TCP connection from `198.51.100.2` to the translated destination `192.168.50.10:80`.

![ISP to DMZ HTTP connection logs](04-Enterprise-Firewall-DMZ/screenshots/ISP-DMZconnection.png)

From Fedora, I also opened Apache directly at `http://192.168.50.10`.

![Apache website accessed from Fedora](04-Enterprise-Firewall-DMZ/screenshots/HTTPweb.png)

## Troubleshooting

### 1. Fedora could reach OPNsense, but not the DMZ server

I connected Fedora to the IT network through an isolated KVM bridge and EVE-NG Management cloud. Fedora could reach the OPNsense LAN address, but initially could not open the DMZ website because it had no specific route to `192.168.50.0/24`.

I added a temporary route on Fedora:

`sudo ip route add 192.168.50.0/24 via 192.168.10.1 dev virbr1`

After this change, Fedora could reach the Apache website. This demonstrated that correct firewall rules are not enough when the client does not have a valid route.

### 2. Debian could not ping its DMZ gateway

The DMZ interface did not have a default allow rule. I checked OPNsense Live View and added a specific rule allowing ICMP from the DMZ network to its gateway. The ping then succeeded.

### 3. DNS queries from Debian were blocked

Live View showed DNS requests from `192.168.50.10` to `192.168.50.1:53` being blocked. I created a rule allowing DNS from the Debian server to the firewall and verified matching pass entries in the logs.

### 4. Testing external access to the DMZ server

The simulated ISP router did not have a web browser, so I used Cisco IOS Telnet to test TCP port 80. The connection opened, and OPNsense logs confirmed that destination NAT forwarded the traffic to the DMZ server.

## Key Takeaways

- Learned how to deploy and manage an OPNsense firewall in EVE-NG.
- Segmented a network into IT, STAFF, DMZ, and WAN security zones.
- Practiced **default deny** and service-specific firewall rules.
- Understood how **stateful connection tracking** handles permitted return traffic.
- Compared automatic **source NAT** with **destination NAT / port forwarding**.
- Used firewall logs to verify blocked and allowed traffic.
- Troubleshot firewall rules, DNS, and routing between virtual networks.

This lab helped me understand **why network segmentation matters** and how a stateful firewall controls communication between networks with different trust levels.

---
