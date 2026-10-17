Acknowledged application messages no longer trigger lane rescue merely because
no response arrives within three round trips. The watchdog now requires
outstanding transport delivery, avoiding repeated recovery for slow origins,
one-way messages and quiet browser connections. Recovery races only QUIC
JOINs; an irreversible TCP handoff starts after the QUIC phase fails, so a
losing TCP attempt cannot retire the client's winning QUIC lane. Cancelling a
recovery attempt also interrupts its JOIN handshake instead of leaving it
blocked until the handshake timeout.
Delayed replay of already-delivered bytes after FIN is acknowledged instead
of aborting a completed response; data extending past FIN remains an error.
