import argparse
import subprocess
import sys


def launch_server(model: str, num_workers: int):
    if model not in {"thread", "process"}:
        print("[ERROR] Invalid model. Choose 'thread' or 'process'.")
        sys.exit(1)

    script = "server_multithread_pool.py" if model == "thread" else "server_multiprocess_pool.py"
    
    try:
        subprocess.run([sys.executable, script, "--workers", str(num_workers)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to launch {script}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the file server using a specific concurrency model.")
    parser.add_argument("--model", type=str, required=True, choices=["thread", "process"], help="Concurrency model to use.")
    parser.add_argument("--workers", type=int, required=True, help="Number of worker threads or processes.")
    
    args = parser.parse_args()
    launch_server(args.model, args.workers)