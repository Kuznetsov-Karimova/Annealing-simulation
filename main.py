import input_reader
import random
from copy import deepcopy
from math import exp

def details_metric(data):

    count_machines = len(data)
    count_details = len(data[0])

    similarity = [[0 for i in range(count_details)] for j in range(count_details)]
    sim_pairs = []

    for first_detail in range(count_details):
        for second_detail in range(first_detail + 1, count_details):

            a, b, c = (0, 0, 0)

            for machine in range(count_machines):

                if data[machine][first_detail] == 1 or data[machine][second_detail] == 1:

                    if data[machine][first_detail] == 0:
                        c += 1
                    elif data[machine][second_detail] == 0:
                        b += 1
                    else:
                        a += 1

            if a+b+c:
                metric = round(a/(a+b+c), 2)
            else:
                metric = 0

            if metric:
                similarity[first_detail][second_detail] = metric
                similarity[second_detail][first_detail] = metric
                sim_pairs.append((metric, first_detail, second_detail))

    sim_pairs.sort(reverse=True)

    return similarity, sim_pairs


def initial_details(data, n_clusters):

    similarity, sim_pairs = details_metric(data)
    print(sim_pairs)

    count_details = len(similarity)
    detail_cluster = [-1] * count_details
    cluster_number = 0
    max_cluster = 0

    for _, first_detail, second_detail in sim_pairs:

        if detail_cluster[first_detail] == -1 and detail_cluster[second_detail] == -1:
            detail_cluster[first_detail] = cluster_number
            detail_cluster[second_detail] = cluster_number
            cluster_number = (cluster_number + 1) % n_clusters
            max_cluster = max_cluster + 1
        elif detail_cluster[first_detail] == -1:
            detail_cluster[first_detail] = detail_cluster[second_detail]
        elif detail_cluster[second_detail] == -1:
            detail_cluster[second_detail] = detail_cluster[first_detail]

    if max_cluster < n_clusters:
        n_clusters = max_cluster

    for detail in range(count_details):
        if detail_cluster[detail] == -1:
            detail_cluster[detail] = random.randint(0, n_clusters - 1)

    print(detail_cluster)

    clusters = {i: [] for i in range(n_clusters)}
    for num, detail_cl in enumerate(detail_cluster):
        clusters[detail_cl].append(num)

    return clusters

def initial_machines(data, detail_cluster):

    count_machines = len(data)
    n_clusters = len(detail_cluster)
    machine_cluster = {i: [] for i in range(n_clusters)}
    errors = []

    for machine in range(count_machines):
        machine_error = []
        for cluster in range(n_clusters):
            n_1_in = 0
            n_0_in = 0
            n_1_out = sum(data[machine])
            for detail in detail_cluster[cluster]:
                if data[machine][detail] == 0:
                    n_0_in += 1
                else:
                    n_1_in +=1
            n_1_out = n_1_out - n_1_in
            machine_error.append(n_1_out + n_0_in)
        errors.append(machine_error)

    for machine in range(count_machines):
        min_error = min(errors[machine])
        not_empty = True
        poses = [pos for pos, value in enumerate(errors[machine]) if value == min_error]
        for cluster in poses:
            if len(machine_cluster[cluster]) == 0:
                machine_cluster[cluster].append(machine)
                not_empty = False
                break
        if not_empty:
            pos = random.choices(poses, k = 1)[0]
            machine_cluster[pos].append(machine)
    return machine_cluster


def init_solution(data, n_clusters):
    detail_cluster = initial_details(data, n_clusters)
    machine_cluster = initial_machines(data, detail_cluster)
    return detail_cluster, machine_cluster

def f_score(data, detail_cluster ,machine_cluster):

    n_1 = sum(list(map(sum, data)))

    n_1_out, n_0_in = (0, 0)

    for cluster in detail_cluster:
        for machine in machine_cluster[cluster]:
            n_1_in = 0
            for detail in detail_cluster[cluster]:
                if data[machine][detail] == 0:
                    n_0_in += 1
                else:
                    n_1_in += 1

            n_1_out += sum(data[machine]) - n_1_in

    if n_1+n_0_in:
        return (n_1 - n_1_out) / (n_1+n_0_in)
    else:
        return 0


