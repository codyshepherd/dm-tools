import json
import os


class AppState(object):

    def __init__(self,
                 visits_file="visits.txt",
                 visitors_file="visitors.txt",
                 write_freq=1000):

        self._visits_file_path = visits_file
        self._visitors_file_path = visitors_file

        self._visits = self.read_visits(self._visits_file_path)
        self._visitors = self.read_visitors(self._visitors_file_path)
        self._write_freq = write_freq

    def close(self):
        self.write_stats()

    def log_visit(self, host, fn):
        self._visits += 1

        by_fn_visits = self._visitors.get(fn, 0)
        by_fn_visits += 1
        self._visitors[fn] = by_fn_visits

        by_host_visits = self._visitors.get(host, {})
        by_host_total_visits = by_host_visits.get("total", 0)
        by_host_total_visits += 1
        by_host_fn_visits = by_host_visits.get(fn, 0)
        by_host_fn_visits += 1
        by_host_visits["total"] = by_host_total_visits
        by_host_visits[fn] = by_host_fn_visits
        self._visitors[host] = by_host_visits

        if self._visits % self._write_freq == 0:
            self.write_stats()

    def read_visitors(self, file_path):
        visitors = {}
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r') as fh:
                visitors = json.loads(fh.read())
        return visitors

    def read_visits(self, file_path):
        visits = 0
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r') as fh:
                contents = fh.read()
            visits = int(contents)
        return visits

    @property
    def visits(self):
        return self._visits

    def write_stats(self):
        with open(self._visits_file_path, 'w') as fh:
            fh.write(str(self._visits))
        with open(self._visitors_file_path, 'w') as fh:
            fh.write(json.dumps(self._visitors))
