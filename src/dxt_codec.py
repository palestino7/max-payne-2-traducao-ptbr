import os
import numpy as np
from PIL import Image

def encode_dxt1_blocks(rgb_arr):
    """
    Vectorized DXT1 encoder in NumPy for an (H, W, 3) uint8 array.
    Returns (H//4, W//4, 8) uint8 array of DXT1 blocks.
    """
    h, w, _ = rgb_arr.shape
    nb_y, nb_x = h // 4, w // 4
    blocks = rgb_arr.reshape(nb_y, 4, nb_x, 4, 3).transpose(0, 2, 1, 3, 4).reshape(nb_y, nb_x, 16, 3).astype(np.float32)

    lum = blocks[:, :, :, 0] * 0.299 + blocks[:, :, :, 1] * 0.587 + blocks[:, :, :, 2] * 0.114
    min_idx = np.argmin(lum, axis=2)
    max_idx = np.argmax(lum, axis=2)

    idx_grid_y, idx_grid_x = np.meshgrid(np.arange(nb_y), np.arange(nb_x), indexing='ij')
    c_min = blocks[idx_grid_y, idx_grid_x, min_idx]
    c_max = blocks[idx_grid_y, idx_grid_x, max_idx]

    def to_rgb565(c):
        r = np.clip(np.round(c[:, :, 0] * 31.0 / 255.0), 0, 31).astype(np.uint16)
        g = np.clip(np.round(c[:, :, 1] * 63.0 / 255.0), 0, 63).astype(np.uint16)
        b = np.clip(np.round(c[:, :, 2] * 31.0 / 255.0), 0, 31).astype(np.uint16)
        return (r << 11) | (g << 5) | b, r, g, b

    c0_565, r0, g0, b0 = to_rgb565(c_max)
    c1_565, r1, g1, b1 = to_rgb565(c_min)

    swap = c0_565 < c1_565
    c0_565_s = np.where(swap, c1_565, c0_565)
    c1_565_s = np.where(swap, c0_565, c1_565)
    r0_s = np.where(swap, r1, r0); g0_s = np.where(swap, g1, g0); b0_s = np.where(swap, b1, b0)
    r1_s = np.where(swap, r0, r1); g1_s = np.where(swap, g0, g1); b1_s = np.where(swap, b0, b1)

    p0 = np.stack([r0_s * 255.0 / 31.0, g0_s * 255.0 / 63.0, b0_s * 255.0 / 31.0], axis=-1)
    p1 = np.stack([r1_s * 255.0 / 31.0, g1_s * 255.0 / 63.0, b1_s * 255.0 / 31.0], axis=-1)
    p2 = (2.0 * p0 + p1) / 3.0
    p3 = (p0 + 2.0 * p1) / 3.0

    palette = np.stack([p0, p1, p2, p3], axis=2)  # (nb_y, nb_x, 4, 3)
    diff = blocks[:, :, :, None, :] - palette[:, :, None, :, :]
    dist = np.sum(diff * diff, axis=-1)  # (nb_y, nb_x, 16, 4)
    best_idx = np.argmin(dist, axis=-1).astype(np.uint32)  # (nb_y, nb_x, 16)

    equal_mask = (c0_565_s == c1_565_s)
    best_idx = np.where(equal_mask[:, :, None], 0, best_idx)

    shifts = (np.arange(16, dtype=np.uint32) * 2).reshape(1, 1, 16)
    packed_indices = np.sum(best_idx << shifts, axis=2, dtype=np.uint32)

    out = np.zeros((nb_y, nb_x, 8), dtype=np.uint8)
    out[:, :, 0] = (c0_565_s & 0xFF).astype(np.uint8)
    out[:, :, 1] = ((c0_565_s >> 8) & 0xFF).astype(np.uint8)
    out[:, :, 2] = (c1_565_s & 0xFF).astype(np.uint8)
    out[:, :, 3] = ((c1_565_s >> 8) & 0xFF).astype(np.uint8)
    out[:, :, 4] = (packed_indices & 0xFF).astype(np.uint8)
    out[:, :, 5] = ((packed_indices >> 8) & 0xFF).astype(np.uint8)
    out[:, :, 6] = ((packed_indices >> 16) & 0xFF).astype(np.uint8)
    out[:, :, 7] = ((packed_indices >> 24) & 0xFF).astype(np.uint8)
    return out


def encode_dxt3_blocks(rgba_arr):
    """
    Vectorized DXT3 encoder in NumPy for an (H, W, 4) uint8 array.
    Returns (H//4, W//4, 16) uint8 array of DXT3 blocks.
    """
    h, w, _ = rgba_arr.shape
    nb_y, nb_x = h // 4, w // 4
    color_blocks = encode_dxt1_blocks(rgba_arr[:, :, :3])
    alpha = rgba_arr[:, :, 3].reshape(nb_y, 4, nb_x, 4).transpose(0, 2, 1, 3).reshape(nb_y, nb_x, 16)
    a4 = np.clip(np.round(alpha.astype(np.float32) * 15.0 / 255.0), 0, 15).astype(np.uint8)
    alpha_bytes = (a4[:, :, 0::2] | (a4[:, :, 1::2] << 4)).astype(np.uint8)  # (nb_y, nb_x, 8)
    return np.concatenate([alpha_bytes, color_blocks], axis=2)


def patch_dds_dxt1(orig_dds_path, new_rgb_arr, out_dds_paths):
    with open(orig_dds_path, 'rb') as f:
        orig_bytes = bytearray(f.read())
    orig_rgb = np.array(Image.open(orig_dds_path).convert('RGB'))
    h, w, _ = orig_rgb.shape
    nb_y, nb_x = h // 4, w // 4

    diff = np.any(orig_rgb != new_rgb_arr, axis=-1)
    block_diff = np.any(diff.reshape(nb_y, 4, nb_x, 4), axis=(1, 3))

    new_blocks = encode_dxt1_blocks(new_rgb_arr)
    orig_blocks = np.frombuffer(orig_bytes, dtype=np.uint8, offset=128).reshape(nb_y, nb_x, 8).copy()
    orig_blocks[block_diff] = new_blocks[block_diff]

    patched_bytes = bytes(orig_bytes[:128]) + orig_blocks.tobytes()
    for p in out_dds_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(patched_bytes)
    return int(np.sum(block_diff))


def patch_dds_dxt3(orig_dds_path, new_rgba_arr, out_dds_paths):
    with open(orig_dds_path, 'rb') as f:
        orig_bytes = bytearray(f.read())
    orig_rgba = np.array(Image.open(orig_dds_path).convert('RGBA'))
    h, w, _ = orig_rgba.shape
    nb_y, nb_x = h // 4, w // 4

    diff = np.any(orig_rgba != new_rgba_arr, axis=-1)
    block_diff = np.any(diff.reshape(nb_y, 4, nb_x, 4), axis=(1, 3))

    new_blocks = encode_dxt3_blocks(new_rgba_arr)
    orig_blocks = np.frombuffer(orig_bytes, dtype=np.uint8, offset=128).reshape(nb_y, nb_x, 16).copy()
    orig_blocks[block_diff] = new_blocks[block_diff]

    patched_bytes = bytes(orig_bytes[:128]) + orig_blocks.tobytes()
    for p in out_dds_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(patched_bytes)
    return int(np.sum(block_diff))
