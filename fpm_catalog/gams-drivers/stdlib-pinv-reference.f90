! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: pinv,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64),allocatable :: a(:,:),original(:,:),u(:),v(:),actual(:,:),expected(:,:),ap(:,:),pa(:,:)
   real(real64) :: denominator,scale
   integer :: m,n,t,i,j,checks
   checks=0
   do m=2,6
      do n=2,5
         allocate(a(m,n),original(m,n),u(m),v(n),actual(n,m),expected(n,m),ap(m,m),pa(n,n))
         do t=1,4
            do i=1,m
               u(i)=real(i+t,real64)/8
            end do
            do j=1,n
               v(j)=real((-1)**j*(j+2),real64)/4
            end do
            denominator=sum(u*u)*sum(v*v)
            do j=1,n
               do i=1,m
                  a(i,j)=u(i)*v(j)
                  expected(j,i)=v(j)*u(i)/denominator
               end do
            end do
            original=a
            actual=pinv(a,rtol=1.e-10_real64,err=state)
            if(.not.state%ok().or..not.all(ieee_is_finite(actual))) error stop 'Pseudoinverse status'
            if(maxval(abs(actual-expected))>2.e-11_real64) error stop 'Outer-product pseudoinverse oracle'
            ap=matmul(a,actual)
            pa=matmul(actual,a)
            scale=max(1._real64,maxval(abs(a)))
            if(maxval(abs(matmul(ap,a)-a))>2.e-11_real64*scale) error stop 'First Moore-Penrose identity'
            if(maxval(abs(matmul(pa,actual)-actual))>2.e-11_real64) error stop 'Second Moore-Penrose identity'
            if(maxval(abs(ap-transpose(ap)))>2.e-11_real64) error stop 'Third Moore-Penrose identity'
            if(maxval(abs(pa-transpose(pa)))>2.e-11_real64) error stop 'Fourth Moore-Penrose identity'
            if(any(a/=original)) error stop 'Pseudoinverse input changed'
            checks=checks+m*n
         end do
         deallocate(a,original,u,v,actual,expected,ap,pa)
      end do
   end do
   print '(a,i0)', '80 rank-one rectangular matrices; closed-form pseudoinverse entries and four identities: ',checks
   print '(a)', 'PASS stdlib-pinv-reference'
end program
