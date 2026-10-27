"""Фабрика веб-драйверов.

Создаёт Chrome/Firefox в headless-режиме (по умолчанию) с отключёнными
диалогами «Save password?», автодополнением и стандартными размерами окна.

Режим задаётся переменной окружения:
    HEADLESS=false  pytest   — браузер с окном (для отладки)
    BROWSER=firefox pytest   — запустить тесты в Firefox
"""
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def create_driver(headless: bool | None = None, browser: str | None = None) -> webdriver.Remote:
    browser = (browser or os.getenv("BROWSER", "chrome")).lower()
    if headless is None:
        headless = os.getenv("HEADLESS", "true").lower() != "false"

    if browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.set_preference("browser.privatebrowsing.autostart", True)
        return webdriver.Firefox(options=options)

    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Отключаем попапы Chrome («Save password?», автодополнение),
    # которые могут перехватить клик по кнопке Calculate.
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "autofill.enabled": False,
        },
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=options)
