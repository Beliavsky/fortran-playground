! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use fftpack, only: wp=>rk,rfft,irfft
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),allocatable :: x(:),saved(:),effective(:),actual(:),restored(:),reference(:)
   real(wp) :: pi,angle,re,im
   integer :: m,n,mode,pattern,j,k,cases
   pi=acos(-1._wp); cases=0
   do m=4,16
      allocate(x(m))
      do pattern=0,3
         do j=1,m
            select case(pattern)
            case(0)
               x(j)=1
            case(1)
               x(j)=0
               if(j==2) x(j)=1
            case(2)
               x(j)=real((-1)**j*j,wp)/8
            case(3)
               x(j)=real(mod(j*j+3*j,11)-5,wp)/8
            end select
         end do
         saved=x
         do mode=0,2
            n=m
            if(mode==0) n=m-2
            if(mode==2) n=m+3
            allocate(effective(n),reference(n)); effective=0
            effective(:min(n,m))=x(:min(n,m)); reference(1)=sum(effective)
            do k=1,(n-1)/2
               re=0; im=0
               do j=0,n-1
                  angle=2*pi*real(j*k,wp)/real(n,wp)
                  re=re+effective(j+1)*cos(angle); im=im-effective(j+1)*sin(angle)
               end do
               reference(2*k)=re; reference(2*k+1)=im
            end do
            if(mod(n,2)==0) reference(n)=sum([(effective(j+1)*real((-1)**j,wp),j=0,n-1)])
            actual=rfft(x,n=n); restored=irfft(actual,n=n)/real(n,wp)
            if(size(actual)/=n.or.size(restored)/=n) error stop 'Real FFT output shape'
            do k=1,n
               call check(actual(k),reference(k)); call check(restored(k),effective(k))
            end do
            if(any(x/=saved)) error stop 'Real FFT source preservation'
            cases=cases+1; deallocate(effective,reference)
         end do
      end do
      deallocate(x)
   end do
   print '(a,i0)', 'Packed real DFT, odd/even lengths, truncation and zero-padding cases: ',cases
   print '(a)', 'PASS fftpack-packed-real-transforms-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
