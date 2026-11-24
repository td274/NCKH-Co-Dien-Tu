# -*- coding: utf-8 -*-
"""Chan doan toc do: so sanh thoi gian 1 lan mo phong khi bat/tat luong tu hoa encoder."""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_v2", str(HERE / "run.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cfg = json.load(open(HERE / "config.json", encoding="utf-8"))
wp = np.array([cfg["waypoints_mm"]["home"], cfg["waypoints_mm"]["pick"],
               cfg["waypoints_mm"]["place"], cfg["waypoints_mm"]["home"]], float)
T = 0.30
for quant in (True, False):
    c = json.loads(json.dumps(cfg))
    c["joint_model"]["quantize_feedback"] = quant
    t0 = time.perf_counter()
    r = mod.run_configuration(c, wp, T, 0.25, True, f"q={quant}")
    dt = time.perf_counter() - t0
    print(f"quantize={quant}: {dt:.2f} s, rmse={r['metrics']['rmse_err_mm']:.4f} mm, "
          f"tau={r['metrics']['tau_max_Nm']:.3f}, omega={r['metrics']['omega_max_rad_s']:.3f}")
