! Assemble a tridiagonal operator, convert LL to CRS, and multiply a vector.
program demo_libsparse
   use, intrinsic :: iso_fortran_env, only: real64, int32
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use modsparse, only: llsparse, crssparse, assignment(=)
   implicit none
   integer(int32), parameter :: n=5
   type(llsparse) :: ll
   type(crssparse) :: crs
   real(real64) :: x(n),y(n),expected(n),dense(n,n)
   integer(int32) :: i,j
   ll = llsparse(n,lupper=.false.)
   dense = 0
   do i=1,n
      call ll%add(i,i,2._real64)
      dense(i,i) = 2
      if (i>1) then
         call ll%add(i,i-1,-1._real64)
         dense(i,i-1) = -1
      end if
      if (i<n) then
         call ll%add(i,i+1,-1._real64)
         dense(i,i+1) = -1
      end if
   end do
   crs = ll
   do j=1,n
      do i=1,n
         if (abs(crs%get(i,j)-dense(i,j))>1e-12_real64) error stop 'CRS conversion failed'
      end do
   end do
   x = [(real(i,real64),i=1,n)]
   call crs%mult(1._real64,'N',x,0._real64,y)
   expected = matmul(dense,x)
   if (.not. all(ieee_is_finite(y))) error stop 'Nonfinite product'
   if (maxval(abs(y-expected))>1e-12_real64) error stop 'Sparse product differs'
   print '(a,i0)', 'Stored nonzeros: ',crs%nonzero()
   print '(a,5f12.5)', 'A*[1,2,3,4,5]: ',y
   call crs%destroy()
   call ll%destroy()
   print '(a)', 'PASS libsparse'
end program
