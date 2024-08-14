import sys
import os
import tempfile
import base64
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks, shared, images
from PIL import Image
import numpy as np
import glob

from image_blend_reverse import (
    process_post_line_removal,
    convert_rgb_to_rgba,
    inverse_multiply_blend,
    inverse_screen_blend,
    create_psd,
    denoise_image
)

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            gr.Markdown("## ImageBlendReverse")

        with gr.Row():
            blended_image = gr.Image(label="Blended Image", type="pil")
            basecolor_image = gr.Image(label="Base Color Image", type="pil")
            lineart_image = gr.Image(label="Line Art", type="pil")

        with gr.Row():
            reference_latest_button = gr.Button("Reference Latest Generated Image")

        with gr.Row():
            denoise_strength = gr.Slider(minimum=0, maximum=30, step=1, value=10, label="Denoise Strength (Multiply Result and Screen Result): A value of 0 is ineffective")

        with gr.Row():
            process_button = gr.Button("Process Images")

        with gr.Row():
            result_multiply_image = gr.Image(label="Multiply Result", elem_id="multiply_result", height=512, width=512)
            result_screen_image = gr.Image(label="Screen Result", elem_id="screen_result", height=512, width=512)

        with gr.Row():
            create_psd_button = gr.Button("Create PSD (Mask: Transparent where Base Color is White, Opaque where Line Art is Black)")

        # 進行状況表示用のコンポーネント
        progress = gr.Textbox(label="Progress", value="")

        # ダウンロードリンクを表示するためのHTML要素
        download_link = gr.HTML()

        def process_images(blended, basecolor, lineart, denoise_strength=10):
            if not all([blended, basecolor, lineart]):
                return [gr.Image.update(value=None), gr.Image.update(value=None)]

            blended = blended.convert('RGB')
            basecolor = basecolor.convert('RGBA')
            lineart = lineart.convert('L')

            # 画像のサイズを統一
            basecolor_size = basecolor.size
            blended = blended.resize(basecolor_size, Image.LANCZOS)
            lineart = lineart.resize(basecolor_size, Image.LANCZOS)
            
            # 処理の実行
            post_line_removal = process_post_line_removal(blended, lineart)
            post_line_removal = convert_rgb_to_rgba(post_line_removal)
            result_multiply = inverse_multiply_blend(post_line_removal, basecolor)
            result_screen = inverse_screen_blend(post_line_removal, basecolor)

            # ノイズ除去
            if denoise_strength > 0:
                result_multiply = denoise_image(result_multiply, denoise_strength)
                result_screen = denoise_image(result_screen, denoise_strength)

            # 結果をグローバル変数に保存
            global processed_images
            processed_images = {
                'basecolor': basecolor,
                'multiply': result_multiply,
                'screen': result_screen,
                'lineart': lineart
            }

            # 両方の結果を返す
            return [result_multiply, result_screen]

        def create_and_prepare_download(progress=gr.Progress()):
            global processed_images
            if 'processed_images' not in globals():
                print("エラー: グローバル変数にprocessed_imagesが見つかりません")
                return None, "Error: processed_images not found"

            progress(0, desc="Starting PSD creation")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, 'temp_output.psd')
                
                progress(0.2, desc="Creating PSD file")
                create_psd(
                    processed_images['basecolor'],
                    processed_images['multiply'],
                    processed_images['screen'],
                    processed_images['lineart'],
                    temp_file_path
                )

                progress(0.6, desc="PSD file created, preparing for download")
                print(f"PSDファイルが作成されました: {temp_file_path}")

                with open(temp_file_path, 'rb') as file:
                    file_content = file.read()

            progress(0.8, desc="Encoding file content")
            file_content_b64 = base64.b64encode(file_content).decode()
            
            progress(0.9, desc="Generating download link")
            download_html = f"""
                <style>
                    .download-button-container {{
                        width: 100%;
                        padding: 10px;
                        box-sizing: border-box;
                    }}
                    .download-button {{
                        display: block;
                        width: 100%;
                        padding: 2vmin 4vmin;
                        font-size: 2vmin;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 1vmin;
                        transition: background-color 0.3s;
                        text-align: center;
                        box-sizing: border-box;
                    }}
                    .download-button:hover {{
                        background-color: #45a049;
                    }}
                </style>
                <div class="download-button-container">
                    <a href="data:application/octet-stream;base64,{file_content_b64}" 
                    download="output.psd" 
                    class="download-button">
                        Download PSD
                    </a>
                </div>
            """
            
            progress(1.0, desc="Download link ready")
            return download_html, "PSD file created. Click the link to download."

        def get_latest_image():           
            folders = [
                shared.opts.outdir_txt2img_samples,
                shared.opts.outdir_img2img_samples
            ]

            all_images = []
            for folder in folders:
                if folder:
                    patterns = [
                        os.path.join(folder, "**", "*.png"),
                    ]

                    for pattern in patterns:
                        image_list = glob.glob(pattern, recursive=True)
                        all_images.extend(image_list)
            
            if all_images:
                latest_image = max(all_images, key=os.path.getmtime)
                return Image.open(latest_image)
            
            return None

        def reference_latest_image():
            latest_image = get_latest_image()
            if latest_image is not None:
                return gr.Image.update(value=latest_image)
            else:
                return gr.Image.update(value=None)


        process_button.click(
            fn=process_images,
            inputs=[blended_image, basecolor_image, lineart_image, denoise_strength],
            outputs=[result_multiply_image, result_screen_image]
        )

        create_psd_button.click(
            fn=create_and_prepare_download,
            inputs=[],
            outputs=[download_link, progress]
        )

        reference_latest_button.click(
            fn=reference_latest_image,
            inputs=[],
            outputs=[blended_image]
        )

        return [(ui_component, "ImageBlendReverse", "image_blend_reverse_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)