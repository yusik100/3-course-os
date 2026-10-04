import random
from memory import PhysicalPage, PageTable

class Kernel:
    def __init__(self, num_physical_pages: int, replacement_algorithm: str):
        self.physical_pages: list[PhysicalPage] = [PhysicalPage(i) for i in range(num_physical_pages)]
        self.algorithm: str = replacement_algorithm 
        self.page_faults_count: int = 0
        self.disk_writes_count: int = 0

    def handle_page_fault(self, vpn: int, page_table: PageTable, current_time: int = 0, pid: int = 0, debug: bool = False) -> None:
        self.page_faults_count += 1
        free_page = next((p for p in self.physical_pages if not p.is_busy), None)
        
        victim_info = ""
        fs_write = "Ні"
        
        if free_page is None:
            if self.algorithm == 'random':
                victim_page = self._replace_random()
                victim_class_str = "N/A"
            else:
                victim_page = self._replace_nru()
                
            victim_entry = victim_page.process_page_table.entries[victim_page.virtual_page_index]
            
            if self.algorithm == 'nru':
                victim_class = (victim_entry.r * 2) + victim_entry.m
                victim_class_str = str(victim_class)

            if victim_entry.m == 1:
                self.disk_writes_count += 1
                fs_write = "Так"
                
            victim_info = f"Витіснено фізичну сторінку {victim_page.page_number} (Клас {self.algorithm.upper()}: {victim_class_str}). Запис у ФС: {fs_write}"
            
            victim_entry.p = 0
            victim_entry.r = 0
            victim_entry.m = 0
            victim_entry.ppn = None
            
            victim_page.free()
            free_page = victim_page
        else:
            victim_info = f"Використано вільну фізичну сторінку {free_page.page_number}."

        entry = page_table.entries[vpn]
        entry.p = 1
        entry.ppn = free_page.page_number
        free_page.allocate(page_table, vpn)
        
        if debug:
            print(f"[Time {current_time}] PID {pid}: Сторінковий промах (VPN {vpn}). {victim_info}")

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

    def free_process_pages(self, page_table: PageTable, current_time: int, pid: int, debug: bool = False) -> None:
        freed_count = 0
        for page in self.physical_pages:
            if page.is_busy and page.process_page_table == page_table:
                entry = page.process_page_table.entries[page.virtual_page_index]
                entry.p = 0
                entry.r = 0
                entry.m = 0
                entry.ppn = None
                page.free()
                freed_count += 1
                
        if debug and freed_count > 0:
            print(f"[Time {current_time}] PID {pid}: Процес завершено. Звільнено {freed_count} фізичних сторінок.")