##kyc/phash.py — The pHash Algorithm:
resize_image()      → Opens image, converts to grayscale, resizes to 32x32
get_pixels()        → Reads all pixel brightness values into a grid
apply_dct()         → Applies DCT math (frequency conversion)
get_top_left()      → Takes only the 8x8 most important values
compute_phash()     → Runs all steps, returns a hex hash string like "f8a3c2..."
hamming_distance()  → Counts how many bits differ between two hashes
check_duplicate()   → Flags if distance < 10 (too similar = possible duplicate)

##kyc/views.py — How pHash is used on upload:
User uploads document
        ↓
compute_phash(image) → generates hash e.g. "f8a3c2b1..."
        ↓
check_duplicate(hash, all_other_docs) → compares against every other document
        ↓
If distance < 10 → flag document as suspicious
        ↓
Save hash + flag to database
        ↓
Staff sees ⚠ warning badge on flagged documents