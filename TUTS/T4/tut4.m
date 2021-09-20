L = length(timeDomain);

Ts = 0.0000001;                                         % Sampling Interval (sec)
Fs = 1/Ts;                                              % Sampling Frequency
Fn = Fs/2;                                              % Nyquist Frequency
FTv = fft(vc)/L;                                        % Fourier Transform
Fv = linspace(0, 1, fix(L/2)+1)*Fn;                     % Frequency Vector (Hz)
Iv = 1:length(Fv);                                      % Index Vector

figure(1)
plot(Fv, abs(FTv(Iv))*2)
grid
xlabel('Frequency (Hz)')
ylabel('X(t)')

