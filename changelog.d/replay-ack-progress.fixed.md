Keep ACK recovery progressing on reused, bidirectional connections. Replayed
DATA re-emits the cumulative ACK, new lanes receive the current ACK state,
and ACK writes prefer lanes that are not suspected stalled. Ordinary ACKs no
longer wait behind blocked application delivery. Already-delivered replay
ending exactly at the receive cursor no longer consumes the reassembly
window; segments crossing that cursor are rejected as overlaps.
