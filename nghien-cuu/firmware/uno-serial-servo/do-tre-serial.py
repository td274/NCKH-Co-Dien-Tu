#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
do-tre-serial.py — đo trễ vòng (round-trip latency) Serial với firmware
"uno-serial-servo".

Cách dùng:
  # Đo thật (cần cắm board):
  D:\\Python312\\python.exe do-tre-serial.py --port COM5 --n 200

  # Tự dò cổng (ưu tiên CH340, bỏ qua cổng Bluetooth SPP):
  D:\\Python312\\python.exe do-tre-serial.py --n 200

  # Dry-run (KHÔNG cần board — chỉ kiểm tra script, số liệu là GIẢ LẬP):
  D:\\Python312\\python.exe do-tre-serial.py --dry-run --n 200

Lưu ý cổng: board clone thường là CH340. Trên Windows, COM6–COM15 thường là
Bluetooth Serial — script tự dò sẽ BỎ QUA chúng, và CẢNH BÁO nếu bạn chỉ định
nhầm bằng --port (giao tiếp sẽ timeout).

Nguyên lý đo: ghi lệnh "J,<t1>,<t2>,<t3>\\n" rồi đợi dòng "A,<micros>\\n".
Đo thời gian từ ngay-trước-khi-ghi tới khi đọc đủ dòng trả lời (perf_counter_ns).
Kết quả ghi CSV + histogram 300 dpi vào thư mục ket-qua/.
"""

import argparse
import csv
import random
import statistics
import sys
import time
from pathlib import Path

# Windows console mặc định dùng cp1252, in tiếng Việt sẽ lỗi UnicodeEncodeError.
# Ép stdout/stderr sang UTF-8 (hỗ trợ từ Python 3.7+).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Giới hạn góc (khớp với config.h) để sinh lệnh J hợp lệ.
JOINT_MIN = (-30.0, -30.0, -30.0)
JOINT_MAX = (+80.0, +80.0, +80.0)


# --------------------------------------------------------------------------- #
#  Transport (giao diện write/readline) — dùng chung cho đo thật và dry-run.
# --------------------------------------------------------------------------- #
class FakeSerial:
    """Mô phỏng board để kiểm tra script không lỗi (dry-run).

    readline() trả về "A,<micros>" với micros tăng dần và thêm một độ trễ giả lập
    ~1.5 ms (phân bố normal). Đây KHÔNG phải số đo phần cứng thật.
    """

    def __init__(self, mean_ms=1.5, sd_ms=0.35, seed=1234):
        self._rng = random.Random(seed)
        self._t0 = time.perf_counter_ns()
        self.mean_ms = mean_ms
        self.sd_ms = sd_ms

    def write(self, data: bytes) -> int:
        return len(data)

    def readline(self) -> bytes:
        lat_ms = max(0.1, self._rng.gauss(self.mean_ms, self.sd_ms))
        time.sleep(lat_ms / 1000.0)
        now_us = (time.perf_counter_ns() - self._t0) // 1000
        return b"A,%d\n" % now_us


class RealSerial:
    """Bọc pyserial: write + readline (đọc tới khi gặp '\\n' hoặc timeout)."""

    def __init__(self, port, baud, timeout=2.0):
        import serial  # import muộn để --dry-run không cần pyserial
        self._ser = serial.Serial(port, baud, timeout=timeout)
        self._ser.reset_input_buffer()

    def write(self, data: bytes) -> int:
        return self._ser.write(data)

    def readline(self) -> bytes:
        return self._ser.readline()

    def close(self):
        self._ser.close()


# --------------------------------------------------------------------------- #
#  Đo trễ
# --------------------------------------------------------------------------- #
def build_j_command(i, n):
    """Sinh lệnh J với góc xác định, quét trong giới hạn khớp."""
    frac = (i % 50) / 49.0          # chu kỳ quét đều
    t1 = JOINT_MIN[0] + (JOINT_MAX[0] - JOINT_MIN[0]) * frac
    t2 = JOINT_MIN[1] + (JOINT_MAX[1] - JOINT_MIN[1]) * ((i * 3) % 50) / 49.0
    t3 = JOINT_MIN[2] + (JOINT_MAX[2] - JOINT_MIN[2]) * ((i * 7) % 50) / 49.0
    return f"J,{t1:.1f},{t2:.1f},{t3:.1f}\n".encode("ascii")


def run_measurement(transport, n):
    """Gửi n lệnh J, đo trễ tới khi nhận 'A,<micros>'. Trả (lat_ms, micros)."""
    lat_ms, micros = [], []
    missed = 0
    for i in range(n):
        cmd = build_j_command(i, n)
        t0 = time.perf_counter_ns()
        transport.write(cmd)
        line = transport.readline()
        t1 = time.perf_counter_ns()

        if not line:
            missed += 1
            continue
        try:
            text = line.decode("ascii", errors="replace").strip()
            tag, val = text.split(",", 1)
            if tag.upper() != "A":
                missed += 1
                continue
            micros.append(int(val))
            lat_ms.append((t1 - t0) / 1e6)
        except (ValueError, UnicodeDecodeError):
            missed += 1
    return lat_ms, micros, missed


def write_report(outdir: Path, lat_ms, micros, missed, n, dry_run):
    """Ghi CSV, thống kê và histogram."""
    outdir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    tag = "dryrun" if dry_run else "real"
    csv_path = outdir / f"latency-{tag}-{ts}.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "latency_ms", "arduino_micros"])
        for idx, (ms, us) in enumerate(zip(lat_ms, micros)):
            w.writerow([idx, f"{ms:.6f}", us])

    if not lat_ms:
        print("[WARN] Không có mẫu hợp lệ nào.")
        return csv_path

    s = sorted(lat_ms)
    def pct(p):
        k = max(0, min(len(s) - 1, int(round(p / 100.0 * (len(s) - 1)))))
        return s[k]

    stats = {
        "n_valid": len(s),
        "n_missed": missed,
        "mean_ms": statistics.fmean(s),
        "median_ms": statistics.median(s),
        "p95_ms": pct(95),
        "p99_ms": pct(99),
        "max_ms": max(s),
        "min_ms": min(s),
        "std_ms": statistics.pstdev(s),
    }

    print("=" * 60)
    print(("DRY-RUN (số liệu GIẢ LẬP — không phải phần cứng thật)"
           if dry_run else "KẾT QUẢ ĐO THẬT"))
    print("=" * 60)
    print(f"  lệnh gửi       : {n}")
    print(f"  mẫu hợp lệ     : {stats['n_valid']}")
    print(f"  mẫu lỗi/missed : {stats['n_missed']}")
    print(f"  trung bình     : {stats['mean_ms']:.3f} ms")
    print(f"  trung vị       : {stats['median_ms']:.3f} ms")
    print(f"  P95            : {stats['p95_ms']:.3f} ms")
    print(f"  P99            : {stats['p99_ms']:.3f} ms")
    print(f"  max            : {stats['max_ms']:.3f} ms")
    print(f"  min            : {stats['min_ms']:.3f} ms")
    print(f"  std (pop)      : {stats['std_ms']:.3f} ms")
    print(f"  CSV            : {csv_path}")
    print("=" * 60)

    # Histogram 300 dpi.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
        ax.hist(s, bins=min(50, max(10, len(s) // 10)), color="#1f77b4",
                edgecolor="white")
        ax.axvline(stats["mean_ms"], color="red", ls="--", lw=1,
                   label=f"mean={stats['mean_ms']:.2f} ms")
        ax.axvline(stats["p95_ms"], color="orange", ls=":", lw=1,
                   label=f"P95={stats['p95_ms']:.2f} ms")
        ax.set_xlabel("round-trip latency (ms)")
        ax.set_ylabel("count")
        ax.set_title(("DRY-RUN (mô phỏng)" if dry_run else "Serial round-trip")
                     + f" — N={len(s)}")
        ax.legend()
        fig.tight_layout()
        png_path = outdir / f"histogram-{tag}-{ts}.png"
        fig.savefig(png_path, dpi=300)
        plt.close(fig)
        print(f"  histogram      : {png_path}")
    except ImportError as e:
        print(f"[WARN] không vẽ histogram (thiếu matplotlib): {e}")

    return csv_path


# --------------------------------------------------------------------------- #
#  Nhận diện cổng serial
# --------------------------------------------------------------------------- #
# Board clone Arduino UNO phổ biến dùng chip CH340. Trên Windows, cổng Bluetooth
# SPP (VD: COM6–COM15 do driver Bluetooth tạo) hiển thị description kiểu
# "Standard Serial over Bluetooth link" — mở nhầm cổng này sẽ không giao tiếp
# được với board (không có Arduino ở đầu kia).
_BT_HINTS = ("bluetooth", "serial over bluetooth")


def _port_description(p) -> str:
    parts = [p.device or ""]
    parts.append(getattr(p, "description", "") or "")
    parts.append(getattr(p, "hwid", "") or "")
    return " ".join(parts)


def looks_like_bluetooth(text: str) -> bool:
    """Trả True nếu mô tả cổng có dấu hiệu Bluetooth SPP (không phải board)."""
    t = text.lower()
    return any(h in t for h in _BT_HINTS)


def _list_ports_summary():
    """Chuỗi liệt kê cổng hiện có + đánh dấu cổng Bluetooth, để in khi lỗi."""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return "  (không có cổng nào)"
    lines = []
    for p in ports:
        desc = _port_description(p)
        mark = " [Bluetooth — KHÔNG phải board!]" if looks_like_bluetooth(desc) else ""
        lines.append(f"  {p.device}: {desc}{mark}")
    return "\n".join(lines)


def warn_if_bluetooth(port: str) -> None:
    """Cảnh báo ra stderr nếu người dùng chọn cổng có dấu hiệu Bluetooth."""
    import serial.tools.list_ports
    for p in serial.tools.list_ports.comports():
        if p.device.upper() == port.upper():
            if looks_like_bluetooth(_port_description(p)):
                print(
                    f"[WARN] Cổng {port} có vẻ là Bluetooth Serial "
                    f"({getattr(p, 'description', '')}). Đây KHÔNG phải board "
                    "Arduino — giao tiếp sẽ timeout. Kiểm tra lại cổng thật.",
                    file=sys.stderr,
                )
            return


def detect_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    # 1) Ưu tiên CH340 (board clone phổ biến).
    for p in ports:
        if "CH340" in _port_description(p).upper():
            return p.device
    # 2) Cổng không phải Bluetooth (loại COM Bluetooth SPP).
    candidates = [p.device for p in ports
                  if not looks_like_bluetooth(_port_description(p))]
    if candidates:
        return candidates[0]
    # 3) Chỉ còn cổng Bluetooth -> không tự chọn, để người dùng dùng --port.
    return None


def main():
    ap = argparse.ArgumentParser(description="Đo trễ vòng Serial uno-serial-servo")
    ap.add_argument("--port", default=None, help="cổng serial, VD: COM5")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--n", type=int, default=200, help="số lệnh J (mặc định 200)")
    ap.add_argument("--outdir", default="ket-qua")
    ap.add_argument("--dry-run", action="store_true",
                    help="chạy giả lập board (không cần phần cứng)")
    args = ap.parse_args()

    outdir = Path(__file__).resolve().parent / args.outdir

    if args.dry_run:
        print("[DRY-RUN] Mô phỏng board nội bộ — kết quả KHÔNG phải số đo thật.")
        transport = FakeSerial()
    else:
        port = args.port or detect_port()
        if not port:
            print("[ERROR] Không tìm thấy cổng serial hợp lệ. Các cổng hiện có:",
                  file=sys.stderr)
            print(_list_ports_summary(), file=sys.stderr)
            print("[ERROR] Nếu chỉ thấy cổng Bluetooth thì board chưa cắm / chưa "
                  "cài driver CH340. Cắm board rồi thử lại, hoặc dùng "
                  "--port COM5.", file=sys.stderr)
            sys.exit(1)
        warn_if_bluetooth(port)
        print(f"[REAL] Kết nối {port} @ {args.baud} ...")
        transport = RealSerial(port, args.baud)

    lat_ms, micros, missed = run_measurement(transport, args.n)
    if not args.dry_run:
        transport.close()
    write_report(outdir, lat_ms, micros, missed, args.n, args.dry_run)


if __name__ == "__main__":
    main()
