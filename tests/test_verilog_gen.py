import pytest
from src.verilog_gen import VerilogGen
from textwrap import dedent

def test_check_syntax():
    with open("tests/data/valid.v", "r") as f:
        valid = f.read()
    assert VerilogGen.check_syntax(valid) is None

    with open("tests/data/invalid.v", "r") as f:
        invalid = f.read()

    assert ":8:1: syntax error, unexpected endmodule, expecting ',' or ';'" in VerilogGen.check_syntax(invalid)

def test_parse_code():
    input = dedent("""
    ```verilog
    module adder (
        input wire [31:0] a,
        input wire [31:0] b,
        input wire clk,
        output reg [31:0] sum
    );

    always @(*) begin
        sum = a + b;
    end

    endmodule
    ```
    """)

    expected = dedent("""
    module adder (
        input wire [31:0] a,
        input wire [31:0] b,
        input wire clk,
        output reg [31:0] sum
    );

    always @(*) begin
        sum = a + b;
    end

    endmodule
    """)

    assert VerilogGen.parse_code(input).strip() == expected.strip()
                      