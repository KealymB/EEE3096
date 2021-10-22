module tb_alu;
//Inputs
 reg[7:0] A,B;
 reg[3:0] ALU_Sel;

//Outputs
 reg[7:0] ALU_Out;
 reg clk;
 // Verilog code for ALU
  integer i;
 ALU test_unit(
   .clk(clk),
   .A(A),
   .B(B),  // ALU 8-bit Inputs
   .ALU_Sel(ALU_Sel),// ALU Selection
   .ALU_out(ALU_Out) // ALU 8-bit Output
  );
  
  
  initial begin
    $dumpfile("dump.vcd"); $dumpvars;
    A = 8'b0101;
    B = 8'b0001;
    ALU_Sel = 4'b0000;
    
    for (i=0;i<=15;i=i+1)
      begin
        clk=1'b1;
        #5;
        ALU_Sel = ALU_Sel + 8'h01;
        clk=1'b0;
        #5;
      end;
    
    
  end
    
endmodule