from memory import PageTable

class PageFaultException(Exception):
    def __init__(self, vpn: int):
        self.vpn: int = vpn
        super().__init__(f"Сторінковий промах для віртуальної сторінки {vpn}")


class MMU:
    def __init__(self):
        pass

    def access_memory(self, page_table: PageTable, vpn: int, access_type: str) -> int:
        entry = page_table.entries[vpn]

        if entry.p == 0:
            raise PageFaultException(vpn)
        entry.r = 1

        if access_type == 'write':
            entry.m = 1

        return entry.ppn