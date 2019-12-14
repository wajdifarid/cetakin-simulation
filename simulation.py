import simpy
import numpy

class Customer(object):
    def __init__(self, env, name, printer, driving_time):
        self.env = env
        self.name = name
        self.printer = printer
        self.driving_time = driving_time
        self.print_duration = numpy.random.exponential(9.029122807017542)
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        # Simulate driving to the printer
        yield self.env.timeout(self.driving_time)

        # Request one of its charging spots
        print('%s arriving at %d' % (self.name, self.env.now))
        with self.printer.request() as req:
            yield req

            # Charge the battery
            print('%s starting to charge at %s' % (self.name, self.env.now))
            yield self.env.timeout(self.print_duration)
            print('%s leaving the printer at %s' % (self.name, self.env.now))

    def charge(self, duration):
        yield self.env.timeout(duration)


import simpy
env = simpy.Environment()
printer = simpy.Resource(env, capacity=2)


current_time = 0
i = 0
while current_time < 60 * 11:
    Customer(env, 'Customer %d' % i, printer, current_time)
    current_time += numpy.random.exponential(46.3289847161572)
    i += 1

env.run()
