import inspect


class Serializable:
    def to_dict(self):
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue

            if isinstance(value, Serializable):
                result[key] = value.to_dict()
            elif (
                isinstance(value, list) and value and isinstance(value[0], Serializable)
            ):
                result[key] = [v.to_dict() for v in value]
            elif isinstance(value, tuple):
                result[key] = list(value)
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data):
        sig = inspect.signature(cls.__init__)
        params = {}

        for param_name in sig.parameters:
            if param_name == "self":
                continue

            if param_name in data:
                value = data[param_name]

                param_annotation = sig.parameters[param_name].annotation
                if "Tuple" in str(param_annotation) and isinstance(value, list):
                    value = tuple(value)

                params[param_name] = value
            elif sig.parameters[param_name].default != inspect.Parameter.empty:
                params[param_name] = sig.parameters[param_name].default

        return cls(**params)
