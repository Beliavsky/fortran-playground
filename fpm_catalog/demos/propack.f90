module playground_operator
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
contains
   ! A is an m-by-n diagonal matrix with diagonal entries 1,...,n.
   subroutine product(trans,m,n,x,y,dparm,iparm)
      character, intent(in) :: trans
      integer :: m, n, iparm(*)
      real(real64) :: x(*), y(*), dparm(*)
      integer :: j
      if (trans == 'n' .or. trans == 'N') then
         y(1:m) = 0.0_real64
      else
         y(1:n) = 0.0_real64
      end if
      do j=1, min(m,n)
         y(j) = j*x(j)
      end do
   end subroutine
end module

program main
   use playground_operator, only: real64, product
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: m=18, n=12, wanted=3, kmax=12, lwork=10000, liwork=1000
   real(real64) :: u(m,kmax+1), v(n,kmax), sigma(kmax), bounds(kmax), work(lwork)
   real(real64) :: options(3), dparm(1), av(m), atu(n), tolerance, residual
   integer :: iwork(liwork), ioptions(2), iparm(1), info, j, k
   interface
      subroutine dlansvd(jobu,jobv,m,n,k,kmax,aprod,u,ldu,sigma,bnd,v,ldv,tolin, &
                         work,lwork,iwork,liwork,doption,ioption,info,dparm,iparm)
         import real64
         character :: jobu, jobv
         integer :: m,n,k,kmax,ldu,ldv,lwork,liwork,info,iwork(liwork),ioption(*),iparm(*)
         real(real64) :: u(ldu,*),v(ldv,*),sigma(*),bnd(*),tolin,work(lwork),doption(*),dparm(*)
         external :: aprod
      end subroutine
   end interface
   u = 0.0_real64
   u(1:n,1) = 1.0_real64
   v = 0.0_real64
   options = [-1.0_real64,-1.0_real64,12.0_real64]
   ioptions = [1,1]
   work = 0.0_real64
   iwork = 0
   dparm = 0.0_real64
   iparm = 0
   tolerance = 1e-12_real64
   ! PROPACK updates k to the number of converged singular values.
   k = wanted
   call dlansvd('Y','Y',m,n,k,kmax,product,u,m,sigma,bounds,v,n,tolerance, &
                work,lwork,iwork,liwork,options,ioptions,info,dparm,iparm)
   if (info /= 0) error stop 'PROPACK did not converge'
   if (k /= wanted) error stop 'unexpected number of singular values'
   if (.not. all(ieee_is_finite(sigma(1:k)))) error stop 'nonfinite singular values'
   do j=1, k
      if (abs(sigma(j)-(n-j+1)) > 1e-8_real64) error stop 'singular value mismatch'
      call product('n',m,n,v(:,j),av,dparm,iparm)
      call product('t',m,n,u(:,j),atu,dparm,iparm)
      residual = max(sqrt(sum((av-sigma(j)*u(:,j))**2)),sqrt(sum((atu-sigma(j)*v(:,j))**2)))
      print '(a,f12.8,a,es12.3)', 'Singular value: ', sigma(j), '  residual: ', residual
      if (.not. ieee_is_finite(residual)) error stop 'nonfinite residual'
      if (residual > 1e-8_real64) error stop 'singular vector residual'
      if (abs(sum(u(:,j)**2)-1) > 1e-8_real64 .or. abs(sum(v(:,j)**2)-1) > 1e-8_real64) &
         error stop 'singular vector normalization'
   end do
   print *, 'PASS propack'
end program
