# Lab 01 — Static Routing Between Two Office Networks

## 1. Overview

This lab demonstrates how to establish communication between two separate networks using static routing on Cisco IOS routers.

The environment was built in **EVE-NG**, running as a virtual machine on Fedora Linux using KVM/QEMU.

The scenario simulates two company offices connected through a point-to-point WAN link.

**Objective:** Enable devices in Office A (`192.168.10.0/24`) to communicate with devices in Office B (`192.168.20.0/24`).

## 2. Technologies Used

- EVE-NG 7.4
- Cisco IOSv 15.9(3)M6
- Cisco IOS CLI
- VPCS virtual hosts
- IPv4 addressing and subnetting
- Static routing

## 3. Network Topology

![EVE-NG static routing topology](screenshots/topology.png)

The topology consists of two Cisco routers and two virtual PCs:

```text
       Office A                       Office B
   192.168.10.0/24                192.168.20.0/24

   PC1 -------- R1 -------------- R2 -------- PC2
                Gi0/0          Gi0/0
                   10.0.12.0/30
```

R1 and R2 are connected through the `10.0.12.0/30` network. Each router acts as the default gateway for its local office network.

## 4. IP Addressing Plan

| Device | Interface | IP Address | Description |
|---|---|---|---|
| R1 | Gi0/0 | 10.0.12.1/30 | WAN connection to R2 |
| R1 | Gi0/1 | 192.168.10.1/24 | Office A gateway |
| R2 | Gi0/0 | 10.0.12.2/30 | WAN connection to R1 |
| R2 | Gi0/1 | 192.168.20.1/24 | Office B gateway |
| PC1 | Ethernet | 192.168.10.2/24 | Office A host |
| PC2 | Ethernet | 192.168.20.2/24 | Office B host |

PC1 uses `192.168.10.1` as its default gateway, while PC2 uses `192.168.20.1`.


## 5. Verification

The following Cisco IOS commands were used to inspect the network:

```cisco
show ip interface brief
show ip route
show running-config
```

### WAN Connectivity

Connectivity was tested between R1 and R2:

From R1:

```cisco
ping 10.0.12.2
```

From R2:

```cisco
ping 10.0.12.1
```

### End-to-End Connectivity

Connectivity was tested from PC1 to PC2:

```text
ping 192.168.20.10
```

**Result:** End-to-end communication between the two office networks was successfully established.

## 6. Troubleshooting Exercise

To simulate a routing issue, the static route on R1 was temporarily removed:

```cisco
configure terminal
no ip route 192.168.20.0 255.255.255.0 10.0.12.2
end
```

This removed R1's route to the Office B network.

The routing table was then inspected using:

```cisco
show ip route
```

The missing route was identified and restored:

```cisco
configure terminal
ip route 192.168.20.0 255.255.255.0 10.0.12.2
end
```

Connectivity was tested again to verify that communication had been restored.

**Troubleshooting takeaway:** A functioning physical or virtual connection does not guarantee end-to-end IP communication. Routers must have valid routes to the destination networks, including a return path.

## 7. Key Takeaways

This lab helped reinforce several networking concepts:

1. Routers use their routing tables to determine where packets should be forwarded.
2. Static routes must be configured manually to reach remote networks.
3. Bidirectional communication requires appropriate routing in both directions.
4. Default gateways allow hosts to communicate beyond their local subnets.
5. Troubleshooting should involve examining interface status, routing tables, and connectivity tests rather than guessing.
