"""Page Object для «Percentage Calculator» на calculator.net.

Страница: https://www.calculator.net/percent-calculator.html

Форма calform: [cpar1]% of [cpar2] = [cpar3].
Сервер требует ровно ДВА заполненных поля из трёх и возвращает результат
в блоке <div class="h2result">Result: ...</div>.

В тестах НЕ должно быть ни find_element, ни By, ни WebDriverWait —
всё это скрыто здесь. Методы возвращают self (fluent API),
assert'ов внутри PO нет.
"""
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class PercentCalculatorPage(BasePage):
    URL = "https://www.calculator.net/percent-calculator.html"

    # ------------------------------------------------------------- локаторы
    FORM = (By.CSS_SELECTOR, "form[name='calform']")
    PERCENT_INPUT = (By.ID, "cpar1")          # какой процент (%)
    OF_INPUT = (By.ID, "cpar2")               # от какого числа (of)
    RESULT_VALUE_INPUT = (By.ID, "cpar3")     # = какому значению
    CALCULATE_BUTTON = (By.CSS_SELECTOR, "form[name='calform'] input[type='submit'][value='Calculate']")
    CLEAR_BUTTON = (By.XPATH, "//form[@name='calform']//input[@value='Clear']")
    RESULT_BLOCK = (By.CSS_SELECTOR, ".h2result")

    # --------------------------------------------------------------- actions
    def enter_percent(self, value) -> "PercentCalculatorPage":
        return self._type_into(self.PERCENT_INPUT, value)

    def enter_of(self, value) -> "PercentCalculatorPage":
        return self._type_into(self.OF_INPUT, value)

    def enter_result_value(self, value) -> "PercentCalculatorPage":
        return self._type_into(self.RESULT_VALUE_INPUT, value)

    def click_calculate(self) -> "PercentCalculatorPage":
        self._click(self.CALCULATE_BUTTON)
        # После клика браузер перезагружает страницу (GET-форма),
        # дождёмся, пока форма снова станет доступна.
        self._find_visible(self.FORM)
        return self

    def click_clear(self) -> "PercentCalculatorPage":
        return self._click(self.CLEAR_BUTTON)

    # --------------------------------------------------------------- getters
    def get_result(self) -> str:
        """Текст результата целиком, например 'Result: 20'."""
        return self._find_visible(self.RESULT_BLOCK).text.strip()

    def get_result_number(self) -> float:
        """Численное значение из текста результата ('Result: 20' -> 20.0).

        Нормализует вид числа: 'E+29', запятые как разделители тысяч.
        Бросает ValueError, если число извлечь не удалось.
        """
        text = self.get_result()
        match = re.search(r"-?[\d.,]+(?:[eE][-+]?\d+)?", text.replace("Result:", ""))
        if not match:
            raise ValueError(f"Не удалось извлечь число из: {text!r}")
        return float(match.group(0).replace(",", ""))

    def wait_for_no_result(self, timeout: int = 6) -> bool:
        """True, если блока с результатом так и нет (невалидный ввод).

        Ждём короткий срок через WebDriverWait: если .h2result не появился —
        страница не показала результат, что и ожидается при неверных данных.
        """
        from selenium.common.exceptions import TimeoutException

        short_wait = WebDriverWait(self.driver, timeout, poll_frequency=0.5)
        try:
            short_wait.until(lambda d: bool(d.find_elements(*self.RESULT_BLOCK)))
            return False      # результат всё-таки появился
        except TimeoutException:
            return True       # результата нет — страница его не показала

    def get_percent_value(self) -> str:
        return self._find_visible(self.PERCENT_INPUT).get_attribute("value")

    def get_of_value(self) -> str:
        return self._find_visible(self.OF_INPUT).get_attribute("value")

    def get_result_value_field(self) -> str:
        return self._find_visible(self.RESULT_VALUE_INPUT).get_attribute("value")
