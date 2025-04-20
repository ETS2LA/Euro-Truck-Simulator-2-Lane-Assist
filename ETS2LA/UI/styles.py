from dataclasses import dataclass
from typing import Optional, Literal
import json


@dataclass
class Style:
    """
    This class contains most of the CSS properties that are available
    in the style attribute of HTML elements. You can use it to add custom
    styling to any of the ETS2LA widgets.
    
    This style class always takes precedence over the default values for
    widgets.
    """
    
    # Layout
    display: Optional[Literal[
        "block", "inline", "inline-block", "flex", "inline-flex",
        "grid", "inline-grid", "none", "contents", "table"
    ]] = None

    position: Optional[Literal[
        "static", "relative", "absolute", "fixed", "sticky"
    ]] = None

    top: Optional[str] = None
    right: Optional[str] = None
    bottom: Optional[str] = None
    left: Optional[str] = None

    float: Optional[Literal["left", "right", "none", "inline-start", "inline-end"]] = None
    clear: Optional[Literal["none", "left", "right", "both", "inline-start", "inline-end"]] = None
    z_index: Optional[str] = None

    overflow: Optional[Literal["visible", "hidden", "scroll", "auto", "clip"]] = None
    overflow_x: Optional[Literal["visible", "hidden", "scroll", "auto", "clip"]] = None
    overflow_y: Optional[Literal["visible", "hidden", "scroll", "auto", "clip"]] = None

    # Flex/Grid
    flex: Optional[str] = None
    flex_direction: Optional[Literal["row", "row-reverse", "column", "column-reverse"]] = None
    flex_wrap: Optional[Literal["nowrap", "wrap", "wrap-reverse"]] = None

    justify_content: Optional[Literal[
        "flex-start", "flex-end", "center",
        "space-between", "space-around", "space-evenly"
    ]] = None

    align_items: Optional[Literal[
        "stretch", "flex-start", "flex-end", "center", "baseline"
    ]] = None

    align_self: Optional[Literal[
        "auto", "flex-start", "flex-end", "center", "baseline", "stretch"
    ]] = None

    gap: Optional[str] = None

    grid_template_columns: Optional[str] = None
    grid_template_rows: Optional[str] = None
    grid_column: Optional[str] = None
    grid_row: Optional[str] = None

    # Sizing
    width: Optional[str] = None
    min_width: Optional[str] = None
    max_width: Optional[str] = None
    height: Optional[str] = None
    min_height: Optional[str] = None
    max_height: Optional[str] = None

    # Spacing
    margin: Optional[str] = None
    margin_top: Optional[str] = None
    margin_right: Optional[str] = None
    margin_bottom: Optional[str] = None
    margin_left: Optional[str] = None

    padding: Optional[str] = None
    padding_top: Optional[str] = None
    padding_right: Optional[str] = None
    padding_bottom: Optional[str] = None
    padding_left: Optional[str] = None

    # Border
    border: Optional[str] = None
    border_top: Optional[str] = None
    border_right: Optional[str] = None
    border_bottom: Optional[str] = None
    border_left: Optional[str] = None
    border_radius: Optional[str] = None
    border_color: Optional[str] = None
    border_style: Optional[Literal[
        "none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"
    ]] = None
    border_width: Optional[str] = None

    # Background
    background: Optional[str] = None
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    background_position: Optional[str] = None
    background_size: Optional[Literal["auto", "cover", "contain"]] = None
    background_repeat: Optional[Literal["repeat", "no-repeat", "repeat-x", "repeat-y"]] = None

    # Typography
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[Literal[
        "normal", "bold", "lighter", "bolder", "100", "200", "300", "400",
        "500", "600", "700", "800", "900"
    ]] = None

    line_height: Optional[str] = None
    letter_spacing: Optional[str] = None

    text_align: Optional[Literal[
        "left", "right", "center", "justify", "start", "end"
    ]] = None

    text_decoration: Optional[Literal[
        "none", "underline", "overline", "line-through"
    ]] = None

    text_transform: Optional[Literal[
        "none", "capitalize", "uppercase", "lowercase"
    ]] = None

    white_space: Optional[Literal[
        "normal", "nowrap", "pre", "pre-line", "pre-wrap"
    ]] = "pre-wrap"

    word_break: Optional[Literal[
        "normal", "break-word", "break-all", "keep-all"
    ]] = None

    color: Optional[str] = None

    # Effects
    box_shadow: Optional[str] = None
    opacity: Optional[str] = None
    visibility: Optional[Literal["visible", "hidden", "collapse"]] = None
    transition: Optional[str] = None
    animation: Optional[str] = None
    transform: Optional[str] = None
    filter: Optional[str] = None

    cursor: Optional[Literal[
        "auto", "default", "pointer", "wait", "text", "move", "not-allowed",
        "crosshair", "grab", "grabbing"
    ]] = None

    # Misc
    user_select: Optional[Literal["auto", "none", "text", "all"]] = None
    pointer_events: Optional[Literal["auto", "none"]] = None
    content: Optional[str] = None

    # Catch-all for raw/unrecognized styles
    classname: Optional[str] = None
    """
    This classname is used to add custom Tailwind classes to the widget.
    By default it will override the default classes, but you can do the following
    to append them instead:
    ```python
    Style(classname="default p-4 bg-blue-500")
    ```
    Where `default` is the default class name for the widget. This way you can
    either prioritize the default classes or append them to the custom ones.
    """

    def to_dict(self) -> dict:
        base = {
            k.replace('_', '-'): v
            for k, v in self.__dict__.items()
            if v is not None
        }
        return base
    
    def __add__(self, other: "Style") -> "Style":
        if not isinstance(other, Style):
            raise TypeError("Can only add Style objects")
        
        self_dict = self.to_dict()
        self_classname = self_dict.pop("classname", None)
        other_dict = other.to_dict()
        other_classname = other_dict.pop("classname", None)
        
        if "default" in self_classname:
            if other_classname and "default" in other_classname:
                other_classname = other_classname.replace("default", "")
                
        combined = {**self_dict, **other_dict}
        combined_classname = f"{self_classname} {other_classname}".strip()
        combined["classname"] = combined_classname
        
        # Replace - in keys to _ for compatibility with the Style class
        combined = {
            k.replace("-", "_"): v
            for k, v in combined.items()
        }
        
        return Style(**combined)

