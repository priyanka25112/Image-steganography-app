import streamlit as st
from PIL import Image
import numpy as np
from main import (
    text_to_emoji, encode_image, decode_image,
    visualize_lsb_changes_overlay, pixel_binary_changes,
    pixel_change_stats, plot_pixel_changes
)

# ================== STREAMLIT APP ==================
st.title("🖼️ Image Steganography with Emoji Mapping + Pixel Overlay")

choice = st.sidebar.selectbox("Choose Action", ["Encode", "Decode"])

if choice == "Encode":
    st.subheader("🔒 Encode a Secret Message")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    secret_text = st.text_input("Enter your secret text")

    if uploaded_file and secret_text:
        input_path = "temp.png"
        Image.open(uploaded_file).save(input_path)
        output_path = "stego.png"

        # Emoji mapping
        emoji_secret = text_to_emoji(secret_text)
        binary_msg = encode_image(input_path, emoji_secret, output_path)

        # Display info
        st.write("📝 Original Text:", secret_text)
        st.write("🔑 Emoji Mapping:", emoji_secret)

        # Display original and stego images side by side
        col1, col2 = st.columns(2)
        with col1:
            st.image(input_path, caption="Original Image", use_container_width=True)
        with col2:
            st.image(output_path, caption="Stego Image", use_container_width=True)

        # Binary representation
        st.subheader("📟 Binary Representation of Emoji Message")
        st.text_area("Binary", binary_msg, height=150)

        # Overlay visualization
        overlay_path = visualize_lsb_changes_overlay(input_path, output_path)
        st.image(overlay_path, caption="🔴 Pixels Changed Highlighted", use_container_width=True)

        # Pixel inspection
        stego_img = np.array(Image.open(output_path))
        st.subheader("🔎 Inspect Pixel Binary Values")
        row = st.number_input("Row (y-coordinate)", min_value=0, max_value=stego_img.shape[0] - 1, value=0)
        col = st.number_input("Column (x-coordinate)", min_value=0, max_value=stego_img.shape[1] - 1, value=0)
        if st.button("Show Pixel Binary Change"):
            changes = pixel_binary_changes(input_path, output_path, (row, col))
            st.write(f"📍 Pixel Location: (row={row}, col={col})")
            for channel, vals in changes.items():
                st.write(f"{channel}: {vals['orig']} → {vals['stego']}")

        # Bar chart
        stats = pixel_change_stats(input_path, output_path)
        fig = plot_pixel_changes(stats)
        st.pyplot(fig)
        st.write(f"✅ Total pixels changed: {stats['Changed']}")
        st.write(f"✅ Total pixels unchanged: {stats['Unchanged']}")

        # Download
        with open(output_path, "rb") as f:
            st.download_button("Download Encoded Image", f, "stego.png")

elif choice == "Decode":
    st.subheader("🔓 Decode Hidden Message")
    uploaded_file = st.file_uploader("Upload a stego image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        input_path = "stego_uploaded.png"
        Image.open(uploaded_file).save(input_path)

        decoded_text, decoded_emoji, binary_msg = decode_image(input_path)

        # Display uploaded stego image and overlay side by side
        col1, col2 = st.columns(2)
        with col1:
            st.image(input_path, caption="Uploaded Stego Image", use_container_width=True)
        overlay_path = visualize_lsb_changes_overlay(input_path, input_path)  # overlay for same image
        with col2:
            st.image(overlay_path, caption="Overlay Image", use_container_width=True)

        st.success(f"✅ Decoded Text: {decoded_text}")
        st.write("🔑 Decoded Emoji Mapping:", decoded_emoji)
        st.subheader("📟 Extracted Binary Representation")
        st.text_area("Binary extracted from image", binary_msg, height=150)
