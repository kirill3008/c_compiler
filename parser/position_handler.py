class FileAwarePosition():
    def __init__(self, content: str):
        self._lines_length = self._get_lines_length(content)
        self.total_len = sum(self._lines_length)

    @staticmethod
    def _get_lines_length(content: str) -> list[int]:
        return [len(line) + 1 for line in content.split('\n')]

    def _get_file_position(self, offset: int) -> str:
        if offset > self.total_len:
            raise ValueError(f'Offset {offset} outside of file')
        line_index = 0
        for line in self._lines_length:
            if offset < line:
                break
            offset -= line
            line_index += 1
        return f'{line_index + 1}:{offset + 1}'

    def error(self, template: str, *args: int, **kwargs: int):
        return SyntaxError(self.string(template, *args, **kwargs))

    def string(self, template: str, *args: int, **kwargs: int):
        pos_args = []
        for arg in args:
            pos_args.append(self._get_file_position(arg))
        key_args = {}
        for key, value in kwargs.items():
            key_args[key] = self._get_file_position(value)
        return template.format(*pos_args, **key_args)

    def convert(self, position: tuple | list | int):
        if isinstance(position, tuple):
            return tuple(self._get_file_position(p) for p in position)
        if isinstance(position, list):
            return tuple(self._get_file_position(p) for p in position)
        if isinstance(position, int):
            return self._get_file_position(position)
        raise ValueError(f'Don\'t know how to process position of type {type(position)}')
