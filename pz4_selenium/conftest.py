"""Фикстуры pytest: драйвер на каждый тест + скриншоты при падении."""
import os

import pytest

from utils.driver_factory import create_driver

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


@pytest.fixture
def driver():
    """Свежий браузер на каждый тест — тесты не зависят от порядка выполнения."""
    drv = create_driver()
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняем скриншот в screenshots/ при падении теста (минимальная замена Allure)."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            name = f"{item.name.replace('/', '_').replace('[', '_').replace(']', '')}.png"
            try:
                drv.save_screenshot(os.path.join(SCREENSHOTS_DIR, name))
                print(f"\n[screenshot saved] {name}")
            except Exception:
                pass  # скриншот — лишь помощь при разборе, не часть проверки
