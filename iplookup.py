import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

def banner():
    print(f"""{CYAN}{BOLD}
========================================
         TERMUX IP LOOKUP TOOL
========================================
{RESET}""")

def info(msg):
    print(f"{CYAN}[INFO]{RESET} {msg}")

def ok(msg):
    print(f"{GREEN}[OK]{RESET} {msg}")

def warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")

def err(msg):
    print(f"{RED}[ERROR]{RESET} {msg}")

def fetch_json(url):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*"
    })
    with urlopen(req, timeout=15) as r:
        raw = r.read().decode("utf-8", errors="replace")
        return json.loads(raw)

def get_public_ip():
    req = Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8").strip()

def normalize_data(source, data, ip):
    if source == "ipwho.is":
        if not data.get("success", False):
            return None
        return {
            "ip": data.get("ip", ip),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone", {}).get("id") if isinstance(data.get("timezone"), dict) else data.get("timezone"),
            "continent": data.get("continent"),
            "org": data.get("connection", {}).get("isp") if isinstance(data.get("connection"), dict) else None,
            "asn": data.get("connection", {}).get("asn") if isinstance(data.get("connection"), dict) else None,
        }

    if source == "ip-api":
        if data.get("status") != "success":
            return None
        return {
            "ip": data.get("query", ip),
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone"),
            "org": data.get("isp"),
            "asn": data.get("as"),
        }

    if source == "geojs":
        return {
            "ip": data.get("ip", ip),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "org": data.get("organization_name"),
            "asn": data.get("organization"),
        }

    if source == "ipapi.co":
        if data.get("error"):
            return None
        return {
            "ip": data.get("ip", ip),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "country_code": data.get("country_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "org": data.get("org"),
            "asn": data.get("asn"),
        }

    return data

def lookup_ip(ip):
    services = [
        ("ipwho.is", f"https://ipwho.is/{ip}"),
        ("geojs", f"https://get.geojs.io/v1/ip/geo/{ip}.json"),
        ("ip-api", f"http://ip-api.com/json/{ip}"),
        ("ipapi.co", f"https://ipapi.co/{ip}/json/"),
    ]

    for name, url in services:
        try:
            info(f"Trying {name} ...")
            data = fetch_json(url)
            normalized = normalize_data(name, data, ip)
            if normalized:
                return name, normalized
            warn(f"{name} returned no usable data.")
        except HTTPError as e:
            warn(f"{name} failed: HTTP {e.code}")
        except URLError as e:
            warn(f"{name} failed: {e.reason}")
        except Exception as e:
            warn(f"{name} failed: {e}")

    return None, None

def show_result(source, data):
    print(f"\n{GREEN}{BOLD}Lookup successful via {source}{RESET}")
    print(f"{BLUE}{'-'*40}{RESET}")

    order = [
        "ip", "city", "region", "country", "country_code",
        "latitude", "longitude", "timezone", "continent",
        "org", "asn"
    ]

    shown = set()
    for key in order:
        value = data.get(key)
        if value not in (None, "", [], {}):
            print(f"{WHITE}{key:<14}{RESET}: {value}")
            shown.add(key)

    for key, value in data.items():
        if key not in shown and value not in (None, "", [], {}):
            print(f"{WHITE}{key:<14}{RESET}: {value}")

    print(f"{BLUE}{'-'*40}{RESET}")

def menu():
    print("1. Lookup a target IP")
    print("2. Show my public IP + geolocation")
    print("3. Show my public IP only")
    print("4. Exit")

def main():
    while True:
        banner()
        menu()
        choice = input(f"{CYAN}Choose [1-4]: {RESET}").strip()

        if choice == "1":
            ip = input(f"{CYAN}Enter target IP: {RESET}").strip()
            if not ip:
                err("No IP entered.")
                input(f"\n{YELLOW}Press Enter to continue...{RESET}")
                continue

            source, data = lookup_ip(ip)
            if data:
                show_result(source, data)
            else:
                err("Could not fetch geolocation details.")

            input(f"\n{YELLOW}Press Enter to continue...{RESET}")

        elif choice == "2":
            try:
                info("Getting your public IP ...")
                public_ip = get_public_ip()
                ok(f"Your public IP: {public_ip}")

                source, data = lookup_ip(public_ip)
                if data:
                    show_result(source, data)
                else:
                    err("Could not fetch geolocation details.")
            except Exception as e:
                err(f"Failed to get public IP: {e}")

            input(f"\n{YELLOW}Press Enter to continue...{RESET}")

        elif choice == "3":
            try:
                info("Getting your public IP ...")
                public_ip = get_public_ip()
                ok(f"Your public IP: {public_ip}")
            except Exception as e:
                err(f"Failed to get public IP: {e}")

            input(f"\n{YELLOW}Press Enter to continue...{RESET}")

        elif choice == "4":
            ok("Goodbye.")
            sys.exit(0)

        else:
            err("Invalid choice.")
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")

if __name__ == "__main__":
    main()
