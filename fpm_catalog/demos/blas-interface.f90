program main
   use iso_fortran_env, only: real64
   use blas, only: gemm=>blas_gemm
   implicit none
   real(real64) :: a(2,2),b(2,2),c(2,2)
   integer :: row
   a=reshape([1._real64,3._real64,2._real64,4._real64],[2,2])
   b=reshape([5._real64,7._real64,6._real64,8._real64],[2,2])
   c=0
   call gemm('N','N',2,2,2,1._real64,a,2,b,2,0._real64,c,2)
   if (maxval(abs(c-matmul(a,b)))>1e-12_real64) error stop
   print *, 'BLAS matrix product (checked against MATMUL):'
   do row=1,2
      print '(2f10.3)', c(row,:)
   end do
   print *, 'PASS blas-interface'
end program main
