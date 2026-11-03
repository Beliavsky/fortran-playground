! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_doe_designs,only: &
      get_full_factorial_matrix_size,full_factorial
   implicit none
   integer,allocatable::levels(:),design(:,:),seen(:)
   integer::factors,variant,rows,cols,expected_rows,i,j,k,key,stride,a,b
   do factors=1,4
      allocate(levels(factors))
      do variant=0,2
         levels=[(1+modulo(variant+i,4),i=1,factors)]
         expected_rows=product(levels)
         call get_full_factorial_matrix_size(levels,rows,cols)
         if(rows/=expected_rows.or.cols/=factors) error stop 'Design dimensions'
         allocate(design(rows,cols),seen(rows));seen=0
         call full_factorial(levels,design)
         do i=1,rows
            key=1;stride=1
            do j=1,cols
               if(design(i,j)<1.or.design(i,j)>levels(j)) error stop 'Design level'
               key=key+(design(i,j)-1)*stride;stride=stride*levels(j)
            end do
            seen(key)=seen(key)+1
         end do
         if(any(seen/=1)) error stop 'Cartesian product coverage'
         do j=1,cols
            do a=1,levels(j)
               if(count(design(:,j)==a)/=rows/levels(j)) error stop 'Marginal balance'
               do k=j+1,cols
                  do b=1,levels(k)
                     if(count(design(:,j)==a.and.design(:,k)==b)/=rows/(levels(j)*levels(k))) &
                        error stop 'Pairwise balance'
                  end do
               end do
            end do
         end do
         deallocate(design,seen)
      end do
      deallocate(levels)
   end do
   print '(a)', '12 full-factorial designs: Cartesian coverage and level balance checked.'
   print '(a)', 'PASS fstats-full-factorial-designs-reference'
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
