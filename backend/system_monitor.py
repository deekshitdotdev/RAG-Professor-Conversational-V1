"""
Reports CPU/RAM/GPU usage so the UI can show live resource bars, the same
way you'd watch Task Manager - useful for making sure nothing is overheating
or swapping to disk.
"""
import logging
import subprocess

import psutil

logger = logging.getLogger("system_monitor")


def get_cpu_ram() -> dict:
    vm = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_used_mb": round((vm.total - vm.available) / 1024 / 1024, 1),
        "ram_total_mb": round(vm.total / 1024 / 1024, 1),
        "ram_percent": vm.percent,
    }


def get_gpu_stats() -> dict:
    """Parses `nvidia-smi`. Returns a friendly 'unavailable' payload if the
    driver/tooling isn't found instead of crashing (e.g. CPU-only machine)."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode != 0:
            return {"available": False, "reason": result.stderr.strip()}

        line = result.stdout.strip().split("\n")[0]
        name, util, mem_used, mem_total, temp = [x.strip() for x in line.split(",")]
        return {
            "available": True,
            "name": name,
            "gpu_util_percent": float(util),
            "vram_used_mb": float(mem_used),
            "vram_total_mb": float(mem_total),
            "temperature_c": float(temp),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"available": False, "reason": str(e)}


def get_status() -> dict:
    return {"cpu_ram": get_cpu_ram(), "gpu": get_gpu_stats()}
