# mf_explore SUMMARY (numbers only; exploratory; no verdicts)

Haar reference for moments: E_Haar[M_q](n) = n * B(q+1/2,(n-1)/2) / B(1/2,(n-1)/2). Entries are the 10 largest |log(trained/null)| of the band-mean
M_q over (matrix, side, band, q != 1, checkpoint); trained/Haar and null/Haar are the band means divided by
E_Haar[M_q](n). Seed-mean rows carry +- sd over seeds.

- 156 checkpoints processed in 83.6s wall (0.54s per checkpoint at workers=8)

## pythia-1.4b  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | v | spike | 4 | step6000 | -13.5200 | 2.27 | 1.689e+06 | 1.215e-08 | 2048 |
| 2 | K | v | spike | 4 | step8000 | -13.2446 | 4.159 | 2.35e+06 | 1.215e-08 | 2048 |
| 3 | K | v | spike | 4 | step4000 | -12.8972 | 1.172 | 4.677e+05 | 1.215e-08 | 2048 |
| 4 | K | v | spike | 4 | step12000 | -12.2589 | 14.65 | 3.09e+06 | 1.215e-08 | 2048 |
| 5 | K | v | spike | 4 | step16000 | -11.1857 | 39.27 | 2.831e+06 | 1.215e-08 | 2048 |
| 6 | K | v | spike | 4 | step3000 | -10.3585 | 1.025 | 3.23e+04 | 1.215e-08 | 2048 |
| 7 | K | v | spike | 4 | step24000 | -9.8233 | 153 | 2.824e+06 | 1.215e-08 | 2048 |
| 8 | MLP_OUT | u | spike | 4 | step3000 | -9.0763 | 2.559 | 2.238e+04 | 1.215e-08 | 2048 |
| 9 | K | v | spike | 3 | step8000 | -8.9899 | 1.435 | 1.151e+04 | 3.566e-06 | 2048 |
| 10 | MLP_IN | u | 1024-2048 | 4 | step128000 | +8.9670 | 7991 | 1.019 | 1.907e-10 | 8192 |

## pythia-410m-seed1  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step12000 | -8.5123 | 23.34 | 1.161e+05 | 9.665e-08 | 1024 |
| 2 | K | u | spike | 4 | step8000 | -8.4786 | 24.98 | 1.202e+05 | 9.665e-08 | 1024 |
| 3 | K | u | spike | 4 | step16000 | -8.4444 | 23.02 | 1.07e+05 | 9.665e-08 | 1024 |
| 4 | K | u | spike | 4 | step6000 | -8.4349 | 25.37 | 1.168e+05 | 9.665e-08 | 1024 |
| 5 | Q | u | spike | 4 | step8000 | -8.2782 | 17.48 | 6.882e+04 | 9.665e-08 | 1024 |
| 6 | Q | u | spike | 4 | step6000 | -8.1873 | 16.77 | 6.028e+04 | 9.665e-08 | 1024 |
| 7 | Q | u | spike | 4 | step4000 | -8.1157 | 11.3 | 3.783e+04 | 9.665e-08 | 1024 |
| 8 | K | u | spike | 4 | step4000 | -8.0931 | 23.97 | 7.842e+04 | 9.665e-08 | 1024 |
| 9 | Q | u | spike | 4 | step12000 | -8.0843 | 18.24 | 5.914e+04 | 9.665e-08 | 1024 |
| 10 | K | u | spike | 4 | step24000 | -8.0629 | 23.07 | 7.323e+04 | 9.665e-08 | 1024 |

## pythia-410m-seed2  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step8000 | -8.4406 | 22.38 | 1.037e+05 | 9.665e-08 | 1024 |
| 2 | MLP_IN | u | spike | 4 | step12000 | -8.3464 | 295.9 | 1.247e+06 | 1.523e-09 | 4096 |
| 3 | K | u | spike | 4 | step12000 | -8.2477 | 19.91 | 7.602e+04 | 9.665e-08 | 1024 |
| 4 | K | u | spike | 4 | step6000 | -8.2456 | 26.69 | 1.017e+05 | 9.665e-08 | 1024 |
| 5 | Q | v | spike | 4 | step48000 | -8.2106 | 3.377 | 1.243e+04 | 9.665e-08 | 1024 |
| 6 | MLP_IN | u | spike | 4 | step6000 | -8.1397 | 47.04 | 1.612e+05 | 1.523e-09 | 4096 |
| 7 | K | u | spike | 4 | step4000 | -8.1238 | 22.42 | 7.565e+04 | 9.665e-08 | 1024 |
| 8 | Q | u | spike | 4 | step6000 | -8.0847 | 17.51 | 5.68e+04 | 9.665e-08 | 1024 |
| 9 | K | u | spike | 4 | step3000 | -8.0562 | 21.17 | 6.676e+04 | 9.665e-08 | 1024 |
| 10 | Q | u | spike | 4 | step4000 | -8.0366 | 12.23 | 3.783e+04 | 9.665e-08 | 1024 |

