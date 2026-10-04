from kernel import Kernel
from process import Process
from mmu import MMU, PageFaultException

def run_simulation(algorithm: str, working_set_size: int, num_physical_pages: int = 50, num_virtual_pages: int = 100, max_time: int = 10000) -> int:
    kernel = Kernel(num_physical_pages, algorithm)
    mmu = MMU()
    
    processes = [
        Process(pid=1, num_virtual_pages=num_virtual_pages, working_set_size=working_set_size, total_accesses_to_run=max_time // 3, ws_change_interval=500),
        Process(pid=2, num_virtual_pages=num_virtual_pages, working_set_size=working_set_size, total_accesses_to_run=max_time // 3, ws_change_interval=500),
        Process(pid=3, num_virtual_pages=num_virtual_pages, working_set_size=working_set_size, total_accesses_to_run=max_time // 3, ws_change_interval=500)
    ]
    
    active_processes = list(processes)
    global_time = 0
    quantum = 50

    while active_processes and global_time < max_time:
        current_process = active_processes.pop(0)

        for _ in range(quantum):
            if current_process.is_finished():
                break

            vpn, access_type = current_process.generate_memory_request()
            global_time += 1
            
            try:
                mmu.access_memory(current_process.page_table, vpn, access_type)
            except PageFaultException:
                kernel.handle_page_fault(vpn, current_process.page_table)
                mmu.access_memory(current_process.page_table, vpn, access_type)
            
            if global_time % 200 == 0:
                kernel.reset_reference_bits()
                
        if not current_process.is_finished():
            active_processes.append(current_process)
            
    return kernel.page_faults_count

def main():
    ws_sizes = [10, 20, 30, 40, 50, 60]
    
    print("Звіт про характеристики віртуальної пам'яті та сторінкові промахи:")
    print(f"{'Розмір роб. набору':<20} | {'NRU (промахи)':<15} | {'Random (промахи)':<15}")
    print("-" * 56)
    
    for ws_size in ws_sizes:
        faults_nru = run_simulation('nru', ws_size)
        faults_random = run_simulation('random', ws_size)
        
        print(f"{ws_size:<20} | {faults_nru:<15} | {faults_random:<15}")
        
    print("\nАналіз результатів:")
    print("1. При збільшенні кількості сторінок у робочому наборі частота промахів має зростати.")
    print("2. Алгоритм Random має призводити до більшої частоти промахів, ніж алгоритм NRU.")

if __name__ == '__main__':
    main()