program main
   use ftlDynArrayIntModule, only: ftlDynArrayInt
   use ftlHashMapStringIntModule, only: ftlHashMapStringInt
   implicit none
   type(ftlDynArrayInt) :: array
   type(ftlHashMapStringInt) :: counts
   integer :: i, removed
   call array%New()
   do i = 1, 8
      call array%PushBack(i*i)
   end do
   if (array%Size() /= 8) error stop 'array size'
   if (any(array%data /= [(i*i,i=1,8)])) error stop 'array values'
   print '(a,8i4)', 'Growing integer array: ', array%data
   removed = array%PopBack()
   if (removed /= 64 .or. array%Size() /= 7) error stop 'pop'
   call counts%New(10)
   call counts%Set('red',2)
   call counts%Set('blue',3)
   call counts%Set('red',5)
   if (counts%Size() /= 2) error stop 'map size'
   if (.not. counts%Has('red') .or. counts%Has('missing')) error stop 'map presence'
   if (counts%Get('red') /= 5 .or. counts%Get('blue') /= 3) error stop 'map values'
   print '(a,i0)', 'red: ', counts%Get('red')
   print '(a,i0)', 'blue: ', counts%Get('blue')
   call counts%Erase('blue')
   if (counts%Has('blue') .or. counts%Size() /= 1) error stop 'map erase'
   call counts%Delete()
   call array%Delete()
   print '(a)', 'PASS ftl'
end program main
