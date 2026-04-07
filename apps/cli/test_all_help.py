import os
import subprocess
import sys

def test_cli_help():
    cli_dir = "/Users/csv610/Projects/CompGeom/CompGeom/apps/cli/"
    files = [f for f in os.listdir(cli_dir) if f.endswith("_cli.py")]
    
    failed = []
    passed = 0
    
    for f in sorted(files):
        path = os.path.join(cli_dir, f)
        print(f"Testing {f}...")
        try:
            # Using sys.executable to ensure we use the same python environment
            result = subprocess.run([sys.executable, path, "-h"], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=10)
            if result.returncode == 0:
                passed += 1
            else:
                print(f"FAILED: {f} (exit code {result.returncode})")
                print(f"Stderr: {result.stderr}")
                failed.append((f, result.stderr))
        except Exception as e:
            print(f"ERROR running {f}: {str(e)}")
            failed.append((f, str(e)))
            
    print("\nSummary:")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed scripts:")
        for f, err in failed:
            print(f"- {f}")
        return False
    return True

if __name__ == "__main__":
    if test_cli_help():
        print("\nAll CLI scripts passed -h check.")
        sys.exit(0)
    else:
        print("\nSome CLI scripts failed -h check.")
        sys.exit(1)
