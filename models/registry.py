from typing import Type, Literal, Dict, Union
from pydantic import BaseModel, create_model

_command_registry: Dict[str, Type[BaseModel]] = {}


def register_command(name: str):
    def decorator(params_model: Type[BaseModel]):
        command_model = create_model(
            f"{name.title().replace('_', '')}Command",
            command=(Literal[name], ...),
            parameters=(params_model, ...),
            __base__=BaseModel,
        )
        _command_registry[name] = command_model
        return params_model
    return decorator


def get_command_union() -> Type[BaseModel]:
    if not _command_registry:
        raise RuntimeError("No commands registered.")
    return Union[tuple(_command_registry.values())]


def get_registered_commands() -> Dict[str, Type[BaseModel]]:
    return _command_registry
