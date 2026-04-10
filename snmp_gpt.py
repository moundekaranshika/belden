# import asyncio
# import random
# from datetime import datetime
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS

# # -----------------------------
# # INFLUX CONFIG
# # -----------------------------
# url = "http://localhost:8086"
# token = "vdc-1LbcjCTQw3RVSFTWiXtKLKMmwnj3_LgcC5D9Ruil3idcuNVFu3PLM5le8zDimELFJapNNbcbGx7U670YDg=="
# org = "anshikamoundekar"
# bucket = "cable_monitor"

# client = InfluxDBClient(url=url, token=token, org=org)
# write_api = client.write_api(write_options=SYNCHRONOUS)

# POLL_INTERVAL = 5

# in_errors = 0
# crc_errors = 0
# temperature = 40
# poe_power = 5


# def simulate_network_conditions():
#     global in_errors, crc_errors, temperature, poe_power

#     in_errors += random.randint(0, 3)
#     crc_errors += random.randint(0, 2)

#     temperature += random.randint(-1, 2)
#     temperature = max(35, min(80, temperature))

#     poe_power = random.randint(3, 15)

#     return in_errors, crc_errors, poe_power, temperature


# def calculate_health(crc_delta, in_err_delta, poe_power, temperature):
#     score = 100
#     score -= crc_delta * 3
#     score -= in_err_delta * 2
#     score -= poe_power * 0.3

#     if temperature > 60:
#         score -= (temperature - 60) * 2

#     return max(score, 0)


# async def monitor():
#     print("Starting InfluxDB Cable Monitoring...\n")

#     prev_in, prev_crc, _, _ = simulate_network_conditions()

#     while True:
#         await asyncio.sleep(POLL_INTERVAL)

#         in_err, crc_err, poe, temp = simulate_network_conditions()

#         in_delta = in_err - prev_in
#         crc_delta = crc_err - prev_crc

#         health = calculate_health(crc_delta, in_delta, poe, temp)

#         print(f"Health: {health}")

#         # -----------------------------
#         # WRITE TO INFLUX
#         # -----------------------------
#         point = (
#             Point("cable_metrics")
#             .tag("device", "switch_1")
#             .field("in_errors_delta", in_delta)
#             .field("crc_errors_delta", crc_delta)
#             .field("poe_power", poe)
#             .field("temperature", temp)
#             .field("health_score", health)
#             .time(datetime.utcnow(), WritePrecision.NS)
#         )

#         write_api.write(bucket=bucket, org=org, record=point)

#         prev_in = in_err
#         prev_crc = crc_err


# if __name__ == "__main__":
#     asyncio.run(monitor())

import asyncio
import random
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# -----------------------------
# INFLUX CONFIG
# -----------------------------
url = "http://localhost:8086"
token = "vdc-1LbcjCTQw3RVSFTWiXtKLKMmwnj3_LgcC5D9Ruil3idcuNVFu3PLM5le8zDimELFJapNNbcbGx7U670YDg=="
org = "anshikamoundekar"
bucket = "cable_monitor"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

POLL_INTERVAL = 5

# -----------------------------
# Simulated Metrics
# -----------------------------
in_errors = 0
crc_errors = 0
temperature = 40
poe_power = 5


def simulate_network_conditions():
    global in_errors, crc_errors, temperature, poe_power

    in_errors += random.randint(0, 3)
    crc_errors += random.randint(0, 2)

    temperature += random.randint(-1, 2)
    temperature = max(35, min(80, temperature))

    poe_power = random.randint(3, 15)

    return in_errors, crc_errors, poe_power, temperature


def calculate_health(crc_delta, in_err_delta, poe_power, temperature):
    score = 100
    score -= crc_delta * 3
    score -= in_err_delta * 2
    score -= poe_power * 0.3

    if temperature > 60:
        score -= (temperature - 60) * 2

    return max(score, 0)


async def monitor():
    print("🚀 Starting InfluxDB Cable Monitoring...\n")

    prev_in, prev_crc, _, _ = simulate_network_conditions()

    while True:
        await asyncio.sleep(POLL_INTERVAL)

        in_err, crc_err, poe, temp = simulate_network_conditions()

        in_delta = in_err - prev_in
        crc_delta = crc_err - prev_crc

        health = calculate_health(crc_delta, in_delta, poe, temp)

        print(f"Health Score: {round(health,2)}")

        # -----------------------------
        # WRITE TO INFLUXDB
        # -----------------------------
        point = (
            Point("cable_metrics")
            .tag("device", "switch_1")
            .field("in_errors_delta", float(in_delta))
            .field("crc_errors_delta", float(crc_delta))
            .field("poe_power", float(poe))
            .field("temperature", float(temp))
            .field("health_score", float(health))
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )

        write_api.write(bucket=bucket, org=org, record=point)

        prev_in = in_err
        prev_crc = crc_err


if __name__ == "__main__":
    asyncio.run(monitor())
