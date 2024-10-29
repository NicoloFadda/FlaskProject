import sys  # Necessario per ottenere il nome del test per gli screenshot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pytest

class TestWhatever():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()
        
    def take_screenshot(self):
        test_name = sys._getframe().f_code.co_name
        self.driver.save_screenshot(f'{test_name}.png')

    def test_login_admin_success(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci le credenziali corrette
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("adminpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Verifica che il nome utente sia presente nella pagina
        assert "admin" in self.driver.page_source, "Admin non trovato nella pagina"
        
        # Screenshot del successo del test
        self.take_screenshot()
        
    def test_login_admin_failure(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci credenziali errate
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Verifica la presenza di un messaggio di errore di login
        assert "Please check your login details and try again" in self.driver.page_source, "Messaggio di errore non trovato"
        
        # Screenshot del fallimento del test
        self.take_screenshot()

    def test_logout(self):
        self.driver.get("http://localhost:5000/auth/login")
        
        # Inserisci le credenziali corrette
        self.driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("adminpassword")
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(2)  # Attesa per il caricamento della pagina
        
        # Fai logout
        self.driver.find_element(By.LINK_TEXT, "Logout").click()
        
        time.sleep(2)  # Attesa per il logout
        
        # Verifica che l'utente è stato disconnesso
        assert "Login" in self.driver.page_source, "Logout non avvenuto correttamente"
        
        # Screenshot del logout
        self.take_screenshot()
    def test_whaterver(self):
        self.driver.save_screenshot(f'{sys._getframe().f_code.co_name}.png') # generates a png file with the name of the test function being called
        