import subprocess
import os
import tempfile
from typing import Tuple

def run_testbench(design: str, testbench: str) -> Tuple[bool, str]:
    """
    Run the simulation for the given design and testbench.

    Returns a tuple of (compiles?, output)
    """
    tempdir = tempfile.TemporaryDirectory()

    design_file = open(os.path.join(tempdir.name, "design.v"), "w")
    testbench_file = open(os.path.join(tempdir.name, "testbench.v"), "w")

    cwd = os.getcwd()

    try:
        os.chdir(tempdir.name)

        # Write design and testbench to temp files
        design_file.write(design)
        testbench_file.write(testbench)
        design_file.close()
        testbench_file.close()



        # Compile with Verilator
        compile_cmd = [
            "verilator", "--Wno-fatal", "--binary", testbench_file.name, design_file.name
        ]
        compile_process = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if compile_process.returncode != 0:
            return False, compile_process.stderr

        # Run the simulation
        run_cmd = ["./obj_dir/Vtestbench"]
        run_process = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if run_process.returncode != 0:
            return False, run_process.stderr

        return True, run_process.stdout

    finally:
        tempdir.cleanup()
        os.chdir(cwd)