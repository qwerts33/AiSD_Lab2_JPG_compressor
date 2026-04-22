import sys
sys.path.insert(0, '..')

from compressor import compress_image, decompress_image
from Task_1.converter import save_raw
import os
import json
import matplotlib.pyplot as plt
from PIL import Image

os.makedirs("results", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

def get_raw_image_type(image):
    if image.mode in ("RGB", "YCbCr", "RGBA"):
        return 1
    if image.mode == "1":
        return 2
    return 0

test_images = [
    ("../Task_1/lena.png", "Lena RGB", True),
    ("../Task_1/rgb.png", "RGB 1024x1024", True),
    ("../Task_1/grayscale.png", "Grayscale", False),
    ("../Task_1/bw.png", "B&W No Dither", False),
    ("../Task_1/bw_wd.png", "B&W With Dither", False),
]

qualities = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
all_results = {}

for img_path, img_name, is_rgb in test_images:
    print(f"\nТестирование: {img_name}")
    print(f"Файл: {img_path}")

    original_img = Image.open(img_path)
    raw_original_path = f"results/{img_name.replace(' ', '_')}_original.raw"
    save_raw(original_img, raw_original_path, get_raw_image_type(original_img))
    original_raw_size = os.path.getsize(raw_original_path)

    print(f"   Размер оригинала (PNG): {os.path.getsize(img_path):,} байт")
    print(f"   Размер оригинала (RAW): {original_raw_size:,} байт")

    results = []

    for q in qualities:
        comp_path = f"results/{img_name.replace(' ', '_')}_q{q}.jpg"
        rest_path = f"results/{img_name.replace(' ', '_')}_q{q}.png"
        raw_restored_path = f"results/{img_name.replace(' ', '_')}_q{q}_restored.raw"
        try:
            compress_image(img_path, comp_path, quality=q)
            comp_size = os.path.getsize(comp_path)
            decompress_image(comp_path, rest_path)
            restored_img = Image.open(rest_path)
            save_raw(restored_img, raw_restored_path, get_raw_image_type(restored_img))
            restored_raw_size = os.path.getsize(raw_restored_path)
            compression_ratio_percent_to_png = (comp_size / os.path.getsize(img_path) * 100)
            compression_ratio_percent_to_raw = (comp_size / original_raw_size * 100)
            compression_factor_raw = (original_raw_size / comp_size)

            results.append({
                'quality': q,
                'compressed_size': comp_size,
                'compression_ratio_percent_to_png': compression_ratio_percent_to_png,
                'compression_ratio_percent_to_raw': compression_ratio_percent_to_raw,
                'compression_factor_raw': compression_factor_raw,
                'restored_raw_size': restored_raw_size,
                'restored_minus_original_raw': restored_raw_size - original_raw_size
            })

            print(f"   Q{q:2d}: контейнер={comp_size:8,} байт | factor={compression_factor_raw:6.2f}x")

        except Exception as e:
            print(f"   Q{q:2d}: ОШИБКА - {str(e)[:50]}")

    all_results[img_name] = {
        'original_png_size': os.path.getsize(img_path),
        'original_raw_size': original_raw_size,
        'results': results
    }

with open("results/all_compression_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
print("\n✓ Результаты сохранены в results/all_compression_results.json")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Сравнение размеров: Оригинал RAW vs Сжатый контейнер vs Восстановленный RAW', fontsize=14)
axes = axes.flatten()

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

for idx, (img_name, data) in enumerate(all_results.items()):
    if idx >= len(axes):
        break

    ax = axes[idx]
    results = data['results']

    if not results:
        ax.text(0.5, 0.5, f'{img_name}\n(Ошибка)',
                ha='center', va='center', fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        continue

    qualities_list = [r['quality'] for r in results]
    compressed_sizes = [r['compressed_size'] / 1024 for r in results]
    restored_raw_sizes = [r['restored_raw_size'] / 1024 for r in results]
    original_raw_kb = data['original_raw_size'] / 1024

    ax.axhline(y=original_raw_kb, color='green', linestyle='-',
               linewidth=2, label=f'Оригинал RAW ({original_raw_kb:.1f} KB)')

    ax.plot(qualities_list, compressed_sizes, marker='o', linewidth=2,
            markersize=6, color=colors[idx], label='Сжатый контейнер')
    ax.plot(qualities_list, restored_raw_sizes, marker='s', linewidth=2,
            markersize=5, color='orange', linestyle='--', label='Восстановленный RAW')

    ax.set_xlabel('Качество', fontsize=10)
    ax.set_ylabel('Размер (KB)', fontsize=10)
    ax.set_title(f'{img_name}\nRAW оригинал: {original_raw_kb:.1f} KB', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(qualities_list)
    ax.legend(fontsize=8)

for idx in range(len(all_results), len(axes)):
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig('graphs/raw_comparison_all_images.png', dpi=150, bbox_inches='tight')
print("✓ График RAW сравнения: graphs/raw_comparison_all_images.png")

fig, ax = plt.subplots(figsize=(12, 7))

for idx, (img_name, data) in enumerate(all_results.items()):
    results = data['results']
    if not results:
        continue

    qualities_list = [r['quality'] for r in results]
    compression_factors = [r['compression_factor_raw'] for r in results]

    ax.plot(qualities_list, compression_factors, marker='o', linewidth=2.5,
            markersize=7, label=img_name, color=colors[idx % len(colors)])

ax.set_xlabel('Уровень качества', fontsize=12)
ax.set_ylabel('Фактор сжатия относительно RAW', fontsize=12)
ax.set_title('Фактор сжатия: original RAW / compressed container', fontsize=14)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(qualities)

plt.tight_layout()
plt.savefig('graphs/compression_factor_vs_quality.png', dpi=150, bbox_inches='tight')
print("✓ График фактора сжатия: graphs/compression_factor_vs_quality.png")

# Итоговая таблица
print("\n" + "=" * 90)
print("ИТОГОВАЯ ТАБЛИЦА (СРАВНЕНИЕ РАЗМЕРОВ RAW)")
print("=" * 90)

for img_name, data in all_results.items():
    print(f"\n📷 {img_name}")
    print(f"   Оригинал PNG: {data['original_png_size']:,} байт")
    print(f"   Оригинал RAW: {data['original_raw_size']:,} байт")
    print(f"\n   {'Q':<4} {'Контейнер':>12} {'Factor':>10} {'RAW restored':>14} {'Разница RAW':>12}")
    print("   " + "-" * 65)

    for result in data['results']:
        diff = result['restored_minus_original_raw']
        print(f"   {result['quality']:<4} {result['compressed_size']:>10,} байт "
              f"{result['compression_factor_raw']:>8.2f}x "
              f"{result['restored_raw_size']:>10,} байт "
              f"{diff:>+10,}")

print("\n" + "=" * 90)
print("✓ ГРАФИКИ СОХРАНЕНЫ В ПАПКУ 'graphs'")
print("  - raw_comparison_all_images.png (сравнение размеров)")
print("  - compression_factor_vs_quality.png (фактор сжатия)")
print("=" * 90)
