//Define the module
module ALU(
    input clk,
  	input [7:0] A,B,
  	input [3:0] ALU_Sel,
  	output reg [7:0] ALU_out
);

reg [7:0] ALU_result;

  always@(posedge clk) //Triggered on rising edge clock
    begin
        case(ALU_Sel)
            4'b0000: // Acc = A + B
           		ALU_result = A + B ; 
            4'b0001: // Acc = A - B
               	ALU_result = A - B ;
            4'b0010: // Acc = A * B
               	ALU_result = A * B;
            4'b0011: // Acc = A / B
               	ALU_result = A / B;
            4'b0100: // Acc = Acc + A
               	ALU_result = ALU_out + A;
            4'b0101: // Acc = Acc * A
               	ALU_result = ALU_out * A;
            4'b0110: // Rotate left Acc = Acc + (A * B)
               	ALU_result = ALU_out + (A * B);
            4'b0111: // Rotate right Acc = A rotated left by 1
               	ALU_result =  {A[6:0],A[7]};
            4'b1000: //  Acc = A rotated right by 1 
              	ALU_result =  {A[0],A[7:1]};
            4'b1001: //  Acc = A and B
              	ALU_result = A & B;
            4'b1010: //  Acc = A or B
              	ALU_result = A | B;
            4'b1011: //  Acc = A xor B  
              	ALU_result = A ^ B;
            4'b1100: // Acc = A nand B
              	ALU_result = ~(A & B);
            4'b1101: // Acc = 0xFF if A=B else 0
              	ALU_result = (A == B) ? 8'hFF : 0;
            4'b1110: // Acc = 0xFF if A>B else 0
              	ALU_result = (A > B) ? 8'hFF : 0;
            4'b1111: // Acc = 0xFF if A<B else 0
              	ALU_result = (A < B) ? 8'hFF : 0;
            default: ALU_result = A;
        endcase

        ALU_out <= ALU_result;
    end    
endmodule