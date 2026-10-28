! Solve a small quasi-definite KKT system using three sparse orderings.
program demo_qdldl
   use qdldl_module, only: qdldl_type, wp=>qdldl_wp, ip=>qdldl_ip, qdldl_success, &
      qdldl_order_natural, qdldl_order_rcm, qdldl_order_amd
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: n=4
   integer(ip), parameter :: row(*)=[1,2,1,2,3,1,2,4], col(*)=[1,2,3,3,3,4,4,4]
   real(wp), parameter :: val(*)=[4._wp,3._wp,1._wp,2._wp,-2._wp,-1._wp,1._wp,-1._wp]
   integer, parameter :: order(*)=[qdldl_order_natural,qdldl_order_rcm,qdldl_order_amd]
   character(7), parameter :: names(*)=['natural','RCM    ','AMD    ']
   type(qdldl_type) :: solver
   real(wp) :: a(n,n), rhs(n), x(n), exact(n), err, residual
   integer :: i,k,status
   integer(ip) :: positive,negative,zero
   a=0
   do k=1,size(val)
      a(row(k),col(k))=val(k)
      a(col(k),row(k))=val(k)
   end do
   exact=[1._wp,-2._wp,3._wp,-4._wp]
   rhs=matmul(a,exact)
   print '(a)', 'Ordering   Max solution error   Max residual   Inertia (+,-,0)'
   do i=1,size(order)
      block
         type(qdldl_type) :: factor
         call factor%analyze(n,row,col,status,ordering=order(i))
         if (status/=qdldl_success) error stop 'Sparse analysis failed'
         call factor%factor(val,status)
         if (status/=qdldl_success) error stop 'Sparse factorization failed'
         x=rhs
         call factor%solve(x,status)
         if (status/=qdldl_success) error stop 'Sparse solve failed'
         if (.not.all(ieee_is_finite(x))) error stop 'Nonfinite solution'
         call factor%inertia(positive,negative,zero)
         err=maxval(abs(x-exact))
         residual=maxval(abs(matmul(a,x)-rhs))
         print '(a7,2es19.3,3i4)', names(i),err,residual,positive,negative,zero
         if (max(err,residual)>1e-11_wp) error stop 'Sparse solution inaccurate'
         if (positive/=2 .or. negative/=2 .or. zero/=0) error stop 'Incorrect matrix inertia'
      end block
   end do
   print '(a)', 'PASS qdldl-fortran'
end program
