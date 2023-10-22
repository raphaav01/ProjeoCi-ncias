import openai

class Chat:
    
    def __init__(self):
        openai.api_key = "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"
        self.__model = "text-davinci-003"
        self.__max_tokens = 100
    
    def ask(self, city: str, country: str) -> list:
        
        try:
            prompt = f"Quais são as plantas mais cultivadas em {city} - {country} (retorne apenas os valores separados por ',', nenhum texto a mais)"
            response = openai.Completion.create(engine=self.__model, prompt=prompt, max_tokens = self.__max_tokens)
            return response.choices[0].text.split(",")
                       
        except Exception as e:
            print(str(e))
            return None
        

