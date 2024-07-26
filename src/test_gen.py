from src.verilog_gen import VerilogGen
from src.gen_types import DesignSpec, VerilogGeneration
import os
from openai.types import Completion

verbose = True

class TestGen(VerilogGen):
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        super().__init__(model, temperature)
        self.prompt_path = "src/prompts/test_gen"
        self.candidates: VerilogGeneration = []
        with open(os.path.join(self.prompt_path, "system.txt"), "r") as file:
            self.system = file.read()

        with open(os.path.join(self.prompt_path, "initial.txt"), "r") as file:
            self.initial_template = file.read()

    def generate_tests(self, spec: DesignSpec, retry_limit = 3) -> list[VerilogGeneration]:

        prompt = spec.apply_template(self.initial_template)

        self.reset_history()

        completion = self.prompt(prompt)
        code = self.parse_code(completion.choices[0].message.content)

        errors = self.check_syntax(code)
        self.candidates.append(VerilogGeneration(code=code, errors=errors))

        retry_count = 0

        while retry_count < retry_limit and errors is not None:
            
            error_correction_prompt = f"Fix the following syntax errors in the code:\n{errors}"

            self.feedback(error_correction_prompt)
            errors = self.candidates[-1].errors

            retry_count += 1

        return self.candidates
    
    def feedback(self, feedback: str):
        completion = self.prompt(feedback)
        code = self.parse_code(completion.choices[0].message.content)

        errors = self.check_syntax(code)
        self.candidates.append(VerilogGeneration(code=code, errors=errors))
        return self.candidates
        


    
if __name__ == '__main__':
    test_gen = TestGen()
    spec = DesignSpec(
        task="Design a module that performs addition.",
        module="adder",
        input_ports=["a", "b", "clk"],
        output_ports=["sum"],
        implementation_hint="Use a combinational logic for addition."
    )

    candidates = test_gen.generate_tests(spec)

    for i, candidate in enumerate(candidates):
        with open(f"tmp/test_{i}.v", "w") as f:
            f.write(candidate.code)