# Forest theme for ttk


## How to use
### Python / tkinter
To use the theme just import the **forest-light.tcl**, or the **forest-dark.tcl** file, and call the `theme_use` method to set the theme:
```python
# Import the tcl file
root.tk.call('source', 'forest-light.tcl / forest-dark.tcl')

# Set the theme with the theme_use method
ttk.Style().theme_use('forest-light / forest-dark')
```

### Tcl / tk
To use the theme just import the **forest-light.tcl**, or the **forest-dark.tcl** file, and call the `theme use` method to set the theme:
```tcl
# Import the tcl file
source "forest-light.tcl / forest-dark.tcl"

# Set theme using the theme use method
ttk::style theme use forest-light / forest-dark
```

## New style elements
The Forest theme similar to my [Azure theme](https://github.com/rdbende/Azure-ttk-theme) has some **new** widget styles, such as an accent button, toggle switch, toggle button and card. You can apply these with the style option.

If you need a highlighted button, use `Accent.TButton`:
```python
button = ttk.Button(root, text='Accent button', style='Accent.TButton', command=callback)
```

To create a toggle button you need a checkbutton, to which you can apply the `ToggleButton` style:
```python
togglebutton = ttk.Checkbutton(root, text='Toggle button', style='ToggleButton', variable=var)
```

The use of switches is becoming more common these days, so this theme has a `Switch` style, that can be applied to checkbuttons:
```python
switch = ttk.Checkbutton(root, text='Switch', style='Switch', variable=var)
```

If you only want a border around your widgets, not an entire LabelFrame then apply the `Card` style to a Frame:
```python
card = ttk.Frame(root, style='Card', padding=(5, 6, 7, 8))
```

## A short example
for Python...
```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Import the tcl file
root.tk.call('source', 'forest-dark.tcl')

# Set the theme with the theme_use method
ttk.Style().theme_use('forest-dark')

# A themed (ttk) button
button = ttk.Button(root, text="I'm a themed button")
button.pack(pady=20)

root.mainloop()
```
...and for Tcl
```tcl
package require Tk 8.6

# Import the tcl file
source "forest-dark.tcl"

# Set theme using the theme use method
ttk::style theme use forest-dark

# A themed (ttk) button
ttk::button .button -text "I'm a themed button"
pack .button -pady 20
```
