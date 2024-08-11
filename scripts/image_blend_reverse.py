from PIL import Image, ImageFilter, ImageOps
from collections import defaultdict
from skimage import color as sk_color
from tqdm import tqdm
from skimage.color import deltaE_ciede2000, rgb2lab
import cv2
import numpy as np
import os
from tqdm import tqdm
from skimage.color import deltaE_ciede2000, rgb2lab
import cv2

import pytoshop
from pytoshop import layers, enums

def denoise_image(image, strength=10):
    # PIL画像をnumpy配列に変換
    img_array = np.array(image)
    
    # アルファチャンネルを分離
    rgb = img_array[:,:,:3]
    alpha = img_array[:,:,3]
    
    # RGBチャンネルにのみノイズ除去を適用
    denoised_rgb = cv2.fastNlMeansDenoisingColored(rgb, None, strength, strength, 7, 21)
    
    # ノイズ除去されたRGBと元のアルファチャンネルを再結合
    denoised = np.dstack((denoised_rgb, alpha))
    
    # PIL画像に戻す
    return Image.fromarray(denoised, 'RGBA')

def create_psd(base_color, inverse_multiply, inverse_screen, lineart, output_psd_path):
    # 白紙のPSDファイルを作る
    psd = pytoshop.core.PsdFile(num_channels=4, height=base_color.height, width=base_color.width)

    # 共通の関数: レイヤーの作成
    def create_layer(image, name, blend_mode=enums.BlendMode.normal):
        # RGBAモードに変換（まだRGBAでない場合）
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        image_array = np.array(image)
        layer_alpha = layers.ChannelImageData(image=image_array[:, :, 3], compression=1)
        layer_r = layers.ChannelImageData(image=image_array[:, :, 0], compression=1)
        layer_g = layers.ChannelImageData(image=image_array[:, :, 1], compression=1)
        layer_b = layers.ChannelImageData(image=image_array[:, :, 2], compression=1)

        return layers.LayerRecord(
            channels={-1: layer_alpha, 0: layer_r, 1: layer_g, 2: layer_b},
            top=0, bottom=image.height, left=0, right=image.width,
            name=name,
            opacity=255,
            blend_mode=blend_mode
        )

    # レイヤーの作成と追加（逆順）
    psd.layer_and_mask_info.layer_info.layer_records.extend([
        create_layer(base_color, "Base Color"),
        create_layer(inverse_multiply, "Multiply", enums.BlendMode.multiply),
        create_layer(inverse_screen, "Screen", enums.BlendMode.screen),
        create_layer(lineart, "Line", enums.BlendMode.multiply)
    ])

    # PSDファイルの書き出し
    with open(output_psd_path, 'wb') as fd:
        psd.write(fd)

def replace_color(image, color_1, blur_radius=2):
    data = np.array(image)
    original_shape = data.shape
    data = data.reshape(-1, 4)
    color_1 = np.array(color_1)
    matches = np.all(data[:, :3] == color_1, axis=1)
    nochange_count = 0
    mask = np.zeros(data.shape[0], dtype=bool)

    while np.any(matches):
        new_matches = np.zeros_like(matches)
        match_num = np.sum(matches)
        for i in tqdm(range(len(data))):
            if matches[i]:
                x, y = divmod(i, original_shape[1])
                neighbors = [
                    (x, y-1), (x, y+1), (x-1, y), (x+1, y)
                ]
                valid_neighbors = []
                for nx, ny in neighbors:
                    if 0 <= nx < original_shape[0] and 0 <= ny < original_shape[1]:
                        ni = nx * original_shape[1] + ny
                        if not np.all(data[ni, :3] == color_1, axis=0):
                            valid_neighbors.append(data[ni, :3])
                if valid_neighbors:
                    new_color = np.mean(valid_neighbors, axis=0).astype(np.uint8)
                    data[i, :3] = new_color
                    data[i, 3] = 255
                    mask[i] = True
                else:
                    new_matches[i] = True
        matches = new_matches
        if match_num == np.sum(matches):
            nochange_count += 1
        if nochange_count > 5:
            break

    data = data.reshape(original_shape)
    mask = mask.reshape(original_shape[:2])

    result_image = Image.fromarray(data, 'RGBA')
    blurred_image = result_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_data = np.array(blurred_image)

    np.copyto(data, blurred_data, where=mask[..., None])

    return Image.fromarray(data, 'RGBA')

def generate_distant_colors(consolidated_colors, distance_threshold):
    consolidated_lab = [rgb2lab(np.array([color], dtype=np.float32) / 255.0).reshape(3) for color, _ in consolidated_colors]
    max_attempts = 10000
    for _ in range(max_attempts):
        random_rgb = np.random.randint(0, 256, size=3)
        random_lab = rgb2lab(np.array([random_rgb], dtype=np.float32) / 255.0).reshape(3)
        if all(deltaE_ciede2000(base_color_lab, random_lab) > distance_threshold for base_color_lab in consolidated_lab):
            return tuple(random_rgb)
    return (128, 128, 128)

