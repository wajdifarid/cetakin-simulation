from config_experiment import OPEN_DURATION_MINUTES
import simpy


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
