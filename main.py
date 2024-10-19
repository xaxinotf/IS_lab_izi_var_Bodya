import csv
import random
from collections import defaultdict

# Параметри алгоритму
POPULATION_SIZE = 100
GENERATIONS = 200
MUTATION_RATE = 0.1

DAYS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця"]
PERIODS = [1, 2, 3, 4]

# Завантаження груп
def load_groups(filename):
    groups = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_name = row['GroupName']
            num_students = int(row['NumStudents'])
            groups[group_name] = num_students
    return groups

# Завантаження предметів
def load_subjects(filename):
    subjects = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_name = row['GroupName']
            subject_info = {
                'subject_name': row['SubjectName'],
                'lecture_hours': int(row['LectureHours']),
                'practice_hours': int(row['PracticeHours']),
                'needs_split': row['NeedsSplit'] == 'Yes'
            }
            subjects[group_name].append(subject_info)
    return subjects

# Завантаження викладачів
def load_lecturers(filename):
    lecturers = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            lecturer_name = row['LecturerName']
            subject_info = {
                'subject_name': row['SubjectName'],
                'class_type': row['ClassType']
            }
            lecturers[lecturer_name].append(subject_info)
    return lecturers

# Завантаження аудиторій
def load_rooms(filename):
    rooms = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            room_name = row['RoomName']
            capacity = int(row['Capacity'])
            rooms[room_name] = capacity
    return rooms

# Створення списку всіх можливих часових слотів
def create_time_slots():
    time_slots = []
    for day in DAYS:
        for period in PERIODS:
            time_slots.append((day, period))
    return time_slots

# Поділ на підгрупи
def create_subgroups(groups, subjects):
    subgroups = {}
    for group in groups:
        subgroups[group] = groups[group]
        for subj in subjects[group]:
            if subj['needs_split']:
                num_students = groups[group]
                subgroup_size = num_students // 2
                subgroups[group + '_1'] = subgroup_size
                subgroups[group + '_2'] = num_students - subgroup_size
    return subgroups

# Генеруємо випадковий розклад
def create_random_schedule(groups, subjects, lecturers, rooms, time_slots):
    schedule = []
    # Генеруємо лекції, об'єднуючи групи за потреби
    lecture_subjects = get_lecture_subjects(subjects)
    for subject_name, group_list in lecture_subjects.items():
        lecture_hours = subjects[group_list[0]][0]['lecture_hours'] // 1.5  # Кількість пар
        for _ in range(int(lecture_hours)):
            gene = create_lecture_gene(group_list, subject_name, 'Лекція', lecturers, rooms, time_slots, groups)
            schedule.append(gene)
    # Генеруємо практичні заняття для кожної групи
    for group in groups:
        for subj in subjects[group]:
            practice_hours = subj['practice_hours'] // 1.5  # Кількість пар
            class_type = 'Практика'
            if subj['needs_split'] and '_1' not in group and '_2' not in group:
                # Поділ на підгрупи
                subgroup1 = group + '_1'
                subgroup2 = group + '_2'
                num_students1 = groups[group] // 2
                num_students2 = groups[group] - num_students1
                for _ in range(int(practice_hours)):
                    gene1 = create_gene(subgroup1, subj['subject_name'], class_type, lecturers, rooms, time_slots, num_students1)
                    gene2 = create_gene(subgroup2, subj['subject_name'], class_type, lecturers, rooms, time_slots, num_students2)
                    schedule.extend([gene1, gene2])
            elif '_1' in group or '_2' in group:
                for _ in range(int(practice_hours)):
                    gene = create_gene(group, subj['subject_name'], class_type, lecturers, rooms, time_slots, groups[group])
                    schedule.append(gene)
            else:
                for _ in range(int(practice_hours)):
                    gene = create_gene(group, subj['subject_name'], class_type, lecturers, rooms, time_slots, groups[group])
                    schedule.append(gene)
    return schedule

