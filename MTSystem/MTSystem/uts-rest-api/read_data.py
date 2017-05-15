import csv

csvfile = open("/Users/tareksakakini/Box Sync/Arches/Aim1/Datasets/OSF_data.csv", "rb")

data = csv.DictReader(csvfile)

for row in data:
	print row["Sig"]

#print data[0]

