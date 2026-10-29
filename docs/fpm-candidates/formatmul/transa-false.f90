program reproduce_false_transpose
   use kinds, only: rk
   use formatmul, only: matmul
   implicit none
   real(rk) :: a(2,3), b(3,2)
   real(rk), allocatable :: c(:,:)
   a = reshape([1.0_rk,4.0_rk,2.0_rk,5.0_rk,3.0_rk,6.0_rk],shape(a))
   b = reshape([7.0_rk,9.0_rk,11.0_rk,8.0_rk,10.0_rk,12.0_rk],shape(b))
   c = matmul(a,b,transA=.false.,option='m1')
   print '(a,2i4)', 'Result shape: ',shape(c)
   if (any(shape(c) /= [2,2])) error stop 'untransposed result must be 2 by 2'
   if (maxval(abs(c-reshape([58.0_rk,139.0_rk,64.0_rk,154.0_rk],[2,2]))) > 1.e-10_rk) &
      error stop 'wrong matrix product'
   print '(a)', 'PASS explicit false transpose'
end program reproduce_false_transpose
