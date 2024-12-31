import server
import pstats
import cProfile
import os
import sys
import subprocess
import threading

# Running the server with cProfile
dir = os.path.dirname(__file__)
profiler = cProfile.Profile()
threading.Thread(target=profiler.runcall, args=(server.main,), daemon=True).start()

# Running 20 clients in parallel to test the server
client_processes = [subprocess.Popen([sys.executable, "client.py"]) for _ in range(20)]
[p.wait() for p in client_processes]

# Ending profiling and saving profiling data
profiler.disable()
profiling_path = os.path.join(dir, "profiling_results.prof")
profiler.dump_stats(profiling_path)
print(f"Profiling results saved to {profiling_path}")

detailed_stats_path = os.path.join(dir, "profiling_results.txt")
with open(detailed_stats_path, "w") as f:
    stats = pstats.Stats(profiler, stream=f)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats()
    stats.print_callers()
    stats.print_callees()
print(f"Detailed profiling results saved to {detailed_stats_path}")


# Running snakeviz to visualize the profiling results
try:
    print("Launching Snakeviz for detailed profiling visualization...")
    profiling_path = os.path.join(dir, "profiling_results.prof")
    subprocess.run(["snakeviz", profiling_path])
except FileNotFoundError:
    print("Snakeviz is not installed. Please install it using 'pip install snakeviz'.")
except Exception as e:
    print(f"Error launching Snakeviz: {e}")
