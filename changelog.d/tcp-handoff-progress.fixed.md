Keep a live TCP fallback lane running after the QUIC recovery manager exits,
instead of aborting pending transfers before the new lane can acknowledge
them. Transfers still fail within the existing no-progress timeout.
