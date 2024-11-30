import requests
import json
from colorama import Fore, Style, init

# Inicializar colorama para soporte de color en la terminal
init(autoreset=True)

class StoryGenerator:
    def __init__(self, baseurl="http://127.0.0.1:5000"):
        # Configuración del modelo
        self.baseurl = baseurl
        self.model_url = f"{baseurl}/v1/completions"
        
        # Niveles de creatividad predefinidos
        self.creativity_levels = {
            1: ("Alta", 1.0),
            2: ("Media", 0.7),
            3: ("Baja", 0.3)
        }
        
        # Lista de modelos disponibles
        self.models = self.get_models()
        self.current_model = None
    
    def get_models(self):
        """Obtener lista de modelos disponibles"""
        try:
            url = f"{self.baseurl}/v1/internal/model/list"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['model_names']
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener la lista de modelos: {e}{Style.RESET_ALL}")
            return []
    
    def select_model(self):
        """Seleccionar un modelo de la lista disponible"""
        if not self.models:
            print(f"{Fore.RED}No hay modelos disponibles.{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.CYAN}\nSelecciona un modelo:{Style.RESET_ALL}")
        for i, model in enumerate(self.models, 1):
            print(f"{Fore.YELLOW}{i}. {model}{Style.RESET_ALL}")
        
        while True:
            try:
                option = int(input("Introduce el número del modelo: ")) - 1
                if 0 <= option < len(self.models):
                    selected_model = self.models[option]
                    self.load_model(selected_model)
                    self.current_model = selected_model
                    return selected_model
                else:
                    print("Por favor, selecciona un modelo válido.")
            except ValueError:
                print("Entrada no válida. Introduce un número.")
    
    def load_model(self, model):
        """Cargar un modelo específico"""
        url = f"{self.baseurl}/v1/internal/model/load"
        
        body = {
            'model_name': model,
            "args": {
                "load_in_4bit": True,
                "n_gpu_layers": 12,
            },
            "settings": {
                "instruction_template": "Alpaca"
            }
        }
        
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(body))
            response.raise_for_status()
            print(f"{Fore.GREEN}Modelo {model} cargado exitosamente.{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al cargar el modelo: {e}{Style.RESET_ALL}")
    
    def select_creativity(self):
        """Seleccionar el nivel de creatividad"""
        print("\nSelecciona el nivel de creatividad:")
        for key, (nivel, _) in self.creativity_levels.items():
            print(f"{key}: {nivel}")
        
        while True:
            try:
                option = int(input("Introduce el número de la creatividad: "))
                if option in self.creativity_levels:
                    return self.creativity_levels[option][1]
                else:
                    print("Por favor, selecciona un nivel válido.")
            except ValueError:
                print("Entrada no válida. Introduce un número.")
    
    def generate_story(self, temperature):
        """Generar una historia con los parámetros especificados"""
        print("\nVamos a generar una historia.")
        
        # Solicitar detalles de la historia
        personaje_principal = input("Main character´s name: ")
        personaje_secundario = input("Secondary character´s name: ")
        lugar = input("Place where the story take place: ")
        accion = input("An important action that must happen in the story: ")
        
        # Construir el prompt
        prompt = (f"Write a creative story about two people: {personaje_principal} and {personaje_secundario}, "
                  f"it happens in {lugar}. The history has to revolve around {accion}.")
        
        # Configuración de la solicitud
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        body = {
            "prompt": prompt, 
            "max_tokens": 200, 
            "temperature": temperature,
            "model": self.current_model
        }
        
        try:
            # Realizar la solicitud
            response = requests.post(url=self.model_url, headers=headers, json=body)
            response.raise_for_status()
            
            # Procesar la respuesta
            message_response = response.json()
            
            # Extraer el texto de la historia
            if 'choices' in message_response and len(message_response['choices']) > 0:
                historia = message_response['choices'][0].get('text', '').strip()
            elif 'text' in message_response:
                historia = message_response['text'].strip()
            else:
                historia = "No se pudo generar la historia."
            
            # Mostrar la historia
            print(f"\n{Fore.GREEN}Historia generada:{Style.RESET_ALL}")
            print(historia)
            return historia
        
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con el modelo: {e}")
            return None

def main():
    print("Bienvenido al generador de historias.\n")
    
    # Crear una instancia del generador de historias
    story_generator = StoryGenerator()
    
    # Seleccionar el modelo inicial
    story_generator.select_model()
    
    # Seleccionar el nivel de creatividad inicial
    creativity = story_generator.select_creativity()
    
    while True:
        # Generar historia
        story_generator.generate_story(creativity)
        
        # Menú de opciones
        print("\nOpciones:")
        print("1: Generar otra historia")
        print("2: Cambiar nivel de creatividad")
        print("3: Cambiar modelo")
        print("4: Salir")
        
        # Manejar la elección del usuario
        option = input("Selecciona una opción: ").strip()
        
        if option == "1":
            continue
        elif option == "2":
            creativity = story_generator.select_creativity()
        elif option == "3":
            story_generator.select_model()
        elif option == "4":
            print("Gracias por usar el generador de historias. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, selecciona nuevamente.")

if __name__ == "__main__":
    main()