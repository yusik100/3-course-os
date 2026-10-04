import random
from memory import PageTable

class Process:
    def __init__(self, pid: int, num_virtual_pages: int, working_set_size: int, total_accesses_to_run: int, ws_change_interval: int, seed: int = None):
        self.rng = random.Random(seed)
        self.pid: int = pid
        self.num_virtual_pages: int = num_virtual_pages
        self.page_table: PageTable = PageTable(num_virtual_pages)
        self.total_accesses_to_run: int = total_accesses_to_run 
        self.accesses_done: int = 0
        self.working_set_size: int = working_set_size
        self.working_set: list[int] = []
        self.ws_change_interval: int = ws_change_interval
        self.update_working_set()

    def update_working_set(self) -> None:
        pages = list(range(self.num_virtual_pages))
        self.working_set = self.rng.sample(pages, min(self.working_set_size, self.num_virtual_pages))

    def generate_memory_request(self) -> tuple[int, str]:
        if self.accesses_done > 0 and self.accesses_done % self.ws_change_interval == 0:
            self.update_working_set()
        self.accesses_done += 1

        if self.rng.random() < 0.90 and self.working_set:
            vpn = self.rng.choice(self.working_set)
        else:
            vpn = self.rng.randint(0, self.num_virtual_pages - 1)
        access_type = 'write' if self.rng.random() < 0.30 else 'read'

        return vpn, access_type

    def is_finished(self) -> bool:
        return self.accesses_done >= self.total_accesses_to_run