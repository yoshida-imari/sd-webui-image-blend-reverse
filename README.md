# sd-webui-image-blend-reverse
[English](#english) | [日本語](#日本語)

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

6. Wait for about 5 seconds. You should see a message saying "Installed into stable-diffusion-webui\extensions\sd-webui-image-blend-reverse. Use Installed tab to restart".

7. Go to the "Installed" tab, click "Check for updates", and then click "Apply and restart UI".

8. Completely restart the Stable Diffusion WebUI, including closing and reopening your terminal or command prompt window. If you're not familiar with terminals, you can simply restart your computer.

9. Once the WebUI is back up, you should see a new tab named "ImageBlendReverse" in the interface.

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

6. 約5秒待ちます。"Installed into stable-diffusion-webui\extensions\sd-webui-image-blend-reverse. Use Installed tab to restart"（sd-webui-image-blend-reverseにインストールされました。Installedタブを使用して再起動してください）というメッセージが表示されるはずです。

7. "Installed"（インストール済み）タブに移動し、"Check for updates"（更新を確認）をクリックしてから、"Apply and restart UI"（適用してUIを再起動）をクリックします。

8. Stable Diffusion WebUIを完全に再起動します。これには、ターミナルやコマンドプロンプトウィンドウを閉じて再度開く作業も含まれます。ターミナルに馴染みがない場合は、単にコンピューターを再起動してください。

9. WebUIが再起動したら、インターフェースに"ImageBlendReverse"という新しいタブが表示されているはずです。

一部の処理は https://gist.github.com/tori29umai0123/4e7781a4820727ca74e5491d67a6dff3 のソースコードを参考にしています。