def get_lecture_subjects(subjects):
    lecture_subjects = defaultdict(list)
    for group, subj_list in subjects.items():
        for subj in subj_list:
            if subj['lecture_hours'] > 0:
                lecture_subjects[subj['subject_name']].append(group)
    return lecture_subjects

# Створення гена для лекції
def create_lecture_gene(group_list, subject, class_type, lecturers, rooms, time_slots, groups):
    possible_lecturers = [lect for lect in lecturers if any(
        subj['subject_name'] == subject and subj['class_type'] == class_type for subj in lecturers[lect])]
    if not possible_lecturers:
        lecturer = 'Невідомий'
    else:
        lecturer = random.choice(possible_lecturers)
    room = random.choice(list(rooms.keys()))
    time_slot = random.choice(time_slots)
    total_students = sum(groups[group] for group in group_list if group in groups)
    gene = {
        'groups': group_list,
        'subject': subject,
        'class_type': class_type,
        'lecturer': lecturer,
        'room': room,
        'day': time_slot[0],
        'period': time_slot[1],
        'num_students': total_students,
        'room_capacity': rooms[room]
    }
    return gene

# Створення гена для практики
def create_gene(group, subject, class_type, lecturers, rooms, time_slots, num_students):
    possible_lecturers = [lect for lect in lecturers if any(
        subj['subject_name'] == subject and subj['class_type'] == class_type for subj in lecturers[lect])]
    if not possible_lecturers:
        lecturer = 'Невідомий'
    else:
        lecturer = random.choice(possible_lecturers)
    room = random.choice(list(rooms.keys()))
    time_slot = random.choice(time_slots)
    gene = {
        'groups': [group],
        'subject': subject,
        'class_type': class_type,
        'lecturer': lecturer,
        'room': room,
        'day': time_slot[0],
        'period': time_slot[1],
        'num_students': num_students,
        'room_capacity': rooms[room]
    }
    return gene

# Обчислення фітнес-функції
def calculate_fitness(schedule):
    penalty = 0
    lecturer_schedule = defaultdict(set)
    group_schedule = defaultdict(set)
    room_schedule = defaultdict(set)
    time_room_gene = {}

    for gene in schedule:
        time_slot = (gene['day'], gene['period'])
        room = gene['room']

        # Перевірка викладача
        lecturer = gene['lecturer']
        if time_slot in lecturer_schedule[lecturer]:
            penalty += 1000  # Жорстке обмеження
        else:
            lecturer_schedule[lecturer].add(time_slot)

        # Перевірка груп
        for group in gene['groups']:
            if time_slot in group_schedule[group]:
                penalty += 1000  # Жорстке обмеження
            else:
                group_schedule[group].add(time_slot)

        # Перевірка аудиторії
        key = (time_slot, room)
        if key in time_room_gene:
            existing_gene = time_room_gene[key]
            if gene['class_type'] == 'Лекція' and existing_gene['class_type'] == 'Лекція' and gene['lecturer'] == existing_gene['lecturer']:
                # Об'єднуємо групи
                gene['groups'] = list(set(gene['groups'] + existing_gene['groups']))
                gene['num_students'] += existing_gene['num_students']
            else:
                penalty += 1000  # Жорстке обмеження
        else:
            time_room_gene[key] = gene
            room_schedule[room].add(time_slot)

        # Перевірка ємності аудиторії
        if gene['num_students'] > gene['room_capacity']:
            penalty += 500  # Нежорстке обмеження

    # Мінімізація "вікон" для груп
    for group, times in group_schedule.items():
        days_periods = defaultdict(list)
        for day, period in times:
            days_periods[day].append(period)
        for periods in days_periods.values():
            periods.sort()
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] > 1:
                    penalty += 10  # Нежорстке обмеження

    # Мінімізація "вікон" для викладачів
    for lecturer, times in lecturer_schedule.items():
        days_periods = defaultdict(list)
        for day, period in times:
            days_periods[day].append(period)
        for periods in days_periods.values():
            periods.sort()
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] > 1:
                    penalty += 10  # Нежорстке обмеження

    return -penalty  # Чим менший штраф, тим краще


