PX_PER_MM = 3.7795275591

def mmtopx(mm): return mm * PX_PER_MM
def chlapik_staff_space(rastralnr):
    return mmtopx({2: 1.88, 3: 1.755, 4: 1.6, 
    5: 1.532, 6: 1.4,
    7: 1.19, 8: 1.02}[rastralnr])

space = chlapik_staff_space(2)
print(space)
