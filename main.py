import pdfplumber
import os
from pathlib import Path

dir_path = "C:\\Users\\Dell-Laptop\\PycharmProjects\\ECyclyAutStats\\results\\"


class Rider:
    total_races = 9
    races_happened = 6
    races_counting = 7

    def __init__(self, name, surname, cat):
        self.name = name
        self.surname = surname
        self.cat = cat
        self.points = []
        self.overall_points = 0
        self.avg_points = 0
        self.races_participated = 0
        self.predicted_points = 0

    def predict_points(self):
        races_remain = self.total_races - self.races_happened
        races_missed = self.races_happened - self.races_participated
        if (races_missed >= 2):
            self.predicted_points = self.overall_points + races_remain * self.avg_points
        else:
            self.predicted_points = self.overall_points + (
                        self.races_counting - self.races_participated) * self.avg_points

    def add_result(self, val):
        int_val = int(val)
        self.points.append(int_val)
        self.overall_points += int_val
        self.avg_points = self.overall_points / len(self.points)
        self.races_participated = len(self.points)
        self.predict_points()

    def get_points_total(self):
        result = 0
        for point in self.points:
            result += point
        return result

    def is_equal(self, name, surname, cat):
        return (self.name == name) and (self.surname == surname) and (self.cat == cat)


def get_project_root() -> Path:
    return Path(__file__).parent


def read_results(rider_data):
    for filename in os.listdir(dir_path):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(dir_path, filename)
            pdf = pdfplumber.open(pdf_file)
            page = pdf.pages[0]
            text = page.extract_text(x_tolerance=1, y_tolerance=1)
            lines = text.splitlines()
            # print(text)
            pdf.close()
            # extract line to RacerInfo
            del lines[0:6]
            for line in lines:
                words = line.split(" ")
                if (words[0] != "DSQ" and words[0] != "DNF" and words[0] != "*"):
                    rider_found = False
                    # TODO add correctnesscheck
                    name = words[2]
                    surname = words[3]
                    if (len(words[len(words) - 2].split(".")) == 2):
                        points_for_race = words[len(words) - 1]
                    else:
                        points_for_race = words[len(words) - 2]
                    cat = words[4]
                    for rider in rider_data:
                        if rider.is_equal(name, surname, cat):
                            rider.add_result(points_for_race)
                            rider_found = True
                            break
                    if (not rider_found):
                        new_rider = Rider(name, surname, cat)
                        new_rider.add_result(points_for_race)
                        rider_data.append(new_rider)
            continue
        else:
            continue


def print_results(riders, cat):
    riders.sort(key=lambda x: x.predicted_points, reverse=True)
    place = 1
    for rider in riders:
        if (rider.cat == cat):
            print('{} {} \t\t {} \t {} ({} || {})'.format(place, rider.name, rider.races_participated,
                                                          rider.predicted_points, rider.overall_points,
                                                          rider.avg_points))
            place += 1


if __name__ == '__main__':
    rider_data = []
    read_results(rider_data)
    print_results(rider_data, "BIKECARD")
