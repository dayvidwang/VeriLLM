module simple_module (
    input wire a,
    input wire b,
    output wire sum
);
    assign sum = a + b  // Missing semicolon here

endmodule
