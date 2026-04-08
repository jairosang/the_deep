# https://doc.mapeditor.org/en/latest/reference/global-tile-ids/ * mic drop *
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG = 0x40000000
FLIPPED_DIAGONALLY_FLAG = 0x20000000
DIAGONAL_FLIP_FLAG = 0x20000000
ALL_FLIP_FLAGS = (FLIPPED_HORIZONTALLY_FLAG | FLIPPED_VERTICALLY_FLAG | FLIPPED_DIAGONALLY_FLAG | FLIPPED_DIAGONALLY_FLAG)

# Just takes the info from the gid
def normalize_gid(encoded_gid: int) -> tuple[int, bool, bool, bool]:
    base_gid = encoded_gid & ~ALL_FLIP_FLAGS
    flip_h = bool(encoded_gid & FLIPPED_HORIZONTALLY_FLAG)
    flip_v = bool(encoded_gid & FLIPPED_VERTICALLY_FLAG)
    flip_diagonal = bool(encoded_gid & DIAGONAL_FLIP_FLAG)
    return base_gid, flip_h, flip_v, flip_diagonal