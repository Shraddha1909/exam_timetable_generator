from datetime import timedelta
import random
import mysql.connector

try:
    # Connect to your MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="sqluser",
        password="password",
        database="exam"
    )
    cursor = conn.cursor()

    # Fetch start date and end date from the database
    cursor.execute("SELECT start_date, end_date FROM date_range")
    start_date, end_date = cursor.fetchone()

    # Fetch data from your database
    cursor.execute("SELECT subject_id FROM subjects")
    subjects = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT teacher_id FROM teachers")
    teachers = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT room_no FROM rooms")
    classrooms = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT slot FROM slot")
    exam_slots = [row[0] for row in cursor.fetchall()]

    # Sample data for teacher and classroom availability (you need to fetch this from your database)
    # You can modify this based on how availability is stored in your database
    teacher_availability = {teacher: exam_slots for teacher in teachers}
    classroom_availability = {classroom: exam_slots for classroom in classrooms}

    # Define chromosome representation (timetable)
    def generate_timetable():
        timetable = {}
        current_date = start_date
        while current_date <= end_date:
            timetable[current_date] = {slot: {"subject": random.choice(subjects),
                                               "teacher": random.choice(teachers),
                                               "classroom": random.choice(classrooms)}
                                        for slot in exam_slots}
            current_date += timedelta(days=1)
        return timetable

    # Define fitness function
    def fitness(timetable):
        conflicts = 0
        uneven_distribution_penalty = 0
        availability_penalty = 0

        # Count conflicts
        subjects_per_slot = {slot: set() for slot in exam_slots}
        for date_schedule in timetable.values():
            for slot, exam in date_schedule.items():
                subject = exam["subject"]
                if subject in subjects_per_slot[slot]:
                    conflicts += 1
                subjects_per_slot[slot].add(subject)

        # Check for uneven distribution of exams across time slots
        max_exams = max(len(subjects) for subjects in subjects_per_slot.values())
        min_exams = min(len(subjects) for subjects in subjects_per_slot.values())
        uneven_distribution_penalty = max_exams - min_exams

        # Check teacher and classroom availability
        for date_schedule in timetable.values():
            for slot, exam in date_schedule.items():
                teacher = exam["teacher"]
                classroom = exam["classroom"]
                if slot not in teacher_availability[teacher] or slot not in classroom_availability[classroom]:
                    availability_penalty += 1

        # Calculate total fitness
        total_fitness = 1 / (1 + conflicts + uneven_distribution_penalty + availability_penalty)

        return total_fitness

    # Genetic algorithm parameters
    population_size = 100
    mutation_rate = 0.1
    generations = 100

    # Generate initial population
    population = [generate_timetable() for _ in range(population_size)]

    # Main loop
    for _ in range(generations):
        # Evaluate fitness
        fitness_scores = [(timetable, fitness(timetable)) for timetable in population]
        sorted_population = sorted(fitness_scores, key=lambda x: x[1], reverse=True)

        # Select parents
        parents = [timetable for timetable, _ in sorted_population[:10]]

        # Generate offspring through crossover and mutation
        offspring = []
        while len(offspring) < population_size:
            parent1, parent2 = random.choices(parents, k=2)
            child = {}
            for date in start_date, end_date:
                child[date] = {}
                for slot in exam_slots:
                    child[date][slot] = parent1[date][slot] if random.random() < 0.5 else parent2[date][slot]
                    if random.random() < mutation_rate:
                        child[date][slot] = {"subject": random.choice(subjects),
                                             "teacher": random.choice(teachers),
                                             "classroom": random.choice(classrooms)}
            offspring.append(child)

        population = offspring

    # Choose the best timetable from the final population
    best_timetable, best_fitness = max(fitness_scores, key=lambda x: x[1])
    print("Best Timetable:", best_timetable)
    print("Fitness:", best_fitness)

except mysql.connector.Error as err:
    print("MySQL Error:", err)

finally:
    # Close database connection
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()

