from PIL import Image, ImageDraw
import numpy as np
import math
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt

# ================== EMOJI MAPPING ==================
emoji_map = {
    'A':'😀','B':'😁','C':'😂','D':'🤣','E':'😃','F':'😄','G':'😅','H':'😆',
    'I':'😉','J':'😊','K':'😋','L':'😎','M':'😍','N':'😘','O':'😗','P':'😙',
    'Q':'😚','R':'🙂','S':'🤗','T':'🤩','U':'🤔','V':'🤨','W':'😐','X':'😑',
    'Y':'😶','Z':'🙄','a':'😏','b':'😣','c':'😥','d':'😮','e':'🤐','f':'😯',
    'g':'😪','h':'😫','i':'🥱','j':'😴','k':'😌','l':'😛','m':'😜','n':'😝',
    'o':'🤤','p':'😒','q':'😓','r':'😔','s':'😕','t':'🙃','u':'🤑','v':'😲',
    'w':'☹','x':'🙁','y':'😖','z':'😞',
    '0':'😟','1':'😤','2':'😢','3':'😭','4':'😦','5':'😧',
    '6':'😨','7':'😩','8':'🤯','9':'😬',
    ' ':'⬜',

    '!':'🧐','@':'🤓','#':'😇','$':'🥳','%':'🥰','^':'😈','&':'👀','*':'👁️',
    '(':'🔥',')':'⭐','-':'⚡','_':'💡','=':'🎯','+':'🚀',
    '[':'🔒',']':'🔑','{':'📌','}':'📎','\\':'✉️','|':'📁',
    ';':'📂',':':'📝','\'':'💻','"':'🖥️',
    ',':'📱','<':'🧠','.':'🛡️','>':'🧩','/':'⬛','?':'⬜',
    '`':'🔴','~':'🟢'
}

reverse_map = {v: k for k, v in emoji_map.items()}

# ================== TEXT ↔ EMOJI ==================
def text_to_emoji(text):
    return ''.join(emoji_map.get(ch, ch) for ch in text)

def emoji_to_text(emoji_text):
    return ''.join(reverse_map.get(ch, ch) for ch in emoji_text)

# ================== TEXT ↔ BINARY ==================
def text_to_binary(text):
    return ''.join(format(b, '08b') for b in text.encode('utf-8'))

def binary_to_text(binary):
    data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
    return data.decode('utf-8', errors='ignore')

# ================== IMAGE ENCODE ==================
def encode_image(input_path, emoji_msg, output_path):
    img = Image.open(input_path).convert("RGB")
    binary = text_to_binary(emoji_msg) + "1111111111111110"

    data = np.array(img).flatten()

    if len(binary) > len(data):
        raise ValueError("Message too large for this image")

    for i in range(len(binary)):
        data[i] = (data[i] & 254) | int(binary[i])

    stego = data.reshape(np.array(img).shape)
    Image.fromarray(stego.astype(np.uint8)).save(output_path)

    return binary

# ================== IMAGE DECODE ==================
def decode_image(path):
    img = Image.open(path).convert("RGB")
    data = np.array(img).flatten()

    binary = ""
    for val in data:
        binary += str(val & 1)
        if binary.endswith("1111111111111110"):
            break

    emoji_msg = binary_to_text(binary[:-16])
    return emoji_to_text(emoji_msg), emoji_msg, binary[:-16]

# ================== LSB OVERLAY ==================
def visualize_lsb_changes_overlay(original_path, stego_path, output_path="overlay.png"):
    o = np.array(Image.open(original_path).convert("RGB"))
    s = np.array(Image.open(stego_path).convert("RGB"))

    overlay = Image.fromarray(s.copy())
    draw = ImageDraw.Draw(overlay)

    for y in range(o.shape[0]):
        for x in range(o.shape[1]):
            if any((o[y, x, c] & 1) != (s[y, x, c] & 1) for c in range(3)):
                draw.point((x, y), fill=(255, 0, 0))

    overlay.save(output_path)
    return output_path

# ================== PIXEL BINARY CHANGES ==================
def pixel_binary_changes(original, stego, position):
    y, x = position
    o = np.array(Image.open(original))
    s = np.array(Image.open(stego))

    result = {}
    channels = ['R', 'G', 'B']
    for i, ch in enumerate(channels):
        result[ch] = {
            'orig': format(o[y, x, i], '08b'),
            'stego': format(s[y, x, i], '08b')
        }
    return result

# ================== PIXEL CHANGE STATS ==================
def pixel_change_stats(original, stego):
    o = np.array(Image.open(original))
    s = np.array(Image.open(stego))

    changed = np.sum((o & 1) != (s & 1))
    total = o.size
    unchanged = total - changed

    return {
        "Changed": changed,
        "Unchanged": unchanged,
        "Total": total
    }

# ================== BAR GRAPH ==================
def plot_pixel_changes(stats):
    fig, ax = plt.subplots()
    ax.bar(stats.keys(), stats.values())
    ax.set_title("Pixel Bit Changes")
    ax.set_ylabel("Count")
    return fig

# ================== PERFORMANCE METRICS ==================
def calculate_metrics(original, stego):
    o = np.array(Image.open(original).convert("RGB")).astype(np.float64)
    s = np.array(Image.open(stego).convert("RGB")).astype(np.float64)

    mse = np.mean((o - s) ** 2)
    psnr = float('inf') if mse == 0 else 10 * math.log10((255 ** 2) / mse)

    data_range = o.max() - o.min()
    ssim_val = ssim(o, s, channel_axis=2, data_range=data_range)

    return mse, psnr, ssim_val
