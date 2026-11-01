! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program vector_reference
   use fortran_vector, only: vector_int,size
   implicit none
   type(vector_int) :: vector
   integer :: reference(256),batch(4),n,scenario,i,j,k,value,removed,operations,entries
   operations=0; entries=0
   do scenario=1,12
      call vector%init(1+modulo(scenario,5)); n=0
      do i=1,96
         value=modulo(i*(scenario+2),19)-9
         call vector%append(value); n=n+1; reference(n)=value; call check()
      end do
      do i=1,6
         batch=[(modulo(i*j+scenario,23)-11,j=1,4)]
         call vector%append(batch); reference(n+1:n+4)=batch; n=n+4; call check()
      end do
      ! A fixed value argument avoids passing an alias of the vector's own storage.
      call vector%remove(0); k=0
      do i=1,n
         if (reference(i)==0) cycle
         k=k+1; reference(k)=reference(i)
      end do
      n=k; call check()
      do i=1,12
         j=1+modulo(i*7,n)
         call vector%delete(j); reference(j:n-1)=reference(j+1:n); n=n-1; call check()
      end do
      call vector%cut(); call check()
      do while(n>0)
         removed=vector%pop()
         if (removed/=reference(n)) error stop 'vector pop reference'
         n=n-1; call check()
      end do
      call vector%clear()
      call vector%init(1)
      call vector%append([scenario,-scenario]); reference(1:2)=[scenario,-scenario]; n=2; call check()
      call vector%clear()
   end do
   print '(a,i0,a,i0)', '12 vector edit traces; checked operations: ',operations,'; element references: ',entries
   print '(a)', 'Scalar/batch append, growth, fixed-value removal, positional delete, cut, pop-to-empty and reinitialization.'
   print '(a)', 'Unique, sorting, invalid indices and self-aliased remove arguments unverified.'
   print '(a)', 'PASS vector-edits-reference'
contains
   subroutine check()
      integer :: j
      if (size(vector)/=n) error stop 'vector size reference'
      do j=1,n
         if (vector%get(j)/=reference(j)) error stop 'vector element reference'
      end do
      operations=operations+1; entries=entries+n
   end subroutine
end program
