import sys
sys.path.insert(0, '..')

from compressor import compress_image, decompress_image
import os
import json
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

test_images = [
    ("../Task_1/lena.png", "Lena RGB", True),
    ("../Task_1/rgb.png", "RGB 1024x1024", True),
    ("../Task_1/grayscale.jpg", "Grayscale", False),
    ("../Task_1/bw.jpg", "B&W No Dither", False),
    ("../Task_1/bw_wd.jpg", "B&W With Dither", False),
]

qualities = [10, 20, 30, 40, 50, 60, 70, 80, 90]
all_results = {}

for img_path, img_name, is_rgb in test_images:
    print(f"\nТестирование: {img_name}")
    print(f"Файл: {img_path}")
    
    if not os.path.exists(img_path):
        print(f"    Файл не найден!")
        continue
    
    original_size = os.path.getsize(img_path)
    print(f"   Размер оригинала: {original_size:,} байт ({original_size/1024:.1f} KB)")
    
    results = []
    
    for q in qualities:
        comp_path = f"results/{img_name.replace(' ', '_')}_q{q}.jpg"
        rest_path = f"results/{img_name.replace(' ', '_')}_q{q}.png"
        
        try:
            # Сжатие
            compress_image(img_path, comp_path, quality=q)
            comp_size = os.path.getsize(comp_path)
            
            # Декомпрессия
            decompress_image(comp_path, rest_path)
            
            ratio = (comp_size / original_size * 100)
            results.append({
                'quality': q,
                'compressed_size': comp_size,
                'ratio_percent': ratio
            })
            
            print(f"   Q{q:2d}: {comp_size:8,} байт ({ratio:5.1f}%) ✓")
            
        except Exception as e:
            print(f"   Q{q:2d}: ОШИБКА - {str(e)[:50]}")
    
    all_results[img_name] = {
        'original_size': original_size,
        'results': results
    }

with open("results/all_compression_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
print(" Результаты сохранены в results/all_compression_results.json")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Зависимость размера сжатого изображения от качества', fontsize=16)
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
    sizes_kb = [r['compressed_size'] / 1024 for r in results]
    ratios = [r['ratio_percent'] for r in results]
    
    ax.plot(qualities_list, sizes_kb, marker='o', linewidth=2, 
           markersize=6, color=colors[idx], label='Размер (KB)')
    ax.fill_between(qualities_list, sizes_kb, alpha=0.3, color=colors[idx])
    
    ax.set_xlabel('Качество', fontsize=10)
    ax.set_ylabel('Размер сжатого (KB)', fontsize=10)
    ax.set_title(f'{img_name}\n(Оригинал: {data["original_size"]/1024:.1f} KB)', 
                fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(qualities)

    ax2 = ax.twinx()
    ax2.plot(qualities_list, ratios, marker='s', linewidth=2, 
            markersize=5, color=colors[idx], alpha=0.5, linestyle='--')
    ax2.set_ylabel('% от оригинала', fontsize=9, alpha=0.7)

if len(all_results) < len(axes):
    axes[-1].axis('off')

plt.tight_layout()
plt.savefig('graphs/compression_all_images.png', dpi=150, bbox_inches='tight')
print(" График сохранен: graphs/compression_all_images.png")

# Создаем сравнительный график (все на одном)
fig, ax = plt.subplots(figsize=(12, 7))

for idx, (img_name, data) in enumerate(all_results.items()):
    results = data['results']
    if not results:
        continue
    
    qualities_list = [r['quality'] for r in results]
    sizes_kb = [r['compressed_size'] / 1024 for r in results]
    
    ax.plot(qualities_list, sizes_kb, marker='o', linewidth=2.5, 
           markersize=7, label=img_name, color=colors[idx])

ax.set_xlabel('Уровень качества', fontsize=12)
ax.set_ylabel('Размер сжатого файла (KB)', fontsize=12)
ax.set_title('Сравнение компрессии для всех изображений', fontsize=14)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(qualities)

plt.tight_layout()
plt.savefig('graphs/compression_comparison.png', dpi=150, bbox_inches='tight')
print("✓ График сравнения сохранен: graphs/compression_comparison.png")

# Создаем таблицу результатов
print("\n" + "=" * 70)
print("ИТОГОВАЯ ТАБЛИЦА")
print("=" * 70)

for img_name, data in all_results.items():
    print(f"\n{img_name}")
    print(f"{'Качество':>10} {'Размер (B)':>15} {'Размер (KB)':>12} {'% от оригинала':>15}")
    print("-" * 55)
    
    for result in data['results']:
        print(f"{result['quality']:>10} {result['compressed_size']:>15,} "
              f"{result['compressed_size']/1024:>12.1f} {result['ratio_percent']:>14.1f}%")

print("\n" + "=" * 70)
print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
print("=" * 70)
print("\nФайлы сохранены:")
print("  📊 results/all_compression_results.json")
print("  📈 graphs/compression_all_images.png")
print("  📈 graphs/compression_comparison.png")
print("  🖼️  Декомпрессированные изображения в results/")
