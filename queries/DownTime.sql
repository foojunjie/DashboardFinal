Select
    ms_flag,
    mc_flag,
    me_flag,
    bt_flag,
    mp_flag,
    qc_flag,
    station_id,
    anomaly_timestamp
From jtc_anomaly_timeslot
where extract(day from anomaly_timestamp) = %s
and extract(month from anomaly_timestamp) = %s
and extract(year from anomaly_timestamp) = %s
