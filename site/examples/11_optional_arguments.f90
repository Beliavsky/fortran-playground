! Example: Procedures: optional and keyword arguments
! Try supplying only offset, or using a different scale.
program optional_arguments
   implicit none
   print '(a,f8.2)', 'Defaults: ', transform(3.0)
   print '(a,f8.2)', 'Scale only: ', transform(3.0,scale=2.0)
   print '(a,f8.2)', 'Keywords in a different order: ', transform(3.0,offset=1.0,scale=2.0)
contains
   function transform(x,scale,offset) result(y)
      real, intent(in) :: x
      real, intent(in), optional :: scale, offset
      real :: y
      y = x
      if (present(scale)) y = y*scale
      if (present(offset)) y = y + offset
   end function transform
end program optional_arguments
