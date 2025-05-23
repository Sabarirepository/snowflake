import os

print("Ran the stage")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
REGION = os.getenv("REGION")

print("AWS Access Key:", AWS_ACCESS_KEY_ID)
print("Secret Access Key:", SECRET_ACCESS_KEY)
print("Region:", REGION)