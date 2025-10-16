from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
 # ================== EMOJI MAPPING ==================
emoji_map = {
    'A': '😀', 'B': '😁', 'C': '😂', 'D': '🤣', 'E': '😃', 'F': '😄',
    'G': '😅', 'H': '😆', 'I': '😉', 'J': '😊', 'K': '😋', 'L': '😎',
    'M': '😍', 'N': '😘', 'O': '😗', 'P': '😙', 'Q': '😚', 'R': '🙂',
    'S': '🤗', 'T': '🤩', 'U': '🤔', 'V': '🤨', 'W': '😐', 'X': '😑',
    'Y': '😶', 'Z': '🙄', 'a': '😏', 'b': '😣', 'c': '😥', 'd': '😮',
    'e': '🤐', 'f': '😯', 'g': '😪', 'h': '😫', 'i': '🥱', 'j': '😴',
    'k': '😌', 'l': '😛', 'm': '😜', 'n': '😝', 'o': '🤤', 'p': '😒',
    'q': '😓', 'r': '😔', 's': '😕', 't': '🙃', 'u': '🤑', 'v': '😲',
    'w': '☹', 'x': '🙁', 'y': '😖', 'z': '😞', '0': '😟', '1': '😤',
    '2': '😢', '3': '😭', '4': '😦', '5': '😧', '6': '😨', '7': '😩',
    '8': '🤯', '9': '😬', ' ': '⬜'
}
reverse_map = {v: k for k, v in emoji_map.items()}

# ================== TEXT ↔ EMOJI ↔ BINARY ==================
def text_to_emoji(text):
    return ''.join(emoji_map.get(ch, ch) for ch in text)

def emoji_to_text(emoji_str):
    return ''.join(reverse_map.get(ch, ch) for ch in emoji_str)

def text_to_binary(text):
    return ''.join(format(b,'08b') for b in text.encode('utf-8'))

def binary_to_text(binary_str):
    bytes_data = bytes(int(binary_str[i:i+8],2)for i in range(0,len(binary_str),8))
    return bytes_data.decode('utf-8',errors='ignore')

# ================== IMAGE ENCODE/DECODE ==================
def encode_image(img_path, emoji_message, output_path):
    img = Image.open(img_path).convert("RGB")
    binary_msg = text_to_binary(emoji_message) + "1111111111111110"  # EOF delimiter

    data = np.array(img)
    flat_data = data.flatten()

    for i in range(len(binary_msg)):
        flat_data[i] = np.uint8((flat_data[i] & 254) | int(binary_msg[i]))


    encoded_img = flat_data.reshape(data.shape)
    Image.fromarray(encoded_img.astype('uint8')).save(output_path)
    return binary_msg

def decode_image(img_path):
    img = Image.open(img_path).convert("RGB")
    data = np.array(img)
    flat_data = data.flatten()

    binary_msg = ""
    for i in range(len(flat_data)):
        binary_msg += str(flat_data[i] & 1)
        if binary_msg.endswith("1111111111111110"):
            break

    secret_emoji = binary_to_text(binary_msg[:-16])
    secret_text = emoji_to_text(secret_emoji)
    return secret_text, secret_emoji, binary_msg[:-16]

# ================== PIXEL CHANGE VISUALIZATION ==================
def visualize_lsb_changes_overlay(orig_path, stego_path):
    orig = np.array(Image.open(orig_path).convert("RGB"))
    stego = np.array(Image.open(stego_path).convert("RGB"))
    overlay_img = Image.open(stego_path).convert("RGB")
    draw = ImageDraw.Draw(overlay_img)

    rows, cols, _ = orig.shape
    for y in range(rows):
        for x in range(cols):
            for c in range(3):
                if (orig[y,x,c] & 1) != (stego[y,x,c] & 1):
                    draw.rectangle([x, y, x, y], fill=(255,0,0))
                    break
    overlay_path = "overlay.png"
    overlay_img.save(overlay_path)
    return overlay_path

def pixel_binary_changes(orig_path, stego_path, pixel):
    row, col = pixel
    orig = np.array(Image.open(orig_path).convert("RGB")).astype(np.int32)
    stego = np.array(Image.open(stego_path).convert("RGB")).astype(np.int32)

    changes = {}
    for i, channel in enumerate(["Red", "Green", "Blue"]):
        changes[channel] = {
            "orig": str(orig[row, col, i] & 1),
            "stego": str(stego[row, col, i] & 1)
        }
    return changes

# ================== PIXEL CHANGE STATS & BAR CHART ==================
def pixel_change_stats(orig_path, stego_path):
    orig = np.array(Image.open(orig_path).convert("RGB")).astype(np.int32)
    stego = np.array(Image.open(stego_path).convert("RGB")).astype(np.int32)

    flat_orig = orig.flatten()
    flat_stego = stego.flatten()

    changed = np.sum((flat_orig & 1) != (flat_stego & 1))
    unchanged = len(flat_orig) - changed

    return {"Changed": int(changed), "Unchanged": int(unchanged), "Total": len(flat_orig)}

def plot_pixel_changes(stats):
    fig, ax = plt.subplots()
    ax.bar(["Unchanged", "Changed"], [stats["Unchanged"], stats["Changed"]], color=["green","red"])
    ax.set_title(f"Pixel Change Summary (Total pixels: {stats['Total']})")
    ax.set_ylabel("Number of Pixels")
    return fig
