# Network Engineering Labs

Welcome to my Network Engineering Lab Portfolio!

I am a student who recently passed the **Cisco Certified Network Associate (CCNA)** exam and is currently developing practical skills to prepare for a career in Network Engineering, Network Security, and Cloud Networking.

This repository documents my hands-on projects involving routing, switching, network security, Linux, cloud infrastructure, Python automation, and troubleshooting.

My goal is to understand not only how to configure networks, but also how they operate, why problems occur, and how to investigate and resolve them.

## Objectives

- Apply CCNA knowledge in practical networking environments.
- Develop Cisco IOS configuration and troubleshooting skills.
- Build and document realistic enterprise network scenarios.
- Gain hands-on experience with network security and firewalls.
- Strengthen my Linux and network virtualization skills.
- Learn Google Cloud networking concepts and infrastructure.
- Develop Python scripts for network diagnostics and automation.
- Practice systematic troubleshooting and technical documentation.
- Prepare for junior Network Engineering, Network Security, and Cloud Networking roles.

## Lab Environment

I use both a local virtualization environment and Google Cloud for my projects.

| Component | Technology |
| --- | --- |
| Host operating system | Fedora Linux |
| Virtualization | KVM/QEMU |
| Network emulator | EVE-NG 7.4 |
| Router operating system | Cisco IOSv 15.9(3)M6 |
| Switch operating system | Cisco IOSvL2 |
| Firewall | OPNsense 26.7 |
| Linux servers | Debian Linux, Apache2 |
| Cloud platform | Google Cloud Platform (GCP) |
| Cloud networking | VPC, subnets, VPC Network Peering, firewall rules |
| Cloud compute | Google Compute Engine |
| Secure cloud access | Identity-Aware Proxy (IAP) |
| Programming | Python 3 |
| Cloud automation | Google Cloud REST APIs, Google Cloud CLI |
| Version control | Git and GitHub |
| Documentation | Markdown, JSON reports |

## Projects

| Lab | Topic | Description | Status |
| --- | --- | --- | --- |
| 01 | [Static Routing](01-Static-Routing/) | Connect two office networks using static routes and practice basic troubleshooting. | Completed |
| 02 | [VLANs, OSPF and Failover](02-VLANS-OSPF-FAILOVER/) | Configure VLANs, inter-VLAN routing, OSPF, and test automatic route failover. | Completed |
| 03 | [Enterprise NAT, ACLs and Failover](03-Enterprise-NAT-ACL/) | Configure PAT, extended ACLs, simulated ISP connectivity, OSPF default routing, and failover testing. | Completed |
| 04 | [Enterprise Firewall & DMZ](04-Enterprise-Firewall-DMZ/) | Deploy OPNsense, configure security zones and stateful firewall rules, implement NAT and DMZ port forwarding, and verify network isolation. | Completed |
| 05 | [Google Cloud Network Troubleshooting & Python Automation](05-GCP-Network-Troubleshooting/) | Build private Google Cloud networks with VPC Peering and IAP, develop Python network diagnostic and cloud configuration audit tools, and investigate firewall connectivity issues. | Version 1 |

Additional networking and automation projects will be added as I continue developing my skills.

## Skills Practiced

### Routing and Switching

- IPv4 addressing and subnetting
- Static and dynamic routing (OSPF)
- VLAN configuration and 802.1Q trunking
- Inter-VLAN routing using Router-on-a-Stick
- OSPF neighbor verification and route analysis
- Default route advertisement through OSPF
- Network redundancy and failover testing
- Cisco IOS CLI configuration and troubleshooting

### Network Security

- NAT/PAT configuration and translation verification
- Extended ACLs for traffic filtering between VLANs
- OPNsense firewall installation and configuration
- Network segmentation using IT, STAFF, and DMZ security zones
- Stateful firewall rules and default-deny policies
- Source NAT and destination NAT (port forwarding)
- Firewall logging and security verification
- Firewall troubleshooting and connectivity testing

### Cloud Networking

- Google Cloud VPC and subnet configuration
- Private connectivity using VPC Network Peering
- Google Compute Engine Linux virtual machines
- Google Cloud VPC firewall rules and network tags
- Secure SSH access using Identity-Aware Proxy (IAP)
- Google Cloud CLI and Cloud Shell
- Cloud networking configuration audits
- Troubleshooting cloud firewall and connectivity issues

### Python and Network Automation

- Python scripting for network diagnostics
- DNS resolution and TCP connection testing using Python sockets
- HTTP connectivity testing and response analysis
- Linux routing information collection
- Error handling and connection timeout analysis
- JSON-based diagnostic reports
- Google Cloud REST API integration
- Automated inspection of VPCs, virtual machines, firewall rules, and peering status
- Configuration validation and troubleshooting automation

### Linux and Infrastructure

- Fedora and Debian Linux administration
- Linux networking commands and troubleshooting
- Linux server configuration and Apache web hosting
- KVM/QEMU virtualization
- EVE-NG network emulation
- Git version control and GitHub
- Technical documentation and incident reports

## Troubleshooting Approach

I use a structured approach when working on network problems:

1. **Identify the problem** — Understand what is failing and which systems are affected.
2. **Collect information** — Examine network configuration, routing tables, firewall rules, and application connectivity.
3. **Investigate the cause** — Use CLI commands, Python scripts, and diagnostic tools to narrow down the issue.
4. **Apply a solution** — Correct the configuration or service responsible for the problem.
5. **Verify the result** — Repeat the tests to confirm that the expected configuration or connectivity has been restored.
6. **Document the findings** — Record the issue, evidence, solution, and lessons learned.

In Lab 05, I started developing Python tools to automate parts of this process and generate structured diagnostic reports.

## About This Portfolio

Each lab documents a network scenario, implementation steps, verification methods, and troubleshooting observations.

The projects started with basic Cisco routing and gradually expanded into enterprise networking, firewall security, Linux infrastructure, and Google Cloud networking.

I am also developing my Python skills to automate repetitive diagnostic tasks and better understand how network engineers can use APIs and programming in their daily work.

**The goal is not only to make networks work, but to understand why they work, how to identify problems, and how to resolve them.**

This repository is an ongoing learning portfolio. I will continue improving existing projects and adding more advanced networking, cloud, security, and automation labs as I gain experience.
