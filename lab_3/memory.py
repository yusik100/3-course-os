class PageTableEntry:
    def __init__(self):
        self.p: int = 0
        self.r: int = 0
        self.m: int = 0
        self.ppn: int | None = None

class PageTable:
    def __init__(self, num_virtual_pages: int):
        self.entries: list[PageTableEntry] = [PageTableEntry() for _ in range(num_virtual_pages)]

class PhysicalPage:
    def __init__(self, physical_page_number: int):
        self.page_number: int = physical_page_number
        self.is_busy: bool = False
        self.process_page_table: PageTable | None = None
        self.virtual_page_index: int | None = None

    def allocate(self, page_table: PageTable, vpn: int) -> None:
        self.is_busy = True
        self.process_page_table = page_table
        self.virtual_page_index = vpn

    def free(self) -> None:
        self.is_busy = False
        self.process_page_table = None
        self.virtual_page_index = None