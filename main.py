import PySimpleGUI as sg
import yt_dlp
import os
import threading

# Función para seleccionar la carpeta de destino
def select_folder():
    folder = sg.popup_get_folder('Seleccione la carpeta de destino')
    if folder:
        window['-FOLDER-'].update(folder)
    return folder

def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes:
            progress = int(downloaded_bytes / total_bytes * 100)
            window['-PROGRESS-'].update_bar(progress)
            window['-PROGRESS_TEXT-'].update(f'{progress}%')

# Función para descargar y convertir video a mp3
def download_video(url, download_folder):
    if not url:
        sg.popup("Advertencia", "Por favor ingrese una URL de YouTube.", icon='warning')
        return

    if not download_folder:
        sg.popup("Advertencia", "Por favor seleccione una carpeta de destino.", icon='warning')
        return

    window['-PROGRESS-'].update(visible=True, current_count=0, max=100)  # Mostrar el spinner de carga
    window['-DOWNLOAD-'].update(disabled=True)  # Deshabilitar el botón de descarga

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],  # Añadir el gancho de progreso
        }
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            downloaded_file = os.path.join(download_folder, f"{video_title}.mp3")
            
            if os.path.exists(downloaded_file):
                sg.popup("¡Listo!", f"Descargado y convertido: {downloaded_file}", icon='info')
            else:
                sg.popup("Advertencia", "No se pudo encontrar el archivo convertido.", icon='warning')

    except Exception as e:
        sg.popup("Error", f"Error al descargar el video: {str(e)}", icon='error')

    window['-PROGRESS-'].update(visible=False)
    window['-PROGRESS_TEXT-'].update('')
    window['-DOWNLOAD-'].update(disabled=False)  # Habilitar el botón de descarga

# Layout de la interfaz gráfica
layout = [
    [sg.Text("URL de YouTube:")],
    [sg.Input(key='-URL-', size=(50, 1)), sg.Button("Pegar enlace", key='-PASTE-')],
    [sg.Button("Seleccionar Carpeta de Destino", key='-SELECT-')],
    [sg.Text("", key='-FOLDER-', size=(50, 1))],
    [sg.Button("Descargar y Convertir", key='-DOWNLOAD-')],
    [sg.Text("", size=(50, 1))],
    [sg.ProgressBar(max_value=100, orientation='h', size=(20, 20), key='-PROGRESS-', visible=False)],
    [sg.Text("", key='-PROGRESS_TEXT-', size=(50, 1), text_color='black')]
]

icon_path = "mi_tube\mito-_1_.ico"
# Crear la ventana
window = sg.Window("Mi Tube II", layout, icon=icon_path)

# Variable para almacenar la carpeta seleccionada
download_folder = ""

def start_download_thread(url, folder):
    threading.Thread(target=download_video, args=(url, folder), daemon=True).start()

# Loop de eventos
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == '-SELECT-':
        download_folder = select_folder()
    elif event == '-DOWNLOAD-':
        download_video(values['-URL-'], download_folder)
    elif event == '-PASTE-':
        clipboard_content = window.TKroot.clipboard_get()
        window['-URL-'].update(clipboard_content)

# Cerrar la ventana
window.close()