class Annealing:
    def __init__(self, path, start_temp, final_temp, cooling_rate, max_iter, max_stag, exchange):
        self.data = input_reader.create_data(path)
        self.start_temp = start_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
        self.max_iter = max_iter
        self.max_stag = max_stag
        self.exchange = exchange
        self.max_attempt = 100
        self.n_clusters = 2
        self.counter_mc = 0
        self.counter_trapped = 0
        self.counter_stag = 0
        self.counter = 0

    def init_sol(self):
        self.current_sol = init_solution(self.data, self.n_clusters)


    def single_move(self, sol):
        detail_cluster = deepcopy(sol[0])
        #print(detail_cluster)
        machine_cluster = deepcopy(sol[1])
        not_solo = False
        attempt = 0
        cluster = 0
        while not(not_solo) and (attempt < self.max_attempt):
            attempt += 1
            cluster = random.randint(0, len(detail_cluster)-1)
            if len(detail_cluster[cluster]) > 1:
                not_solo = True
        if (attempt == self.max_attempt):
            return detail_cluster, machine_cluster
        swap_index = random.randint(0, len(detail_cluster[cluster])-1)
        swap_detail = detail_cluster[cluster][swap_index]
        detail_cluster[cluster].remove(swap_detail)
        best = sol
        max_val = -10000000
        for cl in range(len(detail_cluster)):
            if cl!= cluster:
                detail_cluster[cl].append(swap_detail)
                neigh_machine_cluster = initial_machines(self.data, detail_cluster)
                neight_val = f_score(self.data, detail_cluster, neigh_machine_cluster)
                if neight_val > max_val:
                    max_val = neight_val
                    best = (deepcopy(detail_cluster), neigh_machine_cluster)
                detail_cluster[cl].pop()
        return best

    def exchange_move(self, sol):
        detail_cluster = deepcopy(sol[0])
        #print(detail_cluster)
        machine_cluster = deepcopy(sol[1])
        not_solo = False
        attempt = 0
        cluster = 0
        while not(not_solo) and (attempt < self.max_attempt):
            attempt += 1
            cluster = random.randint(0, len(detail_cluster)-1)
            if len(detail_cluster[cluster]) > 1:
                not_solo = True
        if (attempt == self.max_attempt):
            return detail_cluster, machine_cluster
        swap_index = random.randint(0, len(detail_cluster[cluster])-1)
        swap_detail = detail_cluster[cluster][swap_index]
        detail_cluster[cluster].remove(swap_detail)
        best = sol
        max_val = -10000000
        for cl in range(len(detail_cluster)):
            if cl!= cluster:
                swap_detail_2 = detail_cluster[cl][random.randint(0, len(detail_cluster[cl])-1)]
                detail_cluster[cl].remove(swap_detail_2)
                detail_cluster[cl].append(swap_detail)
                detail_cluster[cluster].append(swap_detail_2)
                neigh_machine_cluster = initial_machines(self.data, detail_cluster)
                neight_val = f_score(self.data, detail_cluster, neigh_machine_cluster)
                if neight_val > max_val:
                    max_val = neight_val
                    best = (deepcopy(detail_cluster), neigh_machine_cluster)
                detail_cluster[cl].pop()
                detail_cluster[cl].append(swap_detail_2)
                detail_cluster[cluster].remove(swap_detail_2)
        return best

    def iteration(self):
        while (self.counter_mc < self.max_iter) and (self.counter_trapped < self.max_iter/2):
            neigh_sol = self.single_move(self.current_sol)
            if self.counter % self.exchange == 0:
                neigh_sol = self.exchange_move(neigh_sol)
            neigh_sol_val = f_score(self.data, *neigh_sol)
            cur_cluster_best_val = f_score(self.data, *self.best_sol_cur_clust)
            if neigh_sol_val > cur_cluster_best_val:
                self.best_sol_cur_clust = neigh_sol
                self.current_sol = neigh_sol
                self.counter_stag = 0
            elif neigh_sol_val == cur_cluster_best_val:
                self.counter_stag += 1
                self.current_sol = neigh_sol
            else:
                cur_val = f_score(self.data, *self.current_sol)
                delta = neigh_sol_val - cur_val

                if random.uniform(0, 1) <= exp(delta/self.cur_temp):
                    self.current_sol = neigh_sol
                    self.counter_trapped = 0
                else:
                    self.counter_trapped += 1

            self.counter_mc +=1



    def current_cluster_opt(self):
        self.counter_mc = 0
        self.counter_trapped = 0
        self.counter_stag = 0
        self.cur_temp = self.start_temp

        if self.n_clusters > 2:
            self.init_sol()
            self.best_sol_cur_clust = self.current_sol

        self.iteration()
        while (self.cur_temp > self.final_temp) and (self.counter_stag <  self.max_stag):
            self.cur_temp *= self.cooling_rate
            self.counter += 1
            self.counter_mc = 0
            print("LOCAL BEST:", f_score(self.data, self.best_sol_cur_clust[0], self.best_sol_cur_clust[1]))
            self.iteration()

    def algorithm(self):
        self.n_clusters = 2
        self.init_sol()
        self.best_sol = self.current_sol
        self.best_sol_cur_clust = self.current_sol
        self.current_cluster_opt()

        while (f_score(self.data, *self.best_sol_cur_clust) > f_score(self.data, *self.best_sol)):
            self.best_sol = self.best_sol_cur_clust
            for s in self.best_sol:
                for ind_s in s:
                    for i in range(len(s[ind_s])):
                        s[ind_s][i] += 1
                print(s)
                for ind_s in s:
                    for i in range(len(s[ind_s])):
                        s[ind_s][i] -= 1
            print(self.best_sol[0], self.best_sol[1])
            print(f_score(self.data, *self.best_sol))
            self.opt_clust = self.n_clusters
            self.n_clusters += 1
            self.current_cluster_opt()


        return self.best_sol

if __name__ == '__main__':

    start_temperature = 0.1
    final_temperature = 0.001
    cooling_rate = 0.7
    max_iterations = 3000
    max_stagnant = 50
    exchange = 10

    path = "benchs/37x53.txt"
    model = Annealing(path, start_temperature, final_temperature, cooling_rate, max_iterations, max_stagnant, exchange)
    print(model.data)
    model.init_sol()
    print(model.current_sol[0])
    print(model.current_sol[1])
    res = f_score(model.data, model.current_sol[0], model.current_sol[1])
    print(res)
    res = model.algorithm()
    res = f_score(model.data, res[0], res[1])
    print(res)
