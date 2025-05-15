import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Русские названия признаков
feature_names = {
    "price": "Цена, ₽",
    "square_meters": "Общая площадь, м²",
    "living_meters": "Жилая площадь, м²",
    "kitchen_meters": "Площадь кухни, м²",
    "ceiling_height": "Высота потолков, м",
    "floor": "Этаж",
    "build_year": "Год постройки",
    "building_floors": "Этажей в доме",
    "apartments_count": "Квартир в доме",
    "entrances_count": "Подъездов в доме",
    "living_ratio": "Доля жилой площади",
    "kitchen_ratio": "Доля кухни",
    "floors_diff": "Позиция по этажности",
    "density": "Квартир на подъезд"
}


def analyze_numeric_corr(df: pd.DataFrame, columns: list, target: str = "price"):
    """Анализирует корреляции с целевой переменной и строит только тепловую карту."""
    corr_matrix = df[[target] + columns].corr()
    renamed = {k: feature_names.get(k, k) for k in [target] + columns}
    corr_matrix = corr_matrix.rename(index=renamed, columns=renamed)

    print("Коэффициенты корреляции с ценой аренды:")
    print(corr_matrix[feature_names[target]].sort_values(ascending=False))

    plt.figure(figsize=(10, 6))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Матрица корреляций с ценой аренды, ₽")
    plt.show()


def analyze_categorical_impact(df: pd.DataFrame, column: str, target: str = "price"):
    """Анализирует категориальный признак по средней цене. Показывает топ и при необходимости — антитоп."""
    grouped = df.groupby(column)[target].mean().sort_values(ascending=False)
    n = len(grouped)
    display_n = min(n, 10)

    print(f"\n=== Анализ по: {column} ===")
    print(f"Всего категорий: {n}\n")

    print(f"ТОП {display_n} по средней цене:")
    print(grouped.head(display_n).round(2))

    if n > 20:
        print(f"\nАНТИТОП 10 по средней цене:")
        print(grouped.tail(10).round(2))


def analyze_list_column_impact(df: pd.DataFrame, column: str, target: str = "price", top_n: int = 10, min_count: int = 5):
    """
    Анализирует списковые признаки (amenities, tags, building_info) по ТОЧНЫМ совпадениям.
    """
    print(f"\n=== Анализ по: {column} ===")

    # Подсчёт частоты отдельных значений
    exploded = df[column].dropna().explode()
    freq = Counter(exploded)
    common_items = [item for item, count in freq.items() if count >= min_count]

    print(f"Всего признаков с частотой ≥ {min_count}: {len(common_items)}\n")

    if not common_items:
        print("Недостаточно признаков для анализа.")
        return

    results = {}
    for item in common_items:
        mask = df[column].apply(lambda x: item in x if isinstance(x, list) else False)
        if mask.sum() == 0:
            continue
        mean_price = df.loc[mask, target].mean()
        if pd.notna(mean_price):
            results[item] = mean_price

    if not results:
        print("Нет признаков с ненулевой средней ценой.")
        return

    sorted_means = pd.Series(results).sort_values(ascending=False)
    top_items = sorted_means.head(min(top_n, len(sorted_means)))

    print(f"ТОП {len(top_items)} по средней цене:")
    print(top_items.round(2))

