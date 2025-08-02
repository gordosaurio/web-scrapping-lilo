import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


try:
    driver = webdriver.Chrome()

    url = 'https://prima-coffee.com/brew/coffee'
    driver.get(url)
    time.sleep(5)

    try:
        contenedor = driver.find_element(By.XPATH, '//*[@id="topOfPage"]/div[6]/div/div[1]/main/div/div[3]/div[2]')
    except Exception as e:
        print("No se encontró el contenedor de productos, verifica el XPATH y que la web cargó bien.")
        raise e

    productos = contenedor.find_elements(By.XPATH, './/a[contains(@class, "product")]')

    datos = []
    for producto in productos:
        try:
            nombre = producto.find_element(By.XPATH, './/h4/a').text.strip()
        except:
            nombre = ''

        try:
            bloque_precios = producto.text
        except:
            bloque_precios = ''

        precios_encontrados = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', bloque_precios)
        precios_encontrados = [p.replace('$', '').replace(',', '').strip() for p in precios_encontrados]

        precio_sin_descuento = ''
        precio_con_descuento = ''
        if len(precios_encontrados) == 1:
            precio_con_descuento = precios_encontrados[0]
        elif len(precios_encontrados) >= 2:
            precio_sin_descuento = precios_encontrados[0]
            precio_con_descuento = precios_encontrados[1]

        datos.append({
            'nombre': nombre,
            'precio_sin_descuento': precio_sin_descuento,
            'precio_con_descuento': precio_con_descuento
        })

    df = pd.DataFrame(datos)
    df.to_csv('productos_prima_coffee.csv', index=False, encoding='utf-8-sig')
    print("Datos guardados en productos_prima_coffee.csv")

except Exception as err:
    print("Error detectado:", err)
finally:
    try:
        driver.quit()
    except:
        pass
