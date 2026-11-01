import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

BASE_URL = "http://127.0.0.1:8000"
TOTAL = 500
WORKERS = 20
SEVERITIES = ["info", "warning", "error", "critical"]


def main():
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        service_id = client.get("/services").json()[0]["id"]

        def send(i):
            body = {
                "service_id": service_id,
                "title": f"load test {i}",
                "severity": random.choice(SEVERITIES),
                "source": "load_test",
            }
            start = time.perf_counter()
            response = client.post("/alerts", json=body)
            return response.status_code, (time.perf_counter() - start) * 1000

        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = list(pool.map(send, range(TOTAL)))
        elapsed = time.perf_counter() - started

    latencies = [ms for code, ms in results if code == 201]
    failures = len(results) - len(latencies)
    quantiles = statistics.quantiles(latencies, n=100)

    print(f"Requests:    {TOTAL}  (workers: {WORKERS})")
    print(f"Failures:    {failures}")
    print(f"Total time:  {elapsed:.2f} s")
    print(f"Throughput:  {TOTAL / elapsed:.1f} requests/s")
    print(f"Latency ms:  avg {statistics.mean(latencies):.1f}, "
          f"p50 {quantiles[49]:.1f}, p95 {quantiles[94]:.1f}, max {max(latencies):.1f}")


if __name__ == "__main__":
    main()