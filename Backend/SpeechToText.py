from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import os 
import mtranslate as mt
from dotenv import load_dotenv


load_dotenv()

InputLanguage = os.getenv("INPUT_LANGUAGE")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")


with open(r"../Data/Voice.html" , "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"file://{os.path.abspath('../Data/Voice.html')}"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = rf"C:\Users\User\Desktop\Jarvis\Frontend\Files"

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data" , "w",encoding="utf-8") as f:
        print("im storing .....")
        f.write(Status)

def QueryModifier(Query):
    new_Query = Query.lower().strip()
    query_words = new_Query.split()
    question_words = ["what", "when", "where", "why", "how", "which", "whose" , "whom" , "who", "can you" ,"what's","where's" , "how's" , "can you"]

    if any(word + " " in new_Query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
           new_Query = new_Query[:-1]+"?"
        else:
           new_Query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
           new_Query = new_Query[:-1]+"."
        else:
           new_Query += "."
    return new_Query.capitalize()


def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en" , "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get(Link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "start")))
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text

            if Text:
                driver.find_element(By.ID, "end").click()
                if InputLanguage.lower()=='en' or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
    