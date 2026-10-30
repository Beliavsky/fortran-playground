! Store mixed values and retrieve them by key, following the upstream README.
program main
   use dictionary
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dictionary_t) :: settings
   integer :: count, values(3)
   real(real64) :: scale
   character(16) :: label
   logical :: success
   settings = ('count'.kv.7)
   settings = settings // ('scale'.kv.2.5_real64) // ('label'.kv.'Fortran') // ('values'.kv.[2,3,5])
   count = -1
   scale = -huge(scale)
   label = ''
   values = 0
   call assign(count, settings, 'count', success=success)
   if (.not. success .or. count /= 7) error stop 'Integer lookup failed'
   call assign(scale, settings, 'scale', success=success)
   if (.not. success .or. .not. ieee_is_finite(scale)) error stop 'Real lookup failed'
   if (abs(scale-2.5_real64) > 1.0e-12_real64) error stop 'Wrong real value'
   call assign(label, settings, 'label')
   if (trim(label) /= 'Fortran') error stop 'String lookup failed'
   call assign(values, settings, 'values', success=success)
   if (.not. success .or. any(values /= [2,3,5])) error stop 'Array lookup failed'
   print '(a,i0,a,f5.2,a,a)', 'count=', count, ', scale=', scale, ', label=', trim(label)
   print '(a,3(i0,1x))', 'values=', values
   call delete(settings)
   print '(a)', 'PASS fdict'
end program main
