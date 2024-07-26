from nicegui import ui
from src.gen_types import DesignSpec
from src.test_gen import TestGen
from src.design_gen import DesignGen
import asyncio


state = {
    'spec': DesignSpec(
        task="Design a module that performs addition.",
        module="adder",
        input_ports=["a", "b", "clk"],
        output_ports=["sum"],
        implementation_hint="Use a combinational logic for addition."
    ),
    'tests': None,
    'design': None
}

@ui.page("/design")
def design_page():
    def confirm_design():
        ui.notify('Design confirmed.', type='success')


    @ui.refreshable
    def design_section():
        ui.label('Generated Design').classes('text-2xl mb-4')
        if state['design'] is None:
            pass
        elif state['design'] == 'loading':
            ui.spinner().classes('mb-4')
        else:
            ui.code(state['design'], language='verilog').classes('mb-4')
            ui.button('Confirm').classes('bg-green-500 text-white').on_click(confirm_design)
            feedback = ui.input('Feedback').classes('mb-4')
            ui.button('Submit Feedback').classes('bg-blue-500 text-white').on_click(lambda: prompt_feedback(feedback.value))

    design_gen = DesignGen()
    async def prompt_feedback(feedback: str):
        state['design'] = 'loading'
        design_section.refresh()

        loop = asyncio.get_running_loop()
        candidates = await loop.run_in_executor(None, design_gen.feedback, feedback)

        state['design'] = candidates[-1].code
        design_section.refresh()

    async def generate_design():
        if state['spec'] is not None:
            state['design'] = 'loading'
            design_section.refresh()

            loop = asyncio.get_running_loop()
            candidates = await loop.run_in_executor(None, design_gen.generate_design, state['spec'])

            state['design'] = candidates[-1].code
            design_section.refresh()
        else:
            ui.notify('Please specify a design spec first.', type='warning')
            ui.navigate.to('/')

    ui.label('Chip Module Design Specification').classes('text-2xl mb-4')
    if state['spec'] is not None:
        ui.label(f'Task: {state["spec"].task}').classes('mb-2')
        ui.label(f'Module: {state["spec"].module}').classes('mb-2')
        ui.label(f'Input Ports: {", ".join(state["spec"].input_ports)}').classes('mb-2')
        ui.label(f'Output Ports: {", ".join(state["spec"].output_ports)}').classes('mb-2')
        ui.label(f'Implementation Hint: {state["spec"].implementation_hint}').classes('mb-2')
    ui.button('Generate Design', on_click=generate_design).classes('mb-4')
    design_section()

@ui.page("/test")
def test_page():

    def confirm_tests():
        ui.navigate.to('/design')

    @ui.refreshable
    def test_section():
        ui.label('Generated Tests').classes('text-2xl mb-4')
        if state['tests'] is None:
            pass
        elif state['tests'] == 'loading':
            ui.spinner().classes('mb-4')
        else:
            ui.code(state['tests'], language='verilog').classes('mb-4')
            ui.button('Confirm').classes('bg-green-500 text-white').on_click(confirm_tests)
            feedback = ui.input('Feedback').classes('mb-4')
            ui.button('Submit Feedback').classes('bg-blue-500 text-white').on_click(lambda: prompt_feedback(feedback.value))   

    test_gen = TestGen()
    
    async def prompt_feedback(feedback: str):
        state['tests'] = 'loading'
        test_section.refresh()

        loop = asyncio.get_running_loop()
        candidates = await loop.run_in_executor(None, test_gen.feedback, feedback)

        state['tests'] = candidates[-1].code
        test_section.refresh()

    async def generate_tests():
        if state['spec'] is not None:
            state['tests'] = 'loading'
            test_section.refresh()

            loop = asyncio.get_running_loop()
            candidates = await loop.run_in_executor(None, test_gen.generate_tests, state['spec'], 0)

            state['tests'] = candidates[-1].code
            test_section.refresh()
        else:
            ui.notify('Please specify a design spec first.', type='warning')
            ui.navigate.to('/')



    ui.label('Chip Module Design Specification').classes('text-2xl mb-4')
    if state['spec'] is not None:
        ui.label(f'Task: {state["spec"].task}').classes('mb-2')
        ui.label(f'Module: {state["spec"].module}').classes('mb-2')
        ui.label(f'Input Ports: {", ".join(state["spec"].input_ports)}').classes('mb-2')
        ui.label(f'Output Ports: {", ".join(state["spec"].output_ports)}').classes('mb-2')
        ui.label(f'Implementation Hint: {state["spec"].implementation_hint}').classes('mb-2')

    ui.button('Generate Tests', on_click=generate_tests).classes('mb-4')
    test_section()
    

@ui.page("/")
def spec_page():
    # Function to add a new item to the list
    def add_item(item_list, item_container):
        with item_container:
            container = ui.row().classes('mb-2')
            with container:
                new_item = ui.input('Enter value')
                ui.button('Delete', on_click=lambda: (item_list.remove(new_item), item_container.remove(container))).classes('ml-2')
            item_list.append(new_item)

    # Function to handle the form submission
    def handle_submit():
        task_description = task_description_input.value
        module_name = module_name_input.value
        input_ports = [item.value for item in input_ports_list if item.value]
        output_ports = [item.value for item in output_ports_list if item.value]
        implementation_hint = implementation_hint_input.value

        state['spec'] = DesignSpec(
            task=task_description,
            module=module_name,
            input_ports=input_ports,
            output_ports=output_ports,
            implementation_hint=implementation_hint
        )

        # Clear input fields
        task_description_input.value = ''
        module_name_input.value = ''
        input_ports_list.clear()
        output_ports_list.clear()
        input_ports_container.clear()
        output_ports_container.clear()
        implementation_hint_input.value = ''

        ui.navigate.to('/test')


    # Create the UI components
    ui.label('Chip Module Design Specification').classes('text-2xl mb-4')

    task_description_input = ui.input('Task Description').classes('mb-4')
    module_name_input = ui.input('Module Name').classes('mb-4')

    input_ports_list = []
    output_ports_list = []

    ui.label('Input Ports').classes('mb-2')
    input_ports_container = ui.column().classes('mb-4')
    ui.button('Add Input Port', on_click=lambda: add_item(input_ports_list, input_ports_container)).classes('mb-4')

    ui.label('Output Ports').classes('mb-2')
    output_ports_container = ui.column().classes('mb-4')
    ui.button('Add Output Port', on_click=lambda: add_item(output_ports_list, output_ports_container)).classes('mb-4')

    implementation_hint_input = ui.input('Implementation Hint').classes('mb-4')

    ui.button('Submit', on_click=handle_submit).classes('mt-4')

# Start the NiceGUI app
ui.run(port=5500)
