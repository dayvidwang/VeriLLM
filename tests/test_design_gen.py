import pytest
from src.design_gen import DesignGen
from src.gen_types import DesignSpec
import tempfile
import os
import subprocess
from src.util import run_testbench

def test_generate_design():
    """
    This is a minimum baseline that the code should pass.
    """
    design_gen = DesignGen()
    spec = DesignSpec(
        task="Design a module that performs addition.",
        module="adder",
        input_ports=["a", "b", "clk"],
        output_ports=["sum"],
        implementation_hint="Use a combinational logic for addition."
    )

    designs = design_gen.generate_design(spec)

    assert len(designs) == 1

    assert design_gen.check_syntax(designs[0]) is None

    with open("tests/data/test_design_gen_adder_tb.v", "r") as f:
        testbench = f.read()

    design = designs[0]

    test_output = run_testbench(design, testbench)

    assert "Failed" not in test_output, test_output
