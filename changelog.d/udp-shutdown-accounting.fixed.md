Recheck service cancellation before recording a failed UDP association, so a
transport error racing service shutdown does not count a clean shutdown as a
failed flow. Normal transport failures still retain their failure count.
