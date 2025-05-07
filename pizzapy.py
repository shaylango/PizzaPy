from textx import metamodel_from_file
from collections import OrderedDict
from os.path import dirname, join
from textx.export import metamodel_export, model_export

class Pizza:
    def interpret(self, model):
        output = interpret_pizza_program(model)
        print(output)

def interpret_pizza_program(model):
    ctx = []
    output = []

    var_ctx = OrderedDict()

    # Get the value of a variable, defaulting to 0 if not yet set
    def ctx_get(name):
        return var_ctx.get(name, 0)

    # Increment the value of a variable by 1
    def increment_ctx(name):
        var_ctx[name] = var_ctx.get(name, 0) + 1

    # Iterate over all instructions
    def eval_instructions(instructions):
        for instr in instructions:
            cls = instr.__class__.__name__

            # Ingredient or AddStatement: store value in the context list
            if cls in ['Ingredient', 'AddStatement']:
                val = instr.value
                ctx.append(val)

            # Bake: convert values in ctx to characters (if printable) and clear ctx
            elif cls == 'Bake':
                for val in ctx:
                    if 32 <= val <= 126 or val == 10:
                        output.append(chr(val))
                ctx.clear()

            # Loop construct: repeat block while variable <= limit 
            elif cls == 'Loop':
                while ctx_get(instr.var) <= instr.limit:
                    eval_instructions(instr.instructions)
                    increment_ctx(instr.var)

            # Conditional: only execute block if var % divisor == 0
            elif cls == 'Conditional':
                if instr.divisor != 0 and ctx_get(instr.var) % instr.divisor == 0:
                    eval_instructions(instr.instructions)

            # NegativeConditional: execute if var % divisor != 0 (if defined)
            elif cls == 'NegativeConditional':
                if instr.divisor != 0 and ctx_get(instr.var) % instr.divisor != 0:
                    eval_instructions(instr.instructions)

            # PrintStatement: append the string value of a variable to output
            elif cls == 'PrintStatement':
                val = ctx_get(instr.var)
                output.append(str(val))

    eval_instructions(model.ingredients + model.instructions)
    return ''.join(output)

def main(debug=False):
    this_folder = dirname(__file__)
    pizza_mm = metamodel_from_file(join(this_folder, 'pizzapy.tx'), debug=debug)

    pizza_mm.register_obj_processors({
        'PrintStatement': lambda x: None
    })

    metamodel_export(pizza_mm, join(this_folder, 'pizza_meta.dot'))
    pizza_model = pizza_mm.model_from_file(join(this_folder, 'program.pizzapy'))
    model_export(pizza_model, join(this_folder, 'program.dot'))

    pizza = Pizza()
    pizza.interpret(pizza_model)

if __name__ == "__main__":
    main()
