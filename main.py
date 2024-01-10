import os
import datetime
from flask import Flask, request, render_template
from transformers import pipeline
from markupsafe import escape
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from google.cloud import storage
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook
import yake

app = Flask(__name__)

@app.route("/")
def home():
   x=" "
   i=0
   bucket_name = "uploaddemo_01"
   blob_name = "TM_ML_Model (1).xlsx"
   storage1 = storage.Client()
   bucket = storage1.get_bucket(bucket_name)
   blob = bucket.blob(blob_name)
   data_bytes = blob.download_as_bytes()
   df1 = pd.read_excel(data_bytes)

   count = 0
   for x in df1["Comments"]:
       count = count +1

   neg=0
   pos=0
   neu=0
   for j in range(count):
    sent = df1.iloc[j,5] 
    if sent == "NEGATIVE":
      neg = neg+1
    elif sent == "POSITIVE":
      pos = pos+1
    else:
      neu = neu+1

   unique_location = df1["Location"].unique()
   unique_Cohort_type = df1["Cohort_type"].unique()
   unique_Quater = df1["Quater"].unique()
   unique_list = df1["Cohort ID"].unique()

   df3 = pd.read_excel(data_bytes)
   df4 = pd.read_excel(data_bytes)
   df5 = pd.read_excel(data_bytes)

   tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
   model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
   sentiment_pipeline = pipeline("sentiment-analysis")

   i=0
   for j in range(count):
       x=df1.iloc[j,1]
       if x=="Blank":
           result1="NEUTRAL"
           result2=.5
       else:
           text = str(sentiment_pipeline(x))
           words = text.split()
           word1=words[1]
           result1 = word1[1:-2]
           word2=words[3]
           result2 = word2[0:-2]
       df1.iloc[i,5] = result1 # df1.iloc[0,1]  # print(df1.iloc[0,5])
       df1.iloc[i,6] = round(float(result2)*100,2)
       i = i+1

   blob1 = bucket.blob("output.xlsx")
   df1.to_excel("output.xlsx")
   blob1.upload_from_filename("output.xlsx")

   i=0
   kw_extractor = yake.KeywordExtractor()
   language = "en"
   max_ngram_size = 3
   deduplication_thresold = 0.9
   deduplication_algo = 'seqm'
   windowSize = 1
   numOfKeywords = 5
   custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
  

   p=1
   j=0
   i=1
   i1=0
   str1=""
   x=""
   for j in range(count):
    if df3.iloc[j,1]!="Blank" and df3.iloc[j,6]=="NEGATIVE":
      x=x + df3.iloc[j,1]
   keywords = custom_kw_extractor.extract_keywords(x)
   for kw in keywords:
    str1 = str1 + str(i) +"." + str(kw[0]) + "." + str("\n")
    i = i+1

   p=1
   j=0
   i=1
   i1=0
   str2=""
   x=""
   for j in range(count):
    if df3.iloc[j,1]!="Blank" and df3.iloc[j,6]=="POSITIVE":
      x=x + df3.iloc[j,1]
   keywords = custom_kw_extractor.extract_keywords(x)
   for kw in keywords:
    str2 = str2 + str(i) +"." + str(kw[0]) + "." + str("\n")
    i = i+1

   p=1
   j=0
   i=1
   i1=0
   str3=""
   x=""
   for j in range(count):
    if df3.iloc[j,1]!="Blank" and df3.iloc[j,6]=="NEUTRAL":
      x=x + df3.iloc[j,1]
   keywords = custom_kw_extractor.extract_keywords(x)
   for kw in keywords:
    str3 = str3 + str(i) +"." + str(kw[0]) + "." + str("\n")
    i = i+1

   #data = {'Sentiment Type' : 'Sentiment', 'Positive' : pos, 'Negative' : neg, 'Neutral' : neu}

   return render_template('index.html', tc_dt=datetime.date.today(), count1=len(unique_list), count2=count, neg1=neg, pos1=pos, neu1=neu, str_pos=str2, str_neg=str1, str_neu=str3)

   #return render_template('index.html', data=data, utc_dt=datetime.date.today(), count1=len(unique_list), count2=count, neg1=neg, pos1=pos, neu1=neu, str_pos=str2, str_neg=str1, str_neu=str3)

if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
