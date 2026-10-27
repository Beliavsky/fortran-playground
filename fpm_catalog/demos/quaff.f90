program main
   use quaff, only: length_t, time_t, speed_t, METERS, SECONDS, FEET_PER_SECOND, &
      METERS_PER_SECOND, operator(.unit.), operator(/)
   implicit none
   type(length_t) :: distance
   type(time_t) :: duration
   type(speed_t) :: speed
   double precision :: speed_in_feet, speed_in_meters
   distance = 100.0d0.unit.METERS
   duration = 10.0d0.unit.SECONDS
   speed = distance/duration
   speed_in_meters = speed.in.METERS_PER_SECOND
   speed_in_feet = speed.in.FEET_PER_SECOND
   if (abs(speed_in_meters-10.0d0) > 1.d-12) error stop 'incorrect speed'
   if (abs(speed_in_feet-10.0d0/0.3048d0) > 1.d-10) error stop 'incorrect unit conversion'
   print *, 'Speed in m/s:', speed_in_meters
   print *, 'Speed in ft/s:', speed_in_feet
   print *, 'PASS quaff'
end program main
