"""Автотесты калькулятора процентов (calculator.net).

В тестах нет find_element / By / WebDriverWait / time.sleep —
взаимодействие со страницей только через PercentCalculatorPage.
"""
import json
import os
import re

import pytest

from pages.percent_calculator_page import PercentCalculatorPage

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "percent_cases.json")


def load_json_cases():
    with open(DATA_FILE, encoding="utf-8") as f:
        return [
            pytest.param(c["percent"], c["of"], c["expected"],
                         id=f"{c['percent']}pct-of-{c['of']}")
            for c in json.load(f)
        ]


# ---------------------------------------------------------------- корректный расчёт
@pytest.mark.parametrize("percent, of_value, expected", load_json_cases())
def test_percent_of_from_json(driver, percent, of_value, expected):
    """Параметризованный happy path из data/percent_cases.json (Доп. 1)."""
    page = (
        PercentCalculatorPage(driver)
        .open()
        .enter_percent(percent)
        .enter_of(of_value)
        .click_calculate()
    )
    assert page.get_result_number() == pytest.approx(expected)


@pytest.mark.parametrize(
    "percent, of_value, expected",
    [
        (10, 200, 20),      # базовый кейс из задания
        (50, 40, 20),
        (7, 300, 21),
        (12.5, 64, 8),
        (99, 99, 98.01),
    ],
)
def test_percent_of_correct(driver, percent, of_value, expected):
    """Корректный расчёт: минимум 5 наборов данных."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(percent).enter_of(of_value).click_calculate()
    assert page.get_result_number() == pytest.approx(expected, rel=1e-6)


def test_solve_missing_base(driver):
    """Режим «процент и результат известны» — калькулятор находит число: 10% от X = 50 -> X=500."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(10).enter_result_value(50).click_calculate()
    assert page.get_result_number() == pytest.approx(500)


def test_solve_missing_percent(driver):
    """Режим «число и результат известны» — калькулятор находит процент: из 200 получилось 20 -> 10%."""
    page = PercentCalculatorPage(driver).open()
    page.enter_of(200).enter_result_value(20).click_calculate()
    assert "10%" in page.get_result()


# ------------------------------------------------------------------ граничные значения
@pytest.mark.parametrize(
    "percent, of_value, expected",
    [
        (0, 500, 0),           # ноль как процент
        (10, 0, 0),            # ноль как число
        (0, 0, 0),             # оба нуля
        (-5, 200, -10),        # отрицательный процент допустим
        (10, -200, -20),       # отрицательное число допустимо
        (1000000, 1000000, 1e10),  # большое значение (upper boundary)
    ],
)
def test_percent_boundaries(driver, percent, of_value, expected):
    """Граничные значения: 0, отрицательные, максимум."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(percent).enter_of(of_value).click_calculate()
    assert page.get_result_number() == pytest.approx(expected, rel=1e-6)


# --------------------------------------------------------------------- неверный ввод
@pytest.mark.parametrize(
    "bad_percent, bad_of",
    [
        ("abc", "200"),            # буквы в первом поле
        ("10", "abc"),             # буквы во втором поле
        ("10;drop table", "200"),  # спецсимволы / попытка инъекции
        ("", ""),                  # оба поля пустые
        ("10", ""),                # заполнено только первое поле
        ("", "200"),               # заполнено только второе поле
    ],
)
def test_invalid_input_shows_no_result(driver, bad_percent, bad_of):
    """Неверный ввод (буквы, пустые поля) — результата на странице нет."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(bad_percent).enter_of(bad_of).click_calculate()
    assert page.wait_for_no_result(timeout=6), \
        "калькулятор не должен показывать результат при невалидном вводе"


def test_very_long_number_is_handled(driver):
    """Слишком длинное число: страница не падает — считает или молча не показывает результат."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent("1" * 40).enter_of("2").click_calculate()
    # Допустимы оба варианта поведения, главное — нет зависания/ошибки страницы
    if not page.wait_for_no_result(timeout=6):
        assert page.get_result_number() > 0


# --------------------------------------------------------------- формат вывода
def test_result_format_percent_sign(driver):
    """Формат вывода: при поиске процента результат показан с знаком % ('Result: 10%')."""
    page = PercentCalculatorPage(driver).open()
    page.enter_of(200).enter_result_value(20).click_calculate()
    result = page.get_result()
    assert result.startswith("Result:")
    assert result.endswith("%")


def test_result_rounding_and_decimal_format(driver):
    """Формат вывода: дробный результат показан десятичным числом с точкой как разделителем.

    Сайт возвращает 'Result: 0.333333333' — проверяем формат, а не точность:
    только цифры/точка/минус, без запятых (локаль) и без лишних слов.
    """
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(33.3333333).enter_of(1).click_calculate()
    result = page.get_result()
    assert result.startswith("Result:")
    number = result.split(":", 1)[1].strip()
    assert re.fullmatch(r"-?\d+(\.\d+)?", number), f"некорректный формат числа: {number!r}"
    assert "," not in number, "локаль: десятичный разделитель должен быть точкой"
    # значение корректно: 33.3333333% от 1
    assert page.get_result_number() == pytest.approx(0.333333333, rel=1e-6)


# --------------------------------------------------------------------- кнопка Clear
def test_clear_resets_inputs(driver):
    """Поведение кнопки «Clear»: поля очищаются, URL остаётся на месте."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(10).enter_of(200)
    url_before = driver.current_url

    page.click_clear()

    assert page.get_percent_value() == ""
    assert page.get_of_value() == ""
    assert driver.current_url == url_before, "Clear не должен перезагружать страницу"


def test_clear_then_new_calculation(driver):
    """После Clear можно посчитать заново — старые значения не подмешиваются."""
    page = PercentCalculatorPage(driver).open()
    page.enter_percent(10).enter_of(200).click_calculate()
    assert page.get_result_number() == pytest.approx(20)

    page.click_clear()
    page.enter_percent(50).enter_of(80).click_calculate()
    assert page.get_result_number() == pytest.approx(40)
