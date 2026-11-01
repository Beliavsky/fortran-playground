! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program bounds_reference
   use array_range, only: array2d_range_type,to_array2d_range
   implicit none
   type(array2d_range_type) :: bounds
   integer, allocatable :: values(:,:)
   integer :: lo1,lo2,n1,n2,i,j,total,expected,visited,cases,entries
   cases=0; entries=0
   do lo1=-3,3
      do lo2=-3,3
         do n1=1,4
            do n2=1,4
               allocate(values(lo1:lo1+n1-1,lo2:lo2+n2-1))
               bounds=to_array2d_range([lbound(values),ubound(values)])
               if (any(bounds%to_array()/=[lo1,lo2,lo1+n1-1,lo2+n2-1])) error stop 'bounds literal reference'
               if (bounds%rank(1)%lower/=lo1 .or. bounds%rank(2)%lower/=lo2) error stop 'lower bounds'
               if (bounds%rank(1)%upper/=lo1+n1-1 .or. bounds%rank(2)%upper/=lo2+n2-1) error stop 'upper bounds'
               total=0; visited=0
               do j=bounds%rank(2)%lower,bounds%rank(2)%upper
                  do i=bounds%rank(1)%lower,bounds%rank(1)%upper
                     values(i,j)=i+10*j; total=total+values(i,j); visited=visited+1
                  end do
               end do
               expected=n2*n1*(2*lo1+n1-1)/2+10*n1*n2*(2*lo2+n2-1)/2
               if (visited/=n1*n2 .or. total/=expected) error stop 'closed-form bounds traversal'
               entries=entries+visited; cases=cases+1
               deallocate(values)
            end do
         end do
      end do
   end do
   if (cases/=784 .or. entries/=4900) error stop 'bounds counts'
   print '(a)', '784 nonempty rank-2 arrays; 3136 bound entries and 4900 traversed elements checked.'
   print '(a)', 'Negative/zero/positive origins, asymmetric shapes and independent arithmetic-progression sums.'
   print '(a)', 'Zero extents, invalid bound arrays and vector/tensor aggregate constructors unverified.'
   print '(a)', 'PASS array-bounds-reference'
end program
