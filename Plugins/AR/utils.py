def is_circle_in_viewport(
    screen_center: tuple[float, ...] | None,
    radius: float,
    viewport_width: float,
    viewport_height: float,
) -> bool:
    if screen_center is None:
        return False

    x, y = screen_center[0], screen_center[1]

    return not (
        x + radius < 0
        or x - radius > viewport_width
        or y + radius < 0
        or y - radius > viewport_height
    )


def is_polygon_in_viewport(
    screen_points: list[tuple[float, ...]] | None,
    viewport_width: float,
    viewport_height: float,
) -> bool:
    if not screen_points or None in screen_points:
        return False

    x_coords = [point[0] for point in screen_points]
    y_coords = [point[1] for point in screen_points]

    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)

    return not (
        max_x < 0 or min_x > viewport_width or max_y < 0 or min_y > viewport_height
    )


def is_point_in_viewport(
    screen_point: tuple[float, ...] | None,
    viewport_width: float,
    viewport_height: float,
) -> bool:
    if screen_point is None:
        return False

    x, y = screen_point[0], screen_point[1]
    return 0 <= x <= viewport_width and 0 <= y <= viewport_height


def is_rectangle_in_viewport(
    screen_start: tuple[float, ...] | None,
    screen_end: tuple[float, ...] | None,
    viewport_width: float,
    viewport_height: float,
) -> bool:
    if screen_start is None or screen_end is None:
        return False

    min_x = min(screen_start[0], screen_end[0])
    max_x = max(screen_start[0], screen_end[0])
    min_y = min(screen_start[1], screen_end[1])
    max_y = max(screen_start[1], screen_end[1])

    return not (
        max_x < 0 or min_x > viewport_width or max_y < 0 or min_y > viewport_height
    )
