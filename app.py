import streamlit as st
from PIL import Image
import numpy as np
from backend1 import *

st.set_page_config(page_title="Image Steganography", layout="wide")
st.title("🖼️ Image Steganography using LSB with Emoji Mapping")

choice = st.sidebar.selectbox("Choose Action", ["Encode", "Decode"])

# ================== ENCODE ==================
if choice == "Encode":
    st.subheader("🔒 Encode a Secret Message")

    uploaded = st.file_uploader("Upload Image", ["png", "jpg", "jpeg"])
    message = st.text_input("Enter Secret Message")

    if uploaded and message:
        Image.open(uploaded).save("original.png")

        emoji_msg = text_to_emoji(message)
        binary = encode_image("original.png", emoji_msg, "stego.png")

        col1, col2 = st.columns(2)
        col1.image("original.png", caption="Original Image", use_container_width=True)
        col2.image("stego.png", caption="Stego Image", use_container_width=True)

        st.subheader("🔑 Emoji Mapping")
        st.code(emoji_msg)

        st.subheader("📟 Binary Representation")
        st.text_area("", binary, height=120)

        st.subheader("🔴 LSB Changes Visualization")
        overlay = visualize_lsb_changes_overlay("original.png", "stego.png")
        st.image(overlay, caption="Red pixels indicate LSB changes", use_container_width=True)

        st.subheader("🔎 Pixel Binary Inspection")
        img = np.array(Image.open("stego.png"))
        r = st.number_input("Row", 0, img.shape[0] - 1, 0)
        c = st.number_input("Column", 0, img.shape[1] - 1, 0)

        if st.button("Inspect Pixel"):
            st.json(pixel_binary_changes("original.png", "stego.png", (r, c)))

        stats = pixel_change_stats("original.png", "stego.png")
        st.pyplot(plot_pixel_changes(stats))

        st.markdown("### 📊 Pixel Change Summary")
        st.write(stats)

        with open("stego.png", "rb") as f:
            st.download_button("Download Encoded Image", f, "stego.png")

        mse, psnr, ssim_val = calculate_metrics("original.png", "stego.png")
        st.subheader("📈 Image Quality Metrics")
        st.write(f"MSE: {mse:.4f}")
        st.write(f"PSNR: {psnr:.2f} dB")
        st.write(f"SSIM: {ssim_val:.4f}")

# ================== DECODE ==================
else:
    st.subheader("🔓 Decode Hidden Message")

    uploaded = st.file_uploader("Upload Stego Image", ["png", "jpg", "jpeg"])

    if uploaded:
        Image.open(uploaded).save("uploaded.png")
        text, emoji, binary = decode_image("uploaded.png")

        st.image("uploaded.png", caption="Stego Image", use_container_width=True)
        st.success("Message decoded successfully!")

        st.subheader("📝 Decoded Text")
        st.write(text)

        st.subheader("🔑 Emoji Mapping")
        st.code(emoji)

        st.subheader("📟 Extracted Binary")
        st.text_area("", binary, height=120)
