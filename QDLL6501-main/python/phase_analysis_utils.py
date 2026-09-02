
import numpy as np

def load_spice_file(file_path):
    data = np.loadtxt(file_path)
    time1 = data[:, 0]
    vin1 = data[:, 1]
    time2 = data[:, 2]
    vin2 = data[:, 3]
    time3 = data[:, 4]
    vout1 = data[:, 5]
    time4 = data[:, 6]
    vout2 = data[:, 7]
    return time1, time2, time3, time4, vin1, vin2, vout1, vout2

def find_crossings(signal, time, level):
    crossing_indices = np.where(np.diff((signal > level).astype(int)))[0]
    crossing_times = []
    for idx in crossing_indices:
        x0, x1 = time[idx], time[idx + 1]
        y0, y1 = signal[idx], signal[idx + 1]
        if y1 == y0:
            continue
        slope = (y1 - y0) / (x1 - x0)
        crossing_time = x0 + (level - y0) / slope
        crossing_times.append(crossing_time)
    return np.array(crossing_times)

def calculate_phase_from_crossings(sig1, sig2, time, threshold=0.6, freq=100e6):
    crossings1 = find_crossings(sig1, time, threshold)
    crossings2 = find_crossings(sig2, time, threshold)
    min_len = min(len(crossings1), len(crossings2))
    if min_len == 0:
        return float('nan'), float('nan')
    delays = crossings2[:min_len] - crossings1[:min_len]
    mean_delay = np.mean(delays)
    phase_diff_deg = (mean_delay * freq * 360) % 360
    return phase_diff_deg, mean_delay

def analyze_signals(time, vin1, vin2, vout1, vout2, threshold=0.6, freq=100e6):
    phi_in = calculate_phase_from_crossings(vin1, vin2, time, threshold, freq)
    phi_out = calculate_phase_from_crossings(vout1, vout2, time, threshold, freq)
    phi_in_out = calculate_phase_from_crossings(vin1, vout1, time, threshold, freq)
    return {
        'phi_in': phi_in,
        'phi_out': phi_out,
        'phi_in_out': phi_in_out
    }


import matplotlib.pyplot as plt

def phase_vs_time(sig1, sig2, time, threshold=0.6, freq=100e6):
    crossings1 = find_crossings(sig1, time, threshold)
    crossings2 = find_crossings(sig2, time, threshold)
    min_len = min(len(crossings1), len(crossings2))
    if min_len == 0:
        return None

    phase_over_time = ((crossings2[:min_len] - crossings1[:min_len]) * freq * 360) % 360
    time_axis = crossings1[:min_len] * 1e9  # Convert to ns

    plt.figure(figsize=(10, 5))
    plt.plot(time_axis, phase_over_time, marker='o')
    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Fase (°)")
    plt.title("Diferencia de fase en función del tiempo")
    plt.grid(True)
    plt.tight_layout()
    plt.ylim(100,70)
    plt.show()
    
    print("t_sim_fin [ns] =", time[-1]*1e9)
    print("N cruces sig1 =", len(crossings1), "último [ns] =", (crossings1[-1]*1e9 if len(crossings1) else None))
    print("N cruces sig2 =", len(crossings2), "último [ns] =", (crossings2[-1]*1e9 if len(crossings2) else None))
    print("min_len =", min_len)



    return time_axis, phase_over_time


def estimate_frequency(signal, time, threshold=0.6):
    crossings = find_crossings(signal, time, threshold)
    if len(crossings) < 2:
        return float('nan')
    periods = np.diff(crossings[::2])  # consider only rising edges
    if len(periods) == 0:
        return float('nan')
    mean_period = np.mean(periods)
    return 1.0 / mean_period


