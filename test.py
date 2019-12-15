import simpy


class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []

    def request(self, *args, **kwargs):
        print(print("penuh gan") if self.count == self.capacity else print("masih muat"))
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.data.append((self._env.now, len(self.queue)))
        return super().release(*args, **kwargs)


def test_process(env, res):
    with res.request() as req:
        yield req
        yield env.timeout(3)


env = simpy.Environment()
res = MonitoredResource(env, capacity=2)
p1 = env.process(test_process(env, res))
p2 = env.process(test_process(env, res))
p3 = env.process(test_process(env, res))
p4 = env.process(test_process(env, res))
env.run()
print(res.data)
