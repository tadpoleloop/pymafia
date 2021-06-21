# pymafia

This library gives you full headless mafia control by reflecting kolmafia.jar into python.

You can launch the gui with `km.launch_gui()`, you can login with `km.login(username)`, and you can launch the relay server with `km.launch_relay_server()`
* You can execute arbitary gcli code with `km.cli`
* You can execute a single line of ash code with `km.ash`
* You can access preferences with `km.get_property` and set them with `km.set_property`
* You can also access any public mafia class via `km.<MafiaClass>`

Example usage:
```python
from kolmafia import km
km.login("devster6")
km.ash("my_name()")
```
> "devster6"
