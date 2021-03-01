import pdfplumber
import os
import argparse
import cmd
from tqdm import tqdm


class Rider:
    total_races = 9
    races_happened = 7  # this is overwritten later by number of found result files
    races_counting = 7  # number of races counting for the final results

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
            nr_of_possible_scratches = max(0, races_remain - (self.races_counting - self.races_participated))
            # replace scratch results in list (with trend of last 3 races)
            for i in range(cpy_list_len - nr_of_possible_scratches, cpy_list_len):
                cpy_point_list_sorted_desc[i - 1] = self.trend
            predicted_list_pts = sum(cpy_point_list_sorted_desc)
            self.predicted_points = predicted_list_pts + (
                    self.races_counting - self.races_participated) * self.trend

    def add_result(self, val):
        """ Add race result to points"""
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
        """ determining equality based on name, surname and race category """
        return (self.name.lower() == name.lower()) and (self.surname.lower() == surname.lower()) and (
                self.cat.lower() == cat.lower())

    def print_stats(self):
        """ print all relevant rider stats"""
        print('{} {}'.format(self.name, self.surname))
        print('{}'.format(self.cat))
        print(f"Participated in {self.races_participated} of {Rider.races_happened} races")
        print(f"Points achieved: {self.overall_points}")
        for pts_of_event in self.points:
            print(f"  {pts_of_event}")
        print("Average points: {:.2f}".format(self.avg_points))
        print("Trending points: {:.2f}".format(self.trend))
        print("Points predicted {:.2f}".format(self.predicted_points))


def read_results(dir_path, rider_data):
    """Import results. Currently, only results from https://www.e-cycling-austria.at/ are supported"""
    file_count = 0
    for filename in tqdm(os.listdir(dir_path)):
        if filename.endswith(".pdf"):
            file_count += 1
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
                    if len(words[-2].split(".")) == 2:
                        points_for_race = words[-1]
                    else:
                        points_for_race = words[-2]
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
    Rider.races_happened = file_count


def print_current_leaderboard(riders, cat):
    """
    Print the current leaderboard of given race category (cat).
    :param riders: data of past results of different riders
    :param cat: race category, which should be predicted. String must exactly match the race category
    """
    place = 1
    print(f"{'Pos.':<5} {'Name':<15} {'races':<6} {'predicted':<10} ({'current':<8} || {'avg':<8} || {'trend':<8})")
    for rider in riders:
        if rider.cat.lower() == cat.lower():
            print('{:<5} {:<15} {:<6} {:<10} ({:<8.2f} || {:<8.2f} || {:<8.2f})'.format(place, rider.name,
                                                                                        rider.races_participated,
                                                                                        rider.overall_points,
                                                                                        rider.predicted_points,
                                                                                        rider.avg_points, rider.trend))
            place += 1


def print_predicted_results(riders, cat):
    """
    Print the predicted results of given race category (cat).
    :param riders: data of past results of different riders
    :param cat: race category, which should be predicted. String must exactly match the race category
    """
    riders.sort(key=lambda x: x.predicted_points, reverse=True)
    place = 1
    print(f"{'Pos.':<5} {'Name':<15} {'races':<6} {'predicted':<10} ({'current':<8} || {'avg':<8} || {'trend':<8})")
    for rider in riders:
        if rider.cat.lower() == cat.lower():
            print('{:<5} {:<15} {:<6} {:<10.2f} ({:<8} || {:<8.2f} || {:<8.2f})'.format(place, rider.name,
                                                                                        rider.races_participated,
                                                                                        rider.predicted_points,
                                                                                        rider.overall_points,
                                                                                        rider.avg_points, rider.trend))
            place += 1


def print_rider(rider_data, name, surname, cat):
    found = False
    for rider in rider_data:
        if rider.is_equal(name, surname, cat):
            rider.print_stats()
            found = True
            break
    if not found:
        print("Rider not found")


def determine_existing_categories(rider_data):
    cat = []
    for rider in rider_data:
        if not rider.cat in cat:
            cat.append(rider.cat)
    return cat


class ProgramShell(cmd.Cmd):
    intro = "Welcome to the Race Analyzer. All Result files were imported. Type help or ? to list all commands\n"
    prompt = '> '
    file = None

    def __init__(self, dataset):
        super(ProgramShell, self).__init__()
        self.data = dataset
        self.existing_cat = determine_existing_categories(dataset)

    def do_predict(self, arg):
        argsplit = parse(arg)
        if len(argsplit) != 1:
            print("Invalid number of arguments - expected three: PREDICT Category")
        else:
            print_predicted_results(self.data, argsplit[0])

    def help_predict(self):
        print(
            f'Display predicted race series results. Category must match exactly. \n  Available categories: {self.existing_cat} \n  --> PREDICT Category')

    def do_riderstats(self, arg):
        argsplit = parse(arg)
        if len(argsplit) != 3:
            print("Invalid number of arguments - expected three: RIDERSTATS Name Surname Category")
        else:
            print_rider(self.data, argsplit[0], argsplit[1], argsplit[2])

    def help_riderstats(self):
        print(
            'Displays stats of a dedicated rider. Name, Surname and Category must match exactly. \n  Available categories: {} \n  --> RIDERSTATS NAME SURNAME CATEGORY'.format(
                self.existing_cat))

    def do_leaderboard(self, arg):
        argsplit = parse(arg)
        if len(argsplit) != 1:
            print("Invalid number of arguments - expected one: LEADERBOARD Category")
        else:
            print_current_leaderboard(self.data, argsplit[0])

    def help_leaderboard(self):
        print(
            f'Display current leaderboard. Category must match exactly. \n  Available categories {self.existing_cat}: \n  --> LEADERBOARD Category')

    def do_exit(self, arg):
        'Stop recording, close the turtle window, and exit:\n  --> EXIT'
        print('Thank you for using Turtle')
        return True


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(arg.split())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir')
    args = parser.parse_args()
    inp_dir_path = args.dir

    # Read data based on given directory
    data = []
    read_results(inp_dir_path, data)

    ProgramShell(data).cmdloop()
