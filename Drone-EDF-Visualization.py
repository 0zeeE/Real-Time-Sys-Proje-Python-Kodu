import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Görev tanımları
tasks = [
    {"name": "Video Stream Handler", "wcet": 10, "period": 33, "color": "skyblue"},
    {"name": "Gimbal Sync", "wcet": 5, "period": 20, "color": "salmon"},
    {"name": "Controller Monitor", "wcet": 5, "period": 20, "color": "lightgreen"},
    {"name": "Telemetry Watchdog", "wcet": 2, "period": 100, "color": "plum"},
    {"name": "LTE Handler", "wcet": 3, "period": 100, "color": "khaki"},
    {"name": "Fail-Safe Switch", "wcet": 1, "period": 10, "color": "gray"},
]

# Idle (boşta) task tanımı
idle_task = {"name": "IDLE", "color": "lightgray"}

# Simülasyon parametreleri
simulation_time = 100
timeline = []  # Her zaman biriminde çalışan görevin adı
ready_queue = []
deadline_misses = []  # Deadline kaçıran görevler

for t in range(simulation_time):
    # Görevleri release et (periyotlarının katı olan zamanlarda)
    for task in tasks:
        if t % task["period"] == 0:
            ready_queue.append({
                "name": task["name"],
                "remaining_time": task["wcet"],
                "deadline": t + task["period"],
                "color": task["color"],
                "release_time": t
            })

    # Deadline'ı geçen görevleri bul ve kaydet
    missed = [task for task in ready_queue if task["deadline"] <= t]
    for m in missed:
        deadline_misses.append({
            "name": m["name"],
            "release_time": m["release_time"],
            "deadline": m["deadline"],
            "miss_time": t
        })
    # Deadline'ı geçen görevleri kuyruktan çıkar
    ready_queue = [task for task in ready_queue if task["deadline"] > t]

    # EDF: deadline, release_time ve isim sırasına göre sırala (deterministik)
    ready_queue.sort(key=lambda x: (x["deadline"], x["release_time"], x["name"]))

    # En öncelikli görevi çalıştır, yoksa idle
    if ready_queue:
        current_task = ready_queue[0]
        timeline.append(current_task["name"])
        current_task["remaining_time"] -= 1
        if current_task["remaining_time"] == 0:
            ready_queue.pop(0)
    else:
        timeline.append(idle_task["name"])

# Toplam kullanım oranı
total_utilization = sum(task["wcet"] / task["period"] for task in tasks)
print(f"Toplam CPU Kullanımı: {total_utilization:.3f} ({total_utilization*100:.1f}%)")

# Schedulability kontrolü (Liu & Layland)
if total_utilization <= 1.0:
    print("✓ Görev kümesi EDF altında zamanında çalıştırılabilir.")
else:
    print("✗ Görev kümesi zamanında çalıştırılamaz - CPU aşırı yüklenmiş.")

# Çizim için renk eşlemesi
task_colors = {task["name"]: task["color"] for task in tasks}
task_colors[idle_task["name"]] = idle_task["color"]

# Zaman çizelgesi görselleştirme
fig, ax = plt.subplots(figsize=(15, 6))
current_task = timeline[0]
start_time = 0

for t in range(1, simulation_time):
    if timeline[t] != current_task:
        ax.broken_barh([(start_time, t - start_time)], (0, 1),
                       facecolors=task_colors.get(current_task, 'white'),
                       edgecolors='black', linewidth=0.5)
        if t - start_time > 3:
            ax.text(start_time + (t - start_time)/2, 0.5, current_task.split()[0],
                    ha='center', va='center', fontsize=8, rotation=90)
        current_task = timeline[t]
        start_time = t

# Son bloğu çiz
if simulation_time > start_time:
    ax.broken_barh([(start_time, simulation_time - start_time)], (0, 1),
                   facecolors=task_colors.get(current_task, 'white'),
                   edgecolors='black', linewidth=0.5)
    if simulation_time - start_time > 3:
        ax.text(start_time + (simulation_time - start_time)/2, 0.5, current_task.split()[0],
                ha='center', va='center', fontsize=8, rotation=90)

# Görevlerin release ve deadline noktalarını göster
for task in tasks:
    release_times = list(range(0, simulation_time, task["period"]))
    for release_time in release_times:
        # Release oku (yukarı)
        ax.annotate('', xy=(release_time, 0), xytext=(release_time, -0.2),
                    arrowprops=dict(arrowstyle='->', color=task["color"], lw=1))
        # Deadline oku (aşağı)
        deadline = release_time + task["period"]
        if deadline <= simulation_time:
            ax.annotate('', xy=(deadline, 1), xytext=(deadline, 1.2),
                        arrowprops=dict(arrowstyle='->', color=task["color"], lw=1))


patches = [mpatches.Patch(color=task["color"], label=f"{task['name']} (WCET={task['wcet']}, T={task['period']})")
           for task in tasks]
patches.append(mpatches.Patch(color=idle_task["color"], label="IDLE"))
ax.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)

# Grafik ayarları
ax.set_ylim(-0.3, 1.3)
ax.set_xlim(0, simulation_time)
ax.set_xlabel("Time (ms)")
ax.set_ylabel("CPU")
ax.set_title(f"EDF Scheduler Diagram (Total Utilization: {total_utilization:.1%})")
ax.grid(True, alpha=0.3)
ax.set_xticks(range(0, simulation_time + 1, 10))

plt.tight_layout()
plt.show()

# İstatistikler
print(f"\nZamanlama Analizi:")
print(f"Simülasyon Süresi: {simulation_time} ms")
idle_time = sum(1 for t in timeline if t == idle_task["name"])
print(f"CPU Boşta Süresi: {idle_time} ms ({idle_time/simulation_time*100:.1f}%)")
print(f"CPU Meşgul Süresi: {simulation_time - idle_time} ms ({(simulation_time-idle_time)/simulation_time*100:.1f}%)")

# Deadline miss raporu
if deadline_misses:
    print("\nDeadline Kaçıran Görevler:")
    for miss in deadline_misses:
        print(f"- {miss['name']} (Release: {miss['release_time']} ms, Deadline: {miss['deadline']} ms, Kaçırıldığı an: {miss['miss_time']} ms)")
else:
    print("\nHiçbir görev deadline'ı kaçırmadı.")