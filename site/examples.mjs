export const examples = {
  sum: `program main
   implicit none
   integer :: i, total
   total = 0
   do i = 1, 10
      total = total + i*i
   end do
   print *, total
end program main
`,
  matrix: `program main
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
`,
  roots: `program main
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64) :: a, b, c, discriminant
   a = 1.0_real64
   b = -3.0_real64
   c = 2.0_real64
   discriminant = b*b - 4*a*c
   print *, (-b + sqrt(discriminant))/(2*a)
   print *, (-b - sqrt(discriminant))/(2*a)
end program main
`,
  helper: `program main
   use, intrinsic :: iso_fortran_env, only: real64
   use python_mod, only: mean
   implicit none
   real(real64) :: x(3) = [1.0_real64, 2.0_real64, 3.0_real64]
   print *, mean(x)
end program main
`,
};
