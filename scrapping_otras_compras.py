#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 08:09:00 2021

@author: anonimo
"""

import pandas as pd
import numpy as np
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

### Se necesitan importar las excepciones de Selenium
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException


### Inicializar el navegador

driver = webdriver.Chrome(ChromeDriverManager().install())
url = 'http://201.238.237.195/VinaDelMar/ControlDecretos/Consultaadquisiciones/index.aspx'
driver.get(url)

### Definir tiempo de esepra
wait = WebDriverWait(driver, 5)


### Objeto que identifica la lista de año y mes
selectioner_year = wait.until(EC.presence_of_element_located((By.XPATH,
                                                              '//*[@id="DD_Año"]')))
selectioner_month = wait.until(EC.presence_of_element_located((By.XPATH,
                                                               '//*[@id="DD_Mes"]')))

dropdown_year = Select(selectioner_year)
dropdown_month = Select(selectioner_month)

### Lista de años y meses
years = [dropdown_year.options[i].text for i in range(1,len(dropdown_year.options))]
months = [dropdown_month.options[i].text for i in range(1,len(dropdown_month.options))]
years.insert(0, 'year')
months.insert(0, 'month')


### Crear lista para guardar los datos
data = []


### For loop para extracción de datos
for i in range(1, len(years)):
    for j in range(1, len(months)):
        print(-i, -j)
        print('Entrando a {} con {}'.format(years[-i], months[-j]))
        dropdown_year.select_by_visible_text(years[-i])
        dropdown_month.select_by_visible_text(months[-j])
        driver.find_element_by_xpath('//*[@id="IB_busca"]').click()
        print('esperando a que este la tabla...')
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Grilla"]')))
            grilla = True
            print('Encontro la grilla...')
        except:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PanelCentroIndex"]/table/tbody/tr[2]/td')))
            grilla = False
            print('No hay grilla...')
        ### Hay que recargar la pagina para que muestre la tabla luego de que \
            # se cargo una tabla que no muestra nada, lo mas facil es recargar \
            # en cada iteración.
        driver.get(driver.current_url)
        
        ### codigo para extraer la información
        if grilla:
            #headers = driver.find_elements_by_tag_name('th')
            headers = driver.find_elements_by_css_selector('th.grillaCabCen')
            columns_names = [headers[i].text for i in range(0, len(headers))]
            td = driver.find_elements_by_css_selector('td.grillaItemCen')
            data += [td[i].text for i in range(0,len(td))]
            while True:
                print('Inside the While')
                td = driver.find_elements_by_css_selector('td.grillaItemCen')
                data += [td[i].text for i in range(0,len(td))]
                try:
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Img_Siguiente"]')))
                    element.click()
                    ### Hay oportunidades que al no haber mas información el \
                        # botón no se desactiva y sale un cuadro de dialogo
                        # extra en donde hay que poner "Ok"
                    try:
                        driver.switch_to.alert.accept()
                        break
                    except:
                        continue
                except TimeoutException:
                    print('brake clickable')
                    break
        
        
        driver.find_element_by_xpath('//*[@id="ImgLimpiar"]').click()
        print('Limpiando campos a seleccionar')
        ### Mensaje de Error --------------------------------------------- \
            # StaleElementReferenceException: stale element reference:
            # element is not attached to the page document
            ### ----------------------------------------------------------
        ### Como sale este error lo mas sencillo es definir nuevamente los \
            # elementos para cada paso, esto según lo que encontré en internet
            # es debido a que JavaScript carga los elementos nuevamente.
        selectioner_year = wait.until(EC.presence_of_element_located((By.XPATH,
                                                              '//*[@id="DD_Año"]')))
        selectioner_month = wait.until(EC.presence_of_element_located((By.XPATH,
                                                               '//*[@id="DD_Mes"]')))
        dropdown_year = Select(selectioner_year)
        dropdown_month = Select(selectioner_month)



### Dado que en la tabla de la pagina el enlace al documento tiene una clase \
    # distinta que el resto de elementos en la tabla no lo reconoce y crea un 
    # problema al momento de pasar los datos a un DataFrame. Por el momento 
    # será eliminado

columns_names.pop(-2)


### Pasar la información a un array y luego crear un DataFrame cambiandole \
    # la forma para que quede en formato tabla.
data = np.array(data)
rows_len = int(data.shape[0]/len(columns_names))
columns_len = len(columns_names)
df = pd.DataFrame(np.reshape(data, (rows_len, columns_len)), columns=columns_names)


### Definir nuevo nombres para las columnas y renombrarlas

col_dict = {'Tipo de Acto Administrativo Aprobatorio':'taaa',
            'Denominacion del Acto Administrativo Aprobatorio':'daaa',
            'Fecha del Acto Administrativo Aprobatorio del Contrato':'fecha_taaa',
            'Número del Acto Administrativo Aprobatorio':'numero_taaa',
            'Nombre Completo o Razón Social de la Persona Contratada':'razon_social',
            'Rut de la Persona Contatada (si Aplica)':'rut',
            'Socios y Accionistas Principales (si Aplica)':'socios_accionistas',
            'Objeto de la Contratación o Adquisición':'motivo_contratacion',
            'Fecha de Inicio del Contarato (DD/MM/AAAAA)':'fecha_inicio',
            'Fecha de Termino del Contarato (DD/MM/AAAA)':'fecha_termino',
            'Monto Total de la Operación':'total_clp',
            'Enlace al Texto Integro del Acto Administrativo Aprovatorio de la Modificación':'enlace'
           }

df.rename(columns=col_dict, inplace=True)


### Guardar la información a un archivo .CSV para su posterior uso.
df.to_csv('otras_compras.csv', index=False)


