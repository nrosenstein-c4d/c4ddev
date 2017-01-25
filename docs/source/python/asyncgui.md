# Async GUI

Just like in many other GUI frameworks and applications, you can not operate
with the GUI layer from any but the main thread in Cinema 4D. If you do
processing in a separate thread and need to update some progress bar in your
dialog, you have to use the message queue in Cinema 4D, via `c4d.EventAdd()`
or `c4d.SpecialEventAdd()`.

The [`nr.concurrency`][0] module provides a lot of utility to work with
background procedures inside of (but not limited to) Cinema 4D. It provides a
`Synchronizable` base-class,an event-notification system, futures and more!

!!!note
    Be sure to read the information on [Third Party Modules](../localimport) first.

```python
with localimport('res/modules'):
  from nr import concurrency

events = concurrency.EventQueue()
# Allow dispose of old events of the same type, so we don't get to process
# multiple events of the same type with different data, but only the most recent.
events.new_event_type('progress-update', mergable=True)
events.new_event_type('status-update', mergable=True)

class MyDialog(c4d.gui.GeDialog):

  def __init__(self):
    super(MyDialog, self).__init__()

  def on_event(self, event, data):
    # Called from the main thread!
    if event == 'progress-update':
      pass
    elif event == 'status-update':
      pass

  def CoreMessage(self, msg_type, bc):
    if msg_type == c4d.EVMSG_CHANGE:
      for event in events.pop_events():
        self.on_event(event.type, event.data)
    return super(MyDialog, self).CoreMessage(msg_type, bc)


def some_function_from_a_thread():
  # ...
  events.add_event('progress-update', {'progress': 50.0})
```

  [0]: https://niklasrosenstein.github.io/py-nr/concurrency/
