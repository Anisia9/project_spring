import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Десериализует списки и добавляет цену за м²."""
    for col in ["amenities", "tags", "building_info"]:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df["price_per_sqm"] = df["price"] / df["square_meters"]
    return df


def build_period(year):
    """Категоризация года постройки по десятилетиям."""
    try:
        y = int(year)
        if y < 1960:
            return "до 1960"
        elif y >= 2025:
            return "2025+"
        else:
            decade = (y // 10) * 10
            return f"{decade}-{decade + 9}"
    except:
        return None


def analyze_by_build_decade(df: pd.DataFrame):
    """Анализ по эпохам постройки."""
    df["build_decade"] = df["build_year"].apply(build_period)
    df_valid = df[df["build_decade"].notna()]  # убираем неуказанные

    order = ["до 1960"] + [f"{d}-{d+9}" for d in range(1960, 2030, 10)] + ["2025+"]
    summary = (
        df_valid.groupby("build_decade")
        .agg(
            count=("price", "count"),
            avg_price=("price", "mean"),
            avg_price_per_sqm=("price_per_sqm", "mean")
        )
        .round(2)
        .reindex([p for p in order if p in df_valid["build_decade"].unique()])
    )

    plt.figure(figsize=(10, 4))
    sns.barplot(data=summary.reset_index(), x="build_decade", y="avg_price")
    plt.title("Средняя цена аренды по эпохам постройки")
    plt.ylabel("Цена, ₽")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return summary


def analyze_price_by_location(df: pd.DataFrame):
    """Анализ средней цены по метро и адресу — таблицы + графики."""
    # Группировка
    metro_df = df.groupby("metro")["price"].mean().dropna().sort_values(ascending=False).head(20).round(2)
    address_df = df.groupby("address")["price"].mean().dropna().sort_values(ascending=False).head(20).round(2)

    # Табличный вывод
    metro_table = pd.DataFrame(metro_df).rename(columns={"price": "avg_price"})
    address_table = pd.DataFrame(address_df).rename(columns={"price": "avg_price"})

    # Визуализация: metro
    plt.figure(figsize=(10, 6))
    sns.barplot(x=metro_df.values, y=metro_df.index, color="steelblue")
    plt.title("ТОП 20 станций метро по средней цене")
    plt.xlabel("Средняя цена, ₽")
    plt.ylabel("Станция метро")
    plt.tight_layout()
    plt.show()

    # Визуализация: address
    plt.figure(figsize=(10, 6))
    sns.barplot(x=address_df.values, y=address_df.index, color="seagreen")
    plt.title("ТОП 20 адресов по средней цене")
    plt.xlabel("Средняя цена, ₽")
    plt.ylabel("Адрес")
    plt.tight_layout()
    plt.show()

    # Возвращаем таблицы (например, для отображения в ноутбуке)
    return (
        metro_table.style.background_gradient(cmap="Blues").format(precision=2),
        address_table.style.background_gradient(cmap="Greens").format(precision=2)
    )


def analyze_price_per_sqm(df: pd.DataFrame):
    """Анализ цены за квадратный метр."""
    valid = df[df["price_per_sqm"].notna()]
    stats = valid["price_per_sqm"].describe().round(2)

    print("\nСтатистика по цене за м²:")
    print(f"Количество объектов: {stats['count']:.0f}")
    print(f"Минимум: {stats['min']} ₽/м²")
    print(f"25-й перцентиль: {stats['25%']} ₽/м²")
    print(f"Медиана: {stats['50%']} ₽/м²")
    print(f"75-й перцентиль: {stats['75%']} ₽/м²")
    print(f"Максимум: {stats['max']} ₽/м²")
    print(f"Среднее: {stats['mean']} ₽/м²")
    print(f"Ст. отклонение: {stats['std']} ₽/м²")

    plt.figure(figsize=(10, 4))
    sns.histplot(valid["price_per_sqm"], bins=40, kde=True)
    plt.title("Распределение цены за квадратный метр")
    plt.xlabel("Цена за м², ₽")
    plt.tight_layout()
    plt.show()

    top5 = valid.sort_values("price_per_sqm", ascending=False).head(5)
    display(top5[["price", "square_meters", "price_per_sqm", "address", "metro"]].round(2))

    top5_table = top5[["price", "square_meters", "price_per_sqm", "address", "metro"]]
    return stats, top5_table


def find_smallest_most_expensive(df: pd.DataFrame):
    """Находит наименьшую квартиру с наибольшей ценой за м²."""
    filtered = df[(df["square_meters"] > 0) & (df["price_per_sqm"].notna())]
    idx = filtered["price_per_sqm"].idxmax()
    row = filtered.loc[idx]

    print("\nСамая дорогая (за м²) и маленькая квартира:")
    print(f"Площадь: {row['square_meters']} м²")
    print(f"Цена: {row['price']} ₽")
    print(f"Цена за м²: {row['price_per_sqm']:.2f} ₽")
    print(f"Адрес: {row['address']}")
    print(f"Метро: {row['metro']}")

    return row
