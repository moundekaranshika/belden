# test_snmp.py
import asyncio
import httpx
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd
)

# ===============================
# CONFIGURATION
# ===============================
SNMP_TARGET = ('127.0.0.1', 161)
COMMUNITY = 'public'
TOTAL_PORTS = 5
SERVER_ENDPOINT = "http://localhost:8000/api/v1/edge-update"
POLL_INTERVAL = 5  # seconds


# ===============================
# SNMP FETCH FUNCTION
# ===============================
async def fetch_port_errors(port_index):
    oid = f'1.3.6.1.2.1.2.2.1.14.{port_index}'

    try:
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(COMMUNITY, mpModel=0),
            UdpTransportTarget(SNMP_TARGET),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            print(f"SNMP Error: {errorIndication}")
            return None

        if errorStatus:
            print(f"SNMP Status Error: {errorStatus.prettyPrint()}")
            return None

        if varBinds:
            return int(varBinds[0][1])

    except Exception as e:
        print("SNMP Exception:", e)

    return None


# ===============================
# EDGE ANALYTICS
# ===============================
def classify_port_status(errors):
    if errors == 0:
        return "Healthy"
    elif errors < 20:
        return "Warning"
    else:
        return "Critical"


def calculate_health(total_errors):
    """
    Rack-level health score (0–100)
    Penalizes based on cumulative errors
    """
    score = 100
    score -= total_errors * 2
    return max(score, 0)


def determine_rack_status(health):
    if health < 40:
        return "Critical"
    elif health < 70:
        return "Warning"
    else:
        return "Healthy"


async def collect_telemetry():
    ports = []
    total_errors = 0
    edge_online = True

    for i in range(1, TOTAL_PORTS + 1):
        errors = await fetch_port_errors(i)

        if errors is None:
            edge_online = False
            errors = 0

        total_errors += errors

        ports.append({
            "id": i,
            "errors": errors,
            "status": classify_port_status(errors)
        })

    # Rack-level analytics
    health_score = calculate_health(total_errors)
    rack_status = determine_rack_status(health_score)

    return ports, total_errors, edge_online, health_score, rack_status


# ===============================
# PUSH TO CLOUD SERVER
# ===============================
async def send_to_server(payload):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(SERVER_ENDPOINT, json=payload)
            if response.status_code == 200:
                print("📡 Telemetry pushed successfully.")
            else:
                print("Server rejected payload:", response.status_code)
        except Exception as e:
            print("Failed to reach server:", e)


# ===============================
# MAIN EDGE LOOP
# ===============================
async def edge_loop():
    print("🚀 Edge Gateway Started...")
    print("Monitoring Virtual Hirschmann Switch...\n")

    while True:
        ports, total_errors, edge_online, health_score, rack_status = await collect_telemetry()

        payload = {
            "rack_id": "BELDEN-RACK-001",
            "ports": ports,
            "total_errors": total_errors,
            "edge_status": edge_online,
            "health_score": health_score,
            "rack_status": rack_status
        }

        print("---- EDGE SNAPSHOT ----")
        print(payload)
        print("------------------------\n")

        await send_to_server(payload)

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(edge_loop())
