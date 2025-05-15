import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def collect_rent_offers(num_pages=2, delay_list=5, delay_offer=2):
    """
    Парсит офферы аренды недвижимости посуточно с сайта realty.yandex.ru.

    Сохраняет данные в ../data/rent_offers.csv:
        - link: ссылка на оффер
        - price: цена в сутки
        - address: адрес (второе <a>)
        - metro: ближайшая станция метро
        - technical_info: список строк
        - amenities: список строк
        - building_info: список строк
        - tags: список строк

    Args:
        num_pages (int): число страниц, которые нужно пройти
        delay_list (float): задержка после загрузки страницы со списком офферов
        delay_offer (float): задержка после загрузки отдельной страницы оффера
    """
    offers_data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for page in range(1, num_pages + 1):
        url = f"https://realty.yandex.ru/moskva/snyat/kvartira/posutochno/?page={page}"
        print(f"\nОткрыта страница: {url}")
        driver.get(url)
        time.sleep(delay_list)

        offers = driver.find_elements(By.CLASS_NAME, "OffersSerpItem__main")
        print(f"Найдено офферов: {len(offers)}")

        for idx, offer in enumerate(offers):
            print(f"\n--- Парсинг оффера {idx + 1} ---")
            try:
                link_elem = offer.find_element(By.CLASS_NAME, "OffersSerpItem__link")
                link = link_elem.get_attribute("href")
                print(f"Ссылка: {link}")

                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(delay_offer)

                try:
                    expand_buttons = driver.find_elements(
                        By.XPATH, "//span[contains(@class, 'ExpandableData__expandControl')]"
                    )
                    for btn in expand_buttons:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.5)
                    print(f"Нажато кнопок 'Показать все': {len(expand_buttons)}")
                except Exception as e:
                    print(f"Ошибка при нажатии на кнопки 'Показать все': {e}")

                try:
                    print("Парсинг цены...")
                    price = driver.find_element(
                        By.XPATH, "//span[contains(@class, 'OfferCardSummaryInfo__price')]"
                    ).text
                except:
                    price = "Не найдено"

                try:
                    print("Парсинг адреса...")
                    address_links = driver.find_elements(
                        By.XPATH, "//div[contains(@class, 'OfferCard__location')]//a"
                    )
                    if len(address_links) >= 2:
                        address = address_links[1].text
                    elif address_links:
                        address = address_links[0].text
                    else:
                        address = "Не найдено"
                except:
                    address = "Не найдено"

                try:
                    print("Парсинг метро...")
                    metro = driver.find_element(
                        By.XPATH, "//div[contains(@class, 'OfferCard__location')]//span[contains(@class, 'MetroStation__title')]"
                    ).text
                except:
                    metro = "Не найдено"

                try:
                    print("Парсинг технических параметров...")
                    labels = driver.find_elements(By.XPATH, "//div[contains(@class, 'Highlights__container')]//div[contains(@class, 'Highlight__label')]")
                    values = driver.find_elements(By.XPATH, "//div[contains(@class, 'Highlights__container')]//div[contains(@class, 'Highlight__value')]")
                    technical_info = [f"{l.text}: {v.text}" for l, v in zip(labels, values)]
                except:
                    technical_info = []

                try:
                    print("Парсинг удобств...")
                    amen_xpath = "//div[contains(@class, 'detailsFeatures')]//div[contains(@class, 'OfferCardFeature__text')]"
                    amenities = [el.text for el in driver.find_elements(By.XPATH, amen_xpath)]
                except:
                    amenities = []

                try:
                    print("Парсинг информации о доме...")
                    build_xpath = "//div[contains(@class, 'buildingFeatures')]//div[contains(@class, 'OfferCardFeature__text')]"
                    building_info = [el.text for el in driver.find_elements(By.XPATH, build_xpath)]
                except:
                    building_info = []

                try:
                    print("Парсинг тегов...")
                    tags_xpath = "//div[contains(@class, 'SummaryTags__tags')]//div[contains(@class, 'Badge__badgeText')]"
                    tags = [el.text for el in driver.find_elements(By.XPATH, tags_xpath)]
                except:
                    tags = []

                offers_data.append({
                    "link": link,
                    "price": price,
                    "address": address,
                    "metro": metro,
                    "technical_info": technical_info,
                    "amenities": amenities,
                    "building_info": building_info,
                    "tags": tags
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Ошибка при обработке оффера: {e}")

    driver.quit()

    print("\nСохранение данных в CSV...")
    df = pd.DataFrame(offers_data)
    output_path = os.path.join(os.path.dirname(__file__), "../data/rent_offers.csv")
    df.to_csv(output_path, index=False)
    print(f"Данные сохранены в: {output_path}")

