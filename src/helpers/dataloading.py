
from pydantic import BaseModel as PydanticBaseModel

# https://github.com/samuelcolvin/pydantic/issues/1168
# Loading nested data without validation is not supported in the lib
class BaseModel(PydanticBaseModel):
    @classmethod
    def construct(cls, _fields_set=None, **values):

        m = cls.__new__(cls)
        fields_values = {}

        for name, field in cls.__fields__.items():
            key = field.alias  # this is the current behaviour of `__init__` by default
            if key:
                if issubclass(field.type_, BaseModel):
                    if field.shape == 2:  # the field is a `list`. You could check other shapes to handle `tuple`, ...
                        fields_values[name] = [
                            field.type_.construct(**e)
                            for e in values[key]
                        ]
                    else:
                        fields_values[name] = field.outer_type_.construct(**values[key])
                else:
                    if values[key] is None and not field.required:
                        fields_values[name] = field.get_default()
                    else:
                        fields_values[name] = values[key]
            elif not field.required:
                fields_values[name] = field.get_default()

        object.__setattr__(m, '__dict__', fields_values)
        if _fields_set is None:
            _fields_set = set(values.keys())
        object.__setattr__(m, '__fields_set__', _fields_set)
        m._init_private_attributes()
        return m

