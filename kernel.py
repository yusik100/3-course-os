import random
from memory import PhysicalPage, PageTable

class Kernel:
    def __init__(self, num_physical_pages: int, replacement_algorithm: str):
        self.physical_pages: list[PhysicalPage] = [PhysicalPage(i) for i in range(num_physical_pages)]
        self.algorithm: str = replacement_algorithm 
        self.page_faults_count: int = 0

    def handle_page_fault(self, vpn: int, page_table: PageTable) -> None:
        self.page_faults_count += 1
        free_page = next((p for p in self.physical_pages if not p.is_busy), None)
        
        if free_page is None:
            if self.algorithm == 'random':
                victim_page = self._replace_random()
            else:
                victim_page = self._replace_nru()
            
            victim_entry = victim_page.process_page_table.entries[victim_page.virtual_page_index]
            
            if victim_entry.m == 1:
                pass
            
            victim_entry.p = 0
            victim_entry.r = 0
            victim_entry.m = 0
            victim_entry.ppn = None
            
            victim_page.free()
            free_page = victim_page

        entry = page_table.entries[vpn]
        entry.p = 1
        entry.ppn = free_page.page_number
        free_page.allocate(page_table, vpn)

    def _replace_random(self) -> PhysicalPage:
        return random.choice([p for p in self.physical_pages if p.is_busy])

    def _replace_nru(self) -> PhysicalPage:
        classes = {0: [], 1: [], 2: [], 3: []}
        
        for page in (p for p in self.physical_pages if p.is_busy):
            entry = page.process_page_table.entries[page.virtual_page_index]
            # Клас 0: R=0, M=0
            # Клас 1: R=0, M=1
            # Клас 2: R=1, M=0
            # Клас 3: R=1, M=1
            class_index = (entry.r * 2) + entry.m
            classes[class_index].append(page)
            
        for i in range(4):
            if classes[i]:
                return random.choice(classes[i])

    def reset_reference_bits(self) -> None:
        for page in self.physical_pages:
            if page.is_busy:
                entry = page.process_page_table.entries[page.virtual_page_index]
                entry.r = 0