! Example: Matrix multiplication
program main
   implicit none
   real :: a(2,2), b(2,2), c(2,2)
   integer :: i
   a = reshape([1.0, 2.0, 3.0, 4.0], [2,2])
   b = reshape([2.0, 0.0, 0.0, 2.0], [2,2])
   c = matmul(a,b)
   do i = 1, 2
      print *, c(i,:)
   end do
end program main
