# Web Scraping
# Trae el valor de dolar_blue para la Compra y Venta desde la web de Clarin y DolarHoy
# Desarrollo : LORENA SANCHEZ - cel: +54 9 291 649 6020 
# Versión: 2024
# 


import requests
from bs4 import BeautifulSoup
import json
import re
import tkinter as tk
from tkinter import messagebox

# Encabezados para simular un navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def formatear_valor(valor):
    valor_float = float(valor.replace('.', '').replace(',', '.'))
    return f"$ {valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def obtener_dolar_blue(url, fuente, parseo_func):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza un error si la respuesta es un error HTTP
        return parseo_func(response.content)
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud a {fuente}: {e}")
        return None

def parseo_clarin(content):
    soup = BeautifulSoup(content, 'html.parser')
    script_tags = soup.find_all('script')
    for script in script_tags:
        if script.string:
            try:
                json_text = re.search(r'\{.*\}', script.string)
                if json_text:
                    datos = json.loads(json_text.group(0))
                    for item in datos['mainEntity']['itemListElement']:
                        if item['name'] == 'Dólar Blue':
                            compra = next(rate['price'] for rate in item['currentExchangeRate'] if rate['priceType'] == 'Compra')
                            venta = next(rate['price'] for rate in item['currentExchangeRate'] if rate['priceType'] == 'Venta')
                            return {"fuente": "Clarin", "compra": compra, "venta": venta}
            except json.JSONDecodeError as e:
                print(f"Error al obtener datos de Clarin: {e}")
    return None

def parseo_cronista(content):
    soup = BeautifulSoup(content, "html.parser")
    try:
        compra = soup.find('span', class_='buy').find('div', class_='val').get_text(strip=True).replace('$', '').strip()
        venta = soup.find('span', class_='sell').find('div', class_='val').get_text(strip=True).replace('$', '').strip()
        return {"fuente": "Cronista", "compra": compra, "venta": venta}
    except AttributeError:
        print("No se pudo encontrar el valor del Dólar Blue de compra o venta.")
        return None

def parseo_dolarHoy(content):
    soup = BeautifulSoup(content, "html.parser")
    try:
        dolar_blue = soup.find('a', href="/cotizaciondolarblue")
        compra = dolar_blue.find('div', class_='compra').text.strip()
        venta = dolar_blue.find('div', class_='venta').text.strip()
        return {"fuente": "DolarHoy", "compra": compra, "venta": venta}
    except AttributeError:
        print("No se pudo encontrar el valor del Dólar Blue de compra o venta.")
        return None

def mostrar_resultados(resultados):
    ventana = tk.Tk()
    ventana.title("Cotización del Dólar Blue - Lorena Sánchez - 2024")
    texto_resultados = tk.Text(ventana, height=10, width=50)
    texto_resultados.pack(pady=10)
    for fuente, valores in resultados.items():
        texto_resultados.insert(tk.END, f"{fuente} - Compra: {valores['compra']} , Venta: {valores['venta']}\n")
    btn_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy)
    btn_cerrar.pack(pady=10)
    ventana.mainloop()

def main():
    urls = [
        ("https://www.clarin.com/economia/divisas-acciones-bonos/monedas/dolar-blue", "Clarin", parseo_clarin),
        ("https://www.cronista.com/MercadosOnline/moneda.html?id=ARSB", "Cronista", parseo_cronista),
        ("https://dolarhoy.com/cotizaciondolarblue", "DolarHoy", parseo_dolarHoy)
    ]
    
    resultados = {}
    for url, fuente, parseo_func in urls:
        resultado = obtener_dolar_blue(url, fuente, parseo_func)
        if resultado:
            resultados[resultado['fuente']] = {
                'compra': formatear_valor(resultado['compra']),
                'venta': formatear_valor(resultado['venta'])
            }
    
    if resultados:
        mostrar_resultados(resultados)
    else:
        messagebox.showwarning("Sin Resultados", "No se pudieron obtener los datos del Dólar Blue.")

if __name__ == "__main__":
    main()