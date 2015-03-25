matrix = []
k_array = []
for current in currents:
  for i in range(N_peaks):
    k_array.append(wn[i])
    point=[current*t_pe[i]*t_pe[i], 
           t_pe[i]*t_pe[i],
           current*current*t_pe[i], 
           (current**4)*t_pe[i], 
           t_pe[i],
           1, -current*current, 
           -current**4, 
           -current**6]
    if not len(matrix):
      matrix=np.array(point)
    else:
      matrix=np.vstack((matrix, point))
res=np.linalg.lstsq(matrix, 
                    np.array(k_array))