@dataclass
class Title(Style):
    classname: str | None = "text-lg font-semibold default"
    font_size: str | None = "1.125rem"
    font_weight: Literal['normal', 'bold', 'lighter', 'bolder', '100', '200', '300', '400', '500', '600', '700', '800', '900'] | None = "600"

@dataclass
class Description(Style):
    classname: str | None = "text-sm text-muted-foreground default"
    
@dataclass
class PlainText(Style):
    classname: str | None = "text-sm default"
    
@dataclass
class FlexHorizontal(Style):
    classname: str | None = "default flex flex-row gap-2"
    
@dataclass
class FlexVertical(Style):
    classname: str | None = "default flex flex-col gap-2"
    
@dataclass
class Padding(Style):
    def __init__(self, padding: str):
        super().__init__()
        self.padding = padding
        
@dataclass 
class MaxWidth(Style):
    def __init__(self, width: str):
        super().__init__()
        self.max_width = width
        
@dataclass
class MaxHeight(Style):
    def __init__(self, height: str):
        super().__init__()
        self.max_height = height
        
@dataclass
class MinWidth(Style):
    def __init__(self, width: str):
        super().__init__()
        self.min_width = width
        
@dataclass
class MinHeight(Style):
    def __init__(self, height: str):
        super().__init__()
        self.min_height = height
        
@dataclass
class Width(Style):
    def __init__(self, width: str):
        super().__init__()
        self.width = width
        
@dataclass
class Height(Style):
    def __init__(self, height: str):
        super().__init__()
        self.height = height
        
@dataclass
class Gap(Style):
    def __init__(self, gap: str):
        super().__init__()
        self.gap = gap
        
@dataclass
class Margin(Style):
    def __init__(self, margin: str):
        super().__init__()
        self.margin = margin
        
@dataclass
class Classname(Style):
    def __init__(self, classname: str):
        super().__init__()
        self.classname = classname