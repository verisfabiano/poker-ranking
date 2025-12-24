#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste usando Selenium para verificar se o conteúdo é renderizado no navegador.
"""
import os
import time

# Verificar se Selenium está instalado
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    print("[OK] Selenium está instalado")
except ImportError:
    print("[ERRO] Selenium não está instalado")
    print("Instale com: pip install selenium")
    print("Também precisa: pip install webdriver-manager")
    exit(1)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    print("[OK] WebDriver Manager está instalado")
except ImportError:
    print("[ERRO] WebDriver Manager não está instalado")
    print("Instale com: pip install webdriver-manager")
    exit(1)

print("\n" + "="*80)
print("TESTE SELENIUM: Renderizando página no navegador Chrome")
print("="*80)

try:
    # Configurar opções do Chrome
    chrome_options = Options()
    # Comentei headless para ver o navegador
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    print("\n[1] Iniciando navegador Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Acessar a página
    print("[2] Acessando http://127.0.0.1:8000/painel/")
    driver.get("http://127.0.0.1:8000/painel/")
    
    # Esperar carregar
    print("[3] Aguardando carregamento (5 segundos)...")
    time.sleep(5)
    
    # Tirar screenshot
    screenshot_path = 'c:\\projetos\\poker_ranking\\painel_screenshot.png'
    driver.save_screenshot(screenshot_path)
    print(f"[4] Screenshot salvo em: {screenshot_path}")
    
    # Verificar se há conteúdo visível
    print("\n[5] Analisando conteúdo visível...")
    
    # Procurar por main tag
    try:
        main = driver.find_element(By.TAG_NAME, "main")
        print("[OK] <main> tag encontrada")
        
        # Pegar tamanho e visibilidade
        main_size = main.size
        main_location = main.location
        main_displayed = main.is_displayed()
        main_text = main.text[:200] if main.text else ""
        
        print(f"    - Size: {main_size}")
        print(f"    - Location: {main_location}")
        print(f"    - Displayed: {main_displayed}")
        print(f"    - Text (primeiras 200 chars): {main_text}...")
        
    except Exception as e:
        print(f"[ERRO] Não consegui encontrar <main>: {e}")
    
    # Procurar por .sidebar-admin
    try:
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar-admin")
        sidebar_displayed = sidebar.is_displayed()
        print(f"\n[OK] Sidebar encontrada")
        print(f"    - Displayed: {sidebar_displayed}")
    except Exception as e:
        print(f"[ERRO] Sidebar não encontrada: {e}")
    
    # Procurar por h1
    try:
        h1 = driver.find_element(By.TAG_NAME, "h1")
        h1_displayed = h1.is_displayed()
        h1_text = h1.text
        print(f"\n[OK] <h1> encontrado")
        print(f"    - Text: {h1_text}")
        print(f"    - Displayed: {h1_displayed}")
    except Exception as e:
        print(f"[ERRO] <h1> não encontrado: {e}")
    
    # Procurar por season-card
    try:
        season_cards = driver.find_elements(By.CLASS_NAME, "ranking-season-card")
        print(f"\n[OK] {len(season_cards)} season-cards encontrados")
        if season_cards:
            first_card = season_cards[0]
            first_card_displayed = first_card.is_displayed()
            first_card_text = first_card.text[:100]
            print(f"    - Primeiro card: {first_card_text}")
            print(f"    - Displayed: {first_card_displayed}")
    except Exception as e:
        print(f"[ERRO] Season-cards não encontrados: {e}")
    
    # Executar JavaScript para calcular altura do conteúdo visível
    print("\n[6] Analisando computações de CSS...")
    try:
        # Procurar por elementos com display: none
        hidden_elements = driver.execute_script("""
            const elements = document.querySelectorAll('*');
            let hidden = [];
            elements.forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                    if (el.className && (el.className.includes('main') || el.className.includes('container') || el.className.includes('content'))) {
                        hidden.push({
                            tag: el.tagName,
                            class: el.className,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity
                        });
                    }
                }
            });
            return hidden;
        """)
        
        if hidden_elements:
            print(f"[ALERTA] {len(hidden_elements)} elementos principais com CSS que os oculta:")
            for el in hidden_elements:
                print(f"    - {el}")
        else:
            print("[OK] Nenhum elemento principal está ocultado por CSS")
    
    except Exception as e:
        print(f"[ERRO] Não consegui executar JavaScript: {e}")
    
    # Pegar o HTML renderizado
    print("\n[7] Salvando HTML renderizado...")
    html_content = driver.page_source
    with open('c:\\projetos\\poker_ranking\\painel_rendered.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[OK] HTML salvo em: c:\\projetos\\poker_ranking\\painel_rendered.html ({len(html_content)} bytes)")
    
    print("\n[AGUARDANDO] Navegador permanecerá aberto por 10 segundos para inspecionar...")
    print("Pressione ENTER para fechar...")
    input()
    
    driver.quit()
    print("\n[OK] Teste concluído!")
    
except Exception as e:
    print(f"\n[ERRO GERAL] {e}")
    import traceback
    traceback.print_exc()
