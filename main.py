import yagmail

yag = yagmail.SMTP("@gmail.com", "your app pass") #get this in your gmai ->turn on 2FA -> search app password

data = {
    "sample@gmail.com": "receiver name",
}


for email, name in data.items():
    yag.send(
        to=email,
        subject="EMAIL AUTOMATION TESTING",
        contents=f"input content"
    )

print("email sent")