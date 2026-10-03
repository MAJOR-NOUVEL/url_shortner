import os
import sys
import time
import statistics
import concurrent.futures

# Configure environment before app creation
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///benchmark.db"
os.environ["DISABLE_TALISMAN"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app import create_app
from app.extensions import db, redis_store
from app.utils.cache import get_cache_telemetry

def run_benchmark(total_requests=1000, concurrency=20):
    app = create_app("development")
    
    # Mock celery task delay to measure pure redirect latency
    from app.tasks.click_logger import record_click_event
    record_click_event.delay = lambda *args, **kwargs: None

    with app.app_context():
        db.create_all()

    client = app.test_client()

    print(f">> Running Benchmark: {total_requests} requests at concurrency={concurrency}")

    # 1. Create seed short link
    res = client.post("/api/urls", json={"url": "https://python.org/benchmark-target"})
    assert res.status_code == 201
    code = res.get_json()["short_code"]
    print(f">> Seed link created: /{code}")

    # Warm cache
    client.get(f"/{code}", follow_redirects=False)

    latencies = []
    status_codes = {}

    def send_request(_):
        start = time.perf_counter()
        resp = client.get(f"/{code}", follow_redirects=False)
        dur = (time.perf_counter() - start) * 1000
        return resp.status_code, dur

    wall_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(send_request, range(total_requests)))
    wall_duration = time.perf_counter() - wall_start

    for code_val, dur in results:
        latencies.append(dur)
        status_codes[code_val] = status_codes.get(code_val, 0) + 1

    latencies.sort()
    rps = round(total_requests / wall_duration, 2)
    p50 = round(statistics.median(latencies), 2)
    p95 = round(latencies[int(len(latencies) * 0.95)], 2)
    p99 = round(latencies[int(len(latencies) * 0.99)], 2)
    avg = round(statistics.mean(latencies), 2)

    telemetry = get_cache_telemetry()

    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Requests:       {total_requests}")
    print(f"Concurrency Level:    {concurrency}")
    print(f"Total Time:           {round(wall_duration, 3)} seconds")
    print(f"Throughput:           {rps} requests/second")
    print(f"Average Latency:      {avg} ms")
    print(f"50th Percentile (p50):{p50} ms")
    print(f"95th Percentile (p95):{p95} ms")
    print(f"99th Percentile (p99):{p99} ms")
    print(f"HTTP Status Codes:    {status_codes}")
    print(f"Cache Hit Ratio:      {telemetry.get('hit_ratio_percent', 100.0)}%")
    print("===================================================\n")

    return {
        "rps": rps,
        "avg": avg,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "codes": status_codes
    }

if __name__ == "__main__":
    run_benchmark(1000, 20)
