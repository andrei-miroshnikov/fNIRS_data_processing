def merge_epochs(open, closed, process_dirs=True, make_epochs=True, duration=2):
    if process_dirs:
        if make_epochs:
            merged_list = []
            for i in range(len(open)):
                    raw_1, epochs_1 = epoch_preprocessing(open[i], condition=0, duration=duration)
                    raw_2, epochs_2 = epoch_preprocessing(closed[i], condition=1, duration=duration)
                    merged = mne.concatenate_epochs([epochs_1, epochs_2])
                    merged_list.append(merged)
            return merged_list
        else:
            merged_list = []
            for i in range(len(open)):
                    merged = mne.concatenate_epochs([open[i], closed[i]])
                    merged_list.append(merged)
            return merged_list

    else:
        if make_epochs:
            raw_1, epochs_1 = epoch_preprocessing(open, condition=0, duration=duration)
            raw_2, epochs_2 = epoch_preprocessing(closed, condition=1, duration=duration)
            merged = mne.concatenate_epochs([epochs_1, epochs_2])
            return merged
        else:
            merged = mne.concatenate_epochs([open, closed])
            return merged


def snirf_list_maker(total_snirf, masks):
    snirf_list = []
    for file in total_snirf:
        for j in masks:
            if j in file:
                snirf_list.append(file)
    return snirf_list


def filter_and_make_even_epochs(i, duration, channels):
    '''Function takes snirf path as i and duration of epochs in seconds or equivalent. If equivalent, the recording will be split into 100 epochs of equal length.
    You can also provide a list of channels into channels arg to select hbo or hbr channels.'''
    raw_snirf = mne.io.read_raw_snirf(i, verbose=False)

    raw_snirf = raw_snirf.copy().load_data()

    raw_intensity = raw_snirf.crop(tmin=15., tmax=raw_snirf.times[-1]-15)

    raw_od = optical_density(raw_intensity)
    raw_od = mne_nirs.signal_enhancement.short_channel_regression(raw_od, max_dist=0.01)  #here we're tryi g to exclude sking vlood circulation

    raw_od.resample(1.5, verbose=False)
    raw_haemo = beer_lambert_law(raw_od, ppf=6)
    raw_haemo = raw_haemo.filter(None, 0.5, h_trans_bandwidth=0.05,
                                     l_trans_bandwidth=0.01, verbose=False, method="fir") #these filter setting were tried as the best so far. FIR os working better than IIR or savgol

    raw_haemo = raw_haemo.pick_channels(ch_names=channels)
    
    if type(duration) is int or type(duration) is float:
        epochs = mne.make_fixed_length_epochs(raw_haemo, duration=duration, preload=False, verbose=False)
        return epochs

    if duration == "equivalent":
        epochs = mne.make_fixed_length_epochs(raw_haemo, duration=raw_haemo.times[-1]/100, preload=False, verbose=False)   
        return epochs

