! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
program main
   use fftpack, only: wp=>rk, dsinti, dsint
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),allocatable :: x(:),saved(:),actual(:),expected(:),restored(:),workspace(:)
   real(wp) :: pi,angle,normalization
   integer :: n,pattern,j,k,cases
   pi=acos(-1._wp); cases=0
   do n=1,24
      allocate(x(n),expected(n),workspace(3*n+20))
      do pattern=0,3
         do j=1,n
            select case(pattern)
            case(0)
               x(j)=1
            case(1)
               x(j)=0
               if(j==min(n,2)) x(j)=1
            case(2)
               x(j)=real((-1)**j*j,wp)/8
            case(3)
               x(j)=real(mod(j*j+3*j,11)-5,wp)/8
            end select
         end do
         saved=x; expected=0
         do k=1,n
            do j=1,n
               angle=pi*real(j*k,wp)/real(n+1,wp)
               expected(k)=expected(k)+2*x(j)*sin(angle)
            end do
         end do
         actual=x
         call dsinti(n,workspace); call dsint(n,actual,workspace)
         restored=actual; call dsint(n,restored,workspace)
         restored=restored/real(2*(n+1),wp)
         do k=1,n
            call check(actual(k),expected(k)); call check(restored(k),saved(k))
         end do
         if(any(x/=saved)) error stop 'Transform source preservation'
         cases=cases+1
      end do
      deallocate(x,expected,workspace)
   end do
   print '(a,i0)', 'Independent direct trigonometric sums and normalized inverse cases: ',cases
   print '(a)', 'PASS fftpack-sine-type1-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
