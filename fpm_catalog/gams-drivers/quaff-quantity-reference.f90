! Independent API consumer; MIT: licenses/quantities-spherical-drivers-MIT.txt.
program quantity_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use quaff, only: length_t,time_t,speed_t,METERS,CENTIMETERS,MILLIMETERS,FEET,INCHES, &
      SECONDS,MINUTES,HOURS,METERS_PER_SECOND,FEET_PER_SECOND,operator(.unit.), &
      operator(/),operator(*),operator(+),operator(-),quantity_abs=>abs,quantity_sum=>sum
   implicit none
   real(dp), parameter :: lengths(*) = [-8._dp,-.125_dp,0._dp,.25_dp,3._dp,1000._dp]
   real(dp), parameter :: times(*) = [.25_dp,1._dp,10._dp]
   type(length_t) :: distance,other,converted,quantities(3)
   type(time_t) :: duration
   type(speed_t) :: speed
   real(dp) :: v,t,max_error
   integer :: i,j,cases
   max_error = 0._dp
   cases = 0
   do i = 1,size(lengths)
      v = lengths(i)
      distance = v.unit.METERS
      call check(distance.in.METERS,v)
      call check(distance.in.CENTIMETERS,100*v)
      call check(distance.in.MILLIMETERS,1000*v)
      call check(distance.in.FEET,v/.3048_dp)
      call check(distance.in.INCHES,v/.0254_dp)
      converted = v.unit.FEET
      call check(converted.in.METERS,.3048_dp*v)
      call check(converted.in.INCHES,12*v)
      converted = v.unit.INCHES
      call check(converted.in.METERS,.0254_dp*v)
      converted = v.unit.CENTIMETERS
      call check(converted.in.METERS,.01_dp*v)
      converted = v.unit.MILLIMETERS
      call check(converted.in.METERS,.001_dp*v)
      other = (2*v+.5_dp).unit.METERS
      call check((distance+other).in.METERS,3*v+.5_dp)
      call check((distance-other).in.METERS,-v-.5_dp)
      call check((-distance).in.METERS,-v)
      call check((2._dp*distance).in.METERS,2*v)
      call check((distance/4._dp).in.METERS,v/4)
      call check(distance/(2._dp.unit.METERS),v/2)
      call check(quantity_abs(distance).in.METERS,abs(v))
      quantities = [distance,other,-distance]
      call check(quantity_sum(quantities).in.METERS,2*v+.5_dp)
      speed = v.unit.FEET_PER_SECOND
      call check(speed.in.METERS_PER_SECOND,.3048_dp*v)
      do j = 1,size(times)
         t = times(j)
         duration = t.unit.SECONDS
         speed = distance/duration
         call check(speed.in.METERS_PER_SECOND,v/t)
         call check(speed.in.FEET_PER_SECOND,v/t/.3048_dp)
         converted = speed*duration
         call check(converted.in.METERS,v)
      end do
   end do
   do j = 1,size(times)
      t = times(j)
      duration = t.unit.SECONDS
      call check(duration.in.MINUTES,t/60)
      call check(duration.in.HOURS,t/3600)
      duration = t.unit.MINUTES
      call check(duration.in.SECONDS,t*60)
      duration = t.unit.HOURS
      call check(duration.in.SECONDS,t*3600)
   end do
   if (cases /= 180) error stop 'quantity fixture count'
   print '(a)', '180 numeric references: signed/zero lengths, five units, time conversions and typed arithmetic.'
   print '(a)', 'Length/time speed and speed*time length checked against scalar SI formulas.'
   print '(a,es12.4)', 'Maximum error / max(1,abs(reference)): ',max_error
   print '(a)', 'PASS quaff-quantity-reference'
contains
   subroutine check(actual,reference)
      real(dp), intent(in) :: actual,reference
      real(dp) :: error
      if (.not. ieee_is_finite(actual)) error stop 'nonfinite quantity result'
      error = abs(actual-reference)/max(1._dp,abs(reference))
      max_error = max(max_error,error)
      if (error > 2.e-12_dp) error stop 'independent quantity reference'
      cases = cases+1
   end subroutine check
end program quantity_reference
