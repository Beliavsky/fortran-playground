! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_descriptive_statistics,only: &
      covariance
   implicit none
   real(wp),allocatable::x(:),y(:),sorted(:),work(:),distances(:)
   real(wp),parameter::quantiles(*)=[0._wp,0.1_wp,0.25_wp,0.5_wp,0.75_wp,0.9_wp,1._wp]
   real(wp)::value,position,fraction,average,other_average,p,expected
   integer::n,i,j,k,variant,cut
   do n=2,33
      allocate(x(n),y(n),sorted(n),work(n),distances(n))
      do variant=1,3
         do i=1,n
            x(i)=real(modulo(7*i+3*n,17)-8,wp)/4
            y(i)=real(modulo(5*i,11)-5,wp)/8
         end do
         select case(variant)
         case(1)
            x=x+1.25_wp
         case(2)
            x=-2*x-0.5_wp
         case(3)
            x=0.5_wp*x+3
         end select
         sorted=x;call insertion_sort(sorted)
         average=sum(x)/n;other_average=sum(y)/n
         expected=sum((x-average)*(y-other_average))/real(n-1,wp)
         call check(covariance(x,y),expected);call check(covariance(y,x),expected)
         call check(covariance(x,2*x+1),2*sum((x-average)**2)/real(n-1,wp))
      end do
      deallocate(x,y,sorted,work,distances)
   end do
   print '(a)', 'Three finite dyadic data families, lengths through 33, independently checked.'
   print '(a)', 'PASS fstats-paired-covariances-reference'
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
