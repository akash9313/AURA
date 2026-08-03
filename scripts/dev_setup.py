import os
import sys
import subprocess

def run_cmd(cmd, cwd="."):
    print(f"Executing: {' '.join(cmd)}")
    use_shell = os.name == "nt"
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=use_shell)
    if res.returncode == 0:
        print(f"  [OK] {res.stdout.strip().splitlines()[0] if res.stdout else 'Success'}")
        return True
    else:
        print(f"  [FAIL] {res.stderr.strip() or res.stdout.strip()}")
        return False


def main():
    print("==================================================")
    print("AURA Developer Environment Diagnostic & Bootstrap")
    print("==================================================\n")

    print("[1/4] Checking Python Environment...")
    print(f"  Python Version: {sys.version.split()[0]}")

    print("\n[2/4] Checking Node.js & NPM...")
    run_cmd(["node", "-v"])
    run_cmd(["npm", "-v"])

    print("\n[3/4] Running Backend Unit Test Suite...")
    test_ok = run_cmd([sys.executable, "-m", "unittest", "discover", "-s", "backend/tests", "-t", "backend"])

    print("\n[4/4] Verifying Frontend TypeScript Compiler...")
    ts_ok = run_cmd(["npx.cmd" if os.name == "nt" else "npx", "tsc"], cwd="frontend")

    print("\n==================================================")
    if test_ok and ts_ok:
        print("SUCCESS: AURA Developer Platform Environment Healthy!")
    else:
        print("WARNING: Some environment checks failed. Review output above.")
    print("==================================================")

if __name__ == "__main__":
    main()
