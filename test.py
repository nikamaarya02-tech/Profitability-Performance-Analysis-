import os

print("Current Folder:", os.getcwd())
print("Files:", os.listdir())

with open("Nassau Candy Distributor.csv", "r") as f:
    print("CSV Found Successfully")