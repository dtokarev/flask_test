import os


def get_disk_usage_perc():
    st = os.statvfs('/')
    return round((st.f_blocks - st.f_bfree) / st.f_blocks * 100, 2)
