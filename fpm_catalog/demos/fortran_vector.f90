program editable_integer_vector
   use fortran_vector, only: vector_int,size
   implicit none
   type(vector_int)::values
   integer::i,last
   call values%init(2)
   do i=1,8
      call values%append(i)
   end do
   if(size(values)/=8) error stop 'Growth lost elements'
   do i=1,8
      if(values%get(i)/=i) error stop 'Growth changed an element'
   end do
   call values%append([3,1,9,9])
   call values%unique()
   if(size(values)/=9) error stop 'Duplicate removal failed'
   do i=1,9
      if(values%get(i)/=i) error stop 'Unique order was not preserved'
   end do
   call values%remove(4)
   call values%delete(2)
   last=values%pop()
   if(last/=9) error stop 'Wrong final element'
   if(size(values)/=6) error stop 'Wrong edited size'
   do i=1,6
      block
         integer,parameter::expected(6)=[1,3,5,6,7,8]
         if(values%get(i)/=expected(i)) error stop 'Wrong edited contents'
      end block
   end do
   call values%cut()
   print '(a)', 'After growth, unique, remove, delete and pop:'
   call values%write()
   call values%clear()
   print *, 'PASS fortran_vector'
end program editable_integer_vector
