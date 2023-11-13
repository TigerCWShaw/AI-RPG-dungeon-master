import openai
import secret_key

openai.api_key = secret_key.SECRET_KEY

class ChatApp:
    def __init__(self):
        # Setting the API key to use the OpenAI API
        openai.api_key = secret_key.SECRET_KEY
        self.messages = []

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"].content})
        return response["choices"][0]["message"]

    def feedback(self, emphasis=''):
        message = "provide 3 feedbacks or improvements for me based on our conversation using formats like this: Feedback 1: content\n Feedback 2: content\n Feedback 3: content\n"
        if emphasis == '':
            return self.chat(message)
        else:
            return self.chat(message + " with emphasis on " + emphasis)