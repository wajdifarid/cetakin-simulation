import simpy
import numpy
from config_experiment import (
    OPEN_DURATION_MINUTES,
    PRINTER_CAPACITY,
    COMPUTER_CAPACITY,
    PRINT_DURATION_SCALE_MINUTES,
    EDIT_DURATION_SCALE_MINUTES,
    ONLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES,
    OFFLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES,
)


queue_count = 0
queue_total_time_in_minutes = 0
computer_queue_count = 0
computer_queue_total_time_in_minutes = 0


class Customer(object):
    def __init__(self, env, name, printer, arrival_time, computer=None):
        self.env = env
        self.name = name
        self.printer = printer
        self.arrival_time = arrival_time
        self.print_duration = numpy.random.exponential(PRINT_DURATION_SCALE_MINUTES)
        if computer:
            self.edit_duration = numpy.random.exponential(EDIT_DURATION_SCALE_MINUTES)
        self.computer = computer
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        # Simulate driving to the printer
        yield self.env.timeout(self.arrival_time)

        # Request one of its printing spots
        arrived_at = self.env.now
        print("%s arriving at %d" % (self.name, self.env.now))
        if self.computer:
            with self.computer.request() as req:
                yield req
                # editing
                print("%s starting to edit at %s" % (self.name, self.env.now))

                if arrived_at != self.env.now:
                    global computer_queue_count
                    computer_queue_count += 1
                    global computer_queue_total_time_in_minutes
                    computer_queue_total_time_in_minutes += self.env.now - arrived_at

                yield self.env.timeout(self.print_duration)
                print("%s leaving the computer at %s" % (self.name, self.env.now))

        arrived_at = self.env.now
        with self.printer.request() as req:
            yield req

            # printing
            print("%s starting to print at %s" % (self.name, self.env.now))
            if arrived_at != self.env.now:
                global queue_count
                queue_count += 1
                global queue_total_time_in_minutes
                queue_total_time_in_minutes += self.env.now - arrived_at

            yield self.env.timeout(self.print_duration)
            print("%s leaving the printer at %s" % (self.name, self.env.now))


def average(array):
    return sum(array) / len(array)


def run_simulation(number_of_simulation):
    service_rates = []
    average_queue_times = []
    customer_serveds = []
    server_utilizations = []

    for i in range(number_of_simulation):
        env = simpy.Environment()
        printer = MonitoredResource(env, capacity=PRINTER_CAPACITY)
        computer = MonitoredResource(env, capacity=COMPUTER_CAPACITY)
        current_time = 0
        customer_number = 0
        while current_time < OPEN_DURATION_MINUTES:
            Customer(
                env, "Customer %d" % customer_number, printer, current_time, computer
            )
            current_time += numpy.random.exponential(
                ONLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES
            )
            customer_number += 1

        global queue_count
        global queue_total_time_in_minutes
        global computer_queue_count
        global computer_queue_total_time_in_minutes
        queue_count = 0
        queue_total_time_in_minutes = 0
        computer_queue_count = 0
        computer_queue_total_time_in_minutes = 0
        env.run()
        average_queue_time = queue_total_time_in_minutes / queue_count
        customer_served = customer_number
        service_rate = customer_served / OPEN_DURATION_MINUTES
        service_rates.append(service_rate)
        average_queue_times.append(average_queue_time)
        customer_serveds.append(customer_served)
        server_utilizations.append(printer.utilization)

    return (
        average(service_rates),
        average(average_queue_times),
        average(customer_serveds),
        queue_count / customer_served,
        average(server_utilizations),
    )


class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrives = []
        self.departs = []

    def request(self, *args, **kwargs):
        self.arrives.append(self._env.now)
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.departs.append(self._env.now)
        return super().release(*args, **kwargs)

    @property
    def utilization(self):
        service_times = [
            self.departs[i] - self.arrives[i] for i in range(len(self.arrives))
        ]
        return sum(service_times) / (OPEN_DURATION_MINUTES * self.capacity)


(
    service_rate,
    average_queue_time,
    customer_served,
    queue_probability,
    server_utilization,
) = run_simulation(100)

with open("result.txt", "a") as f:
    f.write("Service Rate: " + str(service_rate) + "\n")
    f.write("Jumlah Customerterlayani : " + str(customer_served) + "\n")
    f.write("Utilisasi Server : " + str(server_utilization) + "\n")
    f.write("Queue Probabilityy : " + str(queue_probability) + "\n")
    f.write("Average queue time : " + str(average_queue_time) + "\n")
