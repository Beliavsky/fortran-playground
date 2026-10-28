program conjugate_gradient
   use kiss, only: wp, cg_dense
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 8
   real(wp) :: a(n,n), b(n), x(n), exact(n), residual
   integer :: i, info
   a = 0
   do i=1,n
      a(i,i) = 2
      if (i<n) then
         a(i,i+1) = -1
         a(i+1,i) = -1
      end if
   end do
   exact = [(real(i,wp)*(n+1-i),i=1,n)]
   b = matmul(a,exact)
   x = 0
   call cg_dense(a,b,x,atol=1.e-10_wp,info=info)
   residual = norm2(b-matmul(a,x))
   print '(a,8f8.3)', 'Discrete Poisson solution: ', x
   print '(a,es12.4)', 'Residual norm: ', residual
   print '(a,i0)', 'Solver status: ', info
   if (.not. all(ieee_is_finite(x))) error stop 'Nonfinite solution'
   if (residual>1.e-8_wp .or. maxval(abs(x-exact))>1.e-8_wp) error stop 'CG check'
   print *, 'PASS kiss'
end program
