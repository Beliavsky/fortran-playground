! Original D4a1 API driver. MIT: licenses/boundary-spectral-drivers-MIT.txt.
program main
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: n=20,nev=3,ncv=10,lwork=ncv*(ncv+8)
   integer :: ido,info,iparam(11),ipntr(11),i,j,index,mode,calls
   real(dp) :: resid(n),v(n,ncv),workd(3*n),workl(lwork),eigenvalues(nev),z(n,nev)
   real(dp) :: tol,expected,product(n),exact_vector(n),error,gram(nev,nev),identity(nev,nev)
   logical :: selected(ncv)
   character(2) :: which
   interface
      subroutine dsaupd(ido,bmat,n,which,nev,tol,resid,ncv,v,ldv,iparam,ipntr,workd,workl,lworkl,info)
         import dp
         character :: bmat
         character(2) :: which
         integer :: ido,n,nev,ncv,ldv,lworkl,info,iparam(11),ipntr(11)
         real(dp) :: tol,resid(*),v(ldv,*),workd(*),workl(*)
      end subroutine
      subroutine dseupd(rvec,howmny,selected,d,z,ldz,sigma,bmat,n,which,nev,tol, &
         resid,ncv,v,ldv,iparam,ipntr,workd,workl,lworkl,info)
         import dp
         logical :: rvec,selected(*)
         character :: howmny,bmat
         character(2) :: which
         integer :: ldz,n,nev,ncv,ldv,lworkl,info,iparam(11),ipntr(11)
         real(dp) :: d(*),z(ldz,*),sigma,tol,resid(*),v(ldv,*),workd(*),workl(*)
      end subroutine
   end interface
   identity=0
   do j=1,nev
      identity(j,j)=1
   end do
   do mode=1,2
      which='SM'
      if(mode==2) which='LM'
      ido=0; info=1; calls=0
      resid=[(sin(real(i,dp)),i=1,n)]
      iparam=0; ipntr=0; workd=0; workl=0; v=0; selected=.false.
      iparam(1)=1; iparam(3)=1000; iparam(7)=1
      tol=1.e-11_dp
      do
         call dsaupd(ido,'I',n,which,nev,tol,resid,ncv,v,n,iparam,ipntr,workd,workl,lwork,info)
         if(ido==-1 .or. ido==1) then
            call multiply(workd(ipntr(1):ipntr(1)+n-1),product)
            workd(ipntr(2):ipntr(2)+n-1)=product
            calls=calls+1
         else if(ido==2) then
            workd(ipntr(2):ipntr(2)+n-1)=workd(ipntr(1):ipntr(1)+n-1)
         else
            exit
         end if
         if(calls>10000) error stop 'ARPACK operation budget'
      end do
      if(ido/=99 .or. info/=0 .or. iparam(5)/=nev) error stop 'ARPACK convergence'
      call dseupd(.true.,'A',selected,eigenvalues,z,n,0._dp,'I',n,which,nev,tol, &
         resid,ncv,v,n,iparam,ipntr,workd,workl,lwork,info)
      if(info/=0) error stop 'ARPACK extraction'
      if(.not.all(ieee_is_finite(eigenvalues)) .or. .not.all(ieee_is_finite(z))) error stop 'nonfinite eigenpairs'
      print '(a,a)', 'Spectrum selection: ',which
      do j=1,nev
         index=j
         if(mode==2) index=n-nev+j
         expected=4*sin(real(index,dp)*acos(-1._dp)/(2*(n+1)))**2
         call multiply(z(:,j),product)
         error=sqrt(sum((product-eigenvalues(j)*z(:,j))**2))
         if(abs(eigenvalues(j)-expected)>1.e-9_dp .or. error>1.e-9_dp) error stop 'known eigenvalue/residual'
         exact_vector=[(sqrt(2._dp/(n+1))*sin(real(i*index,dp)*acos(-1._dp)/(n+1)),i=1,n)]
         if(abs(abs(dot_product(z(:,j),exact_vector))-1)>1.e-8_dp) error stop 'known eigenvector direction'
         print '(i3,2f22.14,es14.4)',index,eigenvalues(j),expected,error
      end do
      gram=matmul(transpose(z),z)
      if(maxval(abs(gram-identity))>1.e-10_dp) error stop 'eigenvector orthogonality'
      print '(a,i0)', 'Matrix-vector callback count: ',calls
   end do
   print '(a)', 'PASS arpack-poisson-eigenpairs'
contains
   subroutine multiply(x,y)
      real(dp),intent(in) :: x(n)
      real(dp),intent(out) :: y(n)
      y=2*x
      y(2:n)=y(2:n)-x(:n-1)
      y(:n-1)=y(:n-1)-x(2:n)
   end subroutine
end program