# Ініціалізація популяції
def initialize_population(groups, subjects, lecturers, rooms, time_slots):
    population = []
    for _ in range(POPULATION_SIZE):
        individual = create_random_schedule(groups, subjects, lecturers, rooms, time_slots)
        population.append(individual)
    return population

# Селекція
def selection(population):
    population.sort(key=lambda x: calculate_fitness(x), reverse=True)
    return population[:POPULATION_SIZE // 2]

# Кросовер
def crossover(parent1, parent2):
    point = random.randint(0, len(parent1) - 1)
    child = parent1[:point] + parent2[point:]
    return child

# Мутація
def mutate(individual, groups, subjects, lecturers, rooms, time_slots):
    if random.random() < MUTATION_RATE:
        gene_index = random.randint(0, len(individual) - 1)
        gene = individual[gene_index]
        mutated_gene = mutate_gene(gene, lecturers, rooms, time_slots)
        individual[gene_index] = mutated_gene
    return individual

def mutate_gene(gene, lecturers, rooms, time_slots):
    mutation_choice = random.choice(['lecturer', 'room', 'time'])
    if mutation_choice == 'lecturer':
        possible_lecturers = [lect for lect in lecturers if any(
            subj['subject_name'] == gene['subject'] and subj['class_type'] == gene['class_type'] for subj in lecturers[lect])]
        if possible_lecturers:
            gene['lecturer'] = random.choice(possible_lecturers)
    elif mutation_choice == 'room':
        gene['room'] = random.choice(list(rooms.keys()))
        gene['room_capacity'] = rooms[gene['room']]
    elif mutation_choice == 'time':
        time_slot = random.choice(create_time_slots())
        gene['day'] = time_slot[0]
        gene['period'] = time_slot[1]
    return gene

# Генетичний алгоритм
def genetic_algorithm(groups, subjects, lecturers, rooms):
    time_slots = create_time_slots()
    population = initialize_population(groups, subjects, lecturers, rooms, time_slots)
    for generation in range(GENERATIONS):
        # Оцінка популяції
        population.sort(key=lambda x: calculate_fitness(x), reverse=True)
        best_fitness = calculate_fitness(population[0])
        if -best_fitness == 0:
            print(f"Оптимальне рішення знайдено на поколінні {generation}!")
            break
        # Селекція
        selected = selection(population)
        # Кросовер та мутація
        next_generation = []
        while len(next_generation) < POPULATION_SIZE:
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, groups, subjects, lecturers, rooms, time_slots)
            next_generation.append(child)
        population = next_generation
    return population[0]

# Вивід розкладу
def print_schedule(schedule, groups):
    schedule_by_day = defaultdict(list)
    for gene in schedule:
        schedule_by_day[gene['day']].append(gene)

    for day in DAYS:
        print(f"\n{day}:")
        day_schedule = sorted(schedule_by_day[day], key=lambda x: x['period'])
        for gene in day_schedule:
            group_names = ', '.join(gene['groups'])
            print(f"  Пара {gene['period']}: Групи {group_names} - {gene['subject']} ({gene['class_type']})")
            print(f"    Викладач: {gene['lecturer']}, Аудиторія: {gene['room']}")
            # Вивід кількості студентів
            total_students = 0
            for group in gene['groups']:
                num_students = groups.get(group, 'Невідомо')
                print(f"    Студентів з групи {group}: {num_students}")
                if num_students != 'Невідомо':
                    total_students += num_students
            print(f"    Загальна кількість студентів: {total_students}")
            print(f"    Ємність аудиторії: {gene['room_capacity']}")

# Головна функція
def main():
    groups = load_groups('groups.csv')
    subjects = load_subjects('subjects.csv')
    lecturers = load_lecturers('lecturers.csv')
    rooms = load_rooms('rooms.csv')

    # Оновлення груп з урахуванням підгруп
    groups = create_subgroups(groups, subjects)

    best_schedule = genetic_algorithm(groups, subjects, lecturers, rooms)
    print_schedule(best_schedule, groups)

if __name__ == '__main__':
    main()
