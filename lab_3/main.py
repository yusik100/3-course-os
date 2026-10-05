import random
from kernel import Kernel
from process import Process
from mmu import MMU, PageFaultException

def run_simulation(algorithm: str, working_set_size: int, num_physical_pages: int = 50, num_virtual_pages: int = 100, max_time: int = 10000, debug: bool = False, seed: int = None) -> tuple[int, int]:
    kernel = Kernel(num_physical_pages, algorithm)
    mmu = MMU()
    
    sim_rng = random.Random(seed)
    
    pending_processes = []
    num_processes = sim_rng.randint(3, 5) 
    
    for pid in range(1, num_processes + 1):
        arrival_time = 0 if pid == 1 else sim_rng.randint(1, max(1, max_time // 2))
        total_accesses = sim_rng.randint(max_time // 4, max_time // 2)
        ws_interval = sim_rng.randint(300, 700)
        
        process = Process(
            pid=pid, 
            num_virtual_pages=num_virtual_pages, 
            working_set_size=working_set_size,
            total_accesses_to_run=total_accesses, 
            ws_change_interval=ws_interval,
            seed=(seed + pid) if seed is not None else None
        )
        pending_processes.append((arrival_time, process))
        
    pending_processes.sort(key=lambda x: x[0])
    
    active_processes = []
    global_time = 0
    quantum = 50

    while (active_processes or pending_processes) and global_time < max_time:
        
        i = 0
        while i < len(pending_processes):
            arrival_time, process = pending_processes[i]
            if arrival_time <= global_time:
                active_processes.append(process)
                pending_processes.pop(i)
            else:
                i += 1
                
        if not active_processes and pending_processes:
            global_time = pending_processes[0][0]
            continue
            
        current_process = active_processes.pop(0)

        for _ in range(quantum):
            if current_process.is_finished() or global_time >= max_time:
                break

            vpn, access_type = current_process.generate_memory_request()
            
            try:
                mmu.access_memory(current_process.page_table, vpn, access_type)
            except PageFaultException:
                kernel.handle_page_fault(vpn, current_process.page_table, global_time, current_process.pid, debug)
                mmu.access_memory(current_process.page_table, vpn, access_type)
            
            global_time += 1
            
            if global_time % 30 == 0:
                kernel.reset_reference_bits()
                
            j = 0
            while j < len(pending_processes):
                arrival_time, process = pending_processes[j]
                if arrival_time <= global_time:
                    active_processes.append(process)
                    pending_processes.pop(j)
                else:
                    j += 1
                    
        if not current_process.is_finished():
            active_processes.append(current_process)
        else:
            kernel.free_process_pages(current_process.page_table, global_time, current_process.pid, debug)
            
    return kernel.page_faults_count, kernel.disk_writes_count

def main():
    print("Демонстрація логування рішень ядра")
    run_simulation('nru', working_set_size=10, num_physical_pages=5, num_virtual_pages=20, max_time=50, debug=True)
    print("\n" + "="*76 + "\n")

    ws_sizes = [10, 20, 30, 40, 50, 60]
    
    print("Звіт про характеристики віртуальної пам'яті, сторінкові промахи та запис у ФС:")
    print(f"{'Розмір роб. набору':<20} | {'NRU (промахи / запис)':<25} | {'Random (промахи / запис)':<25}")
    print("-" * 76)
    
    for ws_size in ws_sizes:
        faults_nru, writes_nru = run_simulation('nru', ws_size, debug=False, seed=ws_size)
        faults_random, writes_random = run_simulation('random', ws_size, debug=False, seed=ws_size)
        
        nru_stats = f"{faults_nru} / {writes_nru}"
        random_stats = f"{faults_random} / {writes_random}"
        print(f"{ws_size:<20} | {nru_stats:<25} | {random_stats:<25}")
        
    print("\nАналіз результатів:")
    print("1. При збільшенні кількості сторінок у робочому наборі частота промахів має зростати.")
    print("2. Алгоритм Random має призводити до більшої частоти промахів, ніж алгоритм NRU.")
    print("3. Алгоритм NRU враховує наявність модифікованих сторінок, тому кількість вивантажень у ФС для нього зазвичай менша.")

if __name__ == '__main__':
    main()