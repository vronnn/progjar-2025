import argparse
import time
import os
from multiprocessing import Pool as ProcessPool
from threading import Thread
import requests
import random

# Constants
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9000

# Helper Functions

def generate_test_file(file_size_mb):
    """Generates a dummy file of specified size (in MB)."""
    path = f"test_{file_size_mb}MB.dat"
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(os.urandom(file_size_mb * 1024 * 1024))
    return path

def perform_operation(args):
    """Worker function to simulate client operation."""
    operation, file_size_mb = args['operation'], args['file_size']
    success = True
    bytes_processed = 0
    try:
        if operation == 'upload':
            path = generate_test_file(file_size_mb)
            with open(path, 'rb') as f:
                response = requests.post(f"http://{SERVER_HOST}:{SERVER_PORT}/upload", files={"file": f})
                success = response.ok
                if success:
                    bytes_processed = os.path.getsize(path)

        elif operation == 'download':
            filename = f"test_{file_size_mb}MB.dat"
            response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/download/{filename}")
            success = response.ok
            if success:
                bytes_processed = len(response.content)

        elif operation == 'list':
            response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/list")
            success = response.ok

    except Exception as e:
        print(f"[ERROR] Client failed: {e}")
        success = False

    return (success, bytes_processed)

def run_with_threads(args_list, num_clients):
    results = []
    threads = []

    def task_wrapper(arg):
        results.append(perform_operation(arg))

    for arg in args_list:
        t = Thread(target=task_wrapper, args=(arg,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results

def run_with_processes(args_list, num_clients):
    with ProcessPool(processes=num_clients) as pool:
        results = pool.map(perform_operation, args_list)
    return results

def main():
    parser = argparse.ArgumentParser(description='Client Task Runner')
    parser.add_argument('--operation', required=True, choices=['upload', 'download', 'list'])
    parser.add_argument('--file-size', type=int, choices=[10, 50, 100], required=True)
    parser.add_argument('--num-clients', type=int, required=True)
    parser.add_argument('--concurrency-model', choices=['thread', 'process'], required=True)
    args = parser.parse_args()

    args_list = [{'operation': args.operation, 'file_size': args.file_size} for _ in range(args.num_clients)]

    print(f"[INFO] Starting {args.num_clients} client(s) for '{args.operation}' with {args.file_size}MB file using {args.concurrency_model} model")
    start_time = time.time()

    if args.concurrency_model == 'thread':
        results = run_with_threads(args_list, args.num_clients)
    else:
        results = run_with_processes(args_list, args.num_clients)

    end_time = time.time()
    duration = end_time - start_time

    successful = sum(1 for r in results if r[0])
    failed = args.num_clients - successful
    total_bytes = sum(r[1] for r in results if r[0])
    throughput = total_bytes / duration if duration > 0 else 0

    print("\n[RESULT SUMMARY]")
    print(f"Operation: {args.operation}")
    print(f"File Size: {args.file_size}MB")
    print(f"Clients: {args.num_clients}")
    print(f"Concurrency: {args.concurrency_model}")
    print(f"Total Time: {duration:.2f}s")
    print(f"Throughput: {throughput:.2f} B/s")
    print(f"Success: {successful}, Fail: {failed}")

if __name__ == '__main__':
    main()