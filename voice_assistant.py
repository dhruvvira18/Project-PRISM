import datetime
import math
import random
import re
import pyttsx3
import requests
import speech_recognition as sr


class VoiceAssistant:
    def __init__(self):
        self._setup_core_components()
        self._setup_apis()
        self._setup_responses()
        self._initialize_assistant()

    def _setup_core_components(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.assistant_name = "DeepSphere"
        self._configure_voice()

    def _setup_apis(self):
        self.gemini_api_key = "AIzaSyBCykYBBDfStZZidBdtVGksEnSNCjVQouo" # insert your Gemini API key here
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def _setup_responses(self):
        self.responses = {
            "hello": ["Hello! How can I help you today?", "Hi there!", "Hello! Nice to meet you!"],
            "how are you": ["I'm doing great, thank you for asking!", "I'm fine, how about you?"],
            "what is your name": [f"I'm {self.assistant_name}, your personal voice assistant!", f"You can call me {self.assistant_name}.", f"I'm {self.assistant_name}."],
            "goodbye": ["Goodbye! Have a great day!", "See you later!", "Bye! Take care!"],
            "thank you": ["You're welcome!", "Happy to help!", "No problem!"],
        }

    def _initialize_assistant(self):
        print("DeepSphere initialized successfully!")
        self.speak(f"Hello! I'm {self.assistant_name}. How can I help you today?")
        self._test_gemini_connection()

    def _configure_voice(self):
        voices = self.tts_engine.getProperty('voices')
        print(f"Found {len(voices)} voices available")
        
        if voices:
            print(f"Using default voice: {voices[0].name}")
        
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 1.0)

    def _test_gemini_connection(self):
        print("Testing Gemini API connection...")
        if self.ask_gemini("Say hello in one sentence"):
            print("Gemini API connected successfully!")
        else:
            print("Gemini API connection failed - check your API key")

    def speak(self, text):
        print(f"Assistant: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        timeout = 30
        phrase_limit = 60
        threshold = 200
        pause_threshold = 1.5
        try:
            with self.microphone as source:
                print("Listening for input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                self.recognizer.energy_threshold = threshold
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = pause_threshold

                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

            print("Processing speech...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text

        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            error_msg = "I couldn't understand that clearly. Please try again with clearer speech."
            print("Speech was unclear - please try again")
            self.speak(error_msg)
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            self.speak("Sorry, I'm having trouble with the speech recognition service.")
            return None
        except Exception as e:
            print(f"Error during listening: {e}")
            self.speak("Sorry, something went wrong while listening. Please try again.")
            return None

    def ask_gemini(self, prompt):
        try:
            full_prompt = f"You are a friendly voice assistant. Answer naturally and conversationally. Keep responses concise but helpful.\n\nUser: {prompt}\nAssistant:"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.6,
                    "maxOutputTokens": 500,
                    "topP": 0.7,
                    "topK": 30
                }
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                json=payload,
                headers=headers,
                timeout=30
            )
            if response.ok:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        answer = candidate["content"]["parts"][0]["text"].strip()
                        print(f"Gemini Response: {answer[:100]}...")
                        return answer
                else:
                    print(f"Gemini API error: {data}")
            else:
                print(f"Gemini API request failed: {response.status_code} - {response.text}")
            
            return None

        except Exception as e:
            print(f"Gemini API request failed: {e}")
            return None

    def handle_math(self, command):
        try:
            expr = command.lower().strip()
            print(f"Processing math command: {expr}")

            if "square root" in expr or "root" in expr:
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if numbers:
                    number = float(numbers[0])
                    result = math.sqrt(number)
                    return f"The square root of {number} is {result:.4f}"

            if "cube root" in expr:
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if numbers:
                    number = float(numbers[0])
                    result = number ** (1/3)
                    return f"The cube root of {number} is {result:.4f}"

            if "factorial" in expr:
                numbers = re.findall(r'\d+', expr)
                if numbers:
                    number = int(numbers[0])
                    if number < 0:
                        return "Factorial is not defined for negative numbers"
                    if number > 20:
                        return f"Factorial of {number} is too large to calculate"
                    result = math.factorial(number)
                    return f"The factorial of {number} is {result}"

            if any(word in expr for word in ["power", "raised to", "to the power"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    base = float(numbers[0])
                    exponent = float(numbers[1])
                    result = base ** exponent
                    return f"{base} to the power of {exponent} is {result}"

            if any(word in expr for word in ["plus", "add", "addition"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    num1 = float(numbers[0])
                    num2 = float(numbers[1])
                    result = num1 + num2
                    return f"{num1} plus {num2} equals {result}"

            if any(word in expr for word in ["minus", "subtract", "subtraction"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    num1 = float(numbers[0])
                    num2 = float(numbers[1])
                    result = num1 - num2
                    return f"{num1} minus {num2} equals {result}"

            if any(word in expr for word in ["times", "multiply", "multiplication"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    num1 = float(numbers[0])
                    num2 = float(numbers[1])
                    result = num1 * num2
                    return f"{num1} times {num2} equals {result}"

            if any(word in expr for word in ["divided by", "divide", "division"]):
                numbers = re.findall(r'\d+(?:\.\d+)?', expr)
                if len(numbers) >= 2:
                    num1 = float(numbers[0])
                    num2 = float(numbers[1])
                    if num2 == 0:
                        return "Cannot divide by zero"
                    result = num1 / num2
                    return f"{num1} divided by {num2} equals {result:.4f}"

            if any(word in expr for word in ["modulo", "mod", "remainder"]):
                numbers = re.findall(r'\d+', expr)
                if len(numbers) >= 2:
                    num1 = int(numbers[0])
                    num2 = int(numbers[1])
                    if num2 == 0:
                        return "Cannot divide by zero"
                    result = num1 % num2
                    return f"The remainder when {num1} is divided by {num2} is {result}"

            if any(op in expr for op in ["+", "-", "", "/", "*", "%"]):
                clean_expr = re.sub(r'[^\d+\-*/.()%]', '', expr)
                if clean_expr:
                    try:
                        result = eval(clean_expr)
                        if isinstance(result, (int, float)):
                            if result == int(result):
                                result = int(result)
                            return f"The answer is {result}"
                    except:
                        pass

            numbers = re.findall(r'\d+(?:\.\d+)?', expr)
            if numbers:
                return f"I found the numbers: {', '.join(numbers)}. Please specify an operation like 'plus', 'minus', 'times', or 'divided by'."

            return "I couldn't understand the math operation. Please try phrases like '5 plus 3' or '10 times 2'."

        except Exception as e:
            print(f"Math calculation error: {e}")
            return f"Sorry, I couldn't calculate that. Error: {str(e)}"

    def process_command(self, command):
        if not command:
            return True

        command = command.lower().strip()

        if any(word in command for word in ["quit", "exit", "goodbye", "bye", "stop"]):
            self.speak("Goodbye! Have a great day!")
            return False

        basic_response = self._get_basic_response(command)
        if basic_response:
            self.speak(basic_response)
            return True

        if "time" in command and ("what" in command or "tell" in command):
            current_time = datetime.datetime.now().strftime("It's %I:%M %p")
            self.speak(current_time)
            return True

        if "date" in command or "day" in command:
            current_date = datetime.datetime.now().strftime("Today is %A, %B %d, %Y")
            self.speak(current_date)
            return True

        math_indicators = ["plus", "minus", "times", "multiply", "divide", "divided by", "add", "subtract", 
                          "addition", "subtraction", "multiplication", "division", "power", "raised to", 
                          "square root", "root", "cube root", "factorial", "modulo", "mod", "remainder", "calculate", 
                          "solve", "compute", "find", "result", "answer", "how much is", "equals"]
        
        has_math_operation = any(indicator in command for indicator in math_indicators)
        has_math_operators = any(char in command for char in "+-/%*")
        has_numbers = re.search(r'\d+', command)
        
        if ((has_math_operation and has_numbers) or has_math_operators or (has_numbers and any(word in command for word in ["calculate", "solve", "compute", "result", "answer"]))):
            result = self.handle_math(command)
            if result:
                self.speak(result)
                return True

        question_words = ["what", "who", "when", "where", "why", "how", "explain", "define", "tell me", "can you", "could you", "would you", "in detail", "more about", "information", "details", "explanation", "describe", "elaborate", "how to"]
        
        is_complex_question = any(word in command for word in question_words)
        
        if is_complex_question:
            answer = self.ask_gemini(command)
            
            if answer:
                self.speak(answer)
            else:
                self.speak("I'm having trouble getting a response right now. Please try again.")
            return True
        
        answer = self.ask_gemini(command)
        if answer:
            self.speak(answer)
        else:
            fallback_responses = [
                "I'm not sure how to help with that. Could you try rephrasing?",
                "I didn't understand that. Can you ask me something else?",
                "That's interesting! Could you be more specific?"
            ]
            self.speak(random.choice(fallback_responses))
        return True

    def _get_basic_response(self, user_input):
        for key, responses in self.responses.items():
            if key in user_input:
                return random.choice(responses)
        
        return None

    def run(self):
        print("\n" + "="*60)
        print("DEEPSPHERE VOICE ASSISTANT STARTED")
        print("Connected to Gemini AI")
        print("Say 'quit', 'exit', or 'goodbye' to stop")
        print("Continuous listening mode enabled")
        print("I can do math and answer any questions!")
        print("="*60 + "\n")

        while True:
            try:
                user_input = self.listen()

                if user_input:
                    result = self.process_command(user_input)

                    if result == False:
                        break

            except KeyboardInterrupt:
                print("\nShutting down...")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Sorry, something went wrong. Let's try again.")

def main():
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"Failed to start: {e}")
        print("Check your libraries and API key.")


if __name__ == "__main__":
    main()