# Автотесты онлайн-калькулятора процентов (calculator.net)

Набор Selenium-автотестов для **Percentage Calculator** на сайте
[calculator.net](https://www.calculator.net/percent-calculator.html),
построенных по паттерну **Page Object** с параметризацией pytest.

## Что тестируется

Страница содержит форму из трёх полей: `[cpar1]% of [cpar2] = [cpar3]`.
Сервер требует ровно два заполненных поля и возвращает результат в блоке
`<div class="h2result">Result: ...</div>`. Проверяются все три режима:

1. найти значение (`10% от 200 = 20`);
2. найти неизвестное число (`10% от X = 50 → X = 500`);
3. найти неизвестный процент (`из 200 получилось 20 → 10%`).

## Структура проекта

```
pz4_selenium/
├── pages/
│   ├── base_page.py                 # общий PO: WebDriverWait, open(), действия
│   └── percent_calculator_page.py   # PO страницы калькулятора процентов
├── tests/
│   └── test_percent_calculator.py   # все тесты (без локаторов и ожиданий)
├── data/
│   └── percent_cases.json           # тестовые данные для параметризации
├── utils/
│   └── driver_factory.py            # создание Chrome/Firefox, headless-переключатель
├── conftest.py                      # фикстура driver + скриншоты при падении
├── pytest.ini
├── requirements.txt
└── README.md
```

## Page Object

`PercentCalculatorPage` наследует `BasePage`:

- **URL и локаторы** — константы класса (`By.ID`, CSS-селекторы; XPath только для кнопки Clear);
- **конструктор** принимает `driver`, внутри создаётся `WebDriverWait(driver, 15)`;
- **действия**: `open()`, `enter_percent()`, `enter_of()`, `enter_result_value()`,
  `click_calculate()`, `click_clear()` — все возвращают `self` (fluent API);
- **геттеры**: `get_result()` (текст), `get_result_number()` (нормализованное число),
  `wait_for_no_result()` (результата нет), `get_percent_value()` / `get_of_value()` (состояние полей).

Принципы соблюдены: в PO нет `assert` и тестовых данных, в тестах нет
`find_element`, `By.`, `WebDriverWait`, `time.sleep`. Если сайт сменит вёрстку —
правится один файл `pages/percent_calculator_page.py`.

## Тестовые сценарии

| Группа | Тесты | Что проверяется |
|---|---|---|
| Корректный расчёт | `test_percent_of_from_json` (6 наборов из JSON), `test_percent_of_correct` (5 наборов), `test_solve_missing_base`, `test_solve_missing_percent` | 10% от 200 = 20; режим «найти число»; режим «найти процент» |
| Граничные значения | `test_percent_boundaries` (6 параметров) | 0 как процент, 0 как число, оба нуля, отрицательные значения, очень большое число (1 000 000 % × 1 000 000 = 1e10) |
| Неверный ввод | `test_invalid_input_shows_no_result` (6 параметров), `test_very_long_number_is_handled` | буквы в полях, спецсимволы/инъекции, пустые поля, только одно поле, 40-значное число — результат не показывается, страница не падает |
| Формат вывода | `test_result_format_percent_sign`, `test_result_rounding_and_decimal_format` | знак `%` в ответе, десятичный разделитель — точка (не запятая), корректное округление дробного результата |
| Кнопка Clear | `test_clear_resets_inputs`, `test_clear_then_new_calculation` | поля очищаются, страница не перезагружается, после Clear новый расчёт не подмешивает старые значения |

Итого **30 тестов** (с учётом параметризации).

## Требования

- Python 3.12+
- Selenium 4 (`selenium>=4.21`), pytest (`pytest>=8.0`)
- Google Chrome или Mozilla Firefox (Selenium Manager сам скачает драйвер)

## Установка и запуск

```bash
cd pz4_selenium
python -m pip install -r requirements.txt
python -m pytest            # весь прогон одной командой
```

Выборочный запуск:

```bash
python -m pytest -k boundaries          # только граничные значения
python -m pytest tests/test_percent_calculator.py::test_clear_resets_inputs
python -m pytest -v                     # подробный отчёт по каждому параметру
```

## Настройки запуска (переменные окружения)

| Переменная | Значение по умолчанию | Эффект |
|---|---|---|
| `HEADLESS` | `true` | `HEADLESS=false python -m pytest` — браузер с окном (отладка) |
| `BROWSER`  | `chrome` | `BROWSER=firefox python -m pytest` — запуск в Firefox |

Headless-режим включён по умолчанию (`--headless=new`, `--window-size=1920,1080`,
`--no-sandbox`, `--disable-dev-shm-usage`), поэтому тесты работают на CI/сервере
без монитора. Попапы Chrome («Save password?», автодополнение) отключены через
prefs, чтобы они не перехватывали клик по Calculate.

## Отчётность и отладка

- Каждый тест получает **свежий драйвер** через фикстуру — тесты независимы
  и не зависят от порядка выполнения.
- При падении теста скриншот автоматически сохраняется в `screenshots/`
  (хук `pytest_runtest_makereport` в `conftest.py`) — минимальная замена Allure.
- В отчёте pytest видно имя каждого параметра, например
  `test_percent_boundaries[-5-200--10]` — сразу понятно, какой набор данных упал.

## Ожидания

Все ожидания — явные, через `WebDriverWait` внутри Page Object
(`visibility_of_element_located`, `element_to_be_clickable`);
`time.sleep()` не используется. Проверка «результата нет» реализована методом
`wait_for_no_result()` (короткий WebDriverWait + `expected condition`).
