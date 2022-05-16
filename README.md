# e2se-qb   📡

An enigma2 channel list editor – archived.

**This project is freezed in favour of this other: https://github.com/ctlcltd/e2-sat-editor.**

![screenshot](../res/enigma2-channel-editor.jpg)

If you are looking for a ready-to-use Python channel editor, you could try this one: https://github.com/DYefremov/DemonEditor.

I started this project starting from code of my remote controller here: https://github.com/ctlcltd/remote-gx-ir.

*At the moment it supports enigma lamedb version 4 only.*

My goal is obtain an almost fast editor, scriptable, to handle channel lists.

 
## Requirements

* Python >= 3.9
* Qt 6 - PySide 6 (gui: qt6)
* Tcl/Tk - Tkinter (gui: tk)


## Run the editor

- Before start, you need to install **python3** and **pip** (pip3):

https://www.python.org/downloads/

- Some dependencies are required to run it with GUI, you can choose Qt6 or Tk:
* To install Qt 6 - Pyside 6: ```python3 -m pip install pyside6```
* To install Tcl/Tk - Tkinter: ```python3 -m pip install tkinter```

- *Please note:* depending on your OS environment, you should install some dependencies to meet the GUI toolkit requirements.

- Then clone the repository:

```git clone https://github.com/ctlcltd/enigma2-channel-editor.git```

- To select the GUI toolkit, edit the *config.py* file, ```GUI_INTERFACE = 'qt6' # tk | qt6```

- Now you launch it from his folder:

```python3 -m pip python3 start.py```


## Development

To run with live reload, you need **watchdog**:

```python3 -m pip install watchdog```

Lauch with the following command:

```python3 live.py```

 
## Contributing

You can open [issues](https://github.com/ctlcltd/e2-sat-editor-qb/issues) to report bug, request features or send a [Pull Request](https://github.com/ctlcltd/e2-sat-editor-qb/pulls).


## License

[MIT License](LICENSE).
