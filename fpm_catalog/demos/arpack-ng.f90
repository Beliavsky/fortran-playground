! ARPACK reverse communication: three smallest eigenpairs of a tridiagonal matrix.
program main
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   integer, parameter :: n=20, nev=3, ncv=10, lwork=ncv*(ncv+8)
   integer :: ido, info, iparam(11), ipntr(11), i, j
   real(real64) :: resid(n), v(n,ncv), workd(3*n), workl(lwork), eigenvalues(nev), z(n,nev)
   real(real64) :: tol, exact, product(n), error
   logical :: selected(ncv)
   interface
      subroutine dsaupd(ido,bmat,n,which,nev,tol,resid,ncv,v,ldv,iparam,ipntr,workd,workl,lworkl,info)
         import real64
         character :: bmat
         character(2) :: which
         integer :: ido,n,nev,ncv,ldv,lworkl,info,iparam(11),ipntr(11)
         real(real64) :: tol,resid(*),v(ldv,*),workd(*),workl(*)
      end subroutine dsaupd
      subroutine dseupd(rvec,howmny,selected,d,z,ldz,sigma,bmat,n,which,nev,tol, &
         resid,ncv,v,ldv,iparam,ipntr,workd,workl,lworkl,info)
         import real64
         logical :: rvec,selected(*)
         character :: howmny,bmat
         character(2) :: which
         integer :: ldz,n,nev,ncv,ldv,lworkl,info,iparam(11),ipntr(11)
         real(real64) :: d(*),z(ldz,*),sigma,tol,resid(*),v(ldv,*),workd(*),workl(*)
      end subroutine dseupd
   end interface
   ido = 0
   info = 1 ! Supply a reproducible, nonzero initial residual.
   do i=1,n
      resid(i) = sin(real(i,real64))
   end do
   iparam = 0
   iparam(1) = 1
   iparam(3) = 1000
   iparam(7) = 1
   tol = 1.0e-11_real64
   do
      call dsaupd(ido,'I',n,'SM',nev,tol,resid,ncv,v,n,iparam,ipntr,workd,workl,lwork,info)
      if (ido == -1 .or. ido == 1) then
         call multiply(workd(ipntr(1):ipntr(1)+n-1), product)
         workd(ipntr(2):ipntr(2)+n-1) = product
      else if (ido == 2) then
         workd(ipntr(2):ipntr(2)+n-1) = workd(ipntr(1):ipntr(1)+n-1)
      else
         exit
      end if
   end do
   if (info /= 0 .or. iparam(5) /= nev) error stop 'Eigenvalue iteration failed'
   call dseupd(.true.,'A',selected,eigenvalues,z,n,0.0_real64,'I',n,'SM',nev, &
      tol,resid,ncv,v,n,iparam,ipntr,workd,workl,lwork,info)
   if (info /= 0) error stop 'Eigenvector extraction failed'
   print '(a)', 'Computed eigenvalue       Exact eigenvalue         Residual'
   do j=1,nev
      exact = 2.0_real64-2.0_real64*cos(real(j,real64)*acos(-1.0_real64)/real(n+1,real64))
      call multiply(z(:,j),product)
      error = sqrt(sum((product-eigenvalues(j)*z(:,j))**2))
      print '(3es24.14)', eigenvalues(j), exact, error
      if (abs(eigenvalues(j)-exact) > 1.0e-9_real64 .or. error > 1.0e-9_real64) &
         error stop 'Incorrect eigenpair'
   end do
   print '(a)', 'PASS arpack-ng'
contains
   subroutine multiply(x,y)
      real(real64), intent(in) :: x(n)
      real(real64), intent(out) :: y(n)
      y = 2.0_real64*x
      y(2:n) = y(2:n)-x(1:n-1)
      y(1:n-1) = y(1:n-1)-x(2:n)
   end subroutine multiply
end program main
