"""
Assembly to Hex Compiler for Custom CPU
Converts assembly instructions to hex values for Logisim circuit
"""

import re
import sys
from typing import Dict, List, Tuple, Optional

class AssemblyCompiler:
    def __init__(self):
        # Instruction set with opcodes
        self.instructions = {
            'NOP': '0000',
            'JMP': '0001', 
            'JEQ': '0010',
            'STORE': '0011',
            'CMP': '0100',
            'OUT': '0101',
            'IN': '0110',
            'MOV': '0111',
            'HALT': '1000',
            'MOVE_UP': '1001',
            'MOVE_DOWN': '1010',
            'SCORE_INCREMENT': '1011',
            'SPAWN_OBSTACLE': '1100',
            'GAME_OVER': '1101',
            'START_GAME': '1110',
            'TITLE_SCREEN': '1111'
        }
        
        # Labels and their addresses
        self.labels = {}
        self.current_address = 0
        
    def parse_line(self, line: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """Parse a line into label, instruction, and arguments"""
        # Remove comments and strip whitespace
        line = line.split(';')[0].strip()
        if not line:
            return None, None, []
            
        # Check for label (ends with :)
        label = None
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            line = parts[1].strip() if len(parts) > 1 else ''
            
        if not line:
            return label, None, []
            
        # Split instruction and arguments
        parts = line.split()
        instruction = parts[0].upper()
        args = [arg.strip(',') for arg in parts[1:]] if len(parts) > 1 else []
        
        return label, instruction, args
        
    def first_pass(self, lines: List[str]) -> None:
        """First pass: collect labels and their addresses"""
        self.current_address = 0
        
        for line in lines:
            label, instruction, args = self.parse_line(line)
            
            # Handle ORG directive to set current address
            if instruction == 'ORG':
                if len(args) != 1:
                    raise ValueError("ORG directive requires exactly one argument")
                self.current_address = int(self.resolve_argument(args[0]), 2)
                continue
            
            if label:
                self.labels[label] = self.current_address
                
            if instruction and instruction != 'ORG':
                self.current_address += 1
                
    def resolve_argument(self, arg: str) -> str:
        """Resolve argument to 5-bit binary value"""
        # Check if it's a label
        if arg in self.labels:
            addr = self.labels[arg]
            return format(addr, '05b')
            
        # Check if it's a hex number (0x prefix)
        if arg.startswith('0x') or arg.startswith('0X'):
            try:
                val = int(arg, 16)
                if 0 <= val <= 31:
                    return format(val, '05b')
                else:
                    raise ValueError(f"Hex value {arg} out of range (0-31)")
            except ValueError as e:
                raise ValueError(f"Invalid hex number: {arg}")
                
        # Check if it's a binary number (0b prefix)
        if arg.startswith('0b') or arg.startswith('0B'):
            try:
                val = int(arg, 2)
                if 0 <= val <= 31:
                    return format(val, '05b')
                else:
                    raise ValueError(f"Binary value {arg} out of range (0-31)")
            except ValueError as e:
                raise ValueError(f"Invalid binary number: {arg}")
                
        # Check if it's a decimal number
        try:
            val = int(arg)
            if 0 <= val <= 31:
                return format(val, '05b')
            else:
                raise ValueError(f"Decimal value {arg} out of range (0-31)")
        except ValueError:
            pass
            
        raise ValueError(f"Cannot resolve argument: {arg}")
        
    def second_pass(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Second pass: generate machine code with addresses"""
        machine_code = []
        self.current_address = 0
        
        for line_num, line in enumerate(lines, 1):
            try:
                label, instruction, args = self.parse_line(line)
                
                # Handle ORG directive
                if instruction == 'ORG':
                    if len(args) != 1:
                        raise ValueError("ORG directive requires exactly one argument")
                    self.current_address = int(self.resolve_argument(args[0]), 2)
                    continue
                
                if not instruction or instruction == 'ORG':
                    continue
                    
                if instruction not in self.instructions:
                    raise ValueError(f"Unknown instruction: {instruction}")
                    
                opcode = self.instructions[instruction]
                
                # Handle different instruction formats
                if instruction in ['NOP', 'HALT', 'MOVE_UP', 'MOVE_DOWN', 
                                'SCORE_INCREMENT', 'SPAWN_FISH', 'GAME_OVER', 
                                'START_GAME', 'TITLE_SCREEN']:
                    # Instructions with no arguments
                    if args:
                        raise ValueError(f"{instruction} takes no arguments")
                    machine_code.append((self.current_address, opcode + '00000'))
                    
                elif instruction in ['JMP', 'JEQ', 'OUT', 'IN']:
                    # Instructions with one argument
                    if len(args) != 1:
                        raise ValueError(f"{instruction} requires exactly 1 argument")
                    arg_bits = self.resolve_argument(args[0])
                    machine_code.append((self.current_address, opcode + arg_bits))
                    
                elif instruction in ['CMP', 'MOV', 'STORE']:
                    # Instructions with one argument (5-bit addressing)
                    if len(args) != 1:
                        raise ValueError(f"{instruction} requires exactly 1 argument")
                    arg_bits = self.resolve_argument(args[0])
                    machine_code.append((self.current_address, opcode + arg_bits))
                        
                self.current_address += 1
                
            except Exception as e:
                raise Exception(f"Error on line {line_num}: {e}")
                
        return machine_code
        
    def compile(self, assembly_code: str) -> List[Tuple[int, str]]:
        """Compile assembly code to machine code with addresses"""
        lines = assembly_code.strip().split('\n')
        
        # First pass: collect labels
        self.first_pass(lines)
        
        # Second pass: generate machine code
        machine_code = self.second_pass(lines)
        
        return machine_code
        
    def binary_to_hex(self, machine_code: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """Convert binary strings to hex strings"""
        hex_list = []
        for addr, binary in machine_code:
            # Convert 9-bit binary to hex (will be 3 hex digits, but we'll pad to make it clean)
            hex_val = hex(int(binary, 2))[2:].upper().zfill(3)
            hex_list.append((addr, hex_val))
        return hex_list
        
    def compile_to_hex(self, assembly_code: str) -> List[Tuple[int, str]]:
        """Compile assembly code directly to hex with addresses"""
        binary_code = self.compile(assembly_code)
        return self.binary_to_hex(binary_code)

def main():
    compiler = AssemblyCompiler()
    
    # Example usage
    sample_code = """
    ; Boot code at address 0
    ORG 0
    START:
        TITLE_SCREEN
        JMP GAME_CODE
        
    ; Game code at address 10
    ORG 10  
    GAME_CODE:
        START_GAME
        MOV 15         ; Move value 15 to register 
        CMP 10         ; Compare with 10
        JEQ END        ; Jump to END if equal
        SCORE_INCREMENT
        JMP GAME_CODE
        
    ; End routine at address 20
    ORG 20
    END:
        GAME_OVER
        HALT           ; Stop execution
    """
    
    print("Assembly to Hex Compiler")
    print("=" * 40)
    
    try:
        # Compile the sample code
        hex_code = compiler.compile_to_hex(sample_code)
        
        print("Sample Assembly Code:")
        print(sample_code)
        print("\nCompiled Hex Output:")
        for addr, hex_val in hex_code:
            print(f"Address {addr:02d}: {hex_val}")
            
        print(f"\nTotal instructions: {len(hex_code)}")
        print("\nFor Logisim RAM - Address:Value pairs:")
        for addr, hex_val in hex_code:
            print(f"{addr}: {hex_val}")
        
    except Exception as e:
        print(f"Compilation error: {e}")

def compile_file(input_file: str, output_file: str = None):
    """Compile assembly file to hex output"""
    compiler = AssemblyCompiler()
    
    try:
        with open(input_file, 'r') as f:
            assembly_code = f.read()
            
        hex_code = compiler.compile_to_hex(assembly_code)
        
        if output_file:
            with open(output_file, 'w') as f:
                for addr, hex_val in hex_code:
                    f.write(f"{addr}: {hex_val}\n")
            print(f"Compiled {input_file} -> {output_file}")
        else:
            print("Compiled Hex Output:")
            for addr, hex_val in hex_code:
                print(f"{addr:02d}: {hex_val}")
                
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Compilation error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        compile_file(input_file, output_file)
    else:
        main()