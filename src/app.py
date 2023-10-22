import tkinter as tk
from tkinter import ttk
import requests
import datetime
import json
from googletrans import Translator
import locale
from service.chatgpt import Chat

class WeatherForecastApp:
    def __init__(self):
        self.openweathermap_api_key = self.load_api_key()
        self.chat = Chat()
        if not self.openweathermap_api_key:
            raise ValueError(
                "A chave da API não foi fornecida no arquivo de configuração."
            )


        self.location = None
        self.translator = Translator()
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

        self.create_window()


    def load_api_key(self):
        with open("config.json") as config_file:
            config = json.load(config_file)
            return config.get("openweathermap_api_key")

    def create_window(self):
        window = tk.Tk()
        window.title("Previsão do Tempo")
        window.attributes("-fullscreen", True)

        label_location = tk.Label(
            window, text="Localização (Cidade, País):")
        label_location.pack()

        self.location_entry = tk.Entry(window)
        self.location_entry.pack()

        button_get_recommended_crop = ttk.Button(
            window, text="Obter Cultura Recomendada", command=self.process_recommended_crop
        )
        button_get_recommended_crop.pack(pady=10)

        button_get_daily_forecast = ttk.Button(
            window, text="Obter Previsão do Dia", command=self.process_daily_forecast
        )
        button_get_daily_forecast.pack(pady=10)

        self.result_text = tk.Text(window, height=10, width=80)
        self.result_text.pack()

        button_reset = ttk.Button(
            window, text="Limpar", command=self.reset_fields
        )
        button_reset.pack(pady=5)

        button_exit = ttk.Button(window, text="Sair", command=self.exit_app)
        button_exit.pack(pady=10)

        self.window = window
        window.mainloop()

    def process_recommended_crop(self):
        self.location = self.location_entry.get()

        if not self.location:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Localização não fornecida.")
            return

        city, country = self.location.split(",")

        response = self.chat.ask(city, country) 
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(
                tk.END,
                f"As culturas mais indicadas para as condições climáticas é: {response}.",
        )

    def process_daily_forecast(self):
        self.location = self.location_entry.get()

        if not self.location:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Localização não fornecida.")
            return

        city, country = self.location.split(",")

        location_key = self.get_location_key(city.strip(), country.strip())
        if not location_key:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Localização não encontrada.")
            return

        current_datetime = datetime.datetime.now()
        current_date = current_datetime.date()

        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},{country}&appid={self.openweathermap_api_key}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        if forecast_response.status_code == 200:
            forecast_list = forecast_data.get("list", [])

            if forecast_list:
                filtered_forecast = [
                    forecast
                    for forecast in forecast_list
                    if datetime.datetime.fromtimestamp(forecast["dt"]).date() == current_date
                ]

                self.result_text.delete(1.0, tk.END)
                if filtered_forecast:
                    self.show_daily_forecast(filtered_forecast)
                else:
                    self.result_text.insert(
                        tk.END, "Nenhuma previsão encontrada para o dia atual.")
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(
                    tk.END, "Nenhuma previsão encontrada para a data informada."
                )
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, "Erro ao obter previsão do tempo."
            )

    def get_location_key(self, city, country):
        location_url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={self.openweathermap_api_key}"
        location_response = requests.get(location_url)
        location_data = location_response.json()
        location_key = location_data.get("id")
        return location_key

    def get_recommended_crop(self, forecast_list):
        average_temperature = self.calculate_average_temperature(forecast_list)
        average_humidity = self.calculate_average_humidity(forecast_list)

        if 10 <= average_temperature <= 20:
            if 70 <= average_humidity <= 90:
                return "Arroz"
        elif 20 <= average_temperature <= 30:
            if 40 <= average_humidity <= 70:
                return "Maçãs"
        else:
            if 40 <= average_humidity <= 60:
                return "Palmeiras"

        if 10 <= average_temperature <= 20:
            if average_humidity > 90:
                return "Arroz"
        elif 20 <= average_temperature <= 30:
            if average_humidity < 40:
                return "Maçãs"
        else:
            if average_humidity < 40:
                return "Palmeiras"

        # Caso nenhuma cultura se enquadre nas condições, retorna a menos pior
        if average_temperature < 10:
            return "Arroz"
        elif average_temperature > 30:
            return "Palmeiras"
        else:
            return "Maçãs"

    def calculate_average_temperature(self, forecast_list):
        temperatures = [forecast["main"]["temp"] for forecast in forecast_list]
        return sum(temperatures) / len(temperatures)

    def calculate_average_humidity(self, forecast_list):
        humidities = [forecast["main"]["humidity"]
                      for forecast in forecast_list]
        return sum(humidities) / len(humidities)

    def show_daily_forecast(self, forecast_list):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(
            tk.END,
            f"Previsão para hoje ({datetime.datetime.now().strftime('%d/%m/%Y')}):\n"
        )

        for forecast in forecast_list:
            temperature = forecast["main"]["temp"]
            humidity = forecast["main"]["humidity"]
            description = forecast["weather"][0]["description"]

            translation = self.translator.translate(description, dest='pt')
            translated_description = translation.text.capitalize()

            self.result_text.insert(
                tk.END,
                f"Temperatura: {temperature}°C\n"
            )
            self.result_text.insert(
                tk.END,
                f"Umidade: {humidity}%\n"
            )
            self.result_text.insert(
                tk.END,
                f"Descrição: {translated_description}\n"
            )
            self.result_text.insert(tk.END, "------------\n")

    def reset_fields(self):
        self.location_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def exit_app(self):
        self.window.destroy()


if __name__ == "__main__":
    weather_app = WeatherForecastApp()