def compare_phase_vs_time_across_cases(signal_pairs, labels, time_array, threshold=0.6):
    plt.figure(figsize=(10, 6))
    for (sig1, sig2), label in zip(signal_pairs, labels):
        crossings1 = find_crossings(sig1, time_array, threshold)
        crossings2 = find_crossings(sig2, time_array, threshold)
        min_len = min(len(crossings1), len(crossings2))
        if min_len == 0:
            continue
        delays = crossings2[:min_len] - crossings1[:min_len]
        periods = np.diff(crossings1[::2])
        freq = 1.0 / np.mean(periods) if len(periods) > 0 else 100e6
        phase = (delays * freq * 360) % 360
        plt.plot(crossings1[:min_len] * 1e9, phase, label=label)

    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Fase (°)")
    plt.title("Comparación de diferencia de fase en el tiempo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def calculate_jitter(signal, time, threshold=0.6):
    crossings = find_crossings(signal, time, threshold)
    if len(crossings) < 3:
        return float('nan'), []
    periods = np.diff(crossings[::2])
    jitter_std = np.std(periods)
    return jitter_std, periods

def compare_jitter_across_cases(signals, labels, time_array, threshold=0.6):
    results = {}
    for signal, label in zip(signals, labels):
        jitter, periods = calculate_jitter(signal, time_array, threshold)
        results[label] = {
            'jitter_std': jitter,
            'periods': periods
        }
    return results


def compare_phase_vs_time_across_cases(signal_pairs, labels, time_arrays, threshold=0.6):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    for (sig1, sig2), label, t in zip(signal_pairs, labels, time_arrays):
        crossings1 = find_crossings(sig1, t, threshold)
        crossings2 = find_crossings(sig2, t, threshold)
        min_len = min(len(crossings1), len(crossings2))
        if min_len == 0:
            continue
        delays = crossings2[:min_len] - crossings1[:min_len]
        periods = np.diff(crossings1[::2])
        freq = 1.0 / np.mean(periods) if len(periods) > 0 else 100e6
        phase = (delays * freq * 360) % 360
        plt.plot(crossings1[:min_len] * 1e9, phase, label=label)

    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Fase (°)")
    plt.title("Comparación de diferencia de fase en el tiempo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

import numpy as np
import matplotlib.pyplot as plt

def _crossings_one_edge(sig, t, thr, edge="rise"):
    sig = np.asarray(sig)
    t   = np.asarray(t)

    if edge == "rise":
        idx = np.where((sig[:-1] < thr) & (sig[1:] >= thr))[0]
    elif edge == "fall":
        idx = np.where((sig[:-1] > thr) & (sig[1:] <= thr))[0]
    else:
        raise ValueError("edge debe ser 'rise' o 'fall'")

    y0 = sig[idx]
    y1 = sig[idx + 1]
    t0 = t[idx]
    t1 = t[idx + 1]
    denom = (y1 - y0)

    good = np.abs(denom) > 0
    y0, y1, t0, t1, denom = y0[good], y1[good], t0[good], t1[good], denom[good]

    return t0 + (thr - y0) * (t1 - t0) / denom


def phase_vs_time_single_edge(vin, vout, t, threshold=0.6, freq=None, edge="rise",
                              wrap_pm180=True, plot=True, title=None):
    """
    Fase vs tiempo usando SOLO un flanco (rise o fall).

    Retorna:
      t_phase: tiempos (uso los tiempos de cruce de vin, alineados)
      phi_deg: fase en grados
      dt:      delay temporal (s)
      t_in, t_out: tiempos de cruce (s)
    """
    t_in  = _crossings_one_edge(vin,  t, threshold, edge=edge)
    t_out = _crossings_one_edge(vout, t, threshold, edge=edge)

    if len(t_in) == 0 or len(t_out) == 0:
        raise ValueError("No se encontraron cruces para el flanco elegido. Revisá threshold o señales.")

    m = min(len(t_in), len(t_out))
    t_in  = t_in[:m]
    t_out = t_out[:m]

    dt = t_out - t_in  # positivo => vout atrasa respecto a vin

    # Si no pasás freq, estimo con cruces consecutivos de vin (mismo edge)
    if freq is None:
        if m < 2:
            raise ValueError("No puedo estimar freq: necesito al menos 2 cruces de vin.")
        T = np.median(np.diff(t_in))   # robusto ante un poco de jitter
        freq = 1.0 / T

    phi_deg = 360.0 * freq * dt

    if wrap_pm180:
        phi_deg = (phi_deg + 180.0) % 360.0 - 180.0

    # Tiempo asociado a cada medición de fase: el cruce de vin (podés elegir promedio)
    t_phase = t_in

    print("t_sim_fin [ns] =", t[-1]*1e9)
    print("N rises vin =", len(t_in),  "último [ns] =", t_in[-1]*1e9)
    print("N rises vout=", len(t_out), "último [ns] =", t_out[-1]*1e9)
    print("m =", m, "t_phase_fin [ns] =", t_in[m-1]*1e9)


    if plot:
        plt.figure(figsize=(10, 5))  # centrado (figura única)
        plt.plot(t_phase, phi_deg)
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Fase (deg)")
        if title is None:
            title = f"Fase vs tiempo (solo flanco {edge}, thr={threshold}, f={freq:.3g} Hz)"
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        plt.ylim(100,70)
        plt.show()

    return t_phase, phi_deg, dt, t_in, t_out


import numpy as np

def common_time_vector(time1, time2, time3, time4, *,
                       mode="intersection",
                       freq=200e6,
                       n_per_period=500,
                       dt=None):
    """
    Devuelve un vector de tiempo común 'time' (uniforme) para 4 ejes temporales.

    mode:
      - "intersection": usa el rango común a todos [max(t0), min(tf)]
      - "union":        usa el rango total [min(t0), max(tf)]  (ojo: luego tendrás NaNs si no extrapolás)

    dt:
      - si None, se calcula como T/n_per_period con T=1/freq

    Retorna:
      time_common (np.ndarray)
    """
    t1 = np.asarray(time1); t2 = np.asarray(time2)
    t3 = np.asarray(time3); t4 = np.asarray(time4)

    if dt is None:
        dt = (1.0 / freq) / n_per_period

    if mode == "intersection":
        t_start = max(t1[0], t2[0], t3[0], t4[0])
        t_stop  = min(t1[-1], t2[-1], t3[-1], t4[-1])
    elif mode == "union":
        t_start = min(t1[0], t2[0], t3[0], t4[0])
        t_stop  = max(t1[-1], t2[-1], t3[-1], t4[-1])
    else:
        raise ValueError("mode debe ser 'intersection' o 'union'")

    if t_stop <= t_start:
        raise ValueError("No hay rango temporal común (intersection vacía).")

    # +0.5*dt para incluir el final con seguridad (redondeo)
    return np.arange(t_start, t_stop + 0.5*dt, dt)


def resample_to_common_time(t_common, t_src, sig_src):
    """
    Interpola sig_src(t_src) a t_common sin extrapolar.
    Donde no hay datos, devuelve NaN.
    """
    t_src = np.asarray(t_src)
    sig_src = np.asarray(sig_src)
    t_common = np.asarray(t_common)

    out = np.full_like(t_common, np.nan, dtype=float)
    mask = (t_common >= t_src[0]) & (t_common <= t_src[-1])
    out[mask] = np.interp(t_common[mask], t_src, sig_src)
    return out

import numpy as np

def align_pair_to_common_time(t1, s1, t2, s2, *, freq=200e6, n_per_period=500, dt=None):
    """
    Crea un vector de tiempo común (intersección) y re-muestrea ambas señales ahí.
    """
    t1 = np.asarray(t1); s1 = np.asarray(s1)
    t2 = np.asarray(t2); s2 = np.asarray(s2)

    if dt is None:
        dt = (1.0 / freq) / n_per_period

    t_start = max(t1[0], t2[0])
    t_stop  = min(t1[-1], t2[-1])
    if t_stop <= t_start:
        raise ValueError("No hay superposición temporal entre las dos señales.")

    t_common = np.arange(t_start, t_stop + 0.5*dt, dt)

    s1c = np.interp(t_common, t1, s1)
    s2c = np.interp(t_common, t2, s2)
    return t_common, s1c, s2c


def estimate_frequency_rise(sig, t, threshold=0.6):
    # usa SOLO rises (sin el hack crossings[::2])
    tr = _crossings_one_edge(sig, t, threshold, edge="rise")
    print("N rises vin1 =", len(tr), "último [ns] =", tr[-1]*1e9 if len(tr) else None)

    if len(tr) < 2:
        return float("nan")
    T = np.median(np.diff(tr))
    return 1.0 / T



import numpy as np
import matplotlib.pyplot as plt

def match_crossings_by_time(t_ref, t_other, max_skew):
    """
    Para cada evento en t_ref, elige el evento más cercano en t_other.
    Mantiene solo los pares con |delta| <= max_skew.
    """
    t_ref = np.asarray(t_ref)
    t_other = np.asarray(t_other)

    if len(t_ref) == 0 or len(t_other) == 0:
        return np.array([]), np.array([])

    t_ref = np.sort(t_ref)
    t_other = np.sort(t_other)

    j = np.searchsorted(t_other, t_ref)
    j0 = np.clip(j - 1, 0, len(t_other) - 1)
    j1 = np.clip(j,     0, len(t_other) - 1)

    dt0 = np.abs(t_other[j0] - t_ref)
    dt1 = np.abs(t_other[j1] - t_ref)
    jj = np.where(dt1 < dt0, j1, j0)

    t_m = t_other[jj]
    keep = np.abs(t_m - t_ref) <= max_skew
    return t_ref[keep], t_m[keep]


def phase_vs_time_single_edge_time_match(vin, vout, t,
                                         threshold=0.6, freq=None, edge="rise",
                                         wrap_pm180=True, plot=True,
                                         ref="out"):
    """
    Igual que tu phase_vs_time_single_edge, pero empareja cruces por TIEMPO.
    ref:
      - "out": usa los cruces de vout como referencia temporal (te llega hasta ~76 ns en tu caso)
      - "in":  usa los cruces de vin como referencia temporal
    """
    # usa tu crossings_one_edge (pública)
    t_in  = crossings_one_edge(vin,  t, threshold, edge=edge)
    t_out = crossings_one_edge(vout, t, threshold, edge=edge)

    if len(t_in) == 0 or len(t_out) == 0:
        raise ValueError("No se encontraron cruces para el flanco elegido. Revisá threshold o señales.")

    if freq is None:
        if len(t_in) < 2:
            raise ValueError("No puedo estimar freq: necesito al menos 2 rises en vin.")
        T = np.median(np.diff(t_in))
        freq = 1.0 / T

    T = 1.0 / freq
    max_skew = T / 4.0  # ventana razonable

    if ref == "out":
        t_ref, t_match_in = match_crossings_by_time(t_out, t_in, max_skew=max_skew)
        # dt = t_out - t_in
        dt = t_ref - t_match_in
        t_phase = 0.5 * (t_ref + t_match_in)
    elif ref == "in":
        t_ref, t_match_out = match_crossings_by_time(t_in, t_out, max_skew=max_skew)
        dt = t_match_out - t_ref
        t_phase = 0.5 * (t_ref + t_match_out)
    else:
        raise ValueError("ref debe ser 'out' o 'in'")

    if len(dt) == 0:
        raise ValueError("No se pudieron emparejar cruces (max_skew muy chico o señales raras).")

    phi = 360.0 * freq * dt
    if wrap_pm180:
        phi = (phi + 180.0) % 360.0 - 180.0

    if plot:
        plt.figure(figsize=(10, 5))
        plt.plot(t_phase * 1e9, phi, marker='o')
        plt.xlabel("Tiempo (ns)")
        plt.ylabel("Fase (deg)")
        plt.title(f"Fase vs tiempo (match por tiempo, ref={ref}, edge={edge}, f={freq/1e6:.2f} MHz)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    print("t_sim_fin [ns] =", np.asarray(t)[-1] * 1e9)
    print("N rises vin (total)  =", len(t_in),  "último [ns] =", t_in[-1] * 1e9)
    print("N rises vout (total) =", len(t_out), "último [ns] =", t_out[-1] * 1e9)
    print("N pares match =", len(t_phase), "último t_phase [ns] =", t_phase[-1] * 1e9)

    return t_phase, phi, dt, t_in, t_out



import numpy as np

def crossings_one_edge(sig, t, thr=0.6, edge="rise"):
    sig = np.asarray(sig)
    t   = np.asarray(t)

    if edge == "rise":
        idx = np.where((sig[:-1] < thr) & (sig[1:] >= thr))[0]
    elif edge == "fall":
        idx = np.where((sig[:-1] > thr) & (sig[1:] <= thr))[0]
    else:
        raise ValueError("edge debe ser 'rise' o 'fall'")

    if idx.size == 0:
        return np.array([])

    y0 = sig[idx]
    y1 = sig[idx + 1]
    t0 = t[idx]
    t1 = t[idx + 1]
    denom = (y1 - y0)

    good = np.abs(denom) > 0
    y0, t0, t1, denom = y0[good], t0[good], t1[good], denom[good]

    return t0 + (thr - y0) * (t1 - t0) / denom



import numpy as np
import matplotlib.pyplot as plt


def wrap_pm180(phi_deg):
    return (phi_deg + 180.0) % 360.0 - 180.0


def crossings_one_edge(sig, t, thr=0.6, edge="rise"):
    sig = np.asarray(sig)
    t   = np.asarray(t)
    if sig.shape[0] != t.shape[0]:
        raise ValueError(f"sig y t deben tener mismo largo: {len(sig)} vs {len(t)}")

    if edge == "rise":
        idx = np.where((sig[:-1] < thr) & (sig[1:] >= thr))[0]
    elif edge == "fall":
        idx = np.where((sig[:-1] > thr) & (sig[1:] <= thr))[0]
    else:
        raise ValueError("edge debe ser 'rise' o 'fall'")

    if idx.size == 0:
        return np.array([])

    y0 = sig[idx]
    y1 = sig[idx + 1]
    t0 = t[idx]
    t1 = t[idx + 1]
    denom = (y1 - y0)
    good = np.abs(denom) > 0

    y0, t0, t1, denom = y0[good], t0[good], t1[good], denom[good]
    return t0 + (thr - y0) * (t1 - t0) / denom


def estimate_freq_from_rises(sig, t, thr=0.6):
    tr = crossings_one_edge(sig, t, thr=thr, edge="rise")
    if len(tr) < 2:
        return float("nan")
    T = np.median(np.diff(tr))
    return 1.0 / T


def match_by_time(t_ref, t_other, max_skew):
    """
    Para cada evento en t_ref, toma el evento más cercano en t_other.
    Conserva solo pares con |dt| <= max_skew.
    """
    t_ref   = np.asarray(t_ref)
    t_other = np.asarray(t_other)
    if len(t_ref) == 0 or len(t_other) == 0:
        return np.array([]), np.array([])

    t_ref   = np.sort(t_ref)
    t_other = np.sort(t_other)

    j = np.searchsorted(t_other, t_ref)
    j0 = np.clip(j - 1, 0, len(t_other) - 1)
    j1 = np.clip(j,     0, len(t_other) - 1)

    dt0 = np.abs(t_other[j0] - t_ref)
    dt1 = np.abs(t_other[j1] - t_ref)
    jj  = np.where(dt1 < dt0, j1, j0)

    t_m = t_other[jj]
    keep = np.abs(t_m - t_ref) <= max_skew
    return t_ref[keep], t_m[keep]


def phase_and_difference(vin1, t1, vout2, t4,
                         threshold=0.6, freq=None, edge="rise",
                         plot=True, ref="out"):
    """
    Calcula:
      - fase(vin1) y fase(vout2) en sus cruces
      - diferencia de fase Δφ = φ_out - φ_in emparejando cruces por tiempo

    ref:
      - "out": usa cruces de vout2 como referencia temporal (suele “llegar más lejos”)
      - "in" : usa cruces de vin1 como referencia temporal
    """
    c_in  = crossings_one_edge(vin1,  t1, thr=threshold, edge=edge)
    c_out = crossings_one_edge(vout2, t4, thr=threshold, edge=edge)

    if len(c_in) == 0 or len(c_out) == 0:
        raise ValueError("No hay cruces suficientes. Revisá threshold/edge o señales.")

    if freq is None:
        freq = estimate_freq_from_rises(vin1, t1, thr=threshold)

    if not np.isfinite(freq) or freq <= 0:
        raise ValueError("No pude estimar freq (o freq inválida). Pasala manualmente.")

    # Fase “absoluta” en cada cruce (en grados), envuelta a [-180,180]
    phi_in  = wrap_pm180(360.0 * freq * c_in)
    phi_out = wrap_pm180(360.0 * freq * c_out)

    T = 1.0 / freq
    max_skew = T / 4.0

    if ref == "out":
        c_ref, c_match = match_by_time(c_out, c_in, max_skew=max_skew)
        # Buscar índices para levantar fase de esos cruces (como son arrays ordenados, usamos searchsorted)
        idx_ref   = np.searchsorted(c_out, c_ref)
        idx_match = np.searchsorted(c_in,  c_match)
        idx_ref   = np.clip(idx_ref,   0, len(c_out)-1)
        idx_match = np.clip(idx_match, 0, len(c_in)-1)

        dphi = wrap_pm180(phi_out[idx_ref] - phi_in[idx_match])
        t_axis = 0.5 * (c_ref + c_match)

    elif ref == "in":
        c_ref, c_match = match_by_time(c_in, c_out, max_skew=max_skew)
        idx_ref   = np.searchsorted(c_in,  c_ref)
        idx_match = np.searchsorted(c_out, c_match)
        idx_ref   = np.clip(idx_ref,   0, len(c_in)-1)
        idx_match = np.clip(idx_match, 0, len(c_out)-1)

        dphi = wrap_pm180(phi_out[idx_match] - phi_in[idx_ref])
        t_axis = 0.5 * (c_ref + c_match)
    else:
        raise ValueError("ref debe ser 'out' o 'in'")

    if len(dphi) == 0:
        raise ValueError("No se pudieron emparejar cruces (probá otro threshold o revisá señales).")

    if plot:
        plt.figure(figsize=(10, 5))
        plt.plot(t_axis * 1e9, dphi, marker="o")
        plt.xlabel("Tiempo (ns)")
        plt.ylabel("ΔFase (deg)")
        plt.title(f"ΔFase = fase(vout2) - fase(vin1) | edge={edge}, thr={threshold}, f={freq/1e6:.2f} MHz")
        plt.grid(True)
        plt.ylim([-100,-70])
        plt.tight_layout()
        plt.show()

    # resumen útil
    mean_dphi = wrap_pm180(np.mean(dphi))
    return {
        "freq": freq,
        "c_in": c_in, "phi_in": phi_in,
        "c_out": c_out, "phi_out": phi_out,
        "t_axis": t_axis, "dphi": dphi,
        "mean_dphi": mean_dphi
    }




import numpy as np
import matplotlib.pyplot as plt

def plot_phi_crudo_y_delta(vin1, t1, vout2, t2, threshold=0.6, freq=None, edge="rise", ref="out"):
    # --- helpers mínimos (usá los tuyos si ya existen) ---
    def crossings_one_edge(sig, t, thr=0.6, edge="rise"):
        sig = np.asarray(sig); t = np.asarray(t)
        if sig.shape[0] != t.shape[0]:
            raise ValueError(f"sig y t deben tener mismo largo: {len(sig)} vs {len(t)}")

        if edge == "rise":
            idx = np.where((sig[:-1] < thr) & (sig[1:] >= thr))[0]
        elif edge == "fall":
            idx = np.where((sig[:-1] > thr) & (sig[1:] <= thr))[0]
        else:
            raise ValueError("edge debe ser 'rise' o 'fall'")

        if idx.size == 0:
            return np.array([])

        y0, y1 = sig[idx], sig[idx+1]
        t0, t1_ = t[idx], t[idx+1]
        denom = (y1 - y0)
        good = np.abs(denom) > 0
        y0, t0, t1_, denom = y0[good], t0[good], t1_[good], denom[good]
        return t0 + (thr - y0) * (t1_ - t0) / denom

    def estimate_freq_from_rises(sig, t, thr=0.6):
        tr = crossings_one_edge(sig, t, thr=thr, edge="rise")
        if len(tr) < 2:
            return float("nan")
        T = np.median(np.diff(tr))
        return 1.0 / T

    def match_by_time(t_ref, t_other, max_skew):
        t_ref = np.sort(np.asarray(t_ref))
        t_other = np.sort(np.asarray(t_other))
        if len(t_ref) == 0 or len(t_other) == 0:
            return np.array([]), np.array([])

        j = np.searchsorted(t_other, t_ref)
        j0 = np.clip(j - 1, 0, len(t_other) - 1)
        j1 = np.clip(j,     0, len(t_other) - 1)

        dt0 = np.abs(t_other[j0] - t_ref)
        dt1 = np.abs(t_other[j1] - t_ref)
        jj  = np.where(dt1 < dt0, j1, j0)

        t_m = t_other[jj]
        keep = np.abs(t_m - t_ref) <= max_skew
        return t_ref[keep], t_m[keep]

    # --- cruces ---
    c_in  = crossings_one_edge(vin1,  t1, thr=threshold, edge=edge)
    c_out = crossings_one_edge(vout2, t2, thr=threshold, edge=edge)
    if len(c_in) == 0 or len(c_out) == 0:
        raise ValueError("No hay cruces suficientes. Revisá threshold/edge o señales.")

    # --- frecuencia ---
    if freq is None:
        freq = estimate_freq_from_rises(vin1, t1, thr=threshold)
    if not np.isfinite(freq) or freq <= 0:
        raise ValueError("freq inválida. Pasala manualmente o revisá estimate_freq.")

    T = 1.0 / freq
    max_skew = T / 4.0

    # --- fases crudas en cada cruce (OJO: crecen con el tiempo, eso es 'crudo') ---
    phi_in  = 360.0 * freq * c_in
    phi_out = 360.0 * freq * c_out

    # --- emparejar cruces por TIEMPO para Δφ ---
    if ref == "out":
        c_ref, c_match = match_by_time(c_out, c_in, max_skew=max_skew)
        if len(c_ref) == 0:
            raise ValueError("No pude emparejar cruces. Probá otro threshold o revisá señales.")
        iref   = np.clip(np.searchsorted(c_out, c_ref),   0, len(c_out)-1)
        imatch = np.clip(np.searchsorted(c_in,  c_match), 0, len(c_in)-1)
        dphi = phi_out[iref] - phi_in[imatch]
        t_axis = 0.5*(c_ref + c_match)
    elif ref == "in":
        c_ref, c_match = match_by_time(c_in, c_out, max_skew=max_skew)
        if len(c_ref) == 0:
            raise ValueError("No pude emparejar cruces. Probá otro threshold o revisá señales.")
        iref   = np.clip(np.searchsorted(c_in,  c_ref),   0, len(c_in)-1)
        imatch = np.clip(np.searchsorted(c_out, c_match), 0, len(c_out)-1)
        dphi = phi_out[imatch] - phi_in[iref]
        t_axis = 0.5*(c_ref + c_match)
    else:
        raise ValueError("ref debe ser 'out' o 'in'")

    # --- PLOTS (sin subplots, como corresponde) ---
    plt.figure(figsize=(10, 5))
    plt.plot(c_in * 1e9, phi_in, marker='o')
    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Fase cruda vin1 (deg)")
    plt.title(f"Fase cruda vin1 en cruces ({edge}), thr={threshold}, f={freq/1e6:.2f} MHz")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(c_out * 1e9, phi_out, marker='o')
    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Fase cruda vout2 (deg)")
    plt.title(f"Fase cruda vout2 en cruces ({edge}), thr={threshold}, f={freq/1e6:.2f} MHz")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(t_axis * 1e9, dphi, marker='o')
    plt.xlabel("Tiempo (ns)")
    plt.ylabel("Δφ crudo = φ(vout2) − φ(vin1) (deg)")
    plt.title(f"Δφ crudo (match por tiempo, ref={ref}), thr={threshold}, f={freq/1e6:.2f} MHz")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Debug útil
    print("t1_fin [ns] =", np.asarray(t1)[-1]*1e9, "| t2_fin [ns] =", np.asarray(t2)[-1]*1e9)
    print("N rises vin1 =", len(c_in),  "último [ns] =", c_in[-1]*1e9)
    print("N rises vout2=", len(c_out), "último [ns] =", c_out[-1]*1e9)
    print("N pares Δφ  =", len(dphi),   "último t_axis [ns] =", t_axis[-1]*1e9)

    return (c_in, phi_in), (c_out, phi_out), (t_axis, dphi), freq


def plot_phase_difference_full(vin1, t1, vout2, t2, threshold=0.6, freq=None, edge="rise"):
    """
    Plot phase difference between vin1 and vout2 across entire simulation time.
    Uses all crossings without strict time-matching constraint.
    """
    def crossings_one_edge(sig, t, thr=0.6, edge="rise"):
        sig = np.asarray(sig); t = np.asarray(t)
        if sig.shape[0] != t.shape[0]:
            raise ValueError(f"sig y t deben tener mismo largo: {len(sig)} vs {len(t)}")

        if edge == "rise":
            idx = np.where((sig[:-1] < thr) & (sig[1:] >= thr))[0]
        elif edge == "fall":
            idx = np.where((sig[:-1] > thr) & (sig[1:] <= thr))[0]
        else:
            raise ValueError("edge debe ser 'rise' o 'fall'")

        if idx.size == 0:
            return np.array([])

        y0, y1 = sig[idx], sig[idx+1]
        t0, t1_ = t[idx], t[idx+1]
        denom = (y1 - y0)
        good = np.abs(denom) > 0
        y0, t0, t1_, denom = y0[good], t0[good], t1_[good], denom[good]
        return t0 + (thr - y0) * (t1_ - t0) / denom

    def estimate_freq_from_rises(sig, t, thr=0.6):
        tr = crossings_one_edge(sig, t, thr=thr, edge="rise")
        if len(tr) < 2:
            return float("nan")
        T = np.median(np.diff(tr))
        return 1.0 / T

    # Get crossings
    c_in  = crossings_one_edge(vin1,  t1, thr=threshold, edge=edge)
    c_out = crossings_one_edge(vout2, t2, thr=threshold, edge=edge)
    
    if len(c_in) == 0 or len(c_out) == 0:
        raise ValueError("No hay cruces suficientes. Revisá threshold/edge o señales.")

    # Estimate frequency if not provided
    if freq is None:
        freq = estimate_freq_from_rises(vin1, t1, thr=threshold)
    if not np.isfinite(freq) or freq <= 0:
        raise ValueError("freq inválida. Pasala manualmente o revisá estimate_freq.")

    # Calculate raw phases
    phi_in  = 360.0 * freq * c_in
    phi_out = 360.0 * freq * c_out

    # Match all output crossings with nearest input crossing
    min_len = min(len(c_in), len(c_out))
    
    # Use the shorter array as reference and match all
    if len(c_out) <= len(c_in):
        # For each output crossing, find nearest input crossing
        dphi_list = []
        t_axis_list = []
        for i, t_out in enumerate(c_out):
            # Find nearest input crossing
            idx_in = np.argmin(np.abs(c_in - t_out))
            dphi_list.append(phi_out[i] - phi_in[idx_in])
            t_axis_list.append(t_out)
    else:
        # For each input crossing, find nearest output crossing
        dphi_list = []
        t_axis_list = []
        for i, t_in in enumerate(c_in):
            # Find nearest output crossing
            idx_out = np.argmin(np.abs(c_out - t_in))
            dphi_list.append(phi_out[idx_out] - phi_in[i])
            t_axis_list.append(t_in)
    
    dphi = np.array(dphi_list)
    t_axis = np.array(t_axis_list)

    # Plot the full phase difference
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t_axis * 1e9, dphi, marker='o', linestyle='-', linewidth=1, markersize=4)
    ax.set_xlabel("Tiempo (ns)", fontsize=12)
    ax.set_ylabel("Δφ = φ(vout2) − φ(vin1) (°)", fontsize=12)
    ax.set_title(f"Diferencia de Fase (Full Range), thr={threshold}, f={freq/1e6:.2f} MHz, edge={edge}", fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=90,  color='gray', linestyle='--', linewidth=1)
    ax.axhline(y=180, color='gray', linestyle='--', linewidth=1)
    ax.text(x=ax.get_xlim()[1]*0.98, y=90,  s="90°",  va='bottom', ha='right', fontsize=10, color='gray')
    ax.text(x=ax.get_xlim()[1]*0.98, y=180, s="180°", va='bottom', ha='right', fontsize=10, color='gray')
    plt.ylim([0,360])
    fig.tight_layout()

    plt.show()

    # Print debug info
    print(f"\n=== PHASE DIFFERENCE ANALYSIS ===")
    print(f"Simulation end time: {np.asarray(t1)[-1]*1e9:.2f} ns | {np.asarray(t2)[-1]*1e9:.2f} ns")
    print(f"Input crossings (vin1): {len(c_in)}, last at {c_in[-1]*1e9:.2f} ns")
    print(f"Output crossings (vout2): {len(c_out)}, last at {c_out[-1]*1e9:.2f} ns")
    print(f"Phase difference pairs: {len(dphi)}, last time: {t_axis[-1]*1e9:.2f} ns")
    print(f"Frequency: {freq/1e6:.2f} MHz")
    print(f"Mean phase difference: {np.mean(dphi):.2f}°")
    print(f"Std dev phase difference: {np.std(dphi):.2f}°")
    
    return (c_in, phi_in), (c_out, phi_out), (t_axis, dphi), freq
