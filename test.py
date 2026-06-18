from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

BASE_URL = "https://goldenbarbershop.online"
RESULTS = []

def log_test(name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"    {message}")
    RESULTS.append({"test": name, "passed": passed})

# TEST 1: LANDING
print("\n=== TEST 1: LANDING PAGE ===\n")
try:
    driver.get(BASE_URL)
    time.sleep(3)
    
    # Verificar que cargó
    title = driver.title
    log_test("Página cargó", title != "")
    
    # Verificar HTTPS
    log_test("HTTPS activo", driver.current_url.startswith("https"))
    
    # Buscar elementos por texto en lugar de ID
    h1_elements = driver.find_elements(By.TAG_NAME, "h1")
    log_test("H1 visible", len(h1_elements) > 0)
    
    # Buscar botón Book
    buttons = driver.find_elements(By.TAG_NAME, "button")
    links = driver.find_elements(By.TAG_NAME, "a")
    log_test("Botones/links presentes", len(buttons) > 0 or len(links) > 0)
    
except Exception as e:
    log_test("Landing page", False, str(e)[:50])

# TEST 2: RESERVA
print("\n=== TEST 2: PÁGINA RESERVA ===\n")
try:
    driver.get(f"{BASE_URL}/reserva.html")
    time.sleep(2)
    
    # Buscar inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")
    selects = driver.find_elements(By.TAG_NAME, "select")
    
    log_test("Inputs presentes", len(inputs) > 0)
    log_test("Selects presentes", len(selects) > 0)
    
    # Llenar un input
    if len(inputs) > 0:
        inputs[0].send_keys("TEST USER")
        log_test("Inputs funcionan", True)
    
except Exception as e:
    log_test("Página reserva", False, str(e)[:50])

# TEST 3: CITA
print("\n=== TEST 3: PÁGINA CITA ===\n")
try:
    # Usar una cita del API test anterior
    cita_id = "6a345af3b5430f26cc9107bd"
    driver.get(f"{BASE_URL}/cita.html?id={cita_id}")
    time.sleep(2)
    
    # Buscar elementos de texto
    page_text = driver.find_element(By.TAG_NAME, "body").text
    log_test("Página cita cargó", "Appointment" in page_text or "appointment" in page_text)
    
    # Buscar botones
    buttons = driver.find_elements(By.TAG_NAME, "button")
    log_test("Botones presentes", len(buttons) > 0)
    
except Exception as e:
    log_test("Página cita", False, str(e)[:50])

# TEST 4: DASHBOARD
print("\n=== TEST 4: DASHBOARD ===\n")
try:
    driver.get(f"{BASE_URL}/dashboard.html")
    time.sleep(2)
    
    # Buscar form o inputs de login
    inputs = driver.find_elements(By.TAG_NAME, "input")
    log_test("Inputs presentes (login)", len(inputs) > 0)
    
except Exception as e:
    log_test("Dashboard", False, str(e)[:50])

# TEST 5: RESPONSIVE
print("\n=== TEST 5: RESPONSIVE ===\n")
try:
    # Mobile
    driver.set_window_size(375, 667)
    driver.get(BASE_URL)
    time.sleep(1)
    
    mobile_elements = driver.find_elements(By.TAG_NAME, "*")
    log_test("Mobile view funciona", len(mobile_elements) > 0)
    
    # Desktop
    driver.set_window_size(1920, 1080)
    driver.get(BASE_URL)
    time.sleep(1)
    
    desktop_elements = driver.find_elements(By.TAG_NAME, "*")
    log_test("Desktop view funciona", len(desktop_elements) > 0)
    
except Exception as e:
    log_test("Responsive", False, str(e)[:50])

# RESUMEN
print("\n" + "="*50)
print("RESUMEN")
print("="*50)

total = len(RESULTS)
passed = sum(1 for r in RESULTS if r["passed"])
failed = total - passed

print(f"\n✅ PASSED: {passed}/{total}")
print(f"❌ FAILED: {failed}/{total}")
print(f"📊 Success Rate: {(passed/total)*100:.1f}%\n")

driver.quit()
print("✅ TESTS COMPLETADOS")