## pythia-410m-seed3  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step96000 | -8.7030 | 14.21 | 8.553e+04 | 9.665e-08 | 1024 |
| 2 | K | u | spike | 4 | step6000 | -8.5150 | 20.34 | 1.015e+05 | 9.665e-08 | 1024 |
| 3 | K | u | spike | 4 | step8000 | -8.4841 | 20.86 | 1.009e+05 | 9.665e-08 | 1024 |
| 4 | Q | u | spike | 4 | step143000 | -8.3624 | 23.6 | 1.011e+05 | 9.665e-08 | 1024 |
| 5 | K | u | spike | 4 | step12000 | -8.3460 | 20.73 | 8.735e+04 | 9.665e-08 | 1024 |
| 6 | K | u | spike | 4 | step128000 | -8.3228 | 14.32 | 5.897e+04 | 9.665e-08 | 1024 |
| 7 | K | u | spike | 4 | step16000 | -8.2094 | 21.69 | 7.972e+04 | 9.665e-08 | 1024 |
| 8 | K | u | spike | 4 | step143000 | -8.1883 | 15.49 | 5.575e+04 | 9.665e-08 | 1024 |
| 9 | K | u | spike | 4 | step4000 | -8.1426 | 22.86 | 7.86e+04 | 9.665e-08 | 1024 |
| 10 | Q | u | spike | 4 | step128000 | -8.1038 | 26.19 | 8.662e+04 | 9.665e-08 | 1024 |

## pythia-410m-seed4  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step12000 | -8.5433 | 22.63 | 1.161e+05 | 9.665e-08 | 1024 |
| 2 | K | u | spike | 4 | step8000 | -8.5067 | 22.75 | 1.126e+05 | 9.665e-08 | 1024 |
| 3 | K | u | spike | 4 | step6000 | -8.4859 | 24.49 | 1.187e+05 | 9.665e-08 | 1024 |
| 4 | Q | u | spike | 4 | step6000 | -8.4543 | 15.2 | 7.136e+04 | 9.665e-08 | 1024 |
| 5 | Q | u | spike | 4 | step8000 | -8.4347 | 16.15 | 7.435e+04 | 9.665e-08 | 1024 |
| 6 | MLP_IN | u | 512-1024 | 4 | step96000 | +8.3601 | 4372 | 1.023 | 1.523e-09 | 4096 |
| 7 | Q | u | spike | 4 | step96000 | -8.3239 | 31.41 | 1.294e+05 | 9.665e-08 | 1024 |
| 8 | K | u | spike | 4 | step16000 | -8.2102 | 23.08 | 8.487e+04 | 9.665e-08 | 1024 |
| 9 | Q | u | spike | 4 | step4000 | -8.1778 | 12.96 | 4.614e+04 | 9.665e-08 | 1024 |
| 10 | K | u | spike | 4 | step4000 | -8.1603 | 29.41 | 1.029e+05 | 9.665e-08 | 1024 |

## pythia-410m-seed5  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step12000 | -8.5155 | 24.36 | 1.216e+05 | 9.665e-08 | 1024 |
| 2 | K | u | spike | 4 | step16000 | -8.3966 | 22.95 | 1.017e+05 | 9.665e-08 | 1024 |
| 3 | K | u | spike | 4 | step8000 | -8.3755 | 27.9 | 1.211e+05 | 9.665e-08 | 1024 |
| 4 | K | u | spike | 4 | step6000 | -8.3360 | 28.46 | 1.187e+05 | 9.665e-08 | 1024 |
| 5 | MLP_OUT | u | spike | 4 | step4000 | -8.0915 | 2.689 | 8783 | 9.665e-08 | 1024 |
| 6 | MLP_IN | u | 512-1024 | 4 | step96000 | +8.0437 | 3183 | 1.022 | 1.523e-09 | 4096 |
| 7 | K | u | spike | 4 | step4000 | -7.9839 | 29.93 | 8.779e+04 | 9.665e-08 | 1024 |
| 8 | Q | u | spike | 4 | step12000 | -7.9747 | 28.55 | 8.3e+04 | 9.665e-08 | 1024 |
| 9 | Q | u | spike | 4 | step128000 | -7.9686 | 38.93 | 1.125e+05 | 9.665e-08 | 1024 |
| 10 | MLP_IN | u | 512-1024 | 4 | step143000 | +7.9573 | 2929 | 1.025 | 1.523e-09 | 4096 |

## pythia-410m-seedmean  (26 checkpoints: step0, step1, step2, step4, step8, step16, step32, step64, step128, step256, step512, step1000, step2000, step3000, step4000, step6000, step8000, step12000, step16000, step24000, step32000, step48000, step64000, step96000, step128000, step143000)

| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K | u | spike | 4 | step8000 | -8.4571 +- 0.051 | 23.77 | 1.117e+05 | 9.665e-08 | 1024 |
| 2 | K | u | spike | 4 | step12000 | -8.4330 +- 0.130 | 22.19 | 1.034e+05 | 9.665e-08 | 1024 |
| 3 | K | u | spike | 4 | step6000 | -8.4035 +- 0.111 | 25.07 | 1.115e+05 | 9.665e-08 | 1024 |
| 4 | K | u | spike | 4 | step16000 | -8.2241 +- 0.230 | 22.08 | 8.486e+04 | 9.665e-08 | 1024 |
| 5 | K | u | spike | 4 | step4000 | -8.1007 +- 0.070 | 25.72 | 8.468e+04 | 9.665e-08 | 1024 |
| 6 | Q | u | spike | 4 | step6000 | -8.0603 +- 0.328 | 19.09 | 5.89e+04 | 9.665e-08 | 1024 |
| 7 | Q | u | spike | 4 | step8000 | -7.9613 +- 0.454 | 23.62 | 6.376e+04 | 9.665e-08 | 1024 |
| 8 | Q | u | spike | 4 | step4000 | -7.9504 +- 0.272 | 14.34 | 3.948e+04 | 9.665e-08 | 1024 |
| 9 | Q | u | spike | 4 | step12000 | -7.9188 +- 0.244 | 23.16 | 6.337e+04 | 9.665e-08 | 1024 |
| 10 | Q | u | spike | 4 | step16000 | -7.8358 +- 0.161 | 22.56 | 5.66e+04 | 9.665e-08 | 1024 |
