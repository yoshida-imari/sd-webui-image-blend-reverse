import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks, shared, images
from PIL import Image
import numpy as np
import tempfile
import glob

from image_blend_reverse import (
    process_post_line_removal,
    convert_rgb_to_rgba,
    inverse_multiply_blend,
    inverse_screen_blend,
    create_psd
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
            process_button = gr.Button("Process Images")

        with gr.Row():
            result_multiply_image = gr.Image(label="Multiply Result", elem_id="multiply_result", height=512, width=512)
            result_screen_image = gr.Image(label="Screen Result", elem_id="screen_result", height=512, width=512)

        with gr.Row():
            create_psd_button = gr.Button("Create and Download PSD")

        psd_output = gr.File(label="PSD File")

        def process_images(blended, basecolor, lineart):
            if not all([blended, basecolor, lineart]):
                return [gr.Image.update(value=None), gr.Image.update(value=None)]

            blended = blended.convert('RGB')
            basecolor = basecolor.convert('RGBA')
            lineart = lineart.convert('L')

            # 画像のサイズを統一
            basecolor = basecolor.resize(blended.size)
            lineart = lineart.resize(blended.size)

            # 処理の実行
            post_line_removal = process_post_line_removal(blended, lineart)
            post_line_removal = convert_rgb_to_rgba(post_line_removal)
            result_multiply = inverse_multiply_blend(post_line_removal, basecolor)
            result_screen = inverse_screen_blend(post_line_removal, basecolor)

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

        def create_and_download_psd():
            global processed_images
            if 'processed_images' not in globals():
                print("Error: processed_images not found in globals")
                return None

            # PSDファイルを一時ファイルとして作成
            with tempfile.NamedTemporaryFile(delete=False, suffix='.psd') as temp_file:
                temp_filename = temp_file.name
                create_psd(
                    processed_images['basecolor'],
                    processed_images['multiply'],
                    processed_images['screen'],
                    processed_images['lineart'],
                    temp_filename
                )

            print(f"PSD file created: {temp_filename}")

            return temp_filename

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
            inputs=[blended_image, basecolor_image, lineart_image],
            outputs=[result_multiply_image, result_screen_image]
        )

        create_psd_button.click(
            fn=create_and_download_psd,
            inputs=[],
            outputs=[psd_output]
        )

        reference_latest_button.click(
            fn=reference_latest_image,
            inputs=[],
            outputs=[blended_image]
        )

        return [(ui_component, "ImageBlendReverse", "image_blend_reverse_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)