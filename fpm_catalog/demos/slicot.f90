! Solve A^T X + X A = scale*C for a stable, nondiagonal A.
program main
   use, intrinsic :: iso_fortran_env, only: real64
   use slicot, only: sb03md
   implicit none
   integer, parameter :: n=2, ldwork=256
   real(real64) :: a(n,n), original(n,n), u(n,n), c(n,n), rhs(n,n), known(n,n)
   real(real64) :: scale, sep, ferr, wr(n), wi(n), work(ldwork), residual
   integer :: iwork(n*n), info
   original = reshape([-1.0_real64,0.0_real64,1.0_real64,-2.0_real64], [n,n])
   known = reshape([2.0_real64,0.5_real64,0.5_real64,1.0_real64], [n,n])
   rhs = matmul(transpose(original),known) + matmul(known,original)
   a = original
   c = rhs
   call sb03md('C','B','N','N',n,a,n,u,n,c,n,scale,sep,ferr,wr,wi,iwork,work,ldwork,info)
   if (info /= 0 .or. scale <= 0.0_real64) error stop 'Lyapunov solver failed'
   residual = maxval(abs(matmul(transpose(original),c)+matmul(c,original)-scale*rhs))
   print '(a)', 'Solution X / scale:'
   print '(2f12.7)', c(1,:)/scale
   print '(2f12.7)', c(2,:)/scale
   print '(a,es12.4)', 'Maximum Lyapunov residual: ', residual
   if (residual > 1.0e-10_real64) error stop 'Large residual'
   if (maxval(abs(c/scale-known)) > 1.0e-10_real64) error stop 'Incorrect solution'
   print '(a)', 'PASS slicot'
end program main
