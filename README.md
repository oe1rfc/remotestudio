
# RemoteStudio

This is a simple approach for a fully remote controlled multi-user video solution based
on an Atem videomixer and jitsi-meet as low-latency (multiview) video transport and conference solution.

it consists of:
* centralized webinterface for remote studio control, multi-user
* 'worker' clients
  * atem videomixer control
  * several display-clients as 'virtual cameras' eg jitsi

This should be considered a PoC and not a finished product.

# protocol ideas

## rooms and registration
  * for now room names are not fixed
  * users and workers join their channels by sending a `join` command with `room` and `type` arguments.
  * `type` may be one of `user`, `worker`
  * client type is saved in the `session['type']` to use the same websocket interface
  * main room of a client is saved in `session['room']`
### users

room for messages to user: `<room>_user`

### workers

room for messages to workers: `<room>_worker`

workers do have an ID, but all messages inside a room are transmitted to all workers
