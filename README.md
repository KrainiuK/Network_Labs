# Network Engineering Labs

Welcome to my Network Engineering Lab Portfolio!

I am a student who recently passed the **Cisco Certified Network Associate (CCNA)** exam and is currently developing practical networking skills to prepare for a career as a Network Engineer.

This repository documents my hands-on networking projects, including network configuration, routing, switching, network security, troubleshooting, and infrastructure fundamentals.

## Objectives

- Apply CCNA knowledge in practical networking environments.
- Develop Cisco IOS configuration and troubleshooting skills.
- Build and document realistic network scenarios.
- Strengthen my understanding of Linux and network virtualization.
- Gain practical experience with network security and firewalls.
- Prepare for Network Engineer and Junior Network Security Engineer positions.

## Lab Environment

My networking lab runs on the following infrastructure:

| Component | Technology |
| --- | --- |
| Host operating system | Fedora Linux |
| Virtualization | KVM/QEMU |
| Network emulator | EVE-NG 7.4 |
| Router operating system | Cisco IOSv 15.9(3)M6 |
| Switch operating system | Cisco IOSvL2 |
| Firewall | OPNsense 26.7 |
| Linux server | Debian Linux with Apache2 |
| Network devices | Virtual routers, switches, firewalls, servers, and hosts |
| Documentation | Markdown |
| Version control | Git and GitHub |

## Projects

| Lab | Topic | Description | Status |
| --- | --- | --- | --- |
| 01 | [Static Routing](01-Static-Routing/) | Connect two office networks using static routes and practice basic troubleshooting | Completed |
| 02 | [VLANs, OSPF and Failover](02-VLANS-OSPF-FAILOVER/) | Configure VLANs, inter-VLAN routing, OSPF, and test automatic route failover | Completed |
| 03 | [Enterprise NAT, ACLs and Failover](03-Enterprise-NAT-ACL/) | Configure PAT, extended ACLs, simulated ISP connectivity, OSPF default routing, and failover testing | Completed |
| 04 | [Enterprise Firewall & DMZ](04-Enterprise-Firewall-DMZ/) | Deploy OPNsense, configure security zones and stateful firewall rules, implement NAT and DMZ port forwarding, and verify network isolation | Completed |

Additional networking labs will be added as I continue developing my skills.

## Skills Practiced

- IPv4 addressing and subnetting
- Static and dynamic routing (OSPF)
- VLAN configuration and 802.1Q trunking
- Inter-VLAN routing using Router-on-a-Stick
- OSPF neighbor verification and route analysis
- Default route advertisement through OSPF
- NAT/PAT configuration and translation verification
- Extended ACLs for traffic filtering between VLANs
- OPNsense firewall installation and configuration
- Network segmentation using IT, STAFF, and DMZ security zones
- Stateful firewall rules and default-deny policies
- Source NAT and destination NAT (port forwarding)
- Firewall logging, connection tracking, and security verification
- Linux server configuration and Apache web hosting
- Network redundancy and failover testing
- Network connectivity verification and troubleshooting
- Cisco IOS CLI
- Linux and virtualization (Fedora, Debian, KVM/QEMU, EVE-NG)
- Technical documentation and Git version control

## About This Portfolio

Each lab documents a network scenario, implementation steps, verification methods, and troubleshooting observations.

The goal is not only to make networks work, but to understand **why they work, how to identify problems, and how to resolve them**.

This repository will continue to grow as I gain more practical networking experience.
