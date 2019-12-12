import struct
import os


if __name__ == '__main__':
    f_name = "test_files/Beam-Pb-Gap30-Win50_50x50_ch23_1575988787_0_1.raw"
    # f_name = "test_files/Beam-W-Gap30-Win60_50x50_ch23_1575974938_0_1.raw"
    int_size = 4  # bytes2

    with open(f_name, 'rb') as f:
        _, _, _, nos = struct.unpack('hhhh', f.read(2 * int_size))
        event_size = 8 * int_size * nos
        print(os.path.getsize(f_name) // event_size)

    edep = []
    with open(f_name, 'rb') as f:
        event = f.read(event_size)
        while event != b'':
            edep.append(struct.unpack('H' * 2 * 8 * nos, event)[4])
            event = f.read(event_size)

    from matplotlib import pyplot as plt

    plt.hist(edep, bins=512)
    plt.show()
