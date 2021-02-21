import pdfplumber
import os
from pathlib import Path

dir_path = "C:\\Users\\Dell-Laptop\\PycharmProjects\\ECyclyAutStats\\results\\"


class Rider:
    total_races = 9
    races_happened = 7  # TODO replace by count of result files
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
        self.trend = 0

    def predict_points(self):
        races_remain = self.total_races - self.races_happened
        # less/equal than races counting -> no results will be scratched
        if (self.races_counting - self.races_participated) >= races_remain:
            self.predicted_points = self.overall_points + races_remain * self.trend
        # one can chose, which result should count
        else:
            cpy_point_list_sorted_desc = sorted(self.points, reverse=True)
            cpy_list_len = len(cpy_point_list_sorted_desc)
            nr_of_possible_scratches = races_remain - (self.races_counting - self.races_participated)
            # replace scratch results in list
            for i in range(cpy_list_len - nr_of_possible_scratches, cpy_list_len):
                cpy_point_list_sorted_desc[i - 1] = self.trend
            scratch_list_pts = sum(cpy_point_list_sorted_desc)
            self.predicted_points = scratch_list_pts + (
                    self.races_counting - self.races_participated) * self.trend

    def add_result(self, val):
        int_val = int(val)
        self.points.append(int_val)
        self.overall_points += int_val
        self.avg_points = self.overall_points / len(self.points)
        self.races_participated = len(self.points)
        self.predict_points()
        if len(self.points) < 3:
            self.trend = self.avg_points
        else:
            self.trend = sum(self.points[-3:]) / 3

    def get_points_total(self):
        result = 0
        for point in self.points:
            result += point
        return result

    def is_equal(self, name, surname, cat):
        return (self.name == name) and (self.surname == surname) and (self.cat == cat)

    def print_rider_stats(self):
        print('{} {}'.format(self.name, self.surname))
        for event in self.points:
            print(event)


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
                if words[0] != "DSQ" and words[0] != "DNF" and words[0] != "*":
                    rider_found = False
                    # TODO add correctness check
                    name = words[2]
                    surname = words[3]
                    if len(words[len(words) - 2].split(".")) == 2:
                        points_for_race = words[len(words) - 1]
                    else:
                        points_for_race = words[len(words) - 2]
                    cat = words[4]
                    for rider in rider_data:
                        if rider.is_equal(name, surname, cat):
                            rider.add_result(points_for_race)
                            rider_found = True
                            break
                    if not rider_found:
                        new_rider = Rider(name, surname, cat)
                        new_rider.add_result(points_for_race)
                        rider_data.append(new_rider)
            continue
        else:
            continue


def print_results(riders, cat):
    riders.sort(key=lambda x: x.predicted_points, reverse=True)
    place = 1
    print('Pos. Name \t\t races \t predicted (current || avg || trend)')
    for rider in riders:
        if rider.cat == cat:
            print('{} {} \t\t {} \t {} ({} || {} || {})'.format(place, rider.name, rider.races_participated,
                                                                rider.predicted_points, rider.overall_points,
                                                                rider.avg_points, rider.trend))
            place += 1


def print_rider(rider_data, name, surname, cat):
    for rider in rider_data:
        if rider.is_equal(name, surname, cat):
            rider.print_rider_stats()


if __name__ == '__main__':
    data = []
    read_results(data)
    print_results(data, "BIKECARD")
