! Independent API consumer; MIT: licenses/rules-differences-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use mpmodule
   use playground_kronrod, only: init, kronrod, nwds2
   implicit none
   integer,parameter::orders(*)=[1,2,3,4,5,6,7,10]
   type(mp_real),allocatable::x(:),w(:),g(:)
   type(mp_real)::tol,integral,expected,term,zero,one,three,worst,scaled,error
   integer::j,n,i,p,degree,nk,ng,na,gauss_nodes
   if (mpipl<1000) error stop 'MPFUN precision configuration'
   call init()
   zero=mpreal(0.0_real64,nwds2); one=mpreal(1.0_real64,nwds2)
   three=mpreal(3.0_real64,nwds2)
   tol=mpreal(10.0_real64,nwds2)**(-50)
   worst=zero; nk=0; ng=0; na=0
   do j=1,size(orders)
      n=orders(j)
      allocate(x(n+1),w(n+1),g(n+1))
      call kronrod(n,tol,x,w,g)
      if (abs(x(n+1))>tol) error stop 'central node'
      gauss_nodes=0
      do i=1,n+1
         if (x(i)<zero.or.x(i)>=one) error stop 'node outside half interval'
         if (w(i)<=zero.or.g(i)<zero) error stop 'nonpositive weights'
         if (i<=n) then
            if (x(i)<=x(i+1)) error stop 'node ordering'
         end if
         if (g(i)>zero) then
            gauss_nodes=gauss_nodes+2
            if (i==n+1) gauss_nodes=gauss_nodes-1
         end if
      end do
      if (gauss_nodes/=n) error stop 'embedded Gauss node count'
      degree=3*n+1+mod(n,2)
      do p=0,degree,2
         integral=zero
         do i=1,n
            integral=integral+2*w(i)*x(i)**p
         end do
         if (p==0) integral=integral+w(n+1)
         expected=2*one/(p+1)
         call check(integral,expected)
         nk=nk+1
      end do
      do p=0,2*n-2,2
         integral=zero
         do i=1,n
            integral=integral+2*g(i)*x(i)**p
         end do
         if (p==0) integral=integral+g(n+1)
         expected=2*one/(p+1)
         call check(integral,expected)
         ng=ng+1
      end do
      ! Translate [-1,1] to [1,3]; nonsymmetric powers check both reflected halves.
      do p=0,min(2*n-1,8)
         integral=zero
         do i=1,n
            term=(2*one+x(i))**p+(2*one-x(i))**p
            integral=integral+w(i)*term
         end do
         integral=integral+w(n+1)*(2*one)**p
         expected=(three**(p+1)-one)/(p+1)
         call check(integral,expected)
         na=na+1
      end do
      print '(a,i0,a,i0)', 'Gauss order ',n,'; Kronrod nodes ',2*n+1
      deallocate(x,w,g)
   end do
   if (nk/=67.or.ng/=38.or.na/=56) error stop 'fixture accounting'
   print '(a,3i5)', 'Kronrod / Gauss / translated polynomial moments: ',nk,ng,na
   print '(a,es12.4)', 'Maximum normalized moment error: ',dble(worst)
   print '(a)', 'PASS kronrod-moments-reference'
contains
   subroutine check(actual,reference)
      type(mp_real),intent(in)::actual,reference
      error=abs(actual-reference)
      scaled=one
      if (abs(reference)>one) scaled=abs(reference)
      error=error/scaled
      if (error>mpreal(10.0_real64,nwds2)**(-40)) then
         print '(a,i0,a,i0,a,es12.4)', 'Failed n=',n,' power=',p,' normalized error=',dble(error)
         print '(a,2es22.12)', 'Actual/reference: ',dble(actual),dble(reference)
         error stop 'exact polynomial moment'
      end if
      if (error>worst) worst=error
   end subroutine check
end program main
