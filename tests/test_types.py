import pytest
from src.gen_types import DesignSpec
from textwrap import dedent

def test_apply_template():
    template = dedent("""
    Please act as a professional verilog designer.

    {task}

    Module name:
    {module}
    Input ports:
    {input_ports}
    Output ports:
    {output_ports}

    Implementation:
    {implementation_hint}

    Give me the complete code.
    """)
    
    design_spec = DesignSpec(
        task="Design a module that performs addition.",
        module="adder",
        input_ports=["a", "b", "clk"],
        output_ports=["sum"],
        implementation_hint="Use a combinational logic for addition."
    )

    expected_output = dedent("""
    Please act as a professional verilog designer.

    Design a module that performs addition.

    Module name:
    adder
    Input ports:
    a
    b
    clk
    Output ports:
    sum

    Implementation:
    Use a combinational logic for addition.

    Give me the complete code.
    """)

    assert design_spec.apply_template(template).strip() == expected_output.strip()