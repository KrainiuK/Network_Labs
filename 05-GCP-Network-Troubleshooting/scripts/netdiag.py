import argparse
import json
import socket
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


#Function to resolve hostname into IP addresses
def resolve_hostname(host):
    try:
        results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in results})

        return {
                "status": "success",
                "addresses": addresses
                }
    except socket.gaierror as error:
        return {
                "status": "failed",
                "addresses": [],
                "error": str(error)
                }

#Function to determine which route Linux would use
def check_route(ip_address):
    family = "-6" if ":" in ip_address else "-4"

    result = subprocess.run( ["ip", family, "route", "get", ip_address], capture_output=True, text=True)

    return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": (result.stdout or result.stderr).strip()
            }

def check_http(host, port, timeout):
    
    url = f"http://{host}"+f":{port}"

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            elapsed = (time.perf_counter() - start) * 1000
            return {"status": "success",
                    "http_code": response.status,
                    "latency_ms": round(elapsed, 2)}
    except TimeoutError:
        return {"status": "Timeout"}
    except RemoteDisconnected:
        return {"status": "Connection is closed"}
    except ValueError:
        return {"status": "Failed",
                "message": "Not a valid URL"
                }

#Function to attempt tcp connection
def check_tcp(host, port, timeout):
    
    start = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout) as connection: 
            elapsed = (time.perf_counter() - start) * 1000

            return {
                    "status": "connected",
                    "peer_ip": connection.getpeername()[0],
                    "latency_ms": round(elapsed, 2)}
    except ConnectionRefusedError:
        return {"status": "connection refused"}
    except TimeoutError:
        return {"status": "timeout"}
    except OSError as error:
        return {
                "status": "error",
                "message": str(error)
                }

def main():
    parser = argparse.ArgumentParser(description="Python network diagnostic tool")

    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--output", help="Save JSON report")
    parser.add_argument("--http", action="store_true", help="Make a HTTP GET request")

    args = parser.parse_args()

    dns_result = resolve_hostname(args.host)

    if dns_result["addresses"]:
        route_result = check_route(dns_result["addresses"][0])
        tcp_result = check_tcp(args.host, args.port, args.timeout)
    else:
        route_result = {"status": "skipped"}
        tcp_result = {"status": "skipped"}

    if args.http and tcp_result["status"] == "connected":
        http_result = check_http(args.host, args.port, args.timeout)
    else:
        http_result = {"status": "skipped"}

    report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": args.host,
            "port": args.port,
            "dns": dns_result,
            "route": route_result,
            "tcp": tcp_result,
            "http": http_result
            }

    print(json.dumps(report, indent=2))

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report saved: {path}")

if __name__ == "__main__":
    main()
