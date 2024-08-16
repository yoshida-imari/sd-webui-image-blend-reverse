# sd-webui-image-blend-reverse
[English](#english) | [日本語](#日本語)

![image](https://github.com/user-attachments/assets/1bbeb138-4941-4e7c-85c6-27d78ccdd5a8)

## English

ImageBlendReverse is an extension for Stable Diffusion WebUI that can reverse-engineer blended images created from line art and base colors, separating them into component layers.

### Features

* Reference the most recently generated image from txt2img or img2img
* Process blended images to extract multiply and screen layers
* Create and download PSD files containing separated layers

# ImageBlendReverse Installation Instructions

Follow these steps to install the ImageBlendReverse extension for Stable Diffusion WebUI:

1. Open Stable Diffusion WebUI in your browser.

2. Navigate to the "Extensions" tab.

3. Click on the "Install from URL" sub-tab.

4. In the "URL for extension's git repository" field, enter the following URL:
   ```
   https://github.com/yoshida-imari/sd-webui-image-blend-reverse.git
   ```
5. Click the "Install" button.

6. You should see a message saying "Installed into stable-diffusion-webui\extensions\sd-webui-image-blend-reverse. Use Installed tab to restart".

7. Go to the "Installed" tab, click "Check for updates", and then click "Apply and restart UI".

8. Completely restart the Stable Diffusion WebUI, including closing and reopening your terminal or command prompt window. If you're not familiar with terminals, you can simply restart your computer.

9. Once the WebUI is back up, you should see a new tab named "ImageBlendReverse" in the interface.

### Execution Procedure

1. Set the result image in Blended Image or press the Reference Latest Generated Image button.

2. Set a single color base color image with a white background and no shading in Base Color Image.

3. Set a black line art image with a white background in Line Art.

4. Adjust the Denoise Strength value. This reduces noise in the multiply and screen layer images. When the value is 0, no noise reduction is performed.

5. Press the Progress Images button.

6. After about 60 seconds, multiply and screen layer images will be generated.

7. Press the Create PSD button. The white part of the base color will be set as a transparent area and the black area of the line art will be set as an opaque area as layer masks for multiply and screen layers.

8. After about 60 seconds, when the Progress bar shows that the PSD file generation is complete, the Download PSD button will appear.

9. Press Download PSD to download the layered PSD file as output.psd.

Note:
- The line art should be black lines on a white background.
- The base color should be a single color image with a white background, without any shading.

Some of the processing methods are based on the source code from https://gist.github.com/tori29umai0123/4e7781a4820727ca74e5491d67a6dff3.

---

## 日本語

ImageBlendReverseは、Stable Diffusion WebUIの拡張機能で、線画とベースカラーからブレンドされた画像をリバースエンジニアリングし、コンポーネントレイヤーに分離することができます。

### 機能

主な機能：
* txt2imgまたはimg2imgで最後に生成された画像を参照
* ブレンド画像を処理し、乗算レイヤーとスクリーンレイヤーを抽出
* 分離されたレイヤーを含むPSDファイルの作成とダウンロード


# ImageBlendReverseインストール手順

Stable Diffusion WebUIにImageBlendReverse拡張機能をインストールするには、以下の手順に従ってください：

1. ブラウザでStable Diffusion WebUIを開きます。

2. "Extensions"（拡張機能）タブに移動します。

3. "Install from URL"（URLからインストール）サブタブをクリックします。

4. "URL for extension's git repository"（拡張機能のgitリポジトリURL）欄に以下のURLを入力します：
   ```
   https://github.com/yoshida-imari/sd-webui-image-blend-reverse.git
   ```
5. "Install"（インストール）ボタンをクリックします。

6. "Installed into stable-diffusion-webui\extensions\sd-webui-image-blend-reverse. Use Installed tab to restart"（sd-webui-image-blend-reverseにインストールされました。Installedタブを使用して再起動してください）というメッセージが表示されるはずです。

7. "Installed"（インストール済み）タブに移動し、"Check for updates"（更新を確認）をクリックしてから、"Apply and restart UI"（適用してUIを再起動）をクリックします。

8. Stable Diffusion WebUIを完全に再起動します。これには、ターミナルやコマンドプロンプトウィンドウを閉じて再度開く作業も含まれます。ターミナルに馴染みがない場合は、単にコンピューターを再起動してください。

9. WebUIが再起動したら、インターフェースに"ImageBlendReverse"という新しいタブが表示されているはずです。

### 実行手順

1. Blended Imageに結果画像をセットするか、Reference Latest Generated Imageボタンを押してください。

2. Base Color Imageに白背景で陰影のない単色のベースカラー画像をセットしてください。

3. Line Artに白背景で黒色線画の画像をセットしてください。

4. Denoise Strengthの値を調整して下さい。乗算とスクリーンのレイヤー画像のノイズを軽減します。値が0の時はノイズ除去を行いません。

5. Progress Imagesボタンを押してください。

6. 60秒ほど待つと、乗算とスクリーンのレイヤー画像が生成されます。

7. Create PSDボタンを押してください。乗算とスクリーンのレイヤーマスクとして、ベースカラーの白部分が透明領域として、線画の黒領域が不透明領域として追加でセットされます。

8. 60秒ほど待ちます。ProgressバーでPSDファイルが生成完了と出ると、Download PSDボタンが表示されます。

9. Download PSDを押すと、output.psdとしてレイヤー分けされたPSDファイルをダウンロードします。

注意：
- 線画は白背景の黒線画を使用してください。
- ベースカラーは白背景で、陰影のない単色の画像を使用してください。

一部の処理は https://gist.github.com/tori29umai0123/4e7781a4820727ca74e5491d67a6dff3 のソースコードを参考にしています。

