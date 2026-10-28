program main
   use fsparse
   use fsparse_constants, only: dp
   implicit none
   type(COO_dp) :: coo
   real(dp) :: dense(3,3),x(3),y(3),expected(3)
   dense=reshape([2._dp,0._dp,1._dp,0._dp,3._dp,0._dp,1._dp,0._dp,4._dp],[3,3])
   x=[1._dp,2._dp,3._dp]
   expected=matmul(dense,x)
   call dense2coo(dense,coo)
   y=0._dp ! MATVEC adds the product to its output vector.
   call matvec(coo,x,y)
   if (maxval(abs(y-expected))>1e-12_dp) error stop 'Sparse product differs from MATMUL'
   print '(a,3f10.4)', 'Sparse product:',y
   print '(a,3f10.4)', 'Dense product: ',expected
   print *, 'PASS fsparse'
end program main
