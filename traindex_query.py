import requests
import json
import pandas as pd
import re


api_url = "https://api.traindex.io/patents/v6/query"
API_KEY = "xxxxxxxxxxxxxxxxxxxxx"   # Please provide the actual Traidex API_KEY

source = """
Published before 2014-09-30



A vehicular windshield washer fluid replenishing system for conditioning and treating water that impacts the vehicular windshield for use in a preexisting windshield washer reservoir comprising:

a collection funnel for receipt of water that drains from the windshield for directional passage to an outlet;

a housing coupled to said collection funnel outlet, said housing defined by a top wall, a bottom wall, a pair of side walls, an inlet end wall, an outlet end wall, an intermediate wall extending horizontally between the top and bottoms walls, and first and second passageway walls extending orthogonally from the bottom wall to the intermediate wall and from one of the sidewalls to the other sidewalls, wherein the first passageway wall is adjacent the inlet end wall and the second passageway wall is located adjacent the outlet end wall;

an ion exchange resin chamber containing an ion exchange resin, wherein the ion exchange chamber is bounded by the first and second passageway walls, the intermediate wall, the bottom wall, and the pair of sidewalls;

an inlet in a portion of the inlet wall adjacent the first passageway wall;

a fluid conduit coupled to said inlet in said inlet end wall and to said outlet of said collection funnel for conditioning of collected water;

a mixing chamber bounded by the outlet end wall, the second passageway wall, the intermediate wall, the bottom wall, and the pair of sidewalls, wherein said mixing chamber is fluidly coupled to said ion exchange chamber through said second passageway wall and adds a fluid concentrate to the conditioned water;

a concentrate chamber containing said fluid concentrate, wherein the concentrate chamber is bounded by the top wall, the intermediate wall, and the inlet end wall, the outlet end wall, and the pair of sidewalls;

a wick extending from the concentrate chamber to said mixing chamber for providing a capillary draw of said fluid concentrate from the concentrate chamber to said mixing chamber;

an outlet in a portion of the outlet end wall adjacent the mixing chamber; and

a fluid conduit coupled to said outlet in the outlet end wall, wherein said conditioned and treated water is directed to the preexisting windshield washer reservoir through said fluid conduit.
"""


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


def query_traindex_api(input_text, output_num=100):
  headers = {
    "x-api-key": API_KEY
  }

  body = {
    "request": {
      "conceptFeaturesString": input_text["text"],
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
  output = query_traindex_api(input_text)

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
  """
    Filter the output from Traindex API by the date in the first line.
    Ex:
      Published before 2014-09-30
  """
  input_text = clean_input_text(query_text)
  
  if len(input_text["date"]) > 0:
    output = query_traindex_api(input_text)

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
  input_text = clean_input_text(source)
  output = query_traindex_api(input_text, output_num=100)
  print(output)
