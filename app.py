import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# Función para codificar imagen en base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de la app
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")

st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarlo")

# Parámetros del lienzo
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

# Crear el lienzo de dibujo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Entrada para la clave API de OpenAI
ke = st.text_input('Ingresa tu Clave', type='password')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente de OpenAI
client = OpenAI(api_key=api_key)

# Botón para analizar la imagen
analyze_button = st.button("Analiza la imagen", type="secondary")

# Verificación de condiciones antes de procesar
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Convertir el lienzo a imagen y guardar
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        # Codificar imagen en base64
        base64_image = encode_image_to_base64("img.png")

        # Preparar prompt para el modelo
        prompt_text = "Describe en español brevemente la imagen"

        # Crear payload
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                ],
            }
        ]

        # Hacer la petición a la API
        try:
            full_response = ""
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # 🔍 Verificar si contiene placas autorizadas
            contenido = full_response.upper().replace(" ", "")
            if "CKN364" in contenido or "MXL931" in contenido:
                st.success("✅ Acceso permitido: placa autorizada detectada.")
            else:
                st.error("⛔ Acceso denegado: placa no autorizada.")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if not api_key:
        st.warning("Por favor, ingresa tu API key.")
