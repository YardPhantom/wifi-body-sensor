"""
FastAPI Application and WebSocket Telemetry Server for Wi-Fi Radar
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.sensor_core import SensorCore

sensor_core = SensorCore(target_fps=20.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set event loop and start background acquisition
    loop = asyncio.get_running_loop()
    sensor_core.set_event_loop(loop)
    sensor_core.start()
    yield
    # Shutdown
    sensor_core.stop()

app = FastAPI(title="WiFi Body Sensor (Telus Wi-Fi Modem)", lifespan=lifespan)

# Static directory paths
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

class ConfigModel(BaseModel):
    sensitivity: float | None = None
    wall_absorption: float | None = None

@app.get("/")
async def get_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/api/status")
async def get_status():
    with sensor_core.lock:
        frame = dict(sensor_core.latest_frame)
    return JSONResponse(frame)

@app.post("/api/calibrate")
async def trigger_calibrate():
    sensor_core.trigger_calibration(duration_sec=4.0)
    return JSONResponse({"status": "calibrating", "duration_sec": 4.0})

@app.get("/api/config")
async def get_config():
    return JSONResponse({
        "sensitivity": sensor_core.dsp.sensitivity,
        "wall_absorption": sensor_core.dsp.wall_absorption,
        "is_calibrated": sensor_core.dsp.is_calibrated,
        "baseline_rssi_std": round(sensor_core.dsp.baseline_rssi_std, 3),
        "baseline_rtt_std": round(sensor_core.dsp.baseline_rtt_std, 3)
    })

@app.post("/api/config")
async def update_config(conf: ConfigModel):
    sensor_core.update_config(sensitivity=conf.sensitivity, wall_absorption=conf.wall_absorption)
    return JSONResponse({
        "status": "updated",
        "sensitivity": sensor_core.dsp.sensitivity,
        "wall_absorption": sensor_core.dsp.wall_absorption
    })

@app.websocket("/ws/radar")
async def websocket_radar_endpoint(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue(maxsize=10)
    sensor_core.add_subscriber(q)
    try:
        while True:
            # Wait for next telemetry frame from DSP
            frame = await q.get()
            await websocket.send_json(frame)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        sensor_core.remove_subscriber(q)

# Mount static files (css, js, assets)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
