import numpy as np

def generate_sine(amplitude = 0.15):
    x_axis = np.linspace(0, 360, 360, endpoint=False)
    y_axis = amplitude * np.sin(np.radians(x_axis))
    return np.column_stack((x_axis, y_axis))

def align_degree(data, n_wave):
    n_row = len(data)
    row_per_cycle = n_row / n_wave
    deg_per_row = 360 / row_per_cycle

    index_max = np.argmax(data[:int(row_per_cycle)])
    indices = np.arange(n_row)
    relative_indices = indices - index_max
    aligned_degrees = (90 + relative_indices * deg_per_row) % 360
    return aligned_degrees

def filter_noise(data, max, min):
    filtered_data = np.where((data > min) & (data < max), np.nan, data)
    return filtered_data

def create_dummy_y(aligned_degrees, amplitude):
    radians = np.deg2rad(aligned_degrees)
    y_values = amplitude * np.sin(radians)
    return y_values

def generate_stream(data):
    x_axis = np.arange(len(data))
    return np.column_stack((x_axis, data))

def filter_noise_and_align(source, sensor, max_filter, min_filter, cycle):
    filtered_sensor = filter_noise(sensor, max_filter, min_filter)
    aligned_degree = align_degree(source, cycle)
    data_sensor = np.column_stack((aligned_degree, filtered_sensor))
    return data_sensor[~np.isnan(data_sensor).any(axis=1)]

def filter_degree(dataSensor, degStartPos, degEndPos, degStartNeg, degEndNeg):
    try:
        filteredPos = dataSensor[(dataSensor[:, 0] >= degStartPos) & (dataSensor[:, 0] <= degEndPos) & (dataSensor[:, 1] > 0)]
    except:
        filteredPos = dataSensor[(dataSensor[:, 1] > 0)]
    try:
        filteredNeg = dataSensor[(dataSensor[:, 0] >= degStartNeg) & (dataSensor[:, 0] <= degEndNeg) & (dataSensor[:, 1] < 0)]
    except:
        filteredNeg = dataSensor[(dataSensor[:, 1] < 0)]
    return np.vstack((filteredPos, filteredNeg))

# def implement_calibration(data_sensor, a, c):
    