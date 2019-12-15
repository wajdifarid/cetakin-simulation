from config_experiment import OPEN_DURATION_MINUTES
import simpy


class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrives = []
        self.departs = []
        self.count_queued_users = 0
        self.count_users = 0

    def request(self, *args, **kwargs):
        self.arrives.append(self._env.now)
        if self.count == self.capacity:
            self.count_queued_users += 1
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.departs.append(self._env.now)
        self.count_users += 1
        return super().release(*args, **kwargs)

    @property
    def utilization(self):
        service_times = [
            self.departs[i] - self.arrives[i] for i in range(len(self.arrives))
        ]
        return sum(service_times) / (OPEN_DURATION_MINUTES * self.capacity)

    @property
    def queue_probability(self):
        return self.count_queued_users/self.count_users
