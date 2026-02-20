import os
import time
import multiprocessing
from fastapi import FastAPI, Query

app = FastAPI()

def cpu_burner(seconds):
    """The actual 'Heavy Lift' function"""
    end_time = time.time() + seconds
    while time.time() < end_time:
        # Perform heavy math to keep the CPU pinned at 100%
        _ = 12345 * 67890 

@app.get("/stress")
async def trigger_stress(
    seconds: int = Query(10, description="How long to stress"),
    intensity: int = Query(1, description="Number of CPU cores to max out")
):
    processes = []
    
    # Spawn 'intensity' number of processes to burn CPU
    for _ in range(intensity):
        p = multiprocessing.Process(target=cpu_burner, args=(seconds,))
        p.start()
        processes.append(p)

    return {
        "message": f"Load increased!",
        "duration": f"{seconds}s",
        "cores_attacked": intensity,
        "active_processes": len(processes)
    }

@app.get("/status")
def status():
    return {"service": "cpu-stress", "status": "online"}