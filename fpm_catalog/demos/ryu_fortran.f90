program main
   use iso_fortran_env, only: real64,int64
   use ryu, only: d2shortest
   implicit none
   real(real64), parameter :: values(6)=[.1_real64,-0._real64,acos(-1._real64), &
      1e-100_real64,1e100_real64,nearest(1._real64,1._real64)]
   real(real64) :: restored
   character(:), allocatable :: text
   integer :: i
   do i=1,size(values)
      text=d2shortest(values(i))
      read(text,*) restored
      if (transfer(restored,0_int64)/=transfer(values(i),0_int64)) error stop 'Round trip failed'
      print '(a)', text
   end do
   print *, 'All values round-trip with identical bits, including negative zero.'
   print *, 'PASS ryu_fortran'
end program
