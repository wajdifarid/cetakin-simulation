from config_experiment import OPEN_DURATION_MINUTES
import simpy


class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrives = []
        self.departs = []
        self.count_queued_users = 0
        self.count_users = 0
        self.queue_start_times = []
        self.queue_durations = []

    def request(self, *args, **kwargs):
        self.arrives.append(self._env.now)
        if self.count == self.capacity:
            self.count_queued_users += 1
            self.queue_start_times.append(self._env.now)
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.departs.append(self._env.now)
        self.count_users += 1
        if self.queue_start_times:
            queue_start_time = self.queue_start_times.pop(0)
            queue_end_time = self._env.now
            queue_duration = queue_end_time - queue_start_time
            self.queue_durations.append(queue_duration)
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

    @property
    def queue_duration(self):
        return sum(self.queue_durations) / len(self.queue_durations) if self.queue_durations else 0
