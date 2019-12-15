import simpy
import numpy
from config_experiment import (
    OPEN_DURATION_MINUTES,
    IS_PRINTER_HYBRID,
    COMPUTER_CAPACITY,
    PRINT_DURATION_SCALE_MINUTES,
    EDIT_DURATION_SCALE_MINUTES,
    ONLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES,
    OFFLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES,
    HYBRID_PRINTER_CAPACITY,
    SIMULATION_NUMBER,
    ONLINE_PRINTER_CAPACITY,
    OFFLINE_PRINTER_CAPACITY,
)
from customer import OnlineCustomer, OfflineCustomer
from resource import MonitoredResource


def average(array):
    return sum(array) / len(array)


def run_simulation(number_of_simulation):
    service_rates = []
    average_queue_times = []
    customer_serveds = []
    server_utilizations = []

    for i in range(number_of_simulation):
        env = simpy.Environment()

        printers = (
            [MonitoredResource(env, capacity=HYBRID_PRINTER_CAPACITY)]
            if IS_PRINTER_HYBRID
            else [
                MonitoredResource(env, capacity=ONLINE_PRINTER_CAPACITY),
                MonitoredResource(env, capacity=OFFLINE_PRINTER_CAPACITY),
            ]
        )
        computer = MonitoredResource(env, capacity=COMPUTER_CAPACITY)
        offline_current_time = 0
        offline_customer_number = 0
        offline_printer = printers[0] if IS_PRINTER_HYBRID else printers[1]
        while offline_current_time < OPEN_DURATION_MINUTES:
            OfflineCustomer(
                env,
                "Customer %d" % offline_customer_number,
                offline_printer,
                offline_current_time,
                computer,
            )
            offline_current_time += numpy.random.exponential(
                OFFLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES
            )
            offline_customer_number += 1

        current_time = 0
        customer_number = 0
        online_printer = printers[0]
        while current_time < OPEN_DURATION_MINUTES:
            OnlineCustomer(env, "Customer %d" % customer_number, online_printer, current_time)
            current_time += numpy.random.exponential(
                ONLINE_CUSTOMER_INTERARRIVAL_SCALE_MINUTES
            )
            customer_number += 1

        env.run()
        customer_served = offline_customer_number
        service_rate = customer_served / OPEN_DURATION_MINUTES
        service_rates.append(service_rate)
        customer_serveds.append(customer_served)
        server_utilizations.append(printers[0].utilization)

    return (
        average(service_rates),
        average(customer_serveds),
        average(server_utilizations),
    )


if __name__ == "__main__":
    (service_rate, customer_served, server_utilization,) = run_simulation(
        SIMULATION_NUMBER
    )

    with open("result.txt", "a") as f:
        f.write("Service Rate: " + str(service_rate) + "\n")
        f.write("Jumlah Customerterlayani : " + str(customer_served) + "\n")
        f.write("Utilisasi Server : " + str(server_utilization) + "\n")
