#!/usr/bin/env python3
"""
AOI Defect History アプリケーションアイコン作成スクリプト
基板を拡大鏡で検査しているデザイン
"""

import os

from PIL import Image, ImageDraw, ImageFont


def create_pcb_inspection_icon():
    """基板検査をイメージしたアプリケーションアイコンを作成"""

    # 最大サイズでアイコンを作成
    size = 256

    # 背景色 - ダークグリーン（基板をイメージ）
    bg_color = (34, 139, 34, 255)  # ForestGreen

    # 画像を作成
    img = Image.new("RGBA", (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # === 基板パターンの描画 ===
    # 配線パターンを描画（金色）
    trace_color = (218, 165, 32, 255)  # GoldenRod

    # 水平線
    for i in range(4):
        y = 40 + i * 60
        draw.line([(20, y), (size - 20, y)], fill=trace_color, width=3)

    # 垂直線
    for i in range(4):
        x = 40 + i * 60
        draw.line([(x, 20), (x, size - 20)], fill=trace_color, width=3)

    # チップ部品を表現する小さな矩形（黒）
    component_color = (30, 30, 30, 255)
    component_positions = [
        (60, 60),
        (140, 60),
        (220, 60),
        (60, 140),
        (140, 140),
        (220, 140),
        (60, 220),
        (140, 220),
        (220, 220),
    ]

    for x, y in component_positions:
        draw.rectangle(
            [x - 12, y - 8, x + 12, y + 8],
            fill=component_color,
            outline=(200, 200, 200, 200),
            width=1,
        )

    # === 拡大鏡の描画 ===
    # 拡大鏡の中心位置（右上寄り）
    mag_center_x = 180
    mag_center_y = 100
    lens_radius = 55

    # 拡大鏡のレンズ部分（半透明の白）
    # まず外側の円（フレーム）
    frame_color = (192, 192, 192, 255)  # Silver
    draw.ellipse(
        [
            mag_center_x - lens_radius - 5,
            mag_center_y - lens_radius - 5,
            mag_center_x + lens_radius + 5,
            mag_center_y + lens_radius + 5,
        ],
        fill=frame_color,
        outline=(169, 169, 169, 255),
        width=3,
    )

    # レンズ内部（半透明の白で拡大効果を表現）
    lens_fill = (255, 255, 255, 180)
    draw.ellipse(
        [
            mag_center_x - lens_radius,
            mag_center_y - lens_radius,
            mag_center_x + lens_radius,
            mag_center_y + lens_radius,
        ],
        fill=lens_fill,
        outline=(220, 220, 220, 255),
        width=2,
    )

    # レンズ内部に拡大された基板パターンを描画
    # 拡大された配線
    inner_trace_color = (218, 165, 32, 255)
    draw.line(
        [(mag_center_x - 40, mag_center_y), (mag_center_x + 40, mag_center_y)],
        fill=inner_trace_color,
        width=5,
    )
    draw.line(
        [(mag_center_x, mag_center_y - 40), (mag_center_x, mag_center_y + 40)],
        fill=inner_trace_color,
        width=5,
    )

    # 拡大された部品（赤で不良を表現）
    defect_color = (220, 20, 60, 255)  # Crimson
    draw.rectangle(
        [mag_center_x - 15, mag_center_y - 10, mag_center_x + 15, mag_center_y + 10],
        fill=defect_color,
        outline=(255, 0, 0, 255),
        width=2,
    )

    # 不良箇所を示すXマーク
    mark_color = (255, 0, 0, 255)
    mark_size = 8
    draw.line(
        [
            (mag_center_x - mark_size, mag_center_y - mark_size),
            (mag_center_x + mark_size, mag_center_y + mark_size),
        ],
        fill=mark_color,
        width=3,
    )
    draw.line(
        [
            (mag_center_x - mark_size, mag_center_y + mark_size),
            (mag_center_x + mark_size, mag_center_y - mark_size),
        ],
        fill=mark_color,
        width=3,
    )

    # 拡大鏡のハンドル部分
    handle_start_x = mag_center_x + lens_radius - 10
    handle_start_y = mag_center_y + lens_radius - 10
    handle_end_x = mag_center_x + lens_radius + 45
    handle_end_y = mag_center_y + lens_radius + 45

    # ハンドルの影
    shadow_color = (0, 0, 0, 100)
    draw.line(
        [handle_start_x + 2, handle_start_y + 2, handle_end_x + 2, handle_end_y + 2],
        fill=shadow_color,
        width=14,
    )

    # ハンドル本体
    handle_color = (105, 105, 105, 255)  # DimGray
    draw.line(
        [handle_start_x, handle_start_y, handle_end_x, handle_end_y],
        fill=handle_color,
        width=12,
    )

    # ハンドルのグリップ部分
    grip_color = (169, 169, 169, 255)
    for i in range(3):
        grip_y = handle_start_y + 10 + i * 8
        grip_x = handle_start_x + 10 + i * 8
        draw.line(
            [grip_x - 2, grip_y - 2, grip_x + 2, grip_y + 2], fill=grip_color, width=2
        )

    # === 角を丸める ===
    # 新しい画像を作成してマスクを適用
    rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # 角丸マスクを作成
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=30, fill=255)

    # マスクを適用して角を丸める
    rounded.paste(img, (0, 0), mask)

    # === 複数サイズのアイコンを保存 ===
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for s in sizes:
        if s != 256:
            resized = rounded.resize((s, s), Image.Resampling.LANCZOS)
            images.append(resized)
        else:
            images.append(rounded)

    # ICOファイルとして保存
    output_path = "assets/icon.ico"
    rounded.save(output_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"✓ アイコンファイル {output_path} を作成しました")

    # プレビュー用のPNGファイルも作成
    png_path = "assets/icon.png"
    rounded.save(png_path, format="PNG")
    print(f"✓ プレビュー用PNGファイル {png_path} を作成しました")

    # ファイルサイズを表示
    ico_size = os.path.getsize(output_path)
    png_size = os.path.getsize(png_path)
    print(f"\nファイルサイズ:")
    print(f"  icon.ico: {ico_size:,} bytes")
    print(f"  icon.png: {png_size:,} bytes")
    print(f'\n含まれるアイコンサイズ: {", ".join([f"{s}x{s}" for s in sizes])}')


if __name__ == "__main__":
    try:
        # assetsディレクトリが存在することを確認
        os.makedirs("assets", exist_ok=True)

        print("基板検査アイコンを作成中...\n")
        create_pcb_inspection_icon()
        print("\n✓ アイコンの作成が完了しました！")

    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
