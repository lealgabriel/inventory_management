from typing import Union

JsonSerializable = Union[
    dict[str, 'JsonSerializable'],
    dict[str, str],
    dict[str, int],
    dict[str, float],
    dict[str, bool],
    dict[str, None],
    list['JsonSerializable'],
    list[str],
    list[int],
    list[float],
    list[bool],
    list[None],
    str,
    int,
    float,
    bool,
    None,
]