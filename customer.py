import numpy
from config_experiment import PRINT_DURATION_SCALE_MINUTES, EDIT_DURATION_SCALE_MINUTES


class Customer(object):
    def __init__(self, env, name, printers, arrival_time):
        self.env = env
        self.name = name
        self.printers = printers
        self.arrival_time = arrival_time
        self.print_duration = numpy.random.exponential(PRINT_DURATION_SCALE_MINUTES)
    
    def print_documents(self, arrived_at):
        with self.printers.request() as req:
            yield req

            print("%s starting to print at %s" % (self.name, self.env.now))

            # printing
            yield self.env.timeout(self.print_duration)
            print("%s leaving the printer at %s" % (self.name, self.env.now))

class OnlineCustomer(Customer):
    def __init__(self, env, name, printers, arrival_time):
        super().__init__(env, name, printers, arrival_time)
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        # Simulate driving to the printer
        yield self.env.timeout(self.arrival_time)

        # Request one of its printing spots
        print("%s arriving at %d" % (self.name, self.env.now))
        arrived_at = self.env.now
        yield self.env.process(self.print_documents(arrived_at))


class OfflineCustomer(Customer):
    def __init__(self, env, name, printers, arrival_time, computers):
        super().__init__(env, name, printers, arrival_time)
        self.edit_duration = numpy.random.exponential(EDIT_DURATION_SCALE_MINUTES)
        self.computers = computers
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        # Simulate arriving to the computer
        yield self.env.timeout(self.arrival_time)

        # Request one of its computer spots
        arrived_at_computer_at = self.env.now
        yield self.env.process(self.edit(arrived_at_computer_at))
        print("%s arriving at %d" % (self.name, self.env.now))

        arrived_at_printer_at = self.env.now
        yield self.env.process(self.print_documents(arrived_at_printer_at))

    def edit(self, arrived_at_computer_at):
        with self.computers.request() as req:
            yield req
            # editing
            print("%s starting to edit at %s" % (self.name, self.env.now))

            yield self.env.timeout(self.print_duration)
            print("%s leaving the computer at %s" % (self.name, self.env.now))

    
