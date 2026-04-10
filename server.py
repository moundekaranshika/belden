# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import asyncio
# import random
# from pysnmp.hlapi.asyncio import *

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Constants from your proposal (Page 2 & 10)
# CARBON_PER_METER = 0.74  # kg CO2/m
# DOWNTIME_COST_PER_HOUR = 260000 

# async def fetch_port_errors(port_index):
#     # OIDs follow a sequence: .14.1, .14.2, .14.3...
#     oid = f'1.3.6.1.2.1.2.2.1.14.{port_index}'
#     try:
#         errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
#             SnmpEngine(),
#             CommunityData('public', mpModel=0),
#             UdpTransportTarget(('127.0.0.1', 161)),
#             ContextData(),
#             ObjectType(ObjectIdentity(oid))
#         )
#         if varBinds:
#             return int(varBinds[0][1])
#     except Exception:
#         return 0
#     return 0

# # Change this line in server.py
# @app.get("/api/v1/dashboard") 
# async def get_dashboard_data():
#     # ... keep the rest of your multi-port logic here ...
#     ports = []
#     total_errors = 0
    
#     # Step A: Multi-Port Monitoring (Scanning 5 ports)
#     for i in range(1, 6):
#         errs = await fetch_port_errors(i)
#         total_errors += errs
#         status = "Healthy" if errs == 0 else "Warning" if errs < 20 else "Critical"
#         ports.append({"id": i, "errors": errs, "status": status})

#     # Step B: Sustainability & Environmental Fusion
#     # We calculate 'Energy Waste' based on the error rate (proxy for signal resistance/heat)
#     energy_waste_kwh = (total_errors * 0.015) + random.uniform(0.05, 0.1)
    
#     # Step C: The 'No-Brainer' ROI Calculation (Page 9)
#     # Estimated downtime prevented (minutes) based on predictive warnings
#     minutes_saved = 1 if any(p["status"] == "Warning" for p in ports) else 0
#     money_saved = (minutes_saved / 60) * DOWNTIME_COST_PER_HOUR

#     return {
#         "rack_id": "BELDEN-RACK-001",
#         "ports": ports,
#         "sustainability": {
#             "carbon_footprint_kg": round(CARBON_PER_METER * 100, 2),
#             "energy_waste_kwh": round(energy_waste_kwh, 4),
#             "scope_3_status": "Compliant" if energy_waste_kwh < 0.5 else "Audit Required"
#         },
#         "insights": {
#             "roi_saved_usd": round(money_saved, 2),
#             "ai_recommendation": "Replace Port 3 Cable soon" if any(p["errors"] > 10 for p in ports) else "System Optimal"
#         }
#     }
# latest_edge_data = {}

# @app.post("/api/v1/edge-update")
# async def receive_edge_data(payload: dict):
#     global latest_edge_data
#     latest_edge_data = payload
#     return {"status": "received"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

#server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CARBON_PER_METER = 0.74
DOWNTIME_COST_PER_HOUR = 260000

# Store latest edge data
latest_edge_data = {}


# ===============================
# DASHBOARD API (Frontend Uses This)
# ===============================
@app.get("/api/v1/dashboard")
async def get_dashboard_data():

    # If no edge data yet
    if not latest_edge_data:
        return {
            "rack_id": "BELDEN-RACK-001",
            "edge_status": False,
            "ports": [],
            "health_score": 0,
            "rack_status": "Offline",
            "sustainability": {},
            "insights": {}
        }

    ports = latest_edge_data.get("ports", [])
    total_errors = latest_edge_data.get("total_errors", 0)
    edge_status = latest_edge_data.get("edge_status", False)
    health_score = latest_edge_data.get("health_score", 0)
    rack_status = latest_edge_data.get("rack_status", "Offline")

    # Sustainability logic
    energy_waste_kwh = (total_errors * 0.015) + random.uniform(0.05, 0.1)
    minutes_saved = 1 if any(p["status"] == "Warning" for p in ports) else 0
    money_saved = (minutes_saved / 60) * DOWNTIME_COST_PER_HOUR

    return {
        "rack_id": latest_edge_data.get("rack_id", "BELDEN-RACK-001"),
        "edge_status": edge_status,
        "ports": ports,
        "health_score": health_score,
        "rack_status": rack_status,
        "sustainability": {
            "carbon_footprint_kg": round(CARBON_PER_METER * 100, 2),
            "energy_waste_kwh": round(energy_waste_kwh, 4),
            "scope_3_status": "Compliant" if energy_waste_kwh < 0.5 else "Audit Required"
        },
        "insights": {
            "roi_saved_usd": round(money_saved, 2),
            "ai_recommendation": "Replace Cable Soon" if rack_status != "Healthy" else "System Optimal"
        }
    }


# ===============================
# EDGE UPDATE API (Edge Pushes Here)
# ===============================
@app.post("/api/v1/edge-update")
async def receive_edge_data(payload: dict):
    global latest_edge_data
    latest_edge_data = payload
    print("📥 Edge data received:", payload)
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
