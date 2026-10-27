"""Базовый Page Object: общие операции и ожидания для всех страниц."""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    #: URL страницы — переопределяется в наследниках
    URL = ""
    #: таймаут явных ожиданий, сек
    TIMEOUT = 15

    def __init__(self, driver):
        self.driver = driver
        # Единое место для WebDriverWait: ожидания живут в PO, а не в тестах.
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    # ------------------------------------------------------------------ actions
    def open(self):
        """Открывает страницу калькулятора и ждёт её готовности."""
        self.driver.get(self.URL)
        self.wait.until(EC.number_of_windows_to_be(1))
        return self

    def _find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _type_into(self, locator, value):
        field = self._find_visible(locator)
        field.clear()
        field.send_keys(str(value))
        return self

    def _click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        return self

    # ------------------------------------------------------------------ getters
    @property
    def title(self) -> str:
        return self.driver.title
