! Array and forward-mode setup follows test/test_functions.f90 (MIT).
! f(x1,x2) = x1*x2**2 + x1**2; compare analytical and AD gradients.
program main
   use diffstruc
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(array_type) :: x
   type(array_type), pointer :: f, derivative
   real(real32) :: forward(2), reverse(2), exact(2), direction(2), err
   integer :: j

   call x%allocate(array_shape=[2,1])
   x%is_temporary = .false.
   x%val(:,1) = [1.25_real32, -2._real32]
   call x%set_requires_grad(.true.)
   f => pack(x,[1],1)*pack(x,[2],1)**2 + pack(x,[1],1)**2
   f%is_temporary = .false.
   exact = [x%val(2,1)**2+2*x%val(1,1), 2*x%val(1,1)*x%val(2,1)]
   do j = 1, 2
      direction = 0._real32
      direction(j) = 1._real32
      call x%set_direction(direction)
      derivative => f%grad_forward(x)
      derivative%is_temporary = .false.
      forward(j) = derivative%val(1,1)
   end do
   ! Reverse accumulation also uses direction: enable both components.
   call x%set_direction([1._real32,1._real32])
   call f%grad_reverse(reset_graph=.true.)
   if (.not. associated(x%grad)) error stop 'No reverse gradient'
   reverse = x%grad%val(:,1)
   err = max(maxval(abs(forward-exact)),maxval(abs(reverse-exact)))
   print '(a,f12.6)', 'Function value = ', f%val(1,1)
   print '(a,2f12.6)', 'Analytical gradient: ', exact
   print '(a,2f12.6)', 'Forward gradient:    ', forward
   print '(a,2f12.6)', 'Reverse gradient:    ', reverse
   if (.not. ieee_is_finite(err) .or. err > 1.e-5_real32) error stop 'Incorrect gradient'
   print *, 'PASS diffstruc'
end program main
