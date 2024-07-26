from pydantic import BaseModel

class DesignSpec(BaseModel):
    task: str
    module: str
    input_ports: list[str]
    output_ports: list[str]
    implementation_hint: str

    def apply_template(self, template: str) -> str:
        return template.format(
            task=self.task,
            module=self.module,
            input_ports='\n'.join(self.input_ports),
            output_ports='\n'.join(self.output_ports),
            implementation_hint=self.implementation_hint
        )
    
class VerilogGeneration(BaseModel):
    code: str
    errors: str | None = None

    def has_errors(self) -> bool:
        return self.errors is not None

        
