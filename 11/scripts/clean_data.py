import re
import pandas as pd
import ast


def extract_price(value):
    """Преобразует цену из строки в int."""
    cleaned = re.sub(r"[^\d]", "", str(value))
    return int(cleaned) if cleaned.isdigit() else None


def clean_rent_offer_data(input_path: str, output_path: str):
    """
    Загружает и обрабатывает данные аренды недвижимости.
    Удаляет дубликаты, извлекает признаки, обновляет списки и сохраняет результат.
    """
    df = pd.read_csv(input_path)

    # Удаление дубликатов по ссылке
    before = len(df)
    df = df.drop_duplicates(subset="link", keep="first")
    after = len(df)
    print(f"Удалено дубликатов по ссылке: {before - after}")

    # Преобразование строк в списки (если они сериализованы как строки)
    for col in ["technical_info", "amenities", "building_info", "tags"]:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else ast.literal_eval(x))

    # Очистка и извлечение признаков
    df["price"] = df["price"].apply(extract_price)
    df["square_meters"] = None
    df["living_meters"] = None
    df["kitchen_meters"] = None
    df["ceiling_height"] = None
    df["floor"] = None
    df["build_year"] = None
    df["building_floors"] = None
    df["apartments_count"] = None
    df["entrances_count"] = None
    df["bathroom_type"] = None
    df["renovation_type"] = None

    for i, row in df.iterrows():
        tech_remaining = []
        build_remaining = []
        amenity_remaining = []

        # --- technical_info ---
        for item in row["technical_info"]:
            if "общая" in item:
                match = re.search(r"(\d+[,.]?\d*)", item)
                df.at[i, "square_meters"] = float(match.group(1).replace(",", ".")) if match else None
            elif "жилая" in item:
                match = re.search(r"(\d+[,.]?\d*)", item)
                df.at[i, "living_meters"] = float(match.group(1).replace(",", ".")) if match else None
            elif "кухня" in item:
                match = re.search(r"(\d+[,.]?\d*)", item)
                df.at[i, "kitchen_meters"] = float(match.group(1).replace(",", ".")) if match else None
            elif "потолки" in item:
                match = re.search(r"(\d+[,.]?\d*)", item)
                df.at[i, "ceiling_height"] = float(match.group(1).replace(",", ".")) if match else None
            elif "этаж" in item and "из" in item:
                match = re.search(r"из \d+: (\d+)", item)
                df.at[i, "floor"] = int(match.group(1)) if match else None
            elif "год постройки" in item:
                match = re.search(r"\d{4}", item)
                df.at[i, "build_year"] = int(match.group(0)) if match else None
            else:
                tech_remaining.append(item)

        # --- building_info ---
        for item in row["building_info"]:
            if "Дом" in item:
                match = re.search(r"\b(19|20)\d{2}\b", item)
                if match:
                    df.at[i, "build_year"] = int(match.group(0))
            elif "этажей" in item:
                match = re.search(r"(\d+)", item)
                df.at[i, "building_floors"] = int(match.group(1)) if match else None
            elif "квартир" in item:
                match = re.search(r"(\d+)", item)
                df.at[i, "apartments_count"] = int(match.group(1)) if match else None
            elif "подъезд" in item:
                match = re.search(r"(\d+)", item)
                df.at[i, "entrances_count"] = int(match.group(1)) if match else None
            else:
                build_remaining.append(item)

        # --- amenities ---
        for item in row["amenities"]:
            if "Санузел раздельный" == item:
                df.at[i, "bathroom_type"] = "раздельный"
            elif "Санузел совмещённый" == item:
                df.at[i, "bathroom_type"] = "совмещённый"
            elif "Отделка —" in item:
                if df.at[i, "renovation_type"] is None:
                    match = re.search(r"Отделка — ([а-яА-Я ]+)", item)
                    df.at[i, "renovation_type"] = match.group(1).strip() if match else None
            else:
                amenity_remaining.append(item)

        # Обновление списков без извлечённых элементов
        df.at[i, "technical_info"] = tech_remaining
        df.at[i, "building_info"] = build_remaining
        df.at[i, "amenities"] = amenity_remaining

    # Удаление технической информации после обработки
    df.drop(columns=["technical_info"], inplace=True)

    # Сохранение
    df.to_csv(output_path, index=False)
    print(f"Данные сохранены в: {output_path}")
