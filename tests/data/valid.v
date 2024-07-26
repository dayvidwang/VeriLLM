module adder (
    input wire [31:0] a,
    input wire [31:0] b,
    input wire clk,
    output reg [31:0] sum
);

always @(posedge clk) begin
    sum <= a;
end

endmodule