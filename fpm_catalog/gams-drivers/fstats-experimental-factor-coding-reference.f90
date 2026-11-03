! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_doe_coding,only: &
      encode_variables,decode_variables
   implicit none
   real(wp),parameter::low(3)=[-4._wp,2._wp,16._wp],high(3)=[4._wp,6._wp,48._wp]
   real(wp)::natural(9,3),coded(9,3),decoded(9,3),expected(9,3),physical(9,3)
   integer::i,j
   do j=1,3
      do i=1,9
         expected(i,j)=real(i-5,wp)/4
         natural(i,j)=(low(j)+high(j))/2+expected(i,j)*(high(j)-low(j))/2
      end do
   end do
   call encode_variables(natural,low,high,coded)
   call decode_variables(expected,low,high,decoded)
   call decode_variables(coded,low,high,physical)
   do j=1,3
      do i=1,9
         call check(coded(i,j),expected(i,j))
         call check(decoded(i,j),natural(i,j))
         call check(physical(i,j),natural(i,j))
      end do
   end do
   print '(a)', '27 experimental factor coordinates: encoding, decoding and round trips checked.'
   print '(a)', 'PASS fstats-experimental-factor-coding-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine probability_check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite probability'
      if(abs(actual-expected)>2.e-9_wp*max(1.e-30_wp,abs(expected))) then
         print *, 'Actual probability, expected:',actual,expected
         error stop 'Independent probability reference'
      end if
   end subroutine
   subroutine insertion_sort(x)
      real(wp),intent(inout)::x(:)
      real(wp)::value
      integer::i,j
      do i=2,size(x)
         value=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=value) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=value
      end do
   end subroutine
   function local_median(sorted) result(value)
      real(wp),intent(in)::sorted(:)
      real(wp)::value
      integer::n
      n=size(sorted);value=(sorted((n+1)/2)+sorted(n/2+1))/2
   end function
end program
