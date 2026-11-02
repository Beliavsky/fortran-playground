! Independent MIT consumer; see licenses/grids-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_quadrature, only: trapz_weights
   implicit none
   real(real64),parameter :: refs1(400)=[ &
      0.0_real64, 0.0_real64, 0.0_real64, 0.0_real64, 0.0_real64, 0.0_real64, 0.1875_real64, 0.1875_real64, &
      -0.1875_real64, -0.1875_real64, 0.0625_real64, 0.0625_real64, -0.0625_real64, -0.0625_real64, 0.1875_real64, &
      0.1875_real64, -0.1875_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.25_real64, -0.25_real64, &
      -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, &
      -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.125_real64, -0.125_real64, -0.3125_real64, -0.1875_real64, &
      0.1875_real64, 0.4375_real64, 0.3125_real64, 0.0625_real64, -0.0625_real64, -0.3125_real64, -0.4375_real64, &
      -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.0625_real64, -0.0625_real64, -0.25_real64, &
      -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.0625_real64, -0.0625_real64, &
      -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, &
      0.125_real64, -0.125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.25_real64, &
      -0.25_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.0625_real64, -0.0625_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.1875_real64, &
      -0.1875_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.25_real64, -0.25_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.125_real64, -0.125_real64, -0.3125_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.0625_real64, -0.0625_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.0625_real64, -0.0625_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.0625_real64, -0.0625_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.125_real64, -0.125_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.25_real64, -0.25_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, &
      -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, &
      0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, -0.1875_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.0625_real64, -0.0625_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.1875_real64, -0.1875_real64, -0.4375_real64, -0.3125_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.25_real64, -0.25_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.125_real64, &
      -0.125_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, &
      0.1875_real64 ]
   real(real64),parameter :: refs2(400)=[ &
      0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, &
      0.0625_real64, -0.0625_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.0625_real64, -0.0625_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.0625_real64, -0.0625_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.125_real64, -0.125_real64, -0.1875_real64, -0.3125_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.25_real64, &
      -0.25_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64, 0.1875_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, &
      0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, -0.1875_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.0625_real64, -0.0625_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.1875_real64, -0.1875_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.25_real64, -0.25_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, &
      -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, &
      -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.1875_real64, -0.1875_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, &
      0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, &
      0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.125_real64, -0.125_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.1875_real64, 0.1875_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, &
      0.3125_real64, 0.4375_real64, 0.3125_real64, 0.0625_real64, -0.0625_real64, -0.3125_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.1875_real64, 0.0625_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, 0.25_real64, &
      0.0625_real64, -0.0625_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, -0.25_real64, &
      -0.25_real64, -0.25_real64, -0.0625_real64, 0.1875_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, &
      0.4375_real64, 0.3125_real64, 0.1875_real64, 0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, &
      0.3125_real64, 0.4375_real64, 0.3125_real64, 0.1875_real64, 0.0625_real64 ]
   real(real64),parameter :: refs3(16)=[ &
      -0.0625_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, &
      -0.3125_real64, -0.4375_real64, -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.4375_real64, &
      -0.3125_real64, -0.1875_real64, -0.3125_real64, -0.1875_real64 ]
   real(real64),parameter :: expected(*)=[refs1,refs2,refs3]
   real(real64),allocatable :: x(:),w(:),saved(:),other(:)
   integer :: n,k,reverse,even,i,index,count,p
   real(real64) :: exact
   index=0; count=0
   do n=0,16
      allocate(x(n))
      do k=1,3
         do reverse=0,1
            if(n>0) x(1)=-0.75_real64
            do i=2,n
               x(i)=x(i-1)+real(1+mod(i*k,4),real64)/8
            end do
            if(reverse==1) x=x(n:1:-1)
            saved=x
            do even=0,0
               w=trapz_weights(x)
               if(size(w)/=n) error stop 'Weight shape'
               do i=1,n
                  index=index+1; call check(w(i),expected(index))
               end do
               if(n>=2) then
                  do p=0,1
                     exact=(x(n)**(p+1)-x(1)**(p+1))/real(p+1,real64)
                     call check(sum(w*x**p),exact)
                  end do
               end if
               if(any(x/=saved)) error stop 'Grid changed'
               count=count+1
            end do
         end do
      end do
      deallocate(x)
   end do
   if(index/=size(expected)) error stop 'Reference consumption'
   print '(a,i0)', 'Irregular-grid weight cases and exact polynomial integrals: ',count
   print '(a)', 'PASS stdlib-trapz-grid-weights-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine checkz(actual,expected)
      complex(real64),intent(in) :: actual,expected
      call check(real(actual,real64),real(expected,real64))
      call check(aimag(actual),aimag(expected))
   end subroutine
   subroutine check_matrix(actual,expected)
      complex(real64),intent(in) :: actual(:,:),expected(:,:)
      integer :: i,j
      if(any(shape(actual)/=shape(expected))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call checkz(actual(i,j),expected(i,j))
         end do
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in) :: n
      complex(real64) :: a(n,n)
      integer :: i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
   function unitary(n,k) result(q)
      integer,intent(in) :: n,k
      complex(real64) :: q(n,n),v(n)
      real(real64) :: denominator
      integer :: i,j
      do i=1,n
         v(i)=cmplx(real(i,real64),real(mod(i+k,4)-2,real64),real64)
      end do
      denominator=real(dot_product(v,v),real64)
      q=identity(n)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*v(i)*conjg(v(j))/denominator
         end do
      end do
      call check_matrix(matmul(conjg(transpose(q)),q),identity(n))
   end function
end program
