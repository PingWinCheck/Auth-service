def camel_case_to_snake_case(input_str: str) -> str:
    if not isinstance(input_str, str):
        raise TypeError(f"Expected an str, got {type(input_str).__name__} instead")
    if not input_str:
        raise ValueError("Expected non-empty string")
    buffer = [input_str[0].lower()]

    for i in range(1, len(input_str)):
        prev = i - 1
        next_ = i + 1
        if next_ < len(input_str):
            if (
                input_str[prev].islower()
                and input_str[i].isupper()
                or input_str[i].isupper()
                and input_str[next_].islower()
            ):
                buffer.append("_")
        elif input_str[prev].islower() and input_str[i].isupper():
            buffer.append("_")
        buffer.append(input_str[i].lower())

    return "".join(buffer)
