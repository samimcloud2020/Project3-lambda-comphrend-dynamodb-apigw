import requests
import json
import datetime
import boto3
from decimal import Decimal

#this lambda grabs today's headlines, does sentiment analysis using AWS Comprehend
#and saves the news along with sentiment into a dynamodb table
def lambda_handler(event, context):
    print("Start News Online Update")
    if event["action"] == "news":
        findnews()
        
    else:
        deletenews()
        
def findnews():
    r = requests.get("https://newsapi.org/v2/top-headlines?country=in&apiKey=1d38501366bf45ad83a296269ac8ce5e")
    if r.status_code == 200:
        data = r.json()
        if data["status"] == "ok":
            for i in data["articles"]:
                Source = i["source"]["name"]
                Title = i["title"]
                Timestamp = i["publishedAt"]
                Content = i["content"]
                sentiment = json.loads(getsentiment(Title)) #Title is string, and send to getsentiment() as string. after getsentiment() returned string , now json.loads() make it dict
                print(type(sentiment)) #dict
                print(sentiment)
                SentimentScore = Decimal(sentiment['SentimentScore']['Mixed'])
                print(type(SentimentScore))
                Negative = Decimal(sentiment['SentimentScore']['Negative'])
                Neutral = Decimal(sentiment['SentimentScore']['Neutral'])
                Positive = Decimal(sentiment['SentimentScore']['Positive'])
                print(SentimentScore)
                putdynamodb(sentiment["Sentiment"],Timestamp,Title,Source,SentimentScore,Negative,Neutral,Positive)
        else:
            print("ERROR")
             
    else:
        print(f"ERROR: {r.status_code}")
    
def getsentiment(Title):
    client = boto3.client('comprehend')
    return(json.dumps(client.detect_sentiment(Text=Title,LanguageCode='en'), sort_keys=True))
    #fired to comprehend and comphrend returned as dict , so json.dumps() make it string and returned string
    
    
def putdynamodb(Sentiment,Timestamp,Title,Source,SentimentScore,Negative,Neutral,Positive):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('news')
    response = table.put_item(
    Item={
        'sentiment': Sentiment,
        'timestamp': Timestamp,
        'title': Title,
        'source': Source,
        'SentimentScore': SentimentScore,
        'Negative': Negative,
        'Neutral': Neutral,
        'Positive': Positive
        }
        )
        
    
    
  
                
                


    
