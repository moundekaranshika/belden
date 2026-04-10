# #edge_gateway
# import asyncio
# import httpx
# import random
# from datetime import datetime

# # ===============================
# # CONFIGURATION
# # ===============================
# TOTAL_PORTS = 5
# SERVER_ENDPOINT = "http://localhost:8000/api/v1/edge-update"
# POLL_INTERVAL = 5  # seconds

# # Simulated counters
# port_error_counters = {i: 0 for i in range(1, TOTAL_PORTS + 1)}


# # ===============================
# # SIMULATION ENGINE
# # ===============================
# def simulate_port_errors(port_id):
#     global port_error_counters

#     increment = random.randint(0, 3)

#     # occasional spike
#     if random.random() < 0.1:
#         increment += random.randint(10, 25)

#     port_error_counters[port_id] += increment
#     return port_error_counters[port_id]


# # ===============================
# # EDGE ANALYTICS
# # ===============================
# def classify_port_status(errors):
#     if errors == 0:
#         return "Healthy"
#     elif errors < 50:
#         return "Warning"
#     else:
#         return "Critical"


# def calculate_health(total_errors):
#     score = 100
#     score -= total_errors * 0.5
#     return max(score, 0)


# def determine_rack_status(health):
#     if health < 40:
#         return "Critical"
#     elif health < 70:
#         return "Warning"
#     else:
#         return "Healthy"


# async def collect_telemetry():
#     ports = []
#     total_errors = 0

#     # 🔥 FORCE EDGE ONLINE
#     edge_online = True

#     for i in range(1, TOTAL_PORTS + 1):
#         errors = simulate_port_errors(i)
#         total_errors += errors

#         ports.append({
#             "id": i,
#             "errors": errors,
#             "status": classify_port_status(errors)
#         })

#     health_score = calculate_health(total_errors)
#     rack_status = determine_rack_status(health_score)

#     return ports, total_errors, edge_online, health_score, rack_status


# # ===============================
# # PUSH TO SERVER
# # ===============================
# async def send_to_server(payload):
#     async with httpx.AsyncClient(timeout=5.0) as client:
#         try:
#             response = await client.post(SERVER_ENDPOINT, json=payload)
#             if response.status_code == 200:
#                 print("📡 Telemetry pushed successfully.")
#             else:
#                 print("Server rejected payload:", response.status_code)
#         except Exception as e:
#             print("Failed to reach server:", e)


# # ===============================
# # MAIN LOOP
# # ===============================
# async def edge_loop():
#     print("🚀 Edge Gateway Started (Simulation Mode - ONLINE)...\n")

#     while True:
#         ports, total_errors, edge_online, health_score, rack_status = await collect_telemetry()

#         payload = {
#             "rack_id": "BELDEN-RACK-001",
#             "timestamp": datetime.utcnow().isoformat(),
#             "ports": ports,
#             "total_errors": total_errors,
#             "edge_status": True,   # 🔥 Always online
#             "health_score": round(health_score, 2),
#             "rack_status": rack_status
#         }

#         print("---- EDGE SNAPSHOT ----")
#         print(payload)
#         print("------------------------\n")

#         await send_to_server(payload)

#         await asyncio.sleep(POLL_INTERVAL)


# if __name__ == "__main__":
#     try:
#         asyncio.run(edge_loop())
#     except KeyboardInterrupt:
#         print("\n🛑 Edge Gateway stopped gracefully.")
alert_state = {
    "status": "normal",
    "message": ""
}


from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import uvicorn
import datetime
import json
import os
from influxdb_client import InfluxDBClient

# -----------------------------
# INFLUX CONFIG
# -----------------------------
url = "http://localhost:8086"
token = "vdc-1LbcjCTQw3RVSFTWiXtKLKMmwnj3_LgcC5D9Ruil3idcuNVFu3PLM5le8zDimELFJapNNbcbGx7U670YDg=="
org = "anshikamoundekar"
bucket = "cable_monitor"

influx_client = InfluxDBClient(url=url, token=token, org=org)
query_api = influx_client.query_api()

app = FastAPI()



