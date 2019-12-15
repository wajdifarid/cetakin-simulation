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
from customer import OnlineCustomer, OfflineCustomer


queue_count = 0
queue_total_time_in_minutes = 0
computer_queue_count = 0
computer_queue_total_time_in_minutes = 0


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
        offline_current_time = 0
        customer_number = 0
        offline_customer_number = 0
        while offline_current_time < OPEN_DURATION_MINUTES:
            OfflineCustomer(env, "Customer %d" % offline_customer_number, printer, current_time, computer)
            offline_current_time += numpy.random.exponential(OFFLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES)
            offline_customer_number += 1

        while current_time < OPEN_DURATION_MINUTES:
            OnlineCustomer(env, "Customer %d" % customer_number, printer, current_time)
            current_time += numpy.random.exponential(
                ONLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES
            )
            customer_number += 1

        env.run()
        customer_served = customer_number + offline_customer_number
        service_rate = customer_served / OPEN_DURATION_MINUTES
        service_rates.append(service_rate)
        customer_serveds.append(customer_served)
        server_utilizations.append(printer.utilization)

    return (
        average(service_rates),
        average(customer_serveds),
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
    customer_served,
    server_utilization,
) = run_simulation(100)

with open("result.txt", "a") as f:
    f.write("Service Rate: " + str(service_rate) + "\n")
    f.write("Jumlah Customerterlayani : " + str(customer_served) + "\n")
    f.write("Utilisasi Server : " + str(server_utilization) + "\n")
