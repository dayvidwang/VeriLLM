from src.gen_types import DesignSpec, VerilogGeneration
from src.verilog_gen import VerilogGen
from src.util import run_testbench
import os

class DesignGen(VerilogGen):
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        super().__init__(model, temperature)
        self.prompt_path = "src/prompts/design_gen"
        self.candidates: VerilogGeneration = []
        with open(os.path.join(self.prompt_path, "system.txt"), "r") as file:
            self.system = file.read()
        
        with open(os.path.join(self.prompt_path, "initial.txt"), "r") as file:
            self.initial_template = file.read()


    def generate_design(self, spec: DesignSpec, retry_limit = 3) -> list[VerilogGeneration]:
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
    
    def check_tests(code, test_str = None, test_path = None) -> str | None:
        # TODO: use this in verification loop
        if test_str is not None and test_path is not None:
            raise ValueError("Only one of test_str and test_path should be provided.")
        elif test_str is not None:
            success, output = run_testbench(code, test_str)
        elif test_path is not None:
            with open(test_path, "r") as file:
                test_str = file.read()
            success, output = run_testbench(code, test_str)
        else:
            raise ValueError("Either test_str or test_path should be provided.")
        
        if not success:
            return output
        else:
            # TODO: change this to not be hardcoded check for "Failure"
            if "Failure" in output:
                return output
            else:
                return None