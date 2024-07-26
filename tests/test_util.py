import os
import tempfile
import subprocess
import pytest
import shutil
from src.util import run_testbench

verilog_design = """
module adder #(
    parameter WIDTH = 32  // Parameterized bit-width
)(
    input wire [WIDTH-1:0] a,    // Input operand a
    input wire [WIDTH-1:0] b,    // Input operand b
    input wire clk,              // Clock signal
    output reg [WIDTH-1:0] sum   // Output sum
);

always @(posedge clk) begin
    sum <= a + b;
end

endmodule
"""

verilog_design_wrong = """
module adder #(
    parameter WIDTH = 32  // Parameterized bit-width
)(
    input wire [WIDTH-1:0] a,    // Input operand a
    input wire [WIDTH-1:0] b,    // Input operand b
    input wire clk,              // Clock signal
    output reg [WIDTH-1:0] sum   // Output sum
);

always @(posedge clk) begin
    sum <= a;
end

endmodule
"""

verilog_testbench = """
`timescale 1ns / 1ps

module adder_tb;

    // Parameters
    parameter WIDTH = 32;

    // Inputs
    reg [WIDTH-1:0] a;
    reg [WIDTH-1:0] b;
    reg clk;

    // Outputs
    wire [WIDTH-1:0] sum;

    // Instantiate the Unit Under Test (UUT)
    adder #(WIDTH) uut (
        .a(a), 
        .b(b), 
        .clk(clk), 
        .sum(sum)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;  // 10ns period, 100MHz clock
    end

    // Stimulus process
    initial begin
        // Initialize Inputs
        a = 0;
        b = 0;

        // Wait for global reset
        #10;

        // Apply test vectors
        a = 32'h00000001; b = 32'h00000001; #10;  // Test 1: 1 + 1
        if (sum !== 32'h00000002) begin
            $display("Failure: Test 1 failed (1 + 1)");
            $finish;
        end

        a = 32'hFFFFFFFF; b = 32'h00000001; #10;  // Test 2: Max + 1
        if (sum !== 32'h00000000) begin
            $display("Failure: Test 2 failed (Max + 1)");
            $finish;
        end

        a = 32'h12345678; b = 32'h87654321; #10;  // Test 3: Arbitrary values
        if (sum !== 32'h99999999) begin
            $display("Failure: Test 3 failed (12345678 + 87654321)");
            $finish;
        end

        a = 32'h0000FFFF; b = 32'hFFFF0000; #10;  // Test 4: Mixed high/low bits
        if (sum !== 32'hFFFFFFFF) begin
            $display("Failure: Test 4 failed (0000FFFF + FFFF0000)");
            $finish;
        end

        a = 32'hABCDEF12; b = 32'h12345678; #10;  // Test 5: Arbitrary values
        if (sum !== 32'hBE02458A) begin
            $display("Failure: Test 5 failed (ABCDEF12 + 12345678)");
            $finish;
        end

        // If all tests pass
        $display("All tests passed.");
        $finish;
    end

    // Monitor changes
    initial begin
        $monitor("At time %t, a = %h, b = %h, sum = %h", $time, a, b, sum);
    end

endmodule
"""
def test_run_testbench_correct():
    success, output = run_testbench(verilog_design, verilog_testbench)
    assert success
    assert "All tests passed." in output

def test_run_testbench_wrong():
    success, output = run_testbench(verilog_design_wrong, verilog_testbench)
    assert success
    assert "Failure" in output

def test_run_testbench_compile_error():
    mangled_design = verilog_design.replace("adder", "mangled_adder")
    success, output = run_testbench(mangled_design, verilog_testbench)
    assert "adder" in output
    assert not success