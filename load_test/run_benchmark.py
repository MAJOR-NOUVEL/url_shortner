import time
import statistics
import concurrent.futures
import requests

def benchmark_endpoint(base_url="http://127.0.0.1:5000", total_requests=500, concurrency=20):
    print(f">> Starting Concurrency Benchmark against {base_url}")
    print(f"Total Requests: {total_requests} | Concurrency: {concurrency}")

    # 1. Create a seed link
    try:
        res = requests.post(f"{base_url}/api/urls", json={"url": "https://python.org/benchmark"}, timeout=5)
        if res.status_code != 201:
            print("Failed to seed link:", res.text)
            return
        short_code = res.json()["short_code"]
        print(f"Seeded test link: /{short_code}")
    except Exception as e:
        print("Could not connect to target server:", e)
        return

    latencies = []
    status_codes = {}

    def fetch_redirect():
        start = time.perf_counter()
        try:
            r = requests.get(f"{base_url}/{short_code}", allow_redirects=False, timeout=3)
            duration_ms = (time.perf_counter() - start) * 1000
            return r.status_code, duration_ms
        except Exception:
            return 500, (time.perf_counter() - start) * 1000

    start_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(fetch_redirect) for _ in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            code, duration = f.result()
            latencies.append(duration)
            status_codes[code] = status_codes.get(code, 0) + 1

    total_time = time.perf_counter() - start_wall
    rps = round(total_requests / total_time, 2)

    latencies.sort()
    p50 = round(statistics.median(latencies), 2)
    p95 = round(latencies[int(len(latencies) * 0.95)], 2)
    p99 = round(latencies[int(len(latencies) * 0.99)], 2)
    avg = round(statistics.mean(latencies), 2)

    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Completed:  {total_requests} requests in {round(total_time, 2)}s")
    print(f"Throughput:       {rps} req/sec")
    print(f"Average Latency:  {avg} ms")
    print(f"p50 Latency:      {p50} ms")
    print(f"p95 Latency:      {p95} ms")
    print(f"p99 Latency:      {p99} ms")
    print(f"Status Codes:     {status_codes}")
    print("===================================================\n")

    return {
        "requests": total_requests,
        "concurrency": concurrency,
        "rps": rps,
        "avg_ms": avg,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "status_codes": status_codes
    }

if __name__ == "__main__":
    benchmark_endpoint()
