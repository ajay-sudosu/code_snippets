import csv
import requests

quest_data = list(csv.reader(open("quest.csv")))
# old_covid_data = list(csv.reader(open("covid.csv")))

final_data = [quest_data[0]]
# covid_data = [quest_data[0]]

for i in range(1, len(quest_data)):

    if "quest" in quest_data[i][1].lower() or "labcorp" in quest_data[i][1].lower():
        final_data.append(quest_data[i])

# for i in range(1, len(old_covid_data)):
#     temp = old_covid_data[i]

#     temp[12] = temp[12].split(";")[0].replace("m-fr", "Monday-Friday").replace("m-f", "Monday-Friday")
#     covid_data.append(temp)

with open("quest.csv","w+") as my_csv:
    csvWriter = csv.writer(my_csv,delimiter=',')
    csvWriter.writerows(final_data)

# with open("covid.csv","w+") as my_csv:
#     csvWriter = csv.writer(my_csv,delimiter=',')
#     csvWriter.writerows(covid_data)