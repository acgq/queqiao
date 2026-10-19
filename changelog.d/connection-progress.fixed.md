Keep reverse-direction ACKs readable when application delivery fills the
receive event queue, using a bounded overflow queue. Frame-write deadlines
now include writer-lock waits and cancellation interrupts blocked writes.
Repeated selective ACKs no longer reset the stall detector, and ranges beyond
sent data are rejected. Outstanding work shares one 45-second no-progress
budget across recovery attempts; blocked application writes have the same
budget, renewed on partial progress. Idle connections are unaffected.

Remove the extra exponential stall-rescue backoff and allow immediate AUTO
TCP handoff after a QUIC rescue race encounters lane-capacity refusals.
Suspected stalled lanes can be replaced without waiting for the young-lane
protection interval. Memory bounds and healthy racing-lane protection remain.

Stop and join the previous UDP relay reader before publishing its socket for
resumption, preventing it from consuming replies meant for the replacement.

Do not race a rescue JOIN against an unconfirmed optimistic OPEN. Remote
RESET and full-close cancellation bypass paused application delivery.
