! Factor one sparse tridiagonal matrix, then solve two right-hand sides.
program demo_y12m
   use y12m, only: y12mb,y12mc,y12md
   use iso_fortran_env, only: wp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=8,nn=500
   real(wp) :: a(nn),pivot(n),b(n),original_rhs(n),flags(8),matrix(n,n),exact(n),residual
   integer :: columns(nn),rows(nn),ha(n,11),iflag(10),status,nz,i,j,load
   matrix = 0; a = 0; rows = 0; columns = 0; ha = 0; nz = 0
   do i=1,n
      matrix(i,i) = 3
      if (i<n) then
         matrix(i,i+1) = -1
         matrix(i+1,i) = -1
      end if
   end do
   do i=1,n
      do j=1,n
         if (matrix(i,j)==0) cycle
         nz = nz+1; a(nz) = matrix(i,j); rows(nz) = i; columns(nz) = j
      end do
   end do
   iflag = 0; flags = 0
   iflag(2:5) = [3,1,0,2] ! Keep L for subsequent right-hand sides.
   flags(1:4) = [16.0_wp,1e-12_wp,1e16_wp,1e-12_wp]
   exact = 1; b = matmul(matrix,exact)
   call y12mb(n,nz,a,columns,nn,rows,nn,ha,n,flags,iflag,status)
   if (status/=0) error stop 'Sparse preparation failed'
   call y12mc(n,nz,a,columns,nn,rows,nn,pivot,b,ha,n,flags,iflag,status)
   if (status/=0) error stop 'Sparse factorization failed'
   do load=1,2
      if (load==2) then
         exact = [(real(i,wp),i=1,n)]
         b = matmul(matrix,exact)
         iflag(5) = 3 ! Full forward/back substitution using stored factors.
      end if
      original_rhs = matmul(matrix,exact)
      call y12md(n,a,nn,b,pivot,columns,ha,n,iflag,status)
      if (status/=0) error stop 'Sparse solve failed'
      if (.not. all(ieee_is_finite(b))) error stop 'Nonfinite solution'
      residual = maxval(abs(matmul(matrix,b)-original_rhs))
      if (residual>1e-10_wp .or. maxval(abs(b-exact))>1e-10_wp) error stop 'Sparse solution differs'
      print '(a,i0,a,8f8.3)', 'Right-hand side ',load,', solution: ',b
      print '(a,es12.3)', 'Maximum residual: ',residual
   end do
   print '(a)', 'One LU factorization used for both right-hand sides.'
   print '(a)', 'PASS y12m'
end program
