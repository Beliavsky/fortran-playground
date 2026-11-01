! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program any_reference
   use, intrinsic :: iso_fortran_env, only: int32,real64
   use any_t, only: any_type,assignment(=),as_char
   implicit none
   integer :: fixture,i,entries
   entries=0
   do fixture=0,31
      block
         type(any_type) :: box(6)
         integer(int32) :: scalar
         real(real64) :: real_scalar
         logical :: flag
         character(:), allocatable :: text,expected_text
         integer(int32), allocatable :: source(:),restored(:)
         real(real64), allocatable :: matrix(:,:),restored_matrix(:,:)
         expected_text=repeat('ab ',fixture)
         box(1)=int(7*fixture-103,int32); scalar=box(1)
         box(2)=real(fixture-17,real64)/8; real_scalar=box(2)
         box(3)=modulo(fixture,2)==0; flag=box(3)
         box(4)=expected_text; text=as_char(box(4))
         if (scalar/=7*fixture-103 .or. real_scalar/=real(fixture-17,real64)/8) error stop 'any scalar reference'
         if (flag .neqv. (modulo(fixture,2)==0)) error stop 'any logical reference'
         if (len(text)/=len(expected_text) .or. text/=expected_text) error stop 'any character reference'
         source=[(int(3*i-fixture,int32),i=1,fixture)]
         matrix=reshape([(real(i-fixture,real64)/8,i=1,2*fixture)],[2,fixture])
         box(5)=source; box(6)=matrix
         ! Wrapped values must own copies rather than alias mutable inputs.
         source=999; matrix=999
         restored=box(5); restored_matrix=box(6)
         if (size(restored)/=fixture .or. any(shape(restored_matrix)/=[2,fixture])) error stop 'any array shape'
         do i=1,fixture
            if (restored(i)/=3*i-fixture) error stop 'any integer array reference'
         end do
         if (any(reshape(restored_matrix,[2*fixture])/= &
            [(real(i-fixture,real64)/8,i=1,2*fixture)])) error stop 'any matrix reference'
         entries=entries+4+3*fixture
      end block
   end do
   if (entries/=1616) error stop 'any reference counts'
   print '(a)', '32 fresh typed-value groups; 1616 scalar/array value references, including empty arrays and strings.'
   print '(a)', 'INT32, dyadic REAL64, logical and character scalars; owned rank-1/rank-2 array copies.'
   print '(a)', 'Assignment into already populated buffers, type mismatches and arbitrary ranks/kinds unverified.'
   print '(a)', 'PASS any-values-reference'
end program
