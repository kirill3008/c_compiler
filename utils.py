def to_str_column(data: str, index: int) -> tuple[int, int]:
    line_index = 1
    for line in data.split('\n'):
        if index > len(line) + 1:
            index -= len(line) + 1
            line_index += 1
            continue
        return line_index, index + 1
    return -1, -1
