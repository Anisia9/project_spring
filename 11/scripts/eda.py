import pandas as pd


def run_eda(input_path: str) -> pd.DataFrame:
    """
    Возвращает таблицу с обзорной информацией по каждому столбцу:
    - тип данных
    - число пропусков
    - число уникальных значений
    - примеры значений

    Args:
        input_path (str): путь к обработанному CSV

    Returns:
        pd.DataFrame: сводная таблица EDA
    """
    df = pd.read_csv(input_path)

    summary = []

    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isna().sum()
        unique_count = df[col].nunique(dropna=True)
        sample_values = df[col].dropna().unique()[:5]
        sample_preview = ", ".join(map(str, sample_values))

        summary.append({
            "column": col,
            "dtype": str(dtype),
            "nulls": nulls,
            "unique": unique_count,
            "examples": sample_preview
        })

    return pd.DataFrame(summary)
