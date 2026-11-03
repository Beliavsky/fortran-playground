! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_descriptive_statistics,only: &
      pooled_variance
   implicit none
   real(wp),allocatable::variances(:)
   integer,allocatable::counts(:)
   real(wp)::expected
   integer::groups,variant,i
   do groups=2,6
      allocate(variances(groups),counts(groups))
      do variant=1,3
         do i=1,groups
            variances(i)=real(i*i,wp)/4*2._wp**(variant-2)
            counts(i)=2+modulo(3*i+variant,9)
         end do
         expected=sum(real(counts-1,wp)*variances)/real(sum(counts-1),wp)
         call check(pooled_variance(variances,counts),expected)
      end do
      deallocate(variances,counts)
   end do
   print '(a)', '15 pooled-variance summaries independently checked.'
   print '(a)', 'PASS fstats-pooled-group-variances-reference'
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