# -----------------------------
# Data Model
# -----------------------------
class DeviceMetrics(BaseModel):
    device_id: str
    in_error_delta: int
    crc_error_delta: int
    poe_power_watts: float
    temperature_celsius: float


# -----------------------------
# Cable Health Engine
# -----------------------------
def calculate_health(crc_delta, in_err_delta, poe_power, temperature):
    score = 100
    score -= crc_delta * 3
    score -= in_err_delta * 2
    score -= poe_power * 0.3

    if temperature > 60:
        score -= (temperature - 60) * 2

    return max(score, 0)


# -----------------------------
# Logging
# -----------------------------
def log_data(payload):
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r+") as f:
        data = json.load(f)
        data.append(payload)
        f.seek(0)
        json.dump(data, f, indent=4)


# -----------------------------
# API to Receive Data
# -----------------------------
@app.post("/ingest")
def ingest_metrics(metrics: DeviceMetrics):

    health = calculate_health(
        metrics.crc_error_delta,
        metrics.in_error_delta,
        metrics.poe_power_watts,
        metrics.temperature_celsius
    )

    payload = {
        "device_id": metrics.device_id,
        "timestamp": str(datetime.datetime.now()),
        "metrics": metrics.dict(),
        "cable_health_score": round(health, 2)
    }

    if health < 70:
        payload["alert"] = "WARNING"
    if health < 50:
        payload["alert"] = "CRITICAL"

    log_data(payload)

    return {"status": "received"}


# -----------------------------
# Website Dashboard
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "cable_metrics")
        |> filter(fn: (r) => r["device"] == "switch_1")
        |> group(columns: ["_field"])
        |> last()
    '''


    result = query_api.query(org=org, query=query)

    data = {}

    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    if not data:
        return "<h2>No InfluxDB data found.</h2>"

    health = data.get("health_score", 0)

    status = "Healthy"
    color = "good"

    if health < 70:
        status = "Warning"
        color = "warn"
    if health < 50:
        status = "Critical"
        color = "critical"

    html_content = f"""
    <html>
    <head>
        <title>Belden Cable Health Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial; text-align: center; }}
            .card {{
                margin: 50px auto;
                padding: 20px;
                width: 400px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            .good {{ background-color: #d4edda; }}
            .warn {{ background-color: #fff3cd; }}
            .critical {{ background-color: #f8d7da; }}
        </style>
    </head>
    <body>
        <h1>Belden Cable Health Monitor (InfluxDB Backend)</h1>
        <div class="card {color}">
            <h2>Device: switch_1</h2>
            <p><strong>Health Score:</strong> {round(health,2)}</p>
            <p><strong>Temperature:</strong> {data.get('temperature')} °C</p>
            <p><strong>PoE Power:</strong> {data.get('poe_power')} W</p>
            <p><strong>CRC Errors:</strong> {data.get('crc_errors_delta')}</p>
            <p><strong>Input Errors:</strong> {data.get('in_errors_delta')}</p>
            <p><strong>Status:</strong> {status}</p>
        </div>
        <p>Auto-refresh every 5 seconds</p>
    </body>
    </html>
    """

    return html_content

@app.get("/api/history")
def get_history():

    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -10m)
      |> filter(fn: (r) => r._measurement == "cable_metrics")
    '''

    result = query_api.query(org=org, query=query)

    records = {}

    for table in result:
        for record in table.records:

            time = record.get_time().isoformat()
            field = record.get_field()
            value = record.get_value()

        # 🔥 ADD ALERT LOGIC HERE
            if field == "health_score":

                if value < 50:
                    alert_state["status"] = "critical"
                    alert_state["message"] = f"CRITICAL: Health dropped to {round(value,2)}"

                elif value < 70:
                    alert_state["status"] = "warning"
                    alert_state["message"] = f"WARNING: Health at {round(value,2)}"

                else:
                    alert_state["status"] = "normal"
                    alert_state["message"] = ""

        # existing record storing logic
            if time not in records:
                records[time] = {"time": time}

            records[time][field] = value


    return list(records.values())
@app.get("/api/alerts")
def get_alert():
    return alert_state


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("edge_gateway:app", host="127.0.0.1", port=8000, reload=True)