def consolidate_colors(major_colors, threshold):
    colors_lab = [rgb2lab(np.array([[color]], dtype=np.float32)/255.0).reshape(3) for color, _ in major_colors]
    i = 0
    while i < len(colors_lab):
        j = i + 1
        while j < len(colors_lab):
            if deltaE_ciede2000(colors_lab[i], colors_lab[j]) < threshold:
                if major_colors[i][1] >= major_colors[j][1]:
                    major_colors[i] = (major_colors[i][0], major_colors[i][1] + major_colors[j][1])
                    major_colors.pop(j)
                    colors_lab.pop(j)
                else:
                    major_colors[j] = (major_colors[j][0], major_colors[j][1] + major_colors[i][1])
                    major_colors.pop(i)
                    colors_lab.pop(i)
                continue
            j += 1
        i += 1
    return major_colors

def get_major_colors(image, threshold_percentage=0.01):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    color_count = defaultdict(int)
    for pixel in image.getdata():
        color_count[pixel] += 1
    total_pixels = image.width * image.height
    major_colors = [(color, count) for color, count in color_count.items() if (count / total_pixels) >= threshold_percentage]
    return major_colors

def line_color(image, mask, new_color):
    data = np.array(image)
    data[mask, :3] = new_color
    return Image.fromarray(data, 'RGBA')

def convert_rgb_to_rgba(image):
    # NumPy配列に変換
    data = np.array(image)

    # RGBからRGBAに変換（アルファチャンネルを追加）
    if data.shape[-1] == 3:  # RGBの場合
        alpha_channel = 255 * np.ones((data.shape[0], data.shape[1], 1), dtype=np.uint8)  # アルファチャンネルを全て255で埋める
        data = np.concatenate((data, alpha_channel), axis=-1)  # RGBAに変換

    # PIL画像に変換
    image_rgba = Image.fromarray(data, 'RGBA')
    return image_rgba

def process_post_line_removal(image, lineart):
    lineart = lineart.point(lambda x: 0 if x < 200 else 255)
    lineart = ImageOps.invert(lineart)
    kernel = np.ones((3, 3), np.uint8)
    lineart = cv2.dilate(np.array(lineart), kernel, iterations=1)
    lineart = Image.fromarray(lineart)
    mask = np.array(lineart) == 255
    major_colors = get_major_colors(image, threshold_percentage=0.05)
    major_colors = consolidate_colors(major_colors, 10)
    new_color_1 = generate_distant_colors(major_colors, 100)
    image = convert_rgb_to_rgba(image)
    filled_image = line_color(image, mask, new_color_1)
    replace_color_image = replace_color(filled_image, new_color_1, 2).convert('RGB')
    return replace_color_image

def calculate_luminance(color):
    return 0.299 * color[:, :, 0] + 0.587 * color[:, :, 1] + 0.114 * color[:, :, 2]

def detect_unchanged_pixels(known_array, blended_array, mode='multiply'):
    # 明度の差を計算
    known_luminance = calculate_luminance(known_array)
    blended_luminance = calculate_luminance(blended_array)

    # 乗算の場合：ブレンド後が明るければ乗算の影響なしと判断
    # スクリーンの場合：ブレンド後が暗ければスクリーンの影響なしと判断
    if mode == 'multiply':
        return blended_luminance >= known_luminance
    elif mode == 'screen':
        return blended_luminance < known_luminance

# 乗算の逆算
def inverse_multiply_blend(blended, known):
    blended_array = np.array(blended, dtype=np.float32)
    known_array = np.array(known, dtype=np.float32)

    # 0による除算を防ぐために、小さな値を加える
    zero_mask = (known_array[:, :, 0:3] == 0)
    known_array[:, :, 0:3][zero_mask] = np.finfo(float).eps

    original_array = (blended_array[:, :, 0:3] * 255 / known_array[:, :, 0:3]).clip(0, 255)
    original_alpha = blended_array[:, :, 3]  # アルファチャンネルを保持

    # 未使用ピクセルを透明にするためのマスク
    unchanged_mask = detect_unchanged_pixels(known_array, blended_array, mode='multiply')
    original_array[unchanged_mask] = [0, 0, 0]
    original_alpha[unchanged_mask] = 0

    # RGBAに結合
    final_array = np.dstack((original_array, original_alpha))
    return Image.fromarray(final_array.astype(np.uint8), 'RGBA')

def inverse_screen_blend(blended, known):
    # 画像データを浮動小数点型で扱う
    blended_array = np.array(blended, dtype=np.float32) / 255
    known_array = np.array(known, dtype=np.float32) / 255

    # スクリーンブレンドの逆算式
    with np.errstate(divide='ignore', invalid='ignore'):
        original_array = 1 - (1 - blended_array[:, :, 0:3]) / (1 - known_array[:, :, 0:3])
        original_array[~np.isfinite(original_array)] = 0  # 不正な値は0に置換

    # アルファチャンネルを保持
    original_alpha = blended_array[:, :, 3]

    # 未使用ピクセルを透明に設定
    unchanged_mask = detect_unchanged_pixels(known_array, blended_array, mode='screen')
    original_array[unchanged_mask] = [1, 1, 1]
    original_alpha[unchanged_mask] = 0

    # RGBAに結合して画像を作成
    result_array = np.clip(original_array * 255, 0, 255)
    result_array = np.dstack((result_array, original_alpha * 255))

    return Image.fromarray(result_array.astype(np.uint8))
