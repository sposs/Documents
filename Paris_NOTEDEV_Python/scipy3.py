>>> pidxs = np.where(sample_freq > 0)
>>> freqs = sample_freq[pidxs]
>>> power = np.abs(sig_fft)[pidxs]
>>> freq = freqs[power.argmax()]
>>> # check that correct freq is found
>>> np.allclose(freq, 1./period)  
True
>>> sig_fft[np.abs(sample_freq) > freq] = 0
>>> main_sig = fftpack.ifft(sig_fft)
