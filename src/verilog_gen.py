from openai import OpenAI
from openai.types import Completion
import subprocess
import tempfile
import os

class VerilogGen:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0, verbose = True):
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.messages = []

    def call(self, messages: list[str]) -> Completion:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )

    @classmethod
    def check_syntax(cls, code: str) -> str | None:
        """
        Returns syntax errors in the verilog code, if any. Otherwise, returns None
        """


        with tempfile.NamedTemporaryFile(suffix=".v", delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            result = subprocess.run(
                ["verilator", "--lint-only", "--timing", temp_file_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return None
            else:
                return result.stderr
        finally:
            os.remove(temp_file_path)
            pass


    @classmethod
    def parse_code(cls, content: str) -> str:
        # TODO: improve code parsing logic to deal with extra content

        content = content.strip(" \t\n`")
        if content.startswith("verilog"):
            content = content.split("verilog", 1)[1]
        return content
    
    def append_message(self, message: dict):
        self.messages.append(message)
        if self.verbose:
            print(message)

    def prompt(self, prompt: str) -> Completion:
        self.append_message({
            "role": "user",
            "content": prompt
        })
        
        completion = self.call(self.messages)

        message = completion.choices[0].message

        self.append_message(message)

        return completion



    def reset_history(self):
        self.messages = []
        self.candidates = []
        self.append_message({
            "role": "system",
            "content": self.system
        })

