import inspect
from tools.registry_v3 import RegistryV3

sig = inspect.signature(RegistryV3.execute_tool)
print('Registry.execute_tool signature:', sig)
print('Parameters:')
for name, param in sig.parameters.items():
    print(f'  {name}: {param.kind.name}, default={param.default}')
