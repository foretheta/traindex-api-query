import requests
import json
import re
import pandas as pd


api_url = "https://api.traindex.io/patents/v6/query"
API_KEY = "xxxxxxxxxxxxxxxxx"   # Please provide the actual Traidex API_KEY

with open("source.txt") as f:
  source = f.read()


def clean_input_text(input_text):
  text = input_text.strip()
  text_lines = text.split("\n")

  date = re.sub("\D", "", text_lines[0])
  text = " ".join(line.rstrip() for line in text_lines)
  text = text.lower()
  text = re.sub("[^a-z]", " ", text) # Removing digits
  text = re.sub("\s+", " ", text)
  text = [word for word in text.split(" ") if len(word) < 20 and len(word) > 2]
  text = " ".join(text)

  return {"date": date, "text": text.strip()}


def query_traindex_api(query_text, output_num=100):
  headers = {
    "x-api-key": API_KEY
  }

  body = {
    "request": {
      "conceptFeaturesString": query_text,
      "maxNumItems": output_num
    }
  }
  try:
    response = requests.post(api_url, data=json.dumps(body), headers=headers)
    if response.status_code == 403:
      print("Please make sure your API key is correct")
      return
    elif not response.status_code // 100 == 2:
      print(f"Error: Unexpected response {response}")
      print(f"Message: {response.json()['message']}")
      return
    return json.loads(response.text)
  except requests.exceptions.RequestException as e:
    print(e)


def get_full_output(query_text):
  input_text = clean_input_text(query_text)
  output = query_traindex_api(input_text["text"])

  ucid = []
  priority_date = []
  conceptScore = []
  for item in output["foundItems"]:
    ucid.append(item["ucid"].replace("-", ""))
    priority_date.append(item["priority_date"])
    conceptScore.append(item["conceptScore"])

  df = pd.DataFrame({
    "UCID": ucid,
    "Priority Date": priority_date,
    "Concept Score": conceptScore
  })
  df.to_csv("output.csv")


def get_filtered_output_by_date(query_text):
  input_text = clean_input_text(query_text)
  
  if len(input_text["date"]) > 0:
    output = query_traindex_api(input_text["text"])

    ucid = []
    priority_date = []
    conceptScore = []
    for item in output["foundItems"]:
      if item["priority_date"] < input_text["date"]:
        ucid.append(item["ucid"].replace("-", ""))
        priority_date.append(item["priority_date"])
        conceptScore.append(item["conceptScore"])

    df = pd.DataFrame({
      "UCID": ucid,
      "Priority Date": priority_date,
      "Concept Score": conceptScore
    })
    df.to_csv("output.csv")


if __name__ == "__main__":
  get_filtered_output_by_date(source)
