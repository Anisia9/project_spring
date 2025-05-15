import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def calculate_additional_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет расчетные признаки на основе существующих."""
    df["living_ratio"] = df["living_meters"] / df["square_meters"]
    df["kitchen_ratio"] = df["kitchen_meters"] / df["square_meters"]
    df["floors_diff"] = df["floor"] / df["building_floors"]
    df["density"] = df["apartments_count"] / df["entrances_count"]
    return df


def analyze_numeric_column(df: pd.DataFrame, column: str) -> dict:
    """
    Возвращает описательную статистику и выбросы по числовому признаку.

    Если признак не имеет отрицательных значений, нижняя граница обрезается до нуля.
    """
    series = df[column].dropna()
    desc = series.describe()

    q1 = desc["25%"]
    q3 = desc["75%"]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # Корректируем нижнюю границу, если переменная не может быть < 0
    if lower < 0 <= series.min():
        lower = 0

    outliers = series[(series < lower) | (series > upper)]

    return {
        "Количество": len(series),
        "Минимум": desc["min"],
        "1 квартиль (Q1)": q1,
        "Медиана": desc["50%"],
        "Среднее": desc["mean"],
        "3 квартиль (Q3)": q3,
        "Максимум": desc["max"],
        "Ст. отклонение": desc["std"],
        "IQR": iqr,
        "Нижняя граница выбросов": lower,
        "Верхняя граница выбросов": upper,
        "Кол-во выбросов": len(outliers)
    }


def plot_distribution(df: pd.DataFrame, column: str, title_ru: str):
    """Строит гистограмму и boxplot по колонке."""
    series = df[column].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    sns.histplot(series, ax=axes[0], kde=True, bins=30)
    axes[0].set_title(f"Гистограмма: {title_ru}")
    axes[0].set_xlabel(title_ru)

    sns.boxplot(x=series, ax=axes[1])
    axes[1].set_title(f"Boxplot: {title_ru}")
    axes[1].set_xlabel(title_ru)

    plt.tight_layout()
    plt.show()


def analyze_all(df: pd.DataFrame, columns: dict):
    """
    Проводит анализ всех заданных колонок и выводит округлённую статистику и графики.
    """
    df = calculate_additional_columns(df)

    for col, title in columns.items():
        print(f"\n=== Анализ признака: {title} ({col}) ===")
        stats = analyze_numeric_column(df, col)

        for k, v in stats.items():
            if isinstance(v, float):
                v = round(v, 2)
            print(f"{k}: {v}")

        plot_distribution(df, col, title)
