import smtplib, requests

my_mail = "stockeye12@gmail.com"
username = "example@gmail.com"
password = "Stockeye@1122"
connection = smtplib.SMTP("smtp.gmail.com")
connection.starttls()
connection.login(user=my_mail, password=password)


api = "https://newsapi.org/v2/everything"
key = "3e0aecb9400946298af7aedaeee87497"

company = "sbin"
para = {
    "qInTitle": company,
    "apiKey": key,
}
r = requests.get(url=api, params=para)
articles = r.json()["articles"]
three_articles = articles[:3]
list = [
    f"Headlines :{article['title']}.\n Brief:{article['description']}"
    for article in three_articles
]
for x in list:
    connection.sendmail(from_addr=my_mail, to_addrs=username, msg=x)
    connection.close()
