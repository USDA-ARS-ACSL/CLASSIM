INSERT INTO weather_data (weatherstation, weather_id, jday, Date, srad, tmax, tmin, rain, RH) 
SELECT weatherstation, weather_id, jday, Date, srad, tmax, tmin, rain, RH from TARIweather1;