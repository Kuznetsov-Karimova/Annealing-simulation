def create_data(path):

    with open(path, "r") as file:
        count_m, count_p = map(int, file.readline().split())

        data = [[0 for i in range(count_p)] for j in range(count_m)]

        for machine in range(count_m):
            matched_details = list(map(int, file.readline().split()))[1:]
            for detail in matched_details:
                data[machine][detail - 1] = 1

        return data